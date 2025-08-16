import pytest
from datetime import date
from unittest.mock import Mock

from api.schema import Query, Mutation, get_field_name
from api.filters import PurchaseFilterInput, TripFilterInput, TotalFilterInput
from db.models import Purchases, Trips, Totals


class TestGetFieldName:
    """Test the get_field_name utility function."""
    
    def test_get_field_name_purchases(self):
        field_name = get_field_name(Purchases, Purchases.category)
        assert field_name == "category"
    
    def test_get_field_name_trips(self):
        field_name = get_field_name(Trips, Trips.name)
        assert field_name == "name"
    
    def test_get_field_name_totals(self):
        field_name = get_field_name(Totals, Totals.type)
        assert field_name == "type"
    
    def test_get_field_name_invalid_field_raises_error(self):
        with pytest.raises(ValueError, match="Field not found"):
            get_field_name(Purchases, "invalid_field")


class TestQuery:
    """Test the GraphQL Query class."""
    
    def setup_method(self):
        self.query = Query()
    
    def test_purchases_without_filters(self, mock_query_data, sample_purchases):
        mock_query_data.return_value = sample_purchases
        
        result = self.query.purchases()
        
        mock_query_data.assert_called_once_with(Purchases, filters={})
        assert result == sample_purchases
    
    def test_purchases_with_category_filter(self, mock_query_data, sample_purchases):
        mock_query_data.return_value = sample_purchases
        filters = PurchaseFilterInput(categories=["Food", "Transportation"])
        
        result = self.query.purchases(filters=filters)
        
        expected_filters = {"category": ["Food", "Transportation"]}
        mock_query_data.assert_called_once_with(Purchases, filters=expected_filters)
        assert result == sample_purchases
    
    def test_purchases_with_description_filter(self, mock_query_data, sample_purchases):
        mock_query_data.return_value = sample_purchases
        filters = PurchaseFilterInput(descriptions=["Lunch", "Gas"])
        
        result = self.query.purchases(filters=filters)
        
        expected_filters = {"description": ["Lunch", "Gas"]}
        mock_query_data.assert_called_once_with(Purchases, filters=expected_filters)
        assert result == sample_purchases
    
    def test_purchases_with_trip_id_filter(self, mock_query_data, sample_purchases):
        mock_query_data.return_value = sample_purchases
        filters = PurchaseFilterInput(trip_id="trip1")
        
        result = self.query.purchases(filters=filters)
        
        expected_filters = {"trip_id": "trip1"}
        mock_query_data.assert_called_once_with(Purchases, filters=expected_filters)
        assert result == sample_purchases
    
    def test_purchases_with_date_range_filter(self, mock_query_data, sample_purchases):
        mock_query_data.return_value = sample_purchases
        filters = PurchaseFilterInput(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31)
        )
        
        result = self.query.purchases(filters=filters)
        
        expected_filters = {
            "date": [(">=", date(2024, 1, 1)), ("<=", date(2024, 1, 31))]
        }
        mock_query_data.assert_called_once_with(Purchases, filters=expected_filters)
        assert result == sample_purchases
    
    def test_purchases_with_start_date_only(self, mock_query_data, sample_purchases):
        mock_query_data.return_value = sample_purchases
        filters = PurchaseFilterInput(start_date=date(2024, 1, 1))
        
        result = self.query.purchases(filters=filters)
        
        expected_filters = {"date": (">=", date(2024, 1, 1))}
        mock_query_data.assert_called_once_with(Purchases, filters=expected_filters)
        assert result == sample_purchases
    
    def test_purchases_with_end_date_only(self, mock_query_data, sample_purchases):
        mock_query_data.return_value = sample_purchases
        filters = PurchaseFilterInput(end_date=date(2024, 1, 31))
        
        result = self.query.purchases(filters=filters)
        
        expected_filters = {"date": ("<=", date(2024, 1, 31))}
        mock_query_data.assert_called_once_with(Purchases, filters=expected_filters)
        assert result == sample_purchases
    
    def test_purchases_with_amount_range_filter(self, mock_query_data, sample_purchases):
        mock_query_data.return_value = sample_purchases
        filters = PurchaseFilterInput(min_amount=10.0, max_amount=100.0)
        
        result = self.query.purchases(filters=filters)
        
        expected_filters = {
            "amount": [(">=", 10.0), ("<=", 100.0)]
        }
        mock_query_data.assert_called_once_with(Purchases, filters=expected_filters)
        assert result == sample_purchases
    
    def test_purchases_with_min_amount_only(self, mock_query_data, sample_purchases):
        mock_query_data.return_value = sample_purchases
        filters = PurchaseFilterInput(min_amount=10.0)
        
        result = self.query.purchases(filters=filters)
        
        expected_filters = {"amount": (">=", 10.0)}
        mock_query_data.assert_called_once_with(Purchases, filters=expected_filters)
        assert result == sample_purchases
    
    def test_purchases_with_max_amount_only(self, mock_query_data, sample_purchases):
        mock_query_data.return_value = sample_purchases
        filters = PurchaseFilterInput(max_amount=100.0)
        
        result = self.query.purchases(filters=filters)
        
        expected_filters = {"amount": ("<=", 100.0)}
        mock_query_data.assert_called_once_with(Purchases, filters=expected_filters)
        assert result == sample_purchases
    
    def test_trips_without_filters(self, mock_query_data, sample_trips):
        mock_query_data.return_value = sample_trips
        
        result = self.query.trips()
        
        mock_query_data.assert_called_once_with(Trips, filters={})
        assert result == sample_trips
    
    def test_trips_with_names_filter(self, mock_query_data, sample_trips):
        mock_query_data.return_value = sample_trips
        filters = TripFilterInput(names=["Weekend Getaway", "Business Trip"])
        
        result = self.query.trips(filters=filters)
        
        expected_filters = {"name": ["Weekend Getaway", "Business Trip"]}
        mock_query_data.assert_called_once_with(Trips, filters=expected_filters)
        assert result == sample_trips
    
    def test_trips_with_date_range_filter(self, mock_query_data, sample_trips):
        mock_query_data.return_value = sample_trips
        filters = TripFilterInput(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31)
        )
        
        result = self.query.trips(filters=filters)
        
        expected_filters = {
            "start_date": [(">=", date(2024, 1, 1)), ("<=", date(2024, 1, 31))]
        }
        mock_query_data.assert_called_once_with(Trips, filters=expected_filters)
        assert result == sample_trips
    
    def test_trips_with_start_date_only(self, mock_query_data, sample_trips):
        mock_query_data.return_value = sample_trips
        filters = TripFilterInput(start_date=date(2024, 1, 1))
        
        result = self.query.trips(filters=filters)
        
        expected_filters = {"start_date": (">=", date(2024, 1, 1))}
        mock_query_data.assert_called_once_with(Trips, filters=expected_filters)
        assert result == sample_trips
    
    def test_trips_with_end_date_only(self, mock_query_data, sample_trips):
        mock_query_data.return_value = sample_trips
        filters = TripFilterInput(end_date=date(2024, 1, 31))
        
        result = self.query.trips(filters=filters)
        
        expected_filters = {"start_date": ("<=", date(2024, 1, 31))}
        mock_query_data.assert_called_once_with(Trips, filters=expected_filters)
        assert result == sample_trips
    
    def test_totals_without_filters(self, mock_query_data, sample_totals):
        mock_query_data.return_value = sample_totals
        
        result = self.query.totals()
        
        mock_query_data.assert_called_once_with(Totals, filters={})
        assert result == sample_totals
    
    def test_totals_with_types_filter(self, mock_query_data, sample_totals):
        mock_query_data.return_value = sample_totals
        filters = TotalFilterInput(types=["Monthly", "Trip"])
        
        result = self.query.totals(filters=filters)
        
        expected_filters = {"type": ["Monthly", "Trip"]}
        mock_query_data.assert_called_once_with(Totals, filters=expected_filters)
        assert result == sample_totals
    
    def test_totals_with_trip_id_filter(self, mock_query_data, sample_totals):
        mock_query_data.return_value = sample_totals
        filters = TotalFilterInput(trip_id="trip1")
        
        result = self.query.totals(filters=filters)
        
        expected_filters = {"trip_id": "trip1"}
        mock_query_data.assert_called_once_with(Totals, filters=expected_filters)
        assert result == sample_totals
    
    def test_totals_with_date_range_filter(self, mock_query_data, sample_totals):
        mock_query_data.return_value = sample_totals
        filters = TotalFilterInput(
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31)
        )
        
        result = self.query.totals(filters=filters)
        
        expected_filters = {
            "date": [(">=", date(2024, 1, 1)), ("<=", date(2024, 1, 31))]
        }
        mock_query_data.assert_called_once_with(Totals, filters=expected_filters)
        assert result == sample_totals
    
    def test_totals_with_amount_range_filter(self, mock_query_data, sample_totals):
        mock_query_data.return_value = sample_totals
        filters = TotalFilterInput(min_amount=100.0, max_amount=1000.0)
        
        result = self.query.totals(filters=filters)
        
        expected_filters = {
            "amount": [(">=", 100.0), ("<=", 1000.0)]
        }
        mock_query_data.assert_called_once_with(Totals, filters=expected_filters)
        assert result == sample_totals


class TestMutation:
    """Test the GraphQL Mutation class."""
    
    def setup_method(self):
        self.mutation = Mutation()
    
    def test_sync_google_sheets_success(self, mock_sync_google_sheets):
        mock_sync_google_sheets.return_value = {
            "trips": 5,
            "regular_purchases": 100,
            "trip_purchases": 25,
            "total_purchases": 125
        }
        
        result = self.mutation.sync_google_sheets(year="2024", month="01")
        
        mock_sync_google_sheets.assert_called_once_with("2024", "01")
        assert result.trips == 5
        assert result.regular_purchases == 100
        assert result.trip_purchases == 25
        assert result.total_purchases == 125
        assert result.success is True
        assert "Successfully synced data for 01/2024" in result.message
    
    def test_sync_google_sheets_success_year_only(self, mock_sync_google_sheets):
        mock_sync_google_sheets.return_value = {
            "trips": 10,
            "regular_purchases": 500,
            "trip_purchases": 150,
            "total_purchases": 650
        }
        
        result = self.mutation.sync_google_sheets(year="2024")
        
        mock_sync_google_sheets.assert_called_once_with("2024", None)
        assert result.trips == 10
        assert result.regular_purchases == 500
        assert result.trip_purchases == 150
        assert result.total_purchases == 650
        assert result.success is True
        assert "Successfully synced data for year 2024" in result.message
    
    def test_sync_google_sheets_failure(self, mock_sync_google_sheets):
        mock_sync_google_sheets.side_effect = Exception("API connection failed")
        
        result = self.mutation.sync_google_sheets(year="2024", month="01")
        
        mock_sync_google_sheets.assert_called_once_with("2024", "01")
        assert result.trips == 0
        assert result.regular_purchases == 0
        assert result.trip_purchases == 0
        assert result.total_purchases == 0
        assert result.success is False
        assert "Error syncing data: API connection failed" in result.message