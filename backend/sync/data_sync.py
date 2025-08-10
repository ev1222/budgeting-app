"""
Data synchronization utilities for importing Google Sheets data into the database.
"""
from datetime import datetime, date
from collections import defaultdict
from typing import Any, Optional

from db.database import save_data
from db.models import Purchases, Trips, Totals, generate_purchase_id, generate_trip_id, generate_total_id
from sync.Expenses import Expenses
from config import (
    DEFAULT_NA,
    DATE_IDX,
    AMOUNT_IDX,
    CATEGORY_IDX,
    DESCRIPTION_IDX,
    COMMENT_IDX
)
from logs.logger_config import configure_logging

logger = configure_logging()


def parse_date(date_string: str) -> date:
    """Convert date string to date object, supporting both 2 and 4 digit years."""
    try:
        return datetime.strptime(date_string, "%m/%d/%Y").date()  # default to four digit year
    except ValueError:
        return datetime.strptime(date_string, "%m/%d/%y").date()  # fall back to two digit year


def parse_amount(amount_str: str) -> float:
    """Convert amount string (e.g., '$12.34' or '-$5.67') to a float."""
    return float(amount_str.replace("$", "").replace(",", ""))


def parse_percentage(percent_str: str) -> float:
    """Convert percentage string (e.g., '168%') to a float."""
    return float(percent_str.replace("%", "")) / 100


def extract_date_from_sheet_name(sheet_name: str) -> date:
    """Extract month/year from sheet name and return as date object (first of month)."""
    # Extract the date part after "Spending " (e.g., "Spending 1/24" -> "1/24")
    date_part = sheet_name.replace("Spending ", "")
    
    # Add day and use existing parse_date function (e.g., "1/24" -> "1/1/24")
    full_date_str = f"1/{date_part}"
    
    return parse_date(full_date_str)


def is_date_string_date_range(date_str: str) -> bool:
    """Check if date string represents a date range (contains '-')."""
    return "-" in date_str



def process_spending_data(expenses: Expenses, spending_ranges: list[str]) -> list[dict[str, Any]]:
    """Process spending data from Google Sheets ranges into database format."""
    rows = []
    for range in spending_ranges:
        sheet_name = expenses.get_sheet_name_from_range(range)
        data = [i for items in expenses.get_data(range).values() for i in items[1:]]
        for row_index, d in enumerate(data):
            rows.append({
                "id": generate_purchase_id(sheet_name, row_index),
                "date": parse_date(d[DATE_IDX]) if not is_date_string_date_range(d[0]) else d[0],
                "amount": parse_amount(d[AMOUNT_IDX]),
                "category": d[CATEGORY_IDX],
                "description": d[DESCRIPTION_IDX],
                "comment": d[COMMENT_IDX] if len(d) == 5 else None
            })
    return rows


