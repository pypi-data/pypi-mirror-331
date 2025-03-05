from collections.abc import Iterable

from django.db.models import QuerySet

from fast_seeker.core.sorting import BaseSorter, BaseSortingQuery, OrderEntry

DjangoTranslatedQuery = Iterable[str]


class SortingQuery(BaseSortingQuery[str]):
    def default_entry_resolver(self, entry: OrderEntry) -> str:
        return str(entry)


class Sorter(BaseSorter[QuerySet, str]):
    def apply_query(self, *, data: QuerySet, query: Iterable[str], **kwargs) -> QuerySet:
        return data.order_by(*query)
