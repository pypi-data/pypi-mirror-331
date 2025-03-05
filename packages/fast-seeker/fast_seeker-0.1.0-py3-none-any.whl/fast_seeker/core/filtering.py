from abc import abstractmethod
from collections.abc import Iterable
from typing import Any, ClassVar, Generic, TypedDict, TypeVar

from pydantic.fields import FieldInfo

from .base import QueryModel, QueryProcessor, _TData

_TFilterQueryEntry = TypeVar("_TFilterQueryEntry")


class FiltererConfigDict(TypedDict, total=False):
    ignore_none: bool


class BaseFilterQuery(QueryModel[Iterable[_TFilterQueryEntry]], Generic[_TFilterQueryEntry]):
    filter_config: ClassVar[FiltererConfigDict] = FiltererConfigDict(ignore_none=True)

    @abstractmethod
    def default_field_resolver(
        self, field_name: str, field_value: Any, field_info: FieldInfo
    ) -> _TFilterQueryEntry: ...

    def model_dump_query(self) -> Iterable[_TFilterQueryEntry]:
        should_ignore_none = self.filter_config.get("ignore_none", True)
        for field_name, field_info in self.model_fields.items():
            entry_value = getattr(self, field_name)
            if entry_value is None and should_ignore_none:
                continue
            resolver = getattr(self, f"resolve_{field_name}", self.default_field_resolver)
            yield resolver(field_name, entry_value, field_info)


class BaseFilterer(Generic[_TData, _TFilterQueryEntry], QueryProcessor[_TData, Iterable[_TFilterQueryEntry]]):
    @abstractmethod
    def apply_query(self, *, data: _TData, query: Iterable[_TFilterQueryEntry], **kwargs) -> _TData: ...

    def filter(self, data: _TData, query: BaseFilterQuery, **kwargs) -> _TData:
        return self.process(data=data, query=query, **kwargs)
