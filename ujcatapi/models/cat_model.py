import logging
from datetime import datetime
from typing import Dict, Optional

import bson.errors
import pymongo
import pymongo.errors
from bson import ObjectId

from ujcatapi import config, dto
from ujcatapi.exceptions import DuplicateCatError, EmptyResultsFilter
from ujcatapi.models.common import (
    BSONDocument,
    _calculate_db_skip_value,
    bson_id_to_cat_id,
    get_collection,
)

_COLLECTION_NAME = "cats"
_CAT_SUMMARY_PROJECTION = {
    "_id": 1,
    "name": 1,
}


logger = logging.getLogger(__name__)


async def create_cat(new_cat: dto.UnsavedCat, now: datetime) -> dto.Cat:
    unsaved_cat_as_bson = unsaved_cat_to_bson(new_cat, now)
    collection = await get_collection(_COLLECTION_NAME)
    try:
        result = await collection.insert_one(unsaved_cat_as_bson)
    except pymongo.errors.DuplicateKeyError:
        raise DuplicateCatError(f"Cat with name {new_cat.name} already exists.")
    cat_id = bson_id_to_cat_id(result.inserted_id)
    logger.info(f"Successfully created Cat {cat_id} in Ujcatapi")
    return dto.Cat(
        id=cat_id,
        **unsaved_cat_as_bson,
    )


async def find_one(cat_filter: dto.CatFilter) -> Optional[dto.Cat]:
    try:
        match = cat_filter_to_db_match(cat_filter)
    except EmptyResultsFilter:
        return None

    collection = await get_collection(_COLLECTION_NAME)

    found = await collection.find_one(match)

    if found is None:
        return None

    return cat_from_bson(found)


async def find_many(
    cat_filter: Optional[dto.CatFilter] = None,
    cat_sort_params: Optional[dto.CatSortPredicates] = None,
    page: Optional[dto.Page] = None,
) -> dto.PagedResult[dto.CatSummary]:
    cat_filter = cat_filter or dto.CatFilter()
    match = cat_filter_to_db_match(cat_filter)

    # Default sort order. Prepend "_" if the intention is to sort results by ObjectId.
    sort = {f"_{dto.CatSortKey.id}": dto.SortOrder.desc}
    collation = None
    if cat_sort_params is not None:
        sort = cat_sort_params_to_db_sort(cat_sort_params)
        collation = pymongo.collation.Collation(locale=config.DEFAULT_LOCALE)

    facet = {
        "results": [{"$project": _CAT_SUMMARY_PROJECTION}],
    }
    skip_limit = (
        []
        if page is None
        else [{"$skip": _calculate_db_skip_value(page)}, {"$limit": page.size + 1}]
    )

    pipeline = [
        {"$match": match},
        {"$sort": sort},
        *skip_limit,
        {"$facet": facet},
        {"$project": {"results": _CAT_SUMMARY_PROJECTION}},
    ]
    collection = await get_collection(_COLLECTION_NAME)
    results = collection.aggregate(pipeline=pipeline, collation=collation)

    async for document in results:
        cat_summaries = [cat_summary_from_bson(results) for results in document["results"]]

    has_next_page = page is not None and len(cat_summaries) == page.size + 1
    if has_next_page:
        # We are fetching one document more to make sure that there is another page. The extra
        # document will be used in the future to enable token-based pagination.
        cat_summaries = cat_summaries[:-1]

    return dto.PagedResult[dto.CatSummary](
        results=cat_summaries, metadata=dto.PageMetadata(has_next_page=has_next_page)
    )


def cat_sort_params_to_db_sort(
    cat_sort_params: dto.CatSortPredicates,
) -> Dict[str, dto.SortOrder]:
    # TODO: Raise proper exception
    if not cat_sort_params:
        raise EmptyResultsFilter()

    sort_list = {
        sort_pair.key
        if sort_pair.key != dto.CatSortKey.id
        else f"_{dto.CatSortKey.id}": sort_pair.order
        for sort_pair in cat_sort_params
    }
    return sort_list


def unsaved_cat_to_bson(new_cat: dto.UnsavedCat, now: datetime) -> BSONDocument:
    return {
        **new_cat.dict(),
        "ctime": now,
        "mtime": now,
    }


def cat_from_bson(cat: BSONDocument) -> dto.Cat:
    return dto.Cat(
        id=bson_id_to_cat_id(cat["_id"]),
        name=cat["name"],
        ctime=cat["ctime"],
        mtime=cat["mtime"],
    )


def cat_filter_to_db_match(cat_filter: dto.CatFilter) -> BSONDocument:
    match: BSONDocument = {}

    if cat_filter.cat_id is not None:
        try:
            match["_id"] = ObjectId(cat_filter.cat_id)
        except bson.errors.InvalidId:
            raise EmptyResultsFilter()

    if cat_filter.name is not None:
        match["name"] = cat_filter.name

    if cat_filter.scope is not None:
        try:
            match["memberships"] = {
                "$elemMatch": {
                    "type": cat_filter.scope.type.value,
                    "id": ObjectId(cat_filter.scope.id),
                }
            }
        except bson.errors.InvalidId:
            raise EmptyResultsFilter()

    return match


def cat_summary_from_bson(cat: BSONDocument) -> dto.CatSummary:
    return dto.CatSummary(
        id=bson_id_to_cat_id(cat["_id"]),
        **cat,
    )


async def delete_one(cat_id: dto.CatID) -> bool:
    query: BSONDocument = {}
    try:
        query["_id"] = ObjectId(cat_id)
    except bson.errors.InvalidId:
        raise EmptyResultsFilter()

    collection = await get_collection(_COLLECTION_NAME)

    result = await collection.delete_one({"_id": query["_id"]})

    is_deleted = True
    if result.deleted_count == 0:
        is_deleted = False

    return is_deleted
