from collections.abc import Iterable
from typing import Any

from beanie.odm.queries.find import FindMany
from pydantic.fields import FieldInfo

from fast_seeker.core.filtering import BaseFilterer, BaseFilterQuery

BeanieFilterEntry = dict[str, Any]


class FilterQuery(BaseFilterQuery[BeanieFilterEntry]):
    def default_field_resolver(self, field_name: str, field_value: Any, field_info: FieldInfo) -> BeanieFilterEntry:
        return {field_name: field_value}


class Filterer(BaseFilterer[FindMany, BeanieFilterEntry]):
    def apply_query(self, *, data: FindMany, query: Iterable[BeanieFilterEntry], **kwargs) -> FindMany:
        return data.find(*query)
