from abc import abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass
from enum import Enum
from typing import ClassVar, Generic, TypedDict, TypeVar

from typing_extensions import Self

from .base import QueryModel, QueryProcessor, _TData

_TOrderQueryEntry = TypeVar("_TOrderQueryEntry")


ASC_SIGN = "+"
DESC_SIGN = "-"


class SortDirection(Enum):
    ASC = ASC_SIGN
    DESC = DESC_SIGN


@dataclass
class OrderEntry:
    original_key: str
    key: str
    direction: SortDirection

    @classmethod
    def asc(cls, key: str) -> Self:
        return cls(original_key=key, key=key, direction=SortDirection.ASC)

    @classmethod
    def desc(cls, key: str) -> Self:
        return cls(original_key=key, key=key, direction=SortDirection.DESC)

    def __str__(self):
        prefix = self.direction.value if self.direction != SortDirection.ASC else ""
        return f"{prefix}{self.original_key}"


class SortingConfigDict(TypedDict, total=False):
    aliases: dict[str, str]


class BaseSortingQuery(QueryModel[Iterable[_TOrderQueryEntry]], Generic[_TOrderQueryEntry]):
    sorting_config: ClassVar[SortingConfigDict] = SortingConfigDict(aliases={})

    order_by: list[str] = []

    @classmethod
    def _parse_entry(cls, order: str) -> OrderEntry:
        direction = SortDirection.ASC
        original_key = order
        if order.startswith(DESC_SIGN):
            direction = SortDirection.DESC
            original_key = order[1:]
        key = cls.sorting_config.get("aliases", {}).get(original_key, original_key)
        return OrderEntry(original_key=original_key, key=key, direction=direction)

    @abstractmethod
    def default_entry_resolver(self, entry: OrderEntry) -> _TOrderQueryEntry: ...

    def model_dump_query(self) -> Iterable[_TOrderQueryEntry]:
        for order_value in self.order_by:
            parsed_entry = self._parse_entry(order_value)
            entry_resolver = getattr(self, f"resolve_{parsed_entry.original_key}", self.default_entry_resolver)
            yield entry_resolver(parsed_entry)


class BaseSorter(Generic[_TData, _TOrderQueryEntry], QueryProcessor[_TData, Iterable[_TOrderQueryEntry]]):
    @abstractmethod
    def apply_query(self, *, data: _TData, query: Iterable[_TOrderQueryEntry], **kwargs) -> _TData: ...

    def sort(self, *, data: _TData, query: BaseSortingQuery[_TOrderQueryEntry], **kwargs) -> _TData:
        return self.process(data=data, query=query, **kwargs)
