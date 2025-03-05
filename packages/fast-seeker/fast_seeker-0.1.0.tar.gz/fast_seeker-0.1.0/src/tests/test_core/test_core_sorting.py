import pytest

from fast_seeker.core.sorting import BaseSorter, BaseSortingQuery, OrderEntry, SortDirection, SortingConfigDict

##########################
## Tests for OrderEntry ##
##########################


def test_order_entry_asc__should_return_order_entry_with_asc_direction():
    entry = OrderEntry.asc("key")
    assert entry.key == "key"
    assert entry.direction == SortDirection.ASC


def test_order_entry_desc__should_return_order_entry_with_desc_direction():
    entry = OrderEntry.desc("key")
    assert entry.key == "key"
    assert entry.direction == SortDirection.DESC


@pytest.mark.parametrize(
    "entry, expected_str",
    [
        pytest.param(OrderEntry.asc("key"), "key", id="ascending"),
        pytest.param(OrderEntry.desc("key"), "-key", id="descending"),
    ],
)
def test_order_entry_str__should_return_expected_string_representation(entry, expected_str):
    assert str(entry) == expected_str


####################################
## Tests for the BaseSortingQuery ##
####################################


class DummySortingQuery(BaseSortingQuery[OrderEntry]):
    def default_entry_resolver(self, entry: OrderEntry): ...


class DummySortingQueryWithAlias(DummySortingQuery):
    sorting_config = SortingConfigDict(aliases={"key": "alias"})


@pytest.mark.parametrize(
    "query,key_input,expected_key, expected_direction",
    [
        pytest.param(DummySortingQuery, "key", "key", SortDirection.ASC, id="ascending"),
        pytest.param(DummySortingQuery, "-key", "key", SortDirection.DESC, id="descending"),
        pytest.param(DummySortingQueryWithAlias, "key", "alias", SortDirection.ASC, id="ascending_with_alias"),
        pytest.param(DummySortingQueryWithAlias, "-key", "alias", SortDirection.DESC, id="descending_with_alias"),
    ],
)
def test_base_sorting_query_parse_entry__returns_expected_entry_when_valid_value(
    query, key_input, expected_key, expected_direction
):
    entry = query._parse_entry(key_input)
    assert entry.key == expected_key
    assert entry.direction == expected_direction


class DummySortingQueryResolvers(BaseSortingQuery[str]):
    def default_entry_resolver(self, entry: OrderEntry) -> str:
        return "default"

    def resolve_custom_field(self, entry: OrderEntry) -> str:
        return "custom"


def test_base_sorting_query_model_dump_query__uses_expected_resolver():
    query = DummySortingQueryResolvers(order_by=["default_field", "custom_field"])
    result = list(query.model_dump_query())
    assert result == ["default", "custom"]


##############################
## Tests for the BaseSorter ##
##############################


class DummySortingQueryForBaseSorter(BaseSortingQuery[OrderEntry]):
    def default_entry_resolver(self, entry: OrderEntry): ...


class DummySorter(BaseSorter[str, str]):
    def apply_query(self, *, data, query, **kwargs): ...


def test_base_sorter_sort__calls_process_with_expected_arguments(mocker):
    sorter = DummySorter()
    process_mock = mocker.patch.object(sorter, "process")
    data = "data"
    query = DummySortingQueryForBaseSorter(order_by=["key"])
    sorter.sort(data=data, query=query)
    process_mock.assert_called_once_with(data=data, query=query)
