import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from datetime import date
from unittest.mock import Mock, patch
from typing import List, Optional

from db.models import Purchases, Trips, Totals


@pytest.fixture
def sample_purchases() -> List[Purchases]:
    """Sample purchases data for testing."""
    return [
        Purchases(
            id="purchase1",
            date=date(2024, 1, 15),
            amount=25.50,
            category="Food",
            description="Lunch at restaurant",
            comment="Good meal",
            trip_id=None
        ),
        Purchases(
            id="purchase2",
            date=date(2024, 1, 20),
            amount=100.00,
            category="Transportation",
            description="Gas",
            comment=None,
            trip_id="trip1"
        ),
        Purchases(
            id="purchase3",
            date=date(2024, 2, 10),
            amount=75.25,
            category="Shopping",
            description="Groceries",
            comment=None,
            trip_id=None
        ),
    ]


@pytest.fixture
def sample_trips() -> List[Trips]:
    """Sample trips data for testing."""
    return [
        Trips(
            id="trip1",
            name="Weekend Getaway",
            start_date=date(2024, 1, 19),
            end_date=date(2024, 1, 21),
            comment="Fun trip"
        ),
        Trips(
            id="trip2",
            name="Business Trip",
            start_date=date(2024, 2, 5),
            end_date=date(2024, 2, 8),
            comment="Work conference"
        ),
    ]


@pytest.fixture
def sample_totals() -> List[Totals]:
    """Sample totals data for testing."""
    return [
        Totals(
            id="total1",
            date=date(2024, 1, 31),
            type="Monthly",
            amount=1250.00,
            progress=0.75,
            budgeted=1667.00,
            trip_id=None
        ),
        Totals(
            id="total2",
            date=date(2024, 1, 31),
            type="Trip",
            amount=350.00,
            progress=1.0,
            budgeted=350.00,
            trip_id="trip1"
        ),
    ]


@pytest.fixture
def mock_query_data():
    """Mock the query_data function from database module."""
    with patch('api.schema.query_data') as mock:
        yield mock


@pytest.fixture
def mock_sync_google_sheets():
    """Mock the sync_google_sheets_data function."""
    with patch('api.schema.sync_google_sheets_data') as mock:
        yield mock


@pytest.fixture(autouse=True)
def mock_google_api():
    """Automatically mock all Google API calls to prevent rate limiting."""
    with patch('sync.data_sync.sync_google_sheets_data') as mock_sync, \
         patch('api.schema.sync_google_sheets_data') as mock_api_sync, \
         patch('db.database.query_data') as mock_query, \
         patch('api.schema.query_data') as mock_api_query:
        mock_return = {
            "trips": 0,
            "regular_purchases": 0,
            "trip_purchases": 0,
            "total_purchases": 0
        }
        mock_sync.return_value = mock_return
        mock_api_sync.return_value = mock_return
        mock_query.return_value = []  # Return empty list for all queries by default
        mock_api_query.return_value = []  # Return empty list for all queries by default
        yield