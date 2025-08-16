import pytest
from datetime import date
from strawberry.experimental.pydantic import type as pydantic_type

from api.types import PurchasesType, TripsType, TotalsType
from db.models import Purchases, Trips, Totals


class TestPurchasesType:
    """Test the PurchasesType GraphQL type."""
    
    def test_purchases_type_creation(self):
        purchase = Purchases(
            id="test_purchase",
            date=date(2024, 1, 15),
            amount=25.50,
            category="Food",
            description="Lunch at restaurant",
            comment="Good meal",
            trip_id=None
        )
        
        purchases_type = PurchasesType.from_pydantic(purchase)
        
        assert purchases_type.id == "test_purchase"
        assert purchases_type.date == date(2024, 1, 15)
        assert purchases_type.amount == 25.50
        assert purchases_type.category == "Food"
        assert purchases_type.description == "Lunch at restaurant"
        assert purchases_type.comment == "Good meal"
        assert purchases_type.trip_id is None
    
    def test_purchases_type_with_trip_id(self):
        purchase = Purchases(
            id="test_purchase_trip",
            date=date(2024, 1, 20),
            amount=100.00,
            category="Transportation",
            description="Gas",
            comment=None,
            trip_id="trip123"
        )
        
        purchases_type = PurchasesType.from_pydantic(purchase)
        
        assert purchases_type.trip_id == "trip123"
    
    def test_purchases_type_minimal_data(self):
        purchase = Purchases(
            id="minimal_purchase",
            date=date(2024, 1, 1),
            amount=0.0,
            category="",
            description="",
            comment=None,
            trip_id=None
        )
        
        purchases_type = PurchasesType.from_pydantic(purchase)
        
        assert purchases_type.id == "minimal_purchase"
        assert purchases_type.amount == 0.0
        assert purchases_type.category == ""
        assert purchases_type.description == ""
        assert purchases_type.comment is None


class TestTripsType:
    """Test the TripsType GraphQL type."""
    
    def test_trips_type_creation(self):
        trip = Trips(
            id="test_trip",
            name="Weekend Getaway",
            start_date=date(2024, 1, 19),
            end_date=date(2024, 1, 21),
            comment="Fun trip"
        )
        
        trips_type = TripsType.from_pydantic(trip)
        
        assert trips_type.id == "test_trip"
        assert trips_type.name == "Weekend Getaway"
        assert trips_type.start_date == date(2024, 1, 19)
        assert trips_type.end_date == date(2024, 1, 21)
        assert trips_type.comment == "Fun trip"
    
    def test_trips_type_without_comment(self):
        trip = Trips(
            id="business_trip",
            name="Business Trip",
            start_date=date(2024, 2, 5),
            end_date=date(2024, 2, 8),
            comment=None
        )
        
        trips_type = TripsType.from_pydantic(trip)
        
        assert trips_type.comment is None
    
    def test_trips_type_single_day_trip(self):
        trip = Trips(
            id="day_trip",
            name="Day Trip",
            start_date=date(2024, 3, 1),
            end_date=date(2024, 3, 1),
            comment="Same day trip"
        )
        
        trips_type = TripsType.from_pydantic(trip)
        
        assert trips_type.start_date == trips_type.end_date


class TestTotalsType:
    """Test the TotalsType GraphQL type."""
    
    def test_totals_type_creation(self):
        total = Totals(
            id="test_total",
            date=date(2024, 1, 31),
            type="Monthly",
            amount=1250.00,
            progress=0.75,
            budgeted=1667.00,
            trip_id=None
        )
        
        totals_type = TotalsType.from_pydantic(total)
        
        assert totals_type.id == "test_total"
        assert totals_type.date == date(2024, 1, 31)
        assert totals_type.type == "Monthly"
        assert totals_type.amount == 1250.00
        assert totals_type.progress == 0.75
        assert totals_type.budgeted == 1667.00
        assert totals_type.trip_id is None
    
    def test_totals_type_with_trip_id(self):
        total = Totals(
            id="trip_total",
            date=date(2024, 1, 31),
            type="Trip",
            amount=350.00,
            progress=1.0,
            budgeted=350.00,
            trip_id="trip123"
        )
        
        totals_type = TotalsType.from_pydantic(total)
        
        assert totals_type.trip_id == "trip123"
        assert totals_type.progress == 1.0
    
    def test_totals_type_zero_values(self):
        total = Totals(
            id="zero_total",
            date=date(2024, 1, 31),
            type="Monthly",
            amount=0.0,
            progress=0.0,
            budgeted=0.0,
            trip_id=None
        )
        
        totals_type = TotalsType.from_pydantic(total)
        
        assert totals_type.amount == 0.0
        assert totals_type.progress == 0.0
        assert totals_type.budgeted == 0.0
    
    def test_totals_type_over_budget(self):
        total = Totals(
            id="over_budget_total",
            date=date(2024, 1, 31),
            type="Monthly",
            amount=2000.00,
            progress=1.5,
            budgeted=1333.33,
            trip_id=None
        )
        
        totals_type = TotalsType.from_pydantic(total)
        
        assert totals_type.progress == 1.5
        assert totals_type.amount > totals_type.budgeted


class TestTypeIntegration:
    """Test integration between types and models."""
    
    def test_all_types_inherit_from_pydantic_decorator(self):
        """Verify that all GraphQL types are properly decorated with pydantic_type."""
        assert hasattr(PurchasesType, '__strawberry_definition__')
        assert hasattr(TripsType, '__strawberry_definition__')
        assert hasattr(TotalsType, '__strawberry_definition__')
    
    def test_types_have_all_model_fields(self):
        """Verify that GraphQL types expose all model fields."""
        purchase = Purchases(
            id="test",
            date=date.today(),
            amount=10.0,
            category="test",
            description="test",
            comment=None,
            trip_id=None
        )
        purchases_type = PurchasesType.from_pydantic(purchase)
        
        model_fields = set(purchase.model_fields.keys())
        type_fields = set(dir(purchases_type))
        
        for field in model_fields:
            assert hasattr(purchases_type, field), f"Field '{field}' missing from PurchasesType"
        
        trip = Trips(
            id="test",
            name="test",
            start_date=date.today(),
            end_date=date.today(),
            comment=None
        )
        trips_type = TripsType.from_pydantic(trip)
        
        model_fields = set(trip.model_fields.keys())
        for field in model_fields:
            assert hasattr(trips_type, field), f"Field '{field}' missing from TripsType"
        
        total = Totals(
            id="test",
            date=date.today(),
            type="test",
            amount=100.0,
            progress=0.5,
            budgeted=200.0,
            trip_id=None
        )
        totals_type = TotalsType.from_pydantic(total)
        
        model_fields = set(total.model_fields.keys())
        for field in model_fields:
            assert hasattr(totals_type, field), f"Field '{field}' missing from TotalsType"