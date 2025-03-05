from fast_seeker.core.pagination import BaseLimitOffsetQuery, BasePaginator

#################################
## Tests for the BasePaginator ##
#################################


class DummyLimitOffsetQuery(BaseLimitOffsetQuery[dict]):
    def model_dump_query(self): ...


class DummyPaginator(BasePaginator[str, dict]):
    def apply_query(self, *, data, query, **kwargs): ...


def test_base_paginator_paginate__calls_process_with_expected_arguments(mocker):
    paginator = DummyPaginator()
    process_mock = mocker.patch.object(paginator, "process")
    data = "data"
    query = DummyLimitOffsetQuery()
    paginator.paginate(data=data, query=query)
    process_mock.assert_called_once_with(data=data, query=query)
