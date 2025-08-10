# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

This project uses Python and has no package manager configuration files, so dependencies should be installed manually:

- **Install dependencies**: Run `pip install` for each package as needed (fastapi, strawberry-graphql, sqlmodel, streamlit, google-api-python-client, etc.)
- **Run backend**: `cd backend && uvicorn main:app --reload` (FastAPI with GraphQL)
- **Run frontend**: `cd frontend && streamlit run app.py`
- **Database**: SQLite database located at `database/spending.db`

## Architecture Overview

This is a personal budgeting application that integrates Google Sheets data with a local database:

### Backend (`backend/`)
- **FastAPI + GraphQL**: Uses Strawberry GraphQL for API layer (`main.py`)
- **API Layer**: GraphQL schema, types, and filters (`api/schema.py`, `api/types.py`, `api/filters.py`)
- **Database Layer**: SQLModel for ORM with SQLite database (`db/models.py`, `db/database.py`)
- **Data Models**: Three main entities:
  - `Purchases`: Individual spending transactions
  - `Trips`: Travel periods with associated expenses  
  - `Totals`: Monthly budget summaries
- **Google Integration**: Google Sheets API handling (`google/google_api.py`) with credentials in `google/google_api_info/`
- **Data Synchronization**: `sync/Expenses.py` class and `sync/data_sync.py` for fetching and syncing Google Sheets data
- **Logging**: Centralized logging configuration (`logs/logger_config.py`)

### Frontend (`frontend/`)
- **Streamlit**: Simple web interface (`app.py`) - currently minimal

### Data Flow
1. Google Sheets contain expense data organized by year
2. `sync/Expenses.py` class authenticates and fetches data using Google Sheets API
3. Data is processed and stored in SQLite via SQLModel using `sync/data_sync.py`
4. GraphQL API provides filtered access to data through `api/` modules
5. Frontend displays data via Streamlit

### Configuration
- Environment variables in `.env` (database URL, Google API scopes, sheet query patterns)
- Google API credentials stored in `backend/google/google_api_info/`
- Database constants and sheet ranges defined in `backend/config.py`

### Key Patterns
- Context manager pattern for database sessions (`get_db_session()`)
- Complex filtering system in `query_data()` supporting operators and IN clauses
- GraphQL resolvers with optional filtering (`PurchaseFilterInput`)
- Comprehensive logging throughout using configured logger

The codebase follows a clear separation between data access, business logic, and presentation layers with Google Sheets as the primary data source.