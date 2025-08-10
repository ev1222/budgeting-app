from strawberry.experimental.pydantic import type as pydantic_type

from db.models import Purchases, Trips, Totals


@pydantic_type(model=Purchases, all_fields=True)
class PurchasesType:
    pass

@pydantic_type(model=Trips, all_fields=True)
class TripsType:
    pass

@pydantic_type(model=Totals, all_fields=True)
class TotalsType:
    pass