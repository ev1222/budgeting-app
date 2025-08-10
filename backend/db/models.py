from typing import Optional, Union
from datetime import date
import hashlib

from sqlmodel import SQLModel, Field, UniqueConstraint, Relationship

from config import (
    PURCHASES_TABLE_NAME, 
    TOTALS_TABLE_NAME,
    TRIP_TABLE_NAME
)


def generate_purchase_id(sheet_name: str, row_index: int) -> str:
    """Generate a unique, reproducible ID for a purchase based on sheet name and row index."""
    combined = f"{sheet_name}_{row_index}"
    return hashlib.md5(combined.encode()).hexdigest()

def generate_trip_id(name: str, start_date: date, end_date: date) -> str:
    """Generate a unique, reproducible ID for a trip based on name and dates."""
    combined = f"{name}_{start_date}_{end_date}"
    return hashlib.md5(combined.encode()).hexdigest()

def generate_total_id(sheet_name: str, total_type: str, trip_name: Optional[str] = None) -> str:
    """Generate a unique, reproducible ID for totals based on sheet name, total type, and optional trip name."""
    if trip_name:
        combined = f"{sheet_name}_{total_type}_{trip_name}"
    else:
        combined = f"{sheet_name}_{total_type}"
    return hashlib.md5(combined.encode()).hexdigest()


class Trips(SQLModel, table=True):
    """
    ORM representing a trip taken.
    """
    __tablename__ = TRIP_TABLE_NAME

    id: str = Field(primary_key=True) # hash-based ID
    name: str
    start_date: date
    end_date: date
    comment: Optional[str] = None

    purchases: list["Purchases"] = Relationship(back_populates="trip")


class Purchases(SQLModel, table=True):
    """
    ORM representing a purchase made.
    """
    __tablename__ = PURCHASES_TABLE_NAME

    id: str = Field(primary_key=True) # hash-based ID
    date: date
    amount: float
    category: str
    description: str
    comment: Optional[str] = None
    trip_id: Optional[str] = Field(default=None, foreign_key=f"{TRIP_TABLE_NAME}.id")

    trip: Optional[Trips] = Relationship(back_populates="purchases")


class Totals(SQLModel, table=True):
    """
    ORM representing totals for a given month.
    """
    __tablename__ = TOTALS_TABLE_NAME

    id: str = Field(primary_key=True) # hash-based ID
    date: date
    type: str
    amount: float
    progress: float
    budgeted: float
    trip: Optional[str] = Field(default=None, nullable=True)