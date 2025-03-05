from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from pydantic import BaseModel

_TQuery = TypeVar("_TQuery")
_TData = TypeVar("_TData")


class QueryModel(ABC, BaseModel, Generic[_TQuery]):
    @abstractmethod
    def model_dump_query(self) -> _TQuery: ...


class QueryProcessor(ABC, Generic[_TData, _TQuery]):
    @abstractmethod
    def apply_query(self, *, data: _TData, query: _TQuery, **kwargs) -> _TData: ...

    def process(self, *, data: _TData, query: QueryModel, **kwargs) -> _TData:
        return self.apply_query(data=data, query=query.model_dump_query(), **kwargs)
