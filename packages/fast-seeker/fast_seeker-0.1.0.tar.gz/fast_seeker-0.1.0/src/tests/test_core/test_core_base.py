from fast_seeker.core.base import QueryModel, QueryProcessor


class DummyQueryModel(QueryModel[str]):
    field_1: str

    def model_dump_query(self) -> str:
        return self.field_1


class DummyQueryProcessor(QueryProcessor[str, str]):
    def apply_query(self, *, data: str, query: str, **kwargs) -> str:
        return data + query


def test_query_processor_process__returns_expected_result():
    # Arrange
    query_processor = DummyQueryProcessor()
    data = "data"
    query = DummyQueryModel(field_1="query")

    # Act
    result = query_processor.process(data=data, query=query)

    # Assert
    assert result == "dataquery"
