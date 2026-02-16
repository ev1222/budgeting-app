import strawberry
from typing import List, Optional
from db.database import query_data
from sync.data_sync import sync_google_sheets_data

from .types import PurchasesType, TripsType, TotalsType
from .filters import PurchaseFilterInput, TripFilterInput, TotalFilterInput
from db.models import Purchases, Trips, Totals


def _build_date_range_filter(filter_args: dict, field_name: str, start_date, end_date):
    """Add date range filter conditions to filter_args."""
    if start_date and end_date:
        filter_args[field_name] = [(">=", start_date), ("<=", end_date)]
    elif start_date:
        filter_args[field_name] = (">=", start_date)
    elif end_date:
        filter_args[field_name] = ("<=", end_date)


def _build_amount_range_filter(filter_args: dict, field_name: str, min_amount, max_amount):
    """Add amount range filter conditions to filter_args."""
    if min_amount and max_amount:
        filter_args[field_name] = [(">=", min_amount), ("<=", max_amount)]
    elif min_amount:
        filter_args[field_name] = (">=", min_amount)
    elif max_amount:
        filter_args[field_name] = ("<=", max_amount)


@strawberry.type
class Query:
    @strawberry.field
    def purchases(self, filters: Optional[PurchaseFilterInput] = None) -> List[PurchasesType]:
        filter_args = {}

        if filters:
            if filters.categories:
                filter_args["category"] = filters.categories
            if filters.descriptions:
                filter_args["description"] = filters.descriptions
            if filters.trip_id:
                filter_args["trip_id"] = filters.trip_id

            _build_date_range_filter(filter_args, "date", filters.start_date, filters.end_date)
            _build_amount_range_filter(filter_args, "amount", filters.min_amount, filters.max_amount)

        return query_data(Purchases, filters=filter_args)

    @strawberry.field
    def trips(self, filters: Optional[TripFilterInput] = None) -> List[TripsType]:
        filter_args = {}

        if filters:
            if filters.names:
                filter_args["name"] = filters.names

            _build_date_range_filter(filter_args, "start_date", filters.start_date, filters.end_date)

        return query_data(Trips, filters=filter_args)

    @strawberry.field
    def totals(self, filters: Optional[TotalFilterInput] = None) -> List[TotalsType]:
        filter_args = {}

        if filters:
            if filters.types:
                filter_args["type"] = filters.types
            if filters.trip_id:
                filter_args["trip_id"] = filters.trip_id

            _build_date_range_filter(filter_args, "date", filters.start_date, filters.end_date)
            _build_amount_range_filter(filter_args, "amount", filters.min_amount, filters.max_amount)

        return query_data(Totals, filters=filter_args)


@strawberry.type
class SyncResult:
    trips: int
    regular_purchases: int
    trip_purchases: int
    total_purchases: int
    success: bool
    message: str

@strawberry.type
class Mutation:
    @strawberry.field
    def sync_google_sheets(self, year: str, month: Optional[str] = None) -> SyncResult:
        try:
            result = sync_google_sheets_data(year, month)
            sync_period = f"{month}/{year}" if month else f"year {year}"
            return SyncResult(
                trips=result["trips"],
                regular_purchases=result["regular_purchases"],
                trip_purchases=result["trip_purchases"],
                total_purchases=result["total_purchases"],
                success=True,
                message=f"Successfully synced data for {sync_period}"
            )
        except Exception as e:
            return SyncResult(
                trips=0,
                regular_purchases=0,
                trip_purchases=0,
                total_purchases=0,
                success=False,
                message=f"Error syncing data: {str(e)}"
            )


schema = strawberry.Schema(query=Query, mutation=Mutation)
