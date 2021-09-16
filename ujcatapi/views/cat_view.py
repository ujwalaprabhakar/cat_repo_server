import logging

from fastapi import APIRouter, Depends, HTTPException, Path, status

from ujcatapi import dto, serializers
from ujcatapi.domains import cat_domain

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/cats",
    response_model=dto.Cat,
    status_code=status.HTTP_201_CREATED,
)
async def create_cat(unsaved_cat: dto.UnsavedCat) -> dto.JSON:
    """
    Create view for creating a new Cat given an UnsavedCat payload.

    \f
    :return:
    """
    cat = await cat_domain.create_cat(unsaved_cat)
    return cat.dict()


@router.get("/cats/{cat_id}", response_model=dto.Cat, response_model_exclude_unset=True)
async def get_cat(
    cat_id: dto.CatID = Path(..., title="Cat ID", description="The ID of the Cat to get."),
    scope: dto.Scope = Depends(serializers.scope_from_query_param),
) -> dto.JSON:
    """
    Detail view for getting one Cat by ID.

    \f
    :return:
    """
    cat_filter = dto.CatFilter(cat_id=cat_id, scope=scope)

    cat = await cat_domain.find_one(cat_filter=cat_filter)
    if not cat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cat not found.")

    return cat.dict()


@router.get(
    "/cats",
    response_model=dto.ListResponse[dto.CatSummary],
    response_model_exclude_unset=True,
)
async def list_cats(
    scope: dto.Scope = Depends(serializers.scope_from_query_param),
    cat_filter: dto.CatFilter = Depends(serializers.cat_filter_from_query_params),
    cat_sort_params: dto.CatSortPredicates = Depends(
        serializers.cat_sort_params_from_query_params
    ),
    page: dto.Page = Depends(serializers.page_from_query_param),
) -> dto.ListResponse[dto.CatSummary]:
    """
    List view for API Client Summaries.
    API Clients can optionally be filtered by their ID, name, memberships, and secrets.

    \f
    :return:
    """

    cat_filter = dto.CatFilter(scope=scope, **cat_filter.dict(exclude={"scope"}))

    cats = await cat_domain.find_many(
        cat_filter=cat_filter,
        cat_sort_params=cat_sort_params,
        page=page,
    )

    cat_summary_list_response = [cat_summary.dict() for cat_summary in cats.results]

    return dto.ListResponse[dto.CatSummary](
        results=cat_summary_list_response, metadata=cats.metadata
    )


@router.get("/cats/delete/{cat_id}")
async def delete_cat(
    cat_id: dto.CatID = Path(..., title="Cat ID", description="The ID of the Cat to get."),
    scope: dto.Scope = Depends(serializers.scope_from_query_param),
) -> bool:
    """
    View for deleting one Cat by ID.

    \f
    :return:
    """

    is_deleted = await cat_domain.delete_one(cat_id)
    if not is_deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cat not found.")

    return is_deleted
