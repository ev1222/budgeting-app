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
    trip: Optional[int] = None


@strawberry.input
class TripFilterInput:
    names: Optional[list[str]] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    