def process_trip_data(spending_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Extract and process trip data from spending rows."""
    trips = [r for r in spending_rows if not isinstance(r["date"], date)]

    aggregated_trips = defaultdict(lambda: {"name": None, "start_date": None, "end_date": None, "comment": set()})

    for t in trips:
        name = t["description"].split(" ")[0]
        start_date, end_date = map(parse_date, t["date"].split("-"))
        
        key = (name, start_date, end_date)

        aggregated_trips[key]["name"] = name
        aggregated_trips[key]["start_date"] = start_date
        aggregated_trips[key]["end_date"] = end_date
        if t["comment"]:
            aggregated_trips[key]["comment"].add(t["comment"])

    # Convert comments set to a string and build final list
    trip_rows = [
        {
            "id": generate_trip_id(trip["name"], trip["start_date"], trip["end_date"]),
            "name": trip["name"],
            "start_date": trip["start_date"],
            "end_date": trip["end_date"],
            "comment": " | ".join(trip["comment"]) if trip["comment"] else None
        }
        for trip in aggregated_trips.values()
    ]
    
    return trip_rows


def process_trip_spending_data(expenses: Expenses, trip_spending_ranges: list[str], processed_trips: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Process trip-specific spending data from Google Sheets."""
    rows = []
    
    # Create lookup from processed trips data
    trip_lookup = {}
    for trip in processed_trips:
        trip_lookup.setdefault(trip["name"], []).append(trip)
    
    for range in trip_spending_ranges:
        for sheet_name, purchases in expenses.get_data(range).items():
            trip_name = sheet_name.split(" ")[0]
            for row_index, p in enumerate(purchases[1:]):
                purchase_date = parse_date(p[0])
                
                # Find matching trip ID
                trip_id = None
                if trip_name in trip_lookup:
                    for trip in trip_lookup[trip_name]:
                        if trip["start_date"] <= purchase_date <= trip["end_date"]:
                            trip_id = trip["id"]
                            break
                
                rows.append({
                    "id": generate_purchase_id(sheet_name, row_index),
                    "date": purchase_date,
                    "amount": parse_amount(p[1]),
                    "category": p[2],
                    "description": p[3],
                    "comment": p[4] if len(p) == 5 else None,
                    "trip_id": trip_id
                })
    return rows


def process_totals_data(expenses: Expenses, totals_ranges: list[str]) -> list[dict[str, Any]]:
    """Process totals data from Google Sheets ranges into database format."""
    rows = []
    for range in totals_ranges:
        sheet_name = expenses.get_sheet_name_from_range(range)
        data = [i for items in expenses.get_data(range).values() for i in items[1:]]
        for d in data:
            rows.append({
                "id": generate_total_id(sheet_name, d[0]),
                "date": extract_date_from_sheet_name(sheet_name),
                "type": d[0],
                "amount": parse_amount(d[1]),
                "progress": parse_percentage(d[2]),
                "budgeted": parse_amount(d[3]),
            })
    return rows


def process_trip_totals_data(expenses: Expenses, trip_totals_ranges: list[str], processed_trips: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Process trip totals data from Google Sheets ranges into database format."""
    rows = []
    
    # Create lookup from processed trips data
    trip_lookup = {trip["name"]: trip for trip in processed_trips}
    
    for range in trip_totals_ranges:
        sheet_name = expenses.get_sheet_name_from_range(range)
        trip_name = sheet_name.split(" ")[0]  # Extract trip name from sheet name
        
        # Find the corresponding trip to get date and ID
        trip = trip_lookup.get(trip_name)
        if not trip:
            logger.warning(f"Trip '{trip_name}' not found for totals sheet '{sheet_name}'")
            continue
            
        data = [i for items in expenses.get_data(range).values() for i in items[1:]]
        for d in data:
            rows.append({
                "id": generate_total_id(sheet_name, d[0], trip_name),
                "date": trip["start_date"],  # Use trip start date
                "type": d[0],
                "amount": parse_amount(d[1]),
                "progress": DEFAULT_NA, # no budget for travel
                "budgeted": DEFAULT_NA, # no budget for travel
                "trip": trip["id"]  # Use trip ID instead of name
            })
    return rows


def sync_google_sheets_data(year: str, month: Optional[str] = None) -> dict[str, int]:
    """
    Main function to sync all Google Sheets data to the database.
    
    Parameters
    ----------
    year : str
        Year string to sync data for.
    month : Optional[str]
        Month string to sync data for. If provided, only that month will be synced.
        If not provided, entire year will be synced.
        
    Returns
    -------
    dict
        dictionary with counts of imported records,
    """
    # Initialize Expenses object
    expenses = Expenses(year)
    
    if month:
        logger.info(f"Starting Google Sheets sync for {month}/{year}")
        month_int = int(month)
        ranges = expenses.construct_ranges(start_month=month_int, end_month=month_int)
    else:
        logger.info(f"Starting Google Sheets sync for year {year}")
        ranges = expenses.construct_ranges()
    
    spending_ranges = ranges.get('spending_ranges', [])
    totals_ranges = ranges.get('totals_ranges', [])
    trip_spending_ranges = ranges.get('trip_spending_ranges', [])
    trip_totals_ranges = ranges.get('trip_totals_ranges', [])
    
    spending_rows = process_spending_data(expenses, spending_ranges)

    # Get regular purchases (non-trip date ranges)
    purchases = [r for r in spending_rows if isinstance(r["date"], date)]
    totals = process_totals_data(expenses, totals_ranges)
    trips = process_trip_data(spending_rows)
    trip_purchases = process_trip_spending_data(expenses, trip_spending_ranges, trips)
    trip_totals = process_trip_totals_data(expenses, trip_totals_ranges, trips)
    
    # Save all data
    save_data(purchases, Purchases)
    save_data(trip_purchases, Purchases)
    save_data(trips, Trips)
    save_data(totals, Totals)
    save_data(trip_totals, Totals)
    
    result = {
        "trips": len(trips),
        "regular_purchases": len(purchases),
        "trip_purchases": len(trip_purchases),
        "totals": len(totals),
        "trip_totals": len(trip_totals),
        "total_purchases": len(purchases) + len(trip_purchases)
    }
    
    logger.info(f"Sync completed: {result}")
    return result