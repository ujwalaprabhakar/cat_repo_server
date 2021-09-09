import pytest

from ujcatapi import dto, serializers


@pytest.mark.parametrize(
    "scope_query, expected_scope",
    [
        (
            "org:000000000000000000000b00",
            dto.Scope(
                type=dto.MembershipType.organization,
                id=dto.OrganizationID("000000000000000000000b00"),
            ),
        )
    ],
)
def test_scope_from_query_param(scope_query: str, expected_scope: dto.Scope) -> None:
    assert serializers.scope_from_query_param(scope_query) == expected_scope


def test_scope_from_query_param_raises_on_unexpected_prefix() -> None:
    scope_query = "shard:000000000000000000000b00"

    with pytest.raises(ValueError) as scope_value_error:
        serializers.scope_from_query_param(scope_query)

    assert "shard is not a valid scope prefix. Choices are: org." in str(scope_value_error.value)


@pytest.mark.parametrize(
    "sort_by_query, expected_cat_sort_params",
    [
        (
            "name",
            dto.CatSortPredicates(
                [dto.CatSortPredicate(key=dto.CatSortKey.name, order=dto.SortOrder.asc)]
            ),
        ),
        (
            "-id,name",
            dto.CatSortPredicates(
                [
                    dto.CatSortPredicate(
                        key=dto.CatSortKey.id,
                        order=dto.SortOrder.desc,
                    ),
                    dto.CatSortPredicate(
                        key=dto.CatSortKey.name,
                        order=dto.SortOrder.asc,
                    ),
                ]
            ),
        ),
        # Case: Received sort_predicates contain leading and trailing commas, which should be
        # ignored by the serializer.
        (
            ",,,,id,,,name,,,",
            dto.CatSortPredicates(
                [
                    dto.CatSortPredicate(
                        key=dto.CatSortKey.id,
                        order=dto.SortOrder.asc,
                    ),
                    dto.CatSortPredicate(
                        key=dto.CatSortKey.name,
                        order=dto.SortOrder.asc,
                    ),
                ]
            ),
        ),
    ],
)
def test_cat_sort_params_from_query_params(
    sort_by_query: str,
    expected_cat_sort_params: dto.CatSortPredicates,
) -> None:
    assert serializers.cat_sort_params_from_query_params(sort_by_query) == expected_cat_sort_params


@pytest.mark.parametrize(
    "sort_by, expected_error_message",
    [
        ("middle_name", "'middle_name' is not a valid CatSortKey"),
        # Case: Provided sort_predicate was parsed, but is not a valid sort_key and sort_order
        # combination during serialization.
        ("++name", "'++name' is not a valid CatSortKey"),
        ("-name,name", "Duplicate sort_key values provided."),
    ],
)
def test_cat_sort_by_from_str_raises_exception(sort_by: str, expected_error_message: str) -> None:
    with pytest.raises(ValueError) as sort_by_value_error:
        serializers._cat_sort_by_from_str(sort_by)

    assert str(sort_by_value_error.value) == expected_error_message
