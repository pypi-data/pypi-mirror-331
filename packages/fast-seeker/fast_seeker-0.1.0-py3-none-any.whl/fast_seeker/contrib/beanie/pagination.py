from typing import TypedDict

from beanie.odm.queries.find import FindMany

from fast_seeker.core.pagination import (
    BaseLimitOffsetQuery,
    BasePageNumberQuery,
    BasePaginator,
)


class BeanieQueryPage(TypedDict):
    limit: int
    skip: int


class LimitOffsetQuery(BaseLimitOffsetQuery[BeanieQueryPage]):
    def model_dump_query(self) -> BeanieQueryPage:
        return BeanieQueryPage(limit=self.limit, skip=self.offset)


class PageNumberQuery(BasePageNumberQuery[BeanieQueryPage]):
    def model_dump_query(self) -> BeanieQueryPage:
        return BeanieQueryPage(limit=self.size, skip=(self.page - 1) * self.size)


class Paginator(BasePaginator[FindMany, BeanieQueryPage]):
    def apply_query(self, *, data: FindMany, query: BeanieQueryPage, **kwargs) -> FindMany:
        return data.limit(query["limit"]).skip(query["skip"])
