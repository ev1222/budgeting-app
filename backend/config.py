import os
from dotenv import load_dotenv

load_dotenv()

# DB
DB_URL = os.getenv("DATABASE_URL")

DEFAULT_NA = 0.0

DATE_IDX = 0
AMOUNT_IDX = 1
CATEGORY_IDX = 2
DESCRIPTION_IDX = 3
COMMENT_IDX = 4

PURCHASES_TABLE_NAME = "purchases"
TOTALS_TABLE_NAME = "totals"
TRIP_TABLE_NAME = "trips"

# Google API
SCOPES: list[str] = os.getenv("SCOPES_URLS").split(",") # Define the scopes required for Google API access
GOOGLE_INFO_API_DIR: str = "google_api_info" # Directory for storing Google API-related information
EXPENSE_SHEET_QUERY = os.getenv("EXPENSE_SHEET_QUERY") # Query for grabbing names and IDs of expense sheets

SPENDING_RANGE_KEY = "A1:E" # cells from which to retrieve data
TOTALS_RANGE_KEY = "F2:I9" # cells from which to retrieve data
TRIP_SPENDING_RANGE_KEY = "A1:E" # cells from which to retrieve data
TRIP_TOTALS_RANGE_KEY = "F2:G8" # cells from which to retrieve data

