import logging
from datetime import datetime, timezone
from typing import List, Optional

import pytest
from bson import ObjectId

from tests import conftest
from ujcatapi import dto
from ujcatapi.exceptions import DuplicateCatError
from ujcatapi.models import cat_model
from ujcatapi.models.common import BSONDocument, get_collection

UTC = timezone.utc
logger = logging.getLogger(__name__)


@pytest.fixture(autouse=True)
async def remove_cats() -> None:
    logger.warning("removing all Cats")
    cats = await get_collection(cat_model._COLLECTION_NAME)
    await cats.delete_many({})


@pytest.mark.parametrize(
    "unsaved_cat, expected_cat, expected_document",
    [
        (
            dto.UnsavedCat(
                name="Sammybridge Cat",
            ),
            dto.Cat(
                id="...",
                name="Sammybridge Cat",
                ctime=datetime(2020, 1, 1, 0, 0, tzinfo=UTC),
                mtime=datetime(2020, 1, 1, 0, 0, tzinfo=UTC),
            ),
            {
                "_id": "...",
                "name": "Sammybridge Cat",
                "ctime": datetime(2020, 1, 1, 0, 0, tzinfo=UTC),
                "mtime": datetime(2020, 1, 1, 0, 0, tzinfo=UTC),
            },
        )
    ],
)
@conftest.async_test
async def test_create_cat(
    unsaved_cat: dto.UnsavedCat,
    expected_cat: dto.Cat,
    expected_document: BSONDocument,
) -> None:
    now = datetime(2020, 1, 1, 0, 0, tzinfo=UTC)

    collection = await get_collection(cat_model._COLLECTION_NAME)
    created_cat = await cat_model.create_cat(
        new_cat=unsaved_cat,
        now=now,
    )

    # add IDs
    expected_cat = dto.Cat(id=dto.CatID(created_cat.id), **expected_cat.dict(exclude={"id"}))
    expected_document = {**expected_document, "_id": ObjectId(expected_cat.id)}

    assert created_cat == expected_cat
    actual_documents = [document async for document in collection.find()]

    assert actual_documents == [expected_document]


@pytest.mark.parametrize(
    "existing_cat_documents, unsaved_cat",
    [
        (
            [
                {
                    "_id": ObjectId("000000000000000000000101"),
                    "name": "Sammybridge Cat",
                    "ctime": datetime(2020, 1, 1, 0, 0, tzinfo=UTC),
                    "mtime": datetime(2020, 1, 1, 0, 0, tzinfo=UTC),
                },
            ],
            dto.UnsavedCat(
                name="Sammybridge Cat",
            ),
        )
    ],
)
@conftest.async_test
async def test_create_cat_duplicate_name(
    existing_cat_documents: List[BSONDocument],
    unsaved_cat: dto.UnsavedCat,
) -> None:
    now = datetime(2020, 1, 1, 0, 0, tzinfo=UTC)

    collection = await get_collection(cat_model._COLLECTION_NAME)
    await collection.insert_many(existing_cat_documents)

    with pytest.raises(DuplicateCatError) as duplicate_cat_error:
        await cat_model.create_cat(
            new_cat=unsaved_cat,
            now=now,
        )

    assert str(duplicate_cat_error.value) == "Cat with name Sammybridge Cat already exists."


