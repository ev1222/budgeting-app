# Personal Budgeting Application

A Python-based budgeting application that integrates Google Sheets data with a local SQLite database, featuring a GraphQL API and Streamlit frontend.

## Features

- **Google Sheets Integration**: Automatically sync expense data from Google Sheets
- **GraphQL API**: Flexible data querying with filtering capabilities
- **Local Database**: SQLite storage with SQLModel ORM
- **Web Interface**: Simple Streamlit-based frontend
- **Data Models**: Track purchases, trips, and monthly budget totals

## Architecture

### Backend (`backend/`)
- **FastAPI + GraphQL**: Uses Strawberry GraphQL for API layer
- **API Layer**: GraphQL schema, types, and filters
- **Database Layer**: SQLModel ORM with SQLite
- **Google Integration**: Google Sheets API handling
- **Data Synchronization**: Automated data fetching and syncing
- **Logging**: Centralized logging configuration

### Frontend (`frontend/`)
- **Streamlit**: Simple web interface for data visualization

## Setup

### Prerequisites
- Python 3.8+
- Google Sheets with expense data
- Google API credentials

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd budgeting
   ```

2. Install dependencies:
   ```bash
   pip install fastapi strawberry-graphql sqlmodel streamlit google-api-python-client uvicorn
   ```

3. Set up Google API credentials:
   - Create a project in Google Cloud Console
   - Enable Google Sheets API
   - Download credentials and place in `backend/google/google_api_info/credentials.json`

4. Configure environment variables in `.env`:
   - Database URL
   - Google API scopes
   - Sheet query patterns

## Usage

### Running the Backend
```bash
cd backend
uvicorn main:app --reload
```
The GraphQL API will be available at `http://localhost:8000/graphql`

### Running the Frontend
```bash
cd frontend
streamlit run app.py
```

### Data Synchronization
The application automatically fetches data from Google Sheets and stores it in the local SQLite database (`database/spending.db`).

## Data Models

- **Purchases**: Individual spending transactions
- **Trips**: Travel periods with associated expenses
- **Totals**: Monthly budget summaries

## Project Structure

```
budgeting/
├── backend/
│   ├── api/           # GraphQL schema, types, and filters
│   ├── db/            # Database models and connection
│   ├── google/        # Google Sheets API integration
│   ├── logs/          # Logging configuration
│   ├── sync/          # Data synchronization logic
│   ├── config.py      # Configuration constants
│   └── main.py        # FastAPI application entry point
├── frontend/
│   └── app.py         # Streamlit application
├── database/
│   └── spending.db    # SQLite database
└── data/              # CSV and JSON data files
```

## Development

See `CLAUDE.md` for detailed development guidance and architectural patterns.

## License

This is a personal project and is not licensed for public use.