from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List

from .Stores.Store import StoreTypes

@dataclass
class Filter:
    stores: List[str]
    name: str = None
    price_from: float = None
    price_to: float = None
    discount: bool = None


@dataclass
class FilterNew(Filter):
    from_stored = False


@dataclass
class FilterStored(Filter):
    date_from: datetime = datetime.now() - timedelta(weeks=5)
    date_to: datetime = datetime.now()
    from_stored = True

