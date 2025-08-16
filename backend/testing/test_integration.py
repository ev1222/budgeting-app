import pytest
from datetime import date
from unittest.mock import patch, Mock
import strawberry

from api.schema import schema, Query, Mutation
from api.filters import PurchaseFilterInput, TripFilterInput, TotalFilterInput
from db.models import Purchases, Trips, Totals


class TestGraphQLIntegration:
    """Integration tests for full GraphQL workflows."""
    
    def test_schema_creation(self):
        """Test that the GraphQL schema is properly created."""
        assert schema is not None
        assert schema.query is not None
        assert schema.mutation is not None
    
    @patch('api.schema.query_data')
    def test_purchases_query_integration(self, mock_query_data):
        """Test complete purchases query workflow."""
        mock_purchases = [
            Purchases(
                id="purchase1",
                date=date(2024, 1, 15),
                amount=25.50,
                category="Food",
                description="Lunch",
                comment=None,
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
            )
        ]
        mock_query_data.return_value = mock_purchases
        
        query = """
        query GetPurchases($filters: PurchaseFilterInput) {
            purchases(filters: $filters) {
                id
                date
                amount
                category
                description
                comment
                tripId
            }
        }
        """
        
        variables = {
            "filters": {
                "categories": ["Food", "Transportation"],
                "minAmount": 10.0
            }
        }
        
        result = schema.execute_sync(query, variable_values=variables)
        
        assert result.errors is None
        assert result.data is not None
        assert "purchases" in result.data
        assert len(result.data["purchases"]) == 2
        
        purchase_data = result.data["purchases"][0]
        assert purchase_data["id"] == "purchase1"
        assert purchase_data["amount"] == 25.50
        assert purchase_data["category"] == "Food"
    
    @patch('api.schema.query_data')
    def test_trips_query_integration(self, mock_query_data):
        """Test complete trips query workflow."""
        mock_trips = [
            Trips(
                id="trip1",
                name="Weekend Getaway",
                start_date=date(2024, 1, 19),
                end_date=date(2024, 1, 21),
                comment="Fun trip"
            )
        ]
        mock_query_data.return_value = mock_trips
        
        query = """
        query GetTrips($filters: TripFilterInput) {
            trips(filters: $filters) {
                id
                name
                startDate
                endDate
                comment
            }
        }
        """
        
        variables = {
            "filters": {
                "names": ["Weekend Getaway"]
            }
        }
        
        result = schema.execute_sync(query, variable_values=variables)
        
        assert result.errors is None
        assert result.data is not None
        assert "trips" in result.data
        assert len(result.data["trips"]) == 1
        
        trip_data = result.data["trips"][0]
        assert trip_data["id"] == "trip1"
        assert trip_data["name"] == "Weekend Getaway"
    
    @patch('api.schema.query_data')
    def test_totals_query_integration(self, mock_query_data):
        """Test complete totals query workflow."""
        mock_totals = [
            Totals(
                id="total1",
                date=date(2024, 1, 31),
                type="Monthly",
                amount=1250.00,
                progress=0.75,
                budgeted=1667.00,
                trip_id=None
            )
        ]
        mock_query_data.return_value = mock_totals
        
        query = """
        query GetTotals($filters: TotalFilterInput) {
            totals(filters: $filters) {
                id
                date
                type
                amount
                progress
                budgeted
                tripId
            }
        }
        """
        
        variables = {
            "filters": {
                "types": ["Monthly"]
            }
        }
        
        result = schema.execute_sync(query, variable_values=variables)
        
        assert result.errors is None
        assert result.data is not None
        assert "totals" in result.data
        assert len(result.data["totals"]) == 1
        
        total_data = result.data["totals"][0]
        assert total_data["id"] == "total1"
        assert total_data["type"] == "Monthly"
        assert total_data["amount"] == 1250.00
    
    @patch('api.schema.sync_google_sheets_data')
    def test_sync_mutation_integration_success(self, mock_sync):
        """Test complete sync mutation workflow - success case."""
        mock_sync.return_value = {
            "trips": 5,
            "regular_purchases": 100,
            "trip_purchases": 25,
            "total_purchases": 125
        }
        
        mutation = """
        mutation SyncGoogleSheets($year: String!, $month: String) {
            syncGoogleSheets(year: $year, month: $month) {
                trips
                regularPurchases
                tripPurchases
                totalPurchases
                success
                message
            }
        }
        """
        
        variables = {
            "year": "2024",
            "month": "01"
        }
        
        result = schema.execute_sync(mutation, variable_values=variables)
        
        assert result.errors is None
        assert result.data is not None
        assert "syncGoogleSheets" in result.data
        
        sync_data = result.data["syncGoogleSheets"]
        assert sync_data["trips"] == 5
        assert sync_data["regularPurchases"] == 100
        assert sync_data["tripPurchases"] == 25
        assert sync_data["totalPurchases"] == 125
        assert sync_data["success"] is True
        assert "Successfully synced data for 01/2024" in sync_data["message"]
    
    @patch('api.schema.sync_google_sheets_data')
    def test_sync_mutation_integration_failure(self, mock_sync):
        """Test complete sync mutation workflow - failure case."""
        mock_sync.side_effect = Exception("API connection failed")
        
        mutation = """
        mutation SyncGoogleSheets($year: String!, $month: String) {
            syncGoogleSheets(year: $year, month: $month) {
                trips
                regularPurchases
                tripPurchases
                totalPurchases
                success
                message
            }
        }
        """
        
        variables = {
            "year": "2024",
            "month": "01"
        }
        
        result = schema.execute_sync(mutation, variable_values=variables)
        
        assert result.errors is None
        assert result.data is not None
        
        sync_data = result.data["syncGoogleSheets"]
        assert sync_data["trips"] == 0
        assert sync_data["success"] is False
        assert "Error syncing data: API connection failed" in sync_data["message"]
    
    @patch('api.schema.query_data')
    def test_complex_filter_integration(self, mock_query_data):
        """Test complex filtering scenarios."""
        mock_purchases = []  # Empty result for complex filter
        mock_query_data.return_value = mock_purchases
        
        query = """
        query GetFilteredPurchases($filters: PurchaseFilterInput) {
            purchases(filters: $filters) {
                id
                date
                amount
                category
            }
        }
        """
        
        variables = {
            "filters": {
                "categories": ["Food", "Transportation"],
                "descriptions": ["Lunch", "Gas"],
                "startDate": "2024-01-01",
                "endDate": "2024-01-31",
                "tripId": "trip123",
                "minAmount": 10.0,
                "maxAmount": 200.0
            }
        }
        
        result = schema.execute_sync(query, variable_values=variables)
        
        assert result.errors is None
        assert result.data is not None
        assert result.data["purchases"] == []
        
        # Verify the mock was called with correct filter parameters
        mock_query_data.assert_called_once()
        call_args = mock_query_data.call_args
        assert call_args[0][0] == Purchases  # Model class
        
        filters = call_args[1]["filters"]
        assert "category" in filters
        assert "description" in filters
        assert "date" in filters
        assert "trip_id" in filters
        assert "amount" in filters
    
    def test_schema_introspection(self):
        """Test GraphQL schema introspection."""
        introspection_query = """
        query IntrospectionQuery {
            __schema {
                queryType {
                    name
                }
                mutationType {
                    name
                }
                types {
                    name
                    kind
                }
            }
        }
        """
        
        result = schema.execute_sync(introspection_query)
        
        assert result.errors is None
        assert result.data is not None
        
        schema_data = result.data["__schema"]
        assert schema_data["queryType"]["name"] == "Query"
        assert schema_data["mutationType"]["name"] == "Mutation"
        
        type_names = [t["name"] for t in schema_data["types"]]
        assert "PurchasesType" in type_names
        assert "TripsType" in type_names
        assert "TotalsType" in type_names
        assert "PurchaseFilterInput" in type_names
        assert "TripFilterInput" in type_names
        assert "TotalFilterInput" in type_names
    
    @patch('api.schema.query_data')
    def test_error_handling_integration(self, mock_query_data):
        """Test error handling in GraphQL operations."""
        mock_query_data.side_effect = Exception("Database connection failed")
        
        query = """
        query GetPurchases {
            purchases {
                id
            }
        }
        """
        
        result = schema.execute_sync(query)
        
        # GraphQL should handle the exception and return it in errors
        assert result.errors is not None
        assert len(result.errors) > 0
        assert "Database connection failed" in str(result.errors[0])
    
    def test_field_resolution_integration(self):
        """Test that all fields are properly resolvable."""
        # Test that schema can be queried for field information
        field_query = """
        query {
            __type(name: "PurchasesType") {
                fields {
                    name
                    type {
                        name
                    }
                }
            }
        }
        """
        
        result = schema.execute_sync(field_query)
        
        assert result.errors is None
        assert result.data is not None
        
        fields = result.data["__type"]["fields"]
        field_names = [f["name"] for f in fields]
        
        expected_fields = ["id", "date", "amount", "category", "description", "comment", "tripId"]
        for expected_field in expected_fields:
            assert expected_field in field_names