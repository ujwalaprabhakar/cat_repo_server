from datetime import datetime, timezone
from typing import Optional
from unittest import mock

import pytest
from starlette.testclient import TestClient

from ujcatapi import dto
from ujcatapi.main import app

client = TestClient(app)

UTC = timezone.utc


@pytest.mark.parametrize(
    "json_request_body, expected_unsaved_cat, expected_cat, expected_response",
    [
        (
            {
                "name": "Sammybridge Cat",
            },
            dto.UnsavedCat(
                name="Sammybridge Cat",
            ),
            dto.Cat(
                id=dto.CatID("000000000000000000000101"),
                name="Sammybridge Cat",
                ctime=datetime(2020, 1, 1, 0, 0, tzinfo=UTC),
                mtime=datetime(2020, 1, 2, 0, 0, tzinfo=UTC),
            ),
            {
                "id": "000000000000000000000101",
                "name": "Sammybridge Cat",
                "ctime": "2020-01-01T00:00:00+00:00",
                "mtime": "2020-01-02T00:00:00+00:00",
            },
        ),
    ],
)
@mock.patch("ujcatapi.domains.cat_domain.create_cat")
def test_create_cat_success(
    mock_cat_domain_create_cat: mock.Mock,
    json_request_body: dto.JSON,
    expected_unsaved_cat: dto.Cat,
    expected_cat: dto.Cat,
    expected_response: dto.JSON,
) -> None:
    mock_cat_domain_create_cat.return_value = expected_cat

    response = client.post("/v1/cats", json=json_request_body)

    assert (response.status_code, response.json()) == (201, expected_response)
    mock_cat_domain_create_cat.assert_called_once_with(expected_unsaved_cat)


@pytest.mark.parametrize(
    "json_request_body, expected_error_message",
    [({}, {"errors": [{"body.name": {"msg": "field required", "type": "value_error.missing"}}]})],
)
@mock.patch("ujcatapi.domains.cat_domain.create_cat")
def test_create_cat_validation_error(
    mock_cat_domain_create_cat: mock.Mock,
    json_request_body: dto.JSON,
    expected_error_message: dto.JSON,
) -> None:
    response = client.post("/v1/cats", json=json_request_body)

    assert (response.status_code, response.json()) == (
        422,
        expected_error_message,
    )

    mock_cat_domain_create_cat.assert_not_called()


@pytest.mark.parametrize(
    "cat_id, query_params, expected_cat, expected_response",
    [
        (
            dto.CatID("000000000000000000000101"),
            "",
            dto.Cat(
                id=dto.CatID("000000000000000000000101"),
                name="Sammybridge Cat",
                ctime=datetime(2020, 1, 1, 0, 0, tzinfo=UTC),
                mtime=datetime(2020, 1, 2, 0, 0, tzinfo=UTC),
            ),
            {
                "id": "000000000000000000000101",
                "name": "Sammybridge Cat",
                "ctime": "2020-01-01T00:00:00+00:00",
                "mtime": "2020-01-02T00:00:00+00:00",
            },
        )
    ],
)
@mock.patch("ujcatapi.domains.cat_domain.find_one")
def test_get_cat(
    mock_cat_domain_find_one: mock.Mock,
    cat_id: dto.CatID,
    query_params: str,
    expected_cat: dto.Cat,
    expected_response: dto.JSON,
) -> None:
    mock_cat_domain_find_one.return_value = expected_cat

    response = client.get(f"/v1/cats/{cat_id}{query_params}")

    assert (response.status_code, response.json()) == (200, expected_response)
    mock_cat_domain_find_one.assert_called_once_with(cat_filter=dto.CatFilter(cat_id=cat_id))


@mock.patch("ujcatapi.domains.cat_domain.find_one")
def test_get_cat_not_found(
    mock_cat_domain_find_one: mock.Mock,
) -> None:
    mock_cat_domain_find_one.return_value = None

    response = client.get("/v1/cats/000000000000000000000000")

    assert (response.status_code, response.json()) == (404, {"detail": "Cat not found."})


@pytest.mark.parametrize(
    "query_params, "
    "expected_cat_filter, "
    "expected_cat_sort_params, "
    "expected_page, "
    "expected_cat_summaries, "
    "expected_response",
    [
        (
            "?sort_by=name&page_number=1&page_size=15",
            dto.CatFilter(),
            [dto.CatSortPredicate(key=dto.CatSortKey.name, order=dto.SortOrder.asc)],
            dto.Page(number=1, size=15),
            dto.PagedResult[dto.CatSummary](
                results=[
                    dto.CatSummary(
                        id=dto.CatID("000000000000000000000101"),
                        name="Sammybridge Cat",
                    ),
                    dto.CatSummary(
                        id=dto.CatID("000000000000000000000102"),
                        name="Shirasu Sleep Industries Cat",
                    ),
                ],
                metadata=dto.PageMetadata(has_next_page=False),
            ),
            {
                "results": [
                    {"id": "000000000000000000000101", "name": "Sammybridge Cat"},
                    {
                        "id": "000000000000000000000102",
                        "name": "Shirasu Sleep Industries Cat",
                    },
                ],
                "metadata": {"has_next_page": False},
            },
        ),
        (
            "?id=000000000000000000000101&sort_by=name&page_number=1&page_size=15",
            dto.CatFilter(cat_id=dto.CatID("000000000000000000000101")),
            [dto.CatSortPredicate(key=dto.CatSortKey.name, order=dto.SortOrder.asc)],
            dto.Page(number=1, size=15),
            dto.PagedResult[dto.CatSummary](
                results=[
                    dto.CatSummary(
                        id=dto.CatID("000000000000000000000101"),
                        name="Sammybridge Cat",
                    ),
                ],
                metadata=dto.PageMetadata(has_next_page=False),
            ),
            {
                "results": [
                    {"id": "000000000000000000000101", "name": "Sammybridge Cat"},
                ],
                "metadata": {"has_next_page": False},
            },
        ),
    ],
)
@mock.patch("ujcatapi.domains.cat_domain.find_many")
def test_list_cats(
    mock_cat_domain_find_many: mock.Mock,
    query_params: str,
    expected_cat_filter: dto.CatFilter,
    expected_cat_sort_params: Optional[dto.CatSortPredicates],
    expected_page: Optional[dto.Page],
    expected_cat_summaries: dto.PagedResult[dto.CatSummary],
    expected_response: dto.JSON,
) -> None:
    mock_cat_domain_find_many.return_value = expected_cat_summaries

    response = client.get(f"/v1/cats{query_params}")

    assert (response.status_code, response.json()) == (200, expected_response)
    mock_cat_domain_find_many.assert_called_with(
        cat_filter=expected_cat_filter,
        cat_sort_params=expected_cat_sort_params,
        page=expected_page,
    )