@pytest.mark.parametrize(
    "existing_cat_documents, cat_filter, expected_cat",
    [
        (
            [
                {
                    "_id": ObjectId("000000000000000000000101"),
                    "name": "Sammybridge Cat",
                    "ctime": datetime(2020, 1, 1, 0, 0, tzinfo=UTC),
                    "mtime": datetime(2020, 1, 1, 0, 0, tzinfo=UTC),
                },
                {
                    "_id": ObjectId("000000000000000000000102"),
                    "name": "Shirasu Sleep Industries Cat",
                    "ctime": datetime(2020, 1, 1, 0, 0, tzinfo=UTC),
                    "mtime": datetime(2020, 1, 1, 0, 0, tzinfo=UTC),
                },
            ],
            dto.CatFilter(
                cat_id=dto.CatID("000000000000000000000101"),
            ),
            dto.Cat(
                id=dto.CatID("000000000000000000000101"),
                name="Sammybridge Cat",
                ctime=datetime(2020, 1, 1, 0, 0, tzinfo=UTC),
                mtime=datetime(2020, 1, 1, 0, 0, tzinfo=UTC),
            ),
        ),
        (
            [
                {
                    "_id": ObjectId("000000000000000000000101"),
                    "name": "Sammybridge Cat",
                    "ctime": datetime(2020, 1, 1, 0, 0, tzinfo=UTC),
                    "mtime": datetime(2020, 1, 1, 0, 0, tzinfo=UTC),
                },
                {
                    "_id": ObjectId("000000000000000000000102"),
                    "name": "Shirasu Sleep Industries Cat",
                    "ctime": datetime(2020, 1, 1, 0, 0, tzinfo=UTC),
                    "mtime": datetime(2020, 1, 1, 0, 0, tzinfo=UTC),
                },
            ],
            dto.CatFilter(name="Sammybridge Cat"),
            dto.Cat(
                id=dto.CatID("000000000000000000000101"),
                name="Sammybridge Cat",
                ctime=datetime(2020, 1, 1, 0, 0, tzinfo=UTC),
                mtime=datetime(2020, 1, 1, 0, 0, tzinfo=UTC),
            ),
        ),
        (
            [
                {
                    "_id": ObjectId("000000000000000000000101"),
                    "name": "Sammybridge Cat",
                    "ctime": datetime(2020, 1, 1, 0, 0, tzinfo=UTC),
                    "mtime": datetime(2020, 1, 1, 0, 0, tzinfo=UTC),
                },
                {
                    "_id": ObjectId("000000000000000000000102"),
                    "name": "Shirasu Sleep Industries Cat",
                    "ctime": datetime(2020, 1, 1, 0, 0, tzinfo=UTC),
                    "mtime": datetime(2020, 1, 1, 0, 0, tzinfo=UTC),
                },
            ],
            dto.CatFilter(
                cat_id=dto.CatID("000000000000000000000000"),
            ),
            None,
        ),
    ],
)
@conftest.async_test
async def test_find_one(
    existing_cat_documents: List[BSONDocument],
    cat_filter: dto.CatFilter,
    expected_cat: Optional[dto.Cat],
) -> None:
    collection = await get_collection(cat_model._COLLECTION_NAME)
    await collection.insert_many(existing_cat_documents)

    found_cat = await cat_model.find_one(cat_filter)

    assert found_cat == expected_cat


@pytest.mark.parametrize(
    "cat_filter",
    [
        dto.CatFilter(cat_id=dto.CatID("non-ObjectId")),
        dto.CatFilter(
            scope=dto.Scope(
                id=dto.OrganizationID("non-ObjectId"), type=dto.MembershipType.organization
            )
        ),
    ],
)
@conftest.async_test
async def test_find_one_empty_results_filter(
    cat_filter: dto.CatFilter,
) -> None:
    assert await cat_model.find_one(cat_filter) is None


