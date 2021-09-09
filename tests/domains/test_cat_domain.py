from datetime import datetime, timezone
from unittest import mock

import pytest

from tests import conftest
from ujcatapi import dto
from ujcatapi.domains import cat_domain

UTC = timezone.utc


@pytest.mark.parametrize(
    "new_cat, expected_cat",
    [
        (
            dto.UnsavedCat(
                name="Sammybridge Cat",
            ),
            dto.Cat(
                id=dto.CatID("000000000000000000000101"),
                name="Sammybridge Cat",
                ctime=datetime(2020, 1, 1, 0, 0, tzinfo=UTC),
                mtime=datetime(2020, 1, 2, 0, 0, tzinfo=UTC),
            ),
        )
    ],
)
@mock.patch("ujcatapi.models.cat_model.create_cat")
@mock.patch("ujcatapi.libs.dates.get_utcnow")
@conftest.async_test
async def test_create_cat(
    mock_utcnow: mock.Mock,
    mock_cat_model_create_cat: mock.Mock,
    new_cat: dto.UnsavedCat,
    expected_cat: dto.Cat,
) -> None:
    mock_utcnow.return_value = datetime(2019, 1, 1, 23, 59, tzinfo=UTC)
    mock_cat_model_create_cat.return_value = expected_cat

    result = await cat_domain.create_cat(new_cat)

    assert result == expected_cat
    mock_cat_model_create_cat.assert_called_once_with(
        new_cat, now=datetime(2019, 1, 1, 23, 59, tzinfo=UTC)
    )


@pytest.mark.parametrize(
    "cat_filter",
    [
        dto.CatFilter(
            cat_id=dto.CatID("000000000000000000000101"),
            name="Sammybridge Cat",
        )
    ],
)
@mock.patch("ujcatapi.models.cat_model.find_one")
@conftest.async_test
async def test_find_one(mock_cat_model_find_one: mock.Mock, cat_filter: dto.CatFilter) -> None:
    await cat_domain.find_one(cat_filter)

    mock_cat_model_find_one.assert_called_once_with(cat_filter=cat_filter)


@pytest.mark.parametrize(
    "cat_filter, cat_sort_params, page",
    [
        (
            dto.CatFilter(
                cat_id=dto.CatID("000000000000000000000101"),
                name="Sammybridge Cat",
            ),
            [
                dto.CatSortPredicate(key=dto.CatSortKey.id, order=dto.SortOrder.asc),
                dto.CatSortPredicate(key=dto.CatSortKey.name, order=dto.SortOrder.desc),
            ],
            dto.Page(number=2, size=30),
        )
    ],
)
@mock.patch("ujcatapi.models.cat_model.find_many")
@conftest.async_test
async def test_find_many(
    mock_cat_model_find_many: mock.Mock,
    cat_filter: dto.CatFilter,
    cat_sort_params: dto.CatSortPredicates,
    page: dto.Page,
) -> None:
    await cat_domain.find_many(
        cat_filter=cat_filter,
        cat_sort_params=cat_sort_params,
        page=page,
    )

    mock_cat_model_find_many.assert_called_once_with(
        cat_filter=cat_filter,
        cat_sort_params=cat_sort_params,
        page=page,
    )
