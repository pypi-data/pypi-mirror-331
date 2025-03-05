from django.db.models import QuerySet

from fast_seeker.core.pagination import (
    BaseLimitOffsetQuery,
    BasePageNumberQuery,
    BasePaginator,
)


class LimitOffsetQuery(BaseLimitOffsetQuery[slice]):
    def model_dump_query(self):
        return slice(self.offset, self.offset + self.limit)


class PageNumberQuery(BasePageNumberQuery[slice]):
    def model_dump_query(self):
        return slice((self.page - 1) * self.size, self.page * self.size)


class Paginator(BasePaginator[QuerySet, slice]):
    def apply_query(self, *, data: QuerySet, query: slice, **kwargs):
        return data[query]