@pytest.mark.parametrize(
    "existing_cat_documents, "
    "cat_filter, "
    "cat_sort_params, "
    "page, "
    "expected_cat_summaries",
    [
        (
            [
                {
                    "_id": ObjectId("000000000000000000000101"),
                    "name": "Sammybridge Cat",
                    "ctime": datetime(2020, 1, 1, 0, 0, tzinfo=UTC),
                    "mtime": datetime(2020, 1, 1, 0, 0, tzinfo=UTC),
                },
                {
                    "_id": ObjectId("000000000000000000000102"),
                    "name": "Shirasu Sleep Industries Cat",
                    "ctime": datetime(2020, 1, 1, 0, 0, tzinfo=UTC),
                    "mtime": datetime(2020, 1, 1, 0, 0, tzinfo=UTC),
                },
            ],
            dto.CatFilter(),
            [dto.CatSortPredicate(key=dto.CatSortKey.name, order=dto.SortOrder.asc)],
            dto.Page(number=1, size=10),
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
        ),
        (
            [
                {
                    "_id": ObjectId("000000000000000000000101"),
                    "name": "Sammybridge Cat",
                    "ctime": datetime(2020, 1, 1, 0, 0, tzinfo=UTC),
                    "mtime": datetime(2020, 1, 1, 0, 0, tzinfo=UTC),
                },
                {
                    "_id": ObjectId("000000000000000000000102"),
                    "name": "Shirasu Sleep Industries Cat",
                    "ctime": datetime(2020, 1, 1, 0, 0, tzinfo=UTC),
                    "mtime": datetime(2020, 1, 1, 0, 0, tzinfo=UTC),
                },
            ],
            dto.CatFilter(),
            [dto.CatSortPredicate(key=dto.CatSortKey.name, order=dto.SortOrder.asc)],
            dto.Page(number=1, size=1),
            dto.PagedResult[dto.CatSummary](
                results=[
                    dto.CatSummary(
                        id=dto.CatID("000000000000000000000101"),
                        name="Sammybridge Cat",
                    ),
                ],
                metadata=dto.PageMetadata(has_next_page=True),
            ),
        ),
    ],
)
@conftest.async_test
async def test_find_many(
    existing_cat_documents: List[BSONDocument],
    cat_filter: dto.CatFilter,
    cat_sort_params: dto.CatSortPredicates,
    page: dto.Page,
    expected_cat_summaries: dto.PagedResult[dto.CatSummary],
) -> None:
    collection = await get_collection(cat_model._COLLECTION_NAME)
    await collection.insert_many(existing_cat_documents)

    found_cat_summaries = await cat_model.find_many(
        cat_filter=cat_filter,
        cat_sort_params=cat_sort_params,
        page=page,
    )

    assert found_cat_summaries == expected_cat_summaries


@pytest.mark.parametrize(
    "existing_cat_documents, cat_id, cat_metadata, expected_document",
    [
        (
            [
                {
                    "_id": ObjectId("000000000000000000000101"),
                    "name": "Sammybridge Cat",
                    "ctime": datetime(2020, 1, 1, 0, 0, tzinfo=UTC),
                    "mtime": datetime(2020, 1, 1, 0, 0, tzinfo=UTC),
                },
                {
                    "_id": ObjectId("000000000000000000000102"),
                    "name": "Shirasu Sleep Industries Cat",
                    "ctime": datetime(2020, 1, 1, 0, 0, tzinfo=UTC),
                    "mtime": datetime(2020, 1, 1, 0, 0, tzinfo=UTC),
                },
            ],
            dto.CatID("000000000000000000000101"),
            dto.PartialUpdateCat(url="http://placekitten.com/200/300"),
            [
                {
                    "_id": ObjectId("000000000000000000000101"),
                    "name": "Sammybridge Cat",
                    "ctime": datetime(2020, 1, 1, 0, 0, tzinfo=UTC),
                    "mtime": datetime(2020, 1, 1, 0, 0, tzinfo=UTC),
                    "url": "http://placekitten.com/200/300",
                },
                {
                    "_id": ObjectId("000000000000000000000102"),
                    "name": "Shirasu Sleep Industries Cat",
                    "ctime": datetime(2020, 1, 1, 0, 0, tzinfo=UTC),
                    "mtime": datetime(2020, 1, 1, 0, 0, tzinfo=UTC),
                },
            ],
        )
    ],
)
@conftest.async_test
async def test_update_model_cat_metadata(
    existing_cat_documents: List[BSONDocument],
    cat_id: dto.CatID,
    cat_metadata: dto.PartialUpdateCat,
    expected_document: List[BSONDocument],
) -> None:
    collection = await get_collection(cat_model._COLLECTION_NAME)
    await collection.insert_many(existing_cat_documents)

    await cat_model.update_cat_metadata(cat_id, cat_metadata)

    # assert found_cat == expected_result
    actual_documents = [document async for document in collection.find()]

    assert actual_documents == expected_document
