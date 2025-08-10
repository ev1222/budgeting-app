import strawberry
from strawberry.experimental.pydantic import type
from typing import List, Optional
from db.database import query_data
from sync.data_sync import sync_google_sheets_data

from .types import PurchasesType, TripsType, TotalsType
from .filters import PurchaseFilterInput, TripFilterInput
from db.models import Purchases, Trips, Totals


def get_field_name(model: type, field_ref):
    for name in model.model_fields.keys():
        if getattr(model, name) is field_ref:
            return name
    raise ValueError("Field not found")


@strawberry.type
class Query:
    @strawberry.field
    def purchases(self, filters: Optional[PurchaseFilterInput] = None) -> List[PurchasesType]:
        filter_args = {}

        if filters:
            if filters.categories:
                filter_args[get_field_name(Purchases, Purchases.category)] = filters.categories
            if filters.descriptions:
                filter_args[get_field_name(Purchases, Purchases.description)] = filters.descriptions
            if filters.trip:
                filter_args[get_field_name(Purchases, Purchases.trip)] = filters.trip

            if filters.start_date and filters.end_date:
                filter_args[get_field_name(Purchases, Purchases.date)] = [
                    (">=", filters.start_date),
                    ("<=", filters.end_date)
                ]
            elif filters.start_date:
                filter_args[get_field_name(Purchases, Purchases.date)] = (">=", filters.start_date)
            elif filters.end_date:
                filter_args[get_field_name(Purchases, Purchases.date)] = ("<=", filters.end_date)

        purchases = query_data(Purchases, filters=filter_args)
        return purchases

    @strawberry.field
    def trips(self, filters: Optional[TripFilterInput] = None) -> List[TripsType]:
        filter_args = {}

        if filters:
            if filters.names:
                filter_args[get_field_name(Trips, Trips.name)] = filters.names
            if filters.start_date and filters.end_date:
                filter_args[get_field_name(Trips, Trips.start_date)] = [
                    (">=", filters.start_date),
                    ("<=", filters.end_date)
                ]
            elif filters.start_date:
                filter_args[get_field_name(Trips, Trips.start_date)] = (">=", filters.start_date)
            elif filters.end_date:
                filter_args[get_field_name(Trips, Trips.start_date)] = ("<=", filters.end_date)

        trips = query_data(Trips, filters=filter_args)
        return trips

    @strawberry.field
    def totals(self) -> List[TotalsType]:
        return query_data(Totals)


@strawberry.type
class SyncResult:
    trips: int
    regular_purchases: int
    trip_purchases: int
    total_purchases: int
    success: bool
    message: str

@strawberry.type
class Mutation:
    @strawberry.field
    def sync_google_sheets(self, year: str) -> SyncResult:
        try:
            result = sync_google_sheets_data(year)
            return SyncResult(
                trips=result["trips"],
                regular_purchases=result["regular_purchases"],
                trip_purchases=result["trip_purchases"],
                total_purchases=result["total_purchases"],
                success=True,
                message=f"Successfully synced data for year {year}"
            )
        except Exception as e:
            return SyncResult(
                trips=0,
                regular_purchases=0,
                trip_purchases=0,
                total_purchases=0,
                success=False,
                message=f"Error syncing data: {str(e)}"
            )


schema = strawberry.Schema(query=Query, mutation=Mutation)