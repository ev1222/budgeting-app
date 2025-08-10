"""
Contains class definition of 'Expenses' object.
"""
from typing import Optional, Any

from googleapiclient.discovery import build

from config import (
    SPENDING_RANGE_KEY,
    TOTALS_RANGE_KEY,
    TRIP_SPENDING_RANGE_KEY,
    TRIP_TOTALS_RANGE_KEY
)
from google.google_api import authenticate_google_api, get_expense_sheets_info, get_sheet_names
from logs.logger_config import configure_logging

logger = configure_logging()

class Expenses():
    """
    Object representing Expense Sheet for a year and all spending therein.
    """
    def __init__(self, year: str):
        self.year = year
        self.creds = authenticate_google_api()
        self.spreadsheet_id = get_expense_sheets_info(self.creds, self.year)[0]["id"]
        self.sheets = get_sheet_names(self.spreadsheet_id, self.creds)

    def get_sheet_name_from_range(self, range: str):
        """
        Helper function that splits a Sheets range at '!' to return just the sheet name.
        """
        return range.split('!')[0]

    def get_data(
        self, range: str
    ) -> Optional[dict[str: list[list[Any]]]]:
        """
        Retrieves data from a specified range in a Google Sheets spreadsheet.

        This function uses the provided credentials to authenticate and access
        the Google Sheets API. It retrieves the values from the specified
        range within the spreadsheet identified by spreadsheet_id.

        Parameters
        ----------
        creds : Credentials
            The authenticated credentials for accessing the Google Sheets API.
        spreadsheet_id : str
            The ID of the Google Sheets spreadsheet to retrieve data from.
        range : str
            The A1 notation of the range to retrieve data from.
            E.g., [sheet name]![A-Z][1..9]-[A-Z][1..9]

        Returns
        -------
        Optional[dict[str: list[list[Any]]]]
            A dictionary of sheet name to list of lists containing the retrieved values from the specified
            range, or None if an error occurs.

        Raises
        -------
        Exception
            If an error occurs while calling the Sheets API or processing
            the response.
        """
        try:
            service = build("sheets", "v4", credentials=self.creds, cache_discovery=False) # cache_discovery is deprecated

            # Call the Sheets API
            sheet = service.spreadsheets()
            result = sheet.values().get(spreadsheetId=self.spreadsheet_id, range=range).execute()
            values = result.get("values", [])

            if not values:
                logger.debug("No data found.")
                return None  # Return None if no data is found.
            else:
                logger.debug(f"Got data from {range}.")
                data = {self.get_sheet_name_from_range(range): values}
                return data

        except Exception as e:
            logger.error(f"An error occurred while retrieving data: {e}.")
            raise


    def construct_ranges(self, start_month: int = 1, end_month: int = 12) -> dict[str, list[str]]:
        """
        Generate spending and total ranges formatted with the specified year for specific start/end months.
        Also constructs ranges for the trips taken in the time designated.

        Expense spreadsheets are expected to be formatted s.t. A1:D is spending; F2:I9 is metadata TOTALS table.
        Trip expense spreadsheets are expected to be formatted s.t. A1:D is spending; F2:G8 is metadata TOTALS table.

        Will dynamically select which sheets to build ranges for based on the input dates.

        Parameters
        ----------
        start_month : int
            The first month of the range. Defaults to 1, January.
        end_month : int
            The final month of the range. Defaults to 12, December.

        Returns
        -------
        dict[str, list[str]]
            Dictionary of resulting ranges, inlcuding\\
                spending_ranges
                totals_ranges
                trip_spending_ranges
                trip_totals_ranges

        Raises
        ------
        ValueError
            If `start_month` or `end_month` are not in the range of 1 to 12.
            If `start_month` is greater than `end_month`.
        """
        # Validate month parameters
        if not (1 <= start_month <= 12):
            raise ValueError(f"start_month must be between 1 and 12, got {start_month}.")
        if not (1 <= end_month <= 12):
            raise ValueError(f"end_month must be between 1 and 12, got {end_month}.")
        if start_month > end_month:
            raise ValueError(f"start_month ({start_month}) cannot be greater than end_month ({end_month}).")

        def in_range(sheet: str) -> bool:
            """
            Determines if an expense sheet is in the range specified.
            """
            for month in range(start_month, end_month+1):
                if f"{month}" in sheet:
                    return True
            return False

        in_range_sheets = [s for s in self.sheets if in_range(s)]

        spending_sheets = [s for s in in_range_sheets if "Spending" in s]
        trip_sheets = [s for s in in_range_sheets if "Trip" in s]

        spending_ranges = [f"{s}!{SPENDING_RANGE_KEY}" for s in spending_sheets] # all spending
        totals_ranges = [f"{s}!{TOTALS_RANGE_KEY}" for s in spending_sheets] # get totals specifically
        trip_spending_ranges = [f"{s}!{TRIP_SPENDING_RANGE_KEY}" for s in trip_sheets]
        trip_totals_ranges = [f"{s}!{TRIP_TOTALS_RANGE_KEY}" for s in trip_sheets]

        return {
            "spending_ranges": spending_ranges,
            "totals_ranges": totals_ranges,
            "trip_spending_ranges": trip_spending_ranges,
            "trip_totals_ranges": trip_totals_ranges
        }