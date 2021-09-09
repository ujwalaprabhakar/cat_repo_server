from typing import Optional, Tuple

from fastapi import Query
from fastapi.exceptions import RequestValidationError
from pydantic import PositiveInt
from pydantic.error_wrappers import ErrorWrapper

from ujcatapi import dto
from ujcatapi.constants import PREFIX_TO_MEMBERSHIP_TYPE_MAPPING


def scope_from_query_param(
    scope: Optional[str] = Query(
        None,
        title="Scope",
        description=("The scope to filter objects by. Example: 'org:000000000000000000000b00'."),
    )
) -> Optional[dto.Scope]:
    if scope is None:
        return None

    prefix, object_id = scope.split(":")
    try:
        membership_type = PREFIX_TO_MEMBERSHIP_TYPE_MAPPING[prefix]
        return dto.Scope(type=membership_type, id=object_id)
    except KeyError:
        exc_msg = (
            f"{prefix} is not a valid scope prefix. Choices are: "
            f"{', '.join(PREFIX_TO_MEMBERSHIP_TYPE_MAPPING.keys())}."
        )
        scope_value_error = ValueError(exc_msg)
        raise RequestValidationError(
            errors=[ErrorWrapper(exc=scope_value_error, loc=("query.scope",))]
        )


def cat_filter_from_query_params(
    id: Optional[str] = Query(
        None,
        title="ID",
        description=("Cat ID to filter Cats by. Example: '00000000000000000000000a'."),
    ),
    name: Optional[str] = Query(
        None,
        title="Name",
        description=("Name to filter Cats by. Example: 'Sammybridge Cat'."),
    ),
) -> dto.CatFilter:
    cat_id = None
    if id is not None:
        cat_id = dto.CatID(id)

    return dto.CatFilter(cat_id=cat_id, name=name)


def _create_cat_sort_predicate(sort_key: str) -> dto.CatSortPredicate:
    sort_order = dto.SortOrder.asc
    if sort_key.startswith("-"):
        sort_order = dto.SortOrder.desc
        sort_key = sort_key[1:]

    return dto.CatSortPredicate(key=dto.CatSortKey(sort_key), order=sort_order)


def _cat_sort_by_from_str(sort_by: str, loc: Optional[Tuple[str]] = None) -> dto.CatSortPredicates:
    try:
        serialized_sort_predicates = [
            _create_cat_sort_predicate(sort_key) for sort_key in sort_by.split(",") if sort_key
        ]
        return dto.create_unique_cat_sort_predicates_list(serialized_sort_predicates)
    except ValueError as value_error:
        if loc is not None:
            raise RequestValidationError(errors=[ErrorWrapper(exc=value_error, loc=loc)])
        raise value_error


def cat_sort_params_from_query_params(
    sort_by: Optional[str] = Query(
        None,
        title="Sort",
        description=(
            "A comma-separated list of values that will indicate how the fetched Cat "
            "list should be sorted. By default, Cat are sorted in ascending order. "
            "Add a '-' at the beginning of the sort key to set the resulting list in descending "
            "order by that sort key. Example: 'name,-ctime"
        ),
    )
) -> Optional[dto.CatSortPredicates]:
    cat_sort_params = None
    if sort_by:
        cat_sort_params = _cat_sort_by_from_str(sort_by, loc=("query.sort_by",))
    return cat_sort_params


def page_from_query_param(
    page_number: Optional[PositiveInt] = Query(
        None,
        title="Page number",
        description=(
            "A positive integer to indicate which page of the results should be fetched. "
            "This parameter should be passed together with a page_size value."
        ),
    ),
    page_size: Optional[PositiveInt] = Query(
        None,
        title="Page size",
        description=(
            "A positive integer to indicate the number of results to be fetched per page. "
            "This parameter should be passed together with a page_number value."
        ),
    ),
) -> Optional[dto.Page]:
    if page_number is None and page_size is None:
        return None

    try:
        return dto.Page(number=page_number, size=page_size)
    except ValueError as error:
        raise RequestValidationError(errors=[ErrorWrapper(exc=error, loc=("query.page"))])
