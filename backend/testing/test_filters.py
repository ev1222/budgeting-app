import pytest
from datetime import date
import strawberry

from api.filters import PurchaseFilterInput, TripFilterInput, TotalFilterInput


class TestPurchaseFilterInput:
    """Test the PurchaseFilterInput class."""
    
    def test_purchase_filter_input_creation_empty(self):
        filter_input = PurchaseFilterInput()
        
        assert filter_input.categories is None
        assert filter_input.descriptions is None
        assert filter_input.start_date is None
        assert filter_input.end_date is None
        assert filter_input.trip_id is None
        assert filter_input.min_amount is None
        assert filter_input.max_amount is None
    
    def test_purchase_filter_input_with_categories(self):
        filter_input = PurchaseFilterInput(categories=["Food", "Transportation"])
        
        assert filter_input.categories == ["Food", "Transportation"]
        assert filter_input.descriptions is None
    
    def test_purchase_filter_input_with_descriptions(self):
        filter_input = PurchaseFilterInput(descriptions=["Lunch", "Gas"])
        
        assert filter_input.descriptions == ["Lunch", "Gas"]
        assert filter_input.categories is None
    
    def test_purchase_filter_input_with_date_range(self):
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)
        filter_input = PurchaseFilterInput(start_date=start_date, end_date=end_date)
        
        assert filter_input.start_date == start_date
        assert filter_input.end_date == end_date
    
    def test_purchase_filter_input_with_trip_id(self):
        filter_input = PurchaseFilterInput(trip_id="trip123")
        
        assert filter_input.trip_id == "trip123"
    
    def test_purchase_filter_input_with_amount_range(self):
        filter_input = PurchaseFilterInput(min_amount=10.0, max_amount=100.0)
        
        assert filter_input.min_amount == 10.0
        assert filter_input.max_amount == 100.0
    
    def test_purchase_filter_input_with_all_fields(self):
        filter_input = PurchaseFilterInput(
            categories=["Food", "Transportation"],
            descriptions=["Lunch", "Gas"],
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
            trip_id="trip123",
            min_amount=10.0,
            max_amount=100.0
        )
        
        assert filter_input.categories == ["Food", "Transportation"]
        assert filter_input.descriptions == ["Lunch", "Gas"]
        assert filter_input.start_date == date(2024, 1, 1)
        assert filter_input.end_date == date(2024, 1, 31)
        assert filter_input.trip_id == "trip123"
        assert filter_input.min_amount == 10.0
        assert filter_input.max_amount == 100.0
    
    def test_purchase_filter_input_strawberry_input_decorator(self):
        """Verify PurchaseFilterInput is properly decorated as strawberry input."""
        assert hasattr(PurchaseFilterInput, '__strawberry_definition__')
    
    def test_purchase_filter_input_field_types(self):
        """Test that field types are correct for GraphQL input."""
        filter_input = PurchaseFilterInput(
            categories=["Food"],
            descriptions=["Lunch"],
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
            trip_id="trip123",
            min_amount=10.0,
            max_amount=100.0
        )
        
        assert isinstance(filter_input.categories, list)
        assert isinstance(filter_input.descriptions, list)
        assert isinstance(filter_input.start_date, date)
        assert isinstance(filter_input.end_date, date)
        assert isinstance(filter_input.trip_id, str)
        assert isinstance(filter_input.min_amount, float)
        assert isinstance(filter_input.max_amount, float)


class TestTripFilterInput:
    """Test the TripFilterInput class."""
    
    def test_trip_filter_input_creation_empty(self):
        filter_input = TripFilterInput()
        
        assert filter_input.names is None
        assert filter_input.start_date is None
        assert filter_input.end_date is None
    
    def test_trip_filter_input_with_names(self):
        filter_input = TripFilterInput(names=["Weekend Getaway", "Business Trip"])
        
        assert filter_input.names == ["Weekend Getaway", "Business Trip"]
    
    def test_trip_filter_input_with_date_range(self):
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)
        filter_input = TripFilterInput(start_date=start_date, end_date=end_date)
        
        assert filter_input.start_date == start_date
        assert filter_input.end_date == end_date
    
    def test_trip_filter_input_with_all_fields(self):
        filter_input = TripFilterInput(
            names=["Weekend Getaway", "Business Trip"],
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31)
        )
        
        assert filter_input.names == ["Weekend Getaway", "Business Trip"]
        assert filter_input.start_date == date(2024, 1, 1)
        assert filter_input.end_date == date(2024, 1, 31)
    
    def test_trip_filter_input_strawberry_input_decorator(self):
        """Verify TripFilterInput is properly decorated as strawberry input."""
        assert hasattr(TripFilterInput, '__strawberry_definition__')
    
    def test_trip_filter_input_field_types(self):
        """Test that field types are correct for GraphQL input."""
        filter_input = TripFilterInput(
            names=["Trip"],
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31)
        )
        
        assert isinstance(filter_input.names, list)
        assert isinstance(filter_input.start_date, date)
        assert isinstance(filter_input.end_date, date)


