from typing import Union

from pydantic.fields import FieldInfo

from fast_seeker.core.filtering import BaseFilterer, BaseFilterQuery, FiltererConfigDict

###################################
## Tests for the BaseFilterQuery ##
###################################


class DummyFilterQuery(BaseFilterQuery[str]):
    field1: Union[str, None] = None

    def default_field_resolver(self, field_name: str, field_value: str, field_info: FieldInfo) -> str:
        return f"{field_name}={field_value}"


def test_base_filter_query__should_ignore_none_when_passed_to_filter_by_default():
    query = DummyFilterQuery()
    assert list(query.model_dump_query()) == []


class DummyQueryWithIgnoreNoneFalse(DummyFilterQuery):
    filter_config = FiltererConfigDict(ignore_none=False)


class test_base_filter_query__should_not_ignore_none_when_configured:
    query = DummyQueryWithIgnoreNoneFalse()
    assert list(query.model_dump_query()) == ["field1=None"]


class DummyFilterQueryWithIgnoreNoneTrue(DummyFilterQuery):
    filter_config = FiltererConfigDict(ignore_none=True)


def test_base_filter_query__should_ignore_none_when_configured():
    query = DummyFilterQueryWithIgnoreNoneTrue()
    assert list(query.model_dump_query()) == []


class DummyFilterQueryWithCustomResolver(DummyFilterQuery):
    def resolve_field1(self, field_name: str, field_value: str, field_info: str) -> str:
        return f"custom_{field_name}={field_value}"


def test_base_filter_query__should_use_custom_resolver_when_available():
    query = DummyFilterQueryWithCustomResolver(field1="value")
    assert list(query.model_dump_query()) == ["custom_field1=value"]


def test_base_filter_query__should_use_default_resolver_when_no_custom_resolver():
    query = DummyFilterQuery(field1="value")
    assert list(query.model_dump_query()) == ["field1=value"]


################################
## Tests for the BaseFilterer ##
################################


class DummyFilterer(BaseFilterer[str, str]):
    def apply_query(self, *, data, query, **kwargs): ...


def test_base_filterer_filter__calls_process_with_expected_arguments(mocker):
    filterer = DummyFilterer()
    process_mock = mocker.patch.object(filterer, "process")
    data = "data"
    query = DummyFilterQuery(field1="value")
    filterer.filter(data=data, query=query)
    process_mock.assert_called_once_with(data=data, query=query)
