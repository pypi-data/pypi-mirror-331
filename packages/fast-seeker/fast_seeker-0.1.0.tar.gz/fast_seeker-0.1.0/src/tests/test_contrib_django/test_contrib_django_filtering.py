from django.db.models import Q, QuerySet

from fast_seeker.contrib.django.filtering import Filterer, FilterQuery

###########################
## Tests for FilterQuery ##
###########################


def test_django_filter_query_default_field_resolver__should_return_q_object():
    query = FilterQuery()
    assert query.default_field_resolver(field_name="field", field_value="value", field_info=None) == Q(field="value")


########################
## Tests for Filterer ##
########################


def test_django_filterer__should_return_filtered_queryset(mocker):
    filterer = Filterer()
    mock_queryset = mocker.MagicMock(spec=QuerySet)
    q_object = Q(field="value")
    filterer.apply_query(data=mock_queryset, query=[q_object])
    mock_queryset.filter.assert_called_once_with(q_object)
