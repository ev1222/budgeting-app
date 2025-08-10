# filters.py
import strawberry
from typing import Optional
from datetime import date

@strawberry.input
class PurchaseFilterInput:
    categories: Optional[list[str]] = None
    descriptions: Optional[list[str]] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    trip: Optional[str] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None


@strawberry.input
class TotalFilterInput:
    types: Optional[list[str]] = None
    trip: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None


@strawberry.input
class TripFilterInput:
    names: Optional[list[str]] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    