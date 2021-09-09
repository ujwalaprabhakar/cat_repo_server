from fastapi import APIRouter

from ujcatapi import config, dto

router = APIRouter()


@router.get("/status", operation_id="status_view", response_model=dto.StatusViewResponse)
async def status_view() -> dto.JSON:
    """
    Status view returning the name and version of this service and a link to Swagger documentation.

    \f
    :return:
    """
    return {
        "service": "ujcatapi",
        "version": config.VERSION,
        "links": [{"href": "/docs", "rel": "documentation", "type": "GET"}],
        "feature_flags": {"ENABLE_FOO": config.ENABLE_FOO, "ENABLE_BAR": config.ENABLE_BAR},
    }
