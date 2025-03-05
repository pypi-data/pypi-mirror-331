from collections.abc import Iterable

from beanie.odm.enums import SortDirection as BeanieSortDirection
from beanie.odm.queries.find import FindMany

from fast_seeker.core.sorting import (
    BaseSorter,
    BaseSortingQuery,
    OrderEntry,
    SortDirection,
)

BEANIE_DIRECTION_MAP = {
    SortDirection.ASC: BeanieSortDirection.ASCENDING,
    SortDirection.DESC: BeanieSortDirection.DESCENDING,
}


BeanieSortArg = tuple[str, BeanieSortDirection]


class SortingQuery(BaseSortingQuery[BeanieSortArg]):
    def default_entry_resolver(self, entry: OrderEntry) -> BeanieSortArg:
        return entry.key, BEANIE_DIRECTION_MAP[entry.direction]


class Sorter(BaseSorter[FindMany, BeanieSortArg]):
    def apply_query(self, *, data: FindMany, query: Iterable[BeanieSortArg], **kwargs) -> FindMany:
        return data.sort(*query)
