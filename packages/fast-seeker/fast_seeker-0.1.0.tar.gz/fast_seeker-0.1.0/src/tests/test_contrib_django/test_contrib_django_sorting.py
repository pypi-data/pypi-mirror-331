import pytest
from django.db.models import QuerySet

from fast_seeker.contrib.django.sorting import Sorter, SortingQuery
from fast_seeker.core.sorting import OrderEntry

############################
## Tests for SortingQuery ##
############################


@pytest.mark.parametrize(
    "entry, expected",
    [
        pytest.param(OrderEntry.desc("field1"), "-field1", id="descending"),
        pytest.param(OrderEntry.asc("field1"), "field1", id="ascending"),
    ],
)
def test_django_sorting_query_default_entry_resolver__should_return_str_representation(entry, expected):
    assert SortingQuery().default_entry_resolver(entry) == expected


######################
## Tests for Sorter ##
######################


@pytest.mark.parametrize(
    "query",
    [
        pytest.param(["field1"], id="descending"),
        pytest.param(["-field1"], id="ascending"),
    ],
)
def test_django_sorter_apply_query__should_apply_to_queryset(query, mocker):
    mock_queryset = mocker.MagicMock(spec=QuerySet)
    sorter = Sorter()

    sorter.apply_query(data=mock_queryset, query=query)
    mock_queryset.order_by.assert_called_once_with(*query)
