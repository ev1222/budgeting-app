import os
from typing import Optional, List, Any, Dict, Tuple

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config import (
    SCOPES,
    GOOGLE_INFO_API_DIR,
    EXPENSE_SHEET_QUERY,
    SPENDING_RANGE_KEY,
    TOTALS_RANGE_KEY,
    TRIP_SPENDING_RANGE_KEY,
    TRIP_TOTALS_RANGE_KEY
)
from logs.logger_config import configure_logging

logger = configure_logging()


def authenticate_google_api() -> Optional[Credentials]:
    """
    Authenticates the user with the Google API and retrieves credentials.

    Attempts to load existing credentials from a token file. If no valid
    credentials are found, initiates the authorization flow to obtain new
    credentials. The credentials are saved for future use.

    Parameters
    ----------
    None

    Returns
    -------
    Optional[Credentials]
        The authenticated credentials for the Google API, or None if
        authentication fails.

    Raises
    ------
    Exception
        If an error occurs during the authorization flow that cannot be recovered from.
    """
    token_path = os.path.join(GOOGLE_INFO_API_DIR, "token.json")
    credentials_path = os.path.join(GOOGLE_INFO_API_DIR, "credentials.json")
    creds = None
    credentials_updated = False

    # Step 1: Try to load existing credentials
    if os.path.exists(token_path):
        try:
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
            logger.info("Loaded credentials from token file.")
        except Exception as e:
            logger.warning(f"Invalid token file: {e}")
            # Remove invalid token file
            try:
                os.remove(token_path)
            except OSError:
                pass  # Ignore if file already deleted

    # Step 2: Refresh expired credentials if possible
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            logger.info("Credentials refreshed successfully.")
            credentials_updated = True
        except Exception as e:
            logger.warning(f"Failed to refresh credentials: {e}")
            creds = None
            # Remove invalid token file
            try:
                os.remove(token_path)
            except OSError:
                pass

    # Step 3: Run authorization flow if no valid credentials
    if not creds or not creds.valid:
        if not os.path.exists(credentials_path):
            logger.error(f"Credentials file not found at {credentials_path}")
            return None
        
        try:
            logger.info("Starting authorization flow...")
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
            logger.info("Authorization successful.")
            credentials_updated = True
        except Exception as e:
            logger.error(f"Authorization flow failed: {e}")
            return None

    # Step 4: Save credentials if they were updated
    if credentials_updated:
        try:
            with open(token_path, "w") as token:
                token.write(creds.to_json())
            logger.info(f"Credentials saved to {token_path}")
        except IOError as e:
            logger.error(f"Failed to save credentials: {e}")
            # Don't fail the function if saving fails - credentials are still valid

    return creds


def get_expense_sheets_info(creds: Credentials, year: str) -> Optional[List[Dict[str, str]]]:
    """
    Retrieve Google Sheets files containing 'Evan Expenses {year}' from Google Drive.

    Parameters
    ----------
    creds : Credentials 
        The credentials object used to authenticate with Google Drive API.
    year : str
        The year of expenses of interest.

    Returns
    -------
    Optional[List[Dict[str, str]]]
        A list of dictionaries, each containing the name and ID of the matching spreadsheets,
        or None if no sheets are found or if an error occurs.

    Raises
    ------
    HttpError
        If an error occurs while communicating with the Google Drive API.
    Exception
        If an unexpected error occured. 
    """
    service = build('drive', 'v3', credentials=creds, cache_discovery=False) # cache_discovery is deprecated
    
    # Query to find Google Sheets files
    query = EXPENSE_SHEET_QUERY.format(year)
    
    try:
        # List files
        results = service.files().list(
            q=query,
            fields="files(id, name)",
        ).execute()
        items = results.get('files', [])
        
        if not items:
            logger.debug('No spreadsheets found.')
            return None
        
        # Print spreadsheet names and IDs
        for item in items:
            logger.debug(f"Spreadsheet Name: {item['name']}, ID: {item['id']}")
        
        return items  # Returns a list of dictionaries with spreadsheet names and IDs

    except HttpError as http_error:
        logger.error(f"HTTP error occurred: {http_error.resp.status} - {http_error._get_reason()}")
        raise
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise


def get_sheet_names(spreadsheet_id: str, creds) -> List[str]:
    """
    Retrieve the names of all sheets in a Google Spreadsheet.

    Parameters
    ----------
    spreadsheet_id : str
        The ID of the Google Spreadsheet.
    creds : google.auth.credentials.Credentials
        The credentials for accessing the Google Sheets API.

    Returns
    -------
    List[str]
        A list of sheet names.
    """
    try:
        # Build the service
        service = build('sheets', 'v4', credentials=creds, cache_discovery=False)
        
        # Fetch spreadsheet metadata
        spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        
        # Extract sheet names
        sheets = spreadsheet.get('sheets', [])
        sheet_names = [sheet['properties']['title'] for sheet in sheets]
        
        return sheet_names
    
    except Exception as e:
        logger.error(f"An error occurred while fetching sheet names: {e}")
        return []


def construct_ranges(sheet_names: list[str], year: str, start_month: int = 1, end_month: int = 12) -> Tuple[List[str], List[str]]:
    """
    Generate spending and total ranges formatted with the specified year for specific start/end months.
    Also constructs ranges for the trips taken in the time designated.

    Expense spreadsheets are expected to be formatted s.t. A1:D is spending; F2:I9 is metadata TOTALS table.
    Trip expense spreadsheets are expected to be formatted s.t. A1:D is spending; F2:G8 is metadata TOTALS table.

    Will dynamically select which sheets to build ranges for based on the input dates.

    Parameters
    ----------
    sheet_names : list[str]
        A list of all sheet names in budget.
    year : str
        The year of expenses for which to construct a range, e.g., '24'.
    start_month : int
        The first month of the range. Defaults to 1, January.
    end_month : int
        The final month of the range. Defaults to 12, December.

    Returns
    -------
    Tuple[List[str], List[str]]
        A tuple containing the spending and totals ranges, respectively, 
        i.e., (spending_ranges, totals_ranges)

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

    # Truncate year to last 2 digits
    if len(year) > 2:
        year = year[-2:]

    def in_range(sheet: str) -> bool:
        """
        Determines if an expense sheet is in the range specified.
        """
        for month in range(start_month, end_month+1):
            if f"{month}" in sheet:
                return True
        return False

    sheets = [s for s in sheet_names if in_range(s)]

    spending_sheets = [s for s in sheets if "Spending" in s]
    trip_sheets = [s for s in sheets if "Trip" in s]

    spending_ranges = [f"{s}!{SPENDING_RANGE_KEY}" for s in spending_sheets] # all spending
    totals_ranges = [f"{s}!{TOTALS_RANGE_KEY}" for s in spending_sheets] # get totals specifically
    trip_spending_ranges = [f"{s}!{TRIP_SPENDING_RANGE_KEY}" for s in trip_sheets]
    trip_totals_ranges = [f"{s}!{TRIP_TOTALS_RANGE_KEY}" for s in trip_sheets]

    return (spending_ranges, totals_ranges, trip_spending_ranges, trip_totals_ranges)


def get_sheet_name_from_range(range: str):
    """
    Helper function that splits a Sheets range at '!' to return just the sheet name.
    """
    return range.split('!')[0]