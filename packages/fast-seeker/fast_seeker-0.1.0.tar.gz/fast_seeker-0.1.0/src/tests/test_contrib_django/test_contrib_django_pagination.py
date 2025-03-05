from django.db.models import QuerySet

from fast_seeker.contrib.django.pagination import LimitOffsetQuery, PageNumberQuery, Paginator

################################
## Tests for LimitOffsetQuery ##
################################


def test_django_limit_offset_query_model_dump_query__should_return_slice():
    assert LimitOffsetQuery(limit=1, offset=2).model_dump_query() == slice(2, 3)


###############################
## Tests for PageNumberQuery ##
###############################


def test_django_page_number_query_model_dump_query__should_return_slice():
    assert PageNumberQuery(page=1, size=2).model_dump_query() == slice(0, 2)


#########################
## Tests for Paginator ##
#########################


def test_django_paginator_apply_query__should_return_slice(mocker):
    paginator = Paginator()
    mock_queryset = mocker.MagicMock(spec=QuerySet)
    query = slice(2, 3)
    result = paginator.apply_query(data=mock_queryset, query=query)
    assert result == mock_queryset.__getitem__.return_value
    mock_queryset.__getitem__.assert_called_once_with(query)