class TestTotalFilterInput:
    """Test the TotalFilterInput class."""
    
    def test_total_filter_input_creation_empty(self):
        filter_input = TotalFilterInput()
        
        assert filter_input.types is None
        assert filter_input.trip_id is None
        assert filter_input.start_date is None
        assert filter_input.end_date is None
        assert filter_input.min_amount is None
        assert filter_input.max_amount is None
    
    def test_total_filter_input_with_types(self):
        filter_input = TotalFilterInput(types=["Monthly", "Trip"])
        
        assert filter_input.types == ["Monthly", "Trip"]
    
    def test_total_filter_input_with_trip_id(self):
        filter_input = TotalFilterInput(trip_id="trip123")
        
        assert filter_input.trip_id == "trip123"
    
    def test_total_filter_input_with_date_range(self):
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)
        filter_input = TotalFilterInput(start_date=start_date, end_date=end_date)
        
        assert filter_input.start_date == start_date
        assert filter_input.end_date == end_date
    
    def test_total_filter_input_with_amount_range(self):
        filter_input = TotalFilterInput(min_amount=100.0, max_amount=1000.0)
        
        assert filter_input.min_amount == 100.0
        assert filter_input.max_amount == 1000.0
    
    def test_total_filter_input_with_all_fields(self):
        filter_input = TotalFilterInput(
            types=["Monthly", "Trip"],
            trip_id="trip123",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
            min_amount=100.0,
            max_amount=1000.0
        )
        
        assert filter_input.types == ["Monthly", "Trip"]
        assert filter_input.trip_id == "trip123"
        assert filter_input.start_date == date(2024, 1, 1)
        assert filter_input.end_date == date(2024, 1, 31)
        assert filter_input.min_amount == 100.0
        assert filter_input.max_amount == 1000.0
    
    def test_total_filter_input_strawberry_input_decorator(self):
        """Verify TotalFilterInput is properly decorated as strawberry input."""
        assert hasattr(TotalFilterInput, '__strawberry_definition__')
    
    def test_total_filter_input_field_types(self):
        """Test that field types are correct for GraphQL input."""
        filter_input = TotalFilterInput(
            types=["Monthly"],
            trip_id="trip123",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31),
            min_amount=100.0,
            max_amount=1000.0
        )
        
        assert isinstance(filter_input.types, list)
        assert isinstance(filter_input.trip_id, str)
        assert isinstance(filter_input.start_date, date)
        assert isinstance(filter_input.end_date, date)
        assert isinstance(filter_input.min_amount, float)
        assert isinstance(filter_input.max_amount, float)


class TestFilterEdgeCases:
    """Test edge cases and validation for filter inputs."""
    
    def test_empty_lists_in_filters(self):
        """Test behavior with empty lists."""
        purchase_filter = PurchaseFilterInput(categories=[], descriptions=[])
        trip_filter = TripFilterInput(names=[])
        total_filter = TotalFilterInput(types=[])
        
        assert purchase_filter.categories == []
        assert purchase_filter.descriptions == []
        assert trip_filter.names == []
        assert total_filter.types == []
    
    def test_date_edge_cases(self):
        """Test date edge cases."""
        today = date.today()
        
        filter_input = PurchaseFilterInput(
            start_date=today,
            end_date=today  # Same day range
        )
        
        assert filter_input.start_date == filter_input.end_date
    
    def test_amount_edge_cases(self):
        """Test amount edge cases."""
        filter_input = PurchaseFilterInput(
            min_amount=0.0,  # Zero minimum
            max_amount=0.01  # Very small maximum
        )
        
        assert filter_input.min_amount == 0.0
        assert filter_input.max_amount == 0.01
        
        filter_input2 = TotalFilterInput(
            min_amount=9999999.99,  # Large amount
            max_amount=9999999.99   # Same large amount
        )
        
        assert filter_input2.min_amount == filter_input2.max_amount
    
    def test_single_item_lists(self):
        """Test filters with single item lists."""
        purchase_filter = PurchaseFilterInput(categories=["Food"])
        trip_filter = TripFilterInput(names=["Single Trip"])
        total_filter = TotalFilterInput(types=["Monthly"])
        
        assert len(purchase_filter.categories) == 1
        assert len(trip_filter.names) == 1
        assert len(total_filter.types) == 1