from fast_seeker.contrib.beanie.pagination import (
    BeanieQueryPage,
    LimitOffsetQuery,
    PageNumberQuery,
    Paginator,
)

from .utils import DummyFindMany

################################
## Tests for LimitOffsetQuery ##
################################


def test_beanie_limit_offset_query_model_dump_query__should_return_beanie_representation():
    assert LimitOffsetQuery(limit=1, offset=2).model_dump_query() == BeanieQueryPage(limit=1, skip=2)


###############################
## Tests for PageNumberQuery ##
###############################


def test_beanie_page_number_query_model_dump_query__should_return_beanie_representation():
    assert PageNumberQuery(page=1, size=2).model_dump_query() == BeanieQueryPage(limit=2, skip=0)


#########################
## Tests for Paginator ##
#########################


def test_beanie_paginator_apply_query__should_return_slice(mocker):
    paginator = Paginator()
    query = BeanieQueryPage(limit=1, skip=2)
    result = paginator.apply_query(data=DummyFindMany(), query=query)
    assert result.limit_number == query["limit"]
    assert result.skip_number == query["skip"]
