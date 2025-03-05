import pytest

from fast_seeker.contrib.beanie.sorting import Sorter, SortingQuery
from fast_seeker.core.sorting import OrderEntry

from .utils import DummyFindMany

############################
## Tests for SortingQuery ##
############################


@pytest.mark.parametrize(
    "entry, expected",
    [
        pytest.param(OrderEntry.desc("field1"), ("field1", -1), id="descending"),
        pytest.param(OrderEntry.asc("field1"), ("field1", 1), id="ascending"),
    ],
)
def test_beanie_sorting_query_default_entry_resolver__should_return_beanie_representation(entry, expected):
    assert SortingQuery().default_entry_resolver(entry) == expected


######################
## Tests for Sorter ##
######################


@pytest.mark.parametrize(
    "query",
    [
        pytest.param([("field1", 1)], id="descending"),
        pytest.param([("field1", -1)], id="ascending"),
    ],
)
def test_beanie_sorter_apply_query__should_apply_to_find_many(query, mocker):
    sorter = Sorter()

    result = sorter.apply_query(data=DummyFindMany(), query=query)
    assert result.sort_expressions == query
