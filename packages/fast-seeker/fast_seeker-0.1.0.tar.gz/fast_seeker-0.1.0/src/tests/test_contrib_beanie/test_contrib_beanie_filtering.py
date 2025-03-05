from fast_seeker.contrib.beanie.filtering import Filterer, FilterQuery

from .utils import DummyFindMany

###########################
## Tests for FilterQuery ##
###########################


def test_beanie_filter_query_default_entry_resolver__should_return_beanie_representation():
    assert FilterQuery().default_field_resolver(field_name="field", field_value="value", field_info=None) == {
        "field": "value"
    }


########################
## Tests for Filterer ##
########################


def test_beanie_sorter_apply_query__should_apply_to_find_many():
    filterer = Filterer()
    query = [{"field": "value"}]

    result = filterer.apply_query(data=DummyFindMany(), query=query)
    assert result.find_expressions == query
