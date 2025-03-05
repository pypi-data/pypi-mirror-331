from abc import abstractmethod
from typing import Generic, TypeVar

from pydantic import BaseModel, Field

from .base import QueryModel, QueryProcessor, _TData, _TQuery

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    total: int
    results: list[T]


class BaseLimitOffsetQuery(QueryModel[_TQuery], Generic[_TQuery]):
    limit: int = Field(20, ge=1)
    offset: int = Field(0, ge=0)


class BasePageNumberQuery(QueryModel[_TQuery], Generic[_TQuery]):
    page: int = Field(1, ge=1)
    size: int = Field(20, ge=1)


class BasePaginator(Generic[_TData, _TQuery], QueryProcessor[_TData, _TQuery]):
    @abstractmethod
    def apply_query(self, *, data: _TData, query: _TQuery, **kwargs) -> _TData: ...

    def paginate(self, data: _TData, query: QueryModel, **kwargs) -> _TData:
        return self.process(data=data, query=query, **kwargs)
