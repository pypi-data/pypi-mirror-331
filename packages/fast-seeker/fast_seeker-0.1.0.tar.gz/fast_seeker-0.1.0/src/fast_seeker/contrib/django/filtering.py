from collections.abc import Iterable
from typing import Any

from django.db.models import Q, QuerySet
from pydantic.fields import FieldInfo

from fast_seeker.core.filtering import BaseFilterer, BaseFilterQuery


class FilterQuery(BaseFilterQuery[Q]):
    def default_field_resolver(self, field_name: str, field_value: Any, field_info: FieldInfo) -> Q:
        return Q(**{field_name: field_value})


class Filterer(BaseFilterer[QuerySet, Q]):
    def apply_query(self, *, data: QuerySet, query: Iterable[Q], **kwargs) -> QuerySet:
        return data.filter(*query)
