import logging
from typing import Optional

from ujcatapi import dto
from ujcatapi.events.cat_events import fire_cat_created
from ujcatapi.libs import dates
from ujcatapi.models import cat_model

logger = logging.getLogger(__name__)


# async def create_cat(new_cat: dto.UnsavedCat) -> dto.Cat:
#     now = dates.get_utcnow()
#     return await cat_model.create_cat(new_cat, now=now)


async def create_cat(new_cat: dto.UnsavedCat) -> dto.Cat:
    now = dates.get_utcnow()
    created_cat = await cat_model.create_cat(new_cat, now=now)
    fire_cat_created(created_cat.id)

    return created_cat


async def find_one(cat_filter: dto.CatFilter) -> Optional[dto.Cat]:
    return await cat_model.find_one(cat_filter=cat_filter)


async def find_many(
    cat_filter: Optional[dto.CatFilter] = None,
    cat_sort_params: Optional[dto.CatSortPredicates] = None,
    page: Optional[dto.Page] = None,
) -> dto.PagedResult[dto.CatSummary]:
    results = await cat_model.find_many(
        cat_filter=cat_filter,
        cat_sort_params=cat_sort_params,
        page=page,
    )
    return results


async def partial_update_cat_metadata(
    cat_id: dto.CatID, cat_metadata: dto.PartialUpdateCat
) -> Optional[dto.Cat]:

    result = await cat_model.update_cat_metadata(
        cat_id=cat_id,
        cat_metadata=cat_metadata,
    )

    return result
