# SQLite Database Setup

This directory contains the SQLite database for the budgeting application.

## Database File

**spending.db** - Main SQLite database file
- Contains all application data (Purchases, Trips, Totals)
- Managed through SQLModel ORM in `backend/db/`
- Automatically created when the application first runs

## Database Schema

The database contains three main tables:

1. **purchases** - Individual spending transactions
   - Fields: id, date, amount, category, description, trip_id, etc.
   
2. **trips** - Travel periods with associated expenses
   - Fields: id, name, start_date, end_date, budget, etc.
   
3. **totals** - Monthly budget summaries
   - Fields: id, month, year, total_spent, budget, etc.

## Creating/Recreating the Database

If you need to recreate the database:

1. **Delete existing database**: Remove `spending.db` file
2. **Run the application**: The database will be automatically created with proper schema
3. **Sync data**: Use the data synchronization features to populate from Google Sheets

## Database Management

- **Schema defined in**: `backend/db/models.py` using SQLModel
- **Database connection**: `backend/db/database.py`
- **Data synchronization**: `backend/sync/data_sync.py`

## Security Note

The database file is ignored by git (see .gitignore) as it may contain sensitive financial information.