import logging
from typing import Mapping, Optional, Type

from fastapi import Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

import ujcatapi.exceptions

logger = logging.getLogger(__name__)


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder(
            {
                "errors": [
                    {
                        ".".join(str(loc) for loc in error["loc"]): {  # use str() for list indexes
                            "msg": error["msg"],
                            "type": error["type"],
                            "reason_code": error.get("ctx", {}).get("reason_code"),
                        }
                        if error.get("ctx", {}).get("reason_code")
                        else {"msg": error["msg"], "type": error["type"]}
                    }
                    for error in exc.errors()
                ]
            }
        ),
    )


async def exception_handler(request: Optional[Request], exc: Exception) -> JSONResponse:
    exception_to_http_error_mapping: Mapping[Type[Exception], int] = {
        ujcatapi.exceptions.EntityNotFoundError: status.HTTP_404_NOT_FOUND,
        ujcatapi.exceptions.DuplicateEntityError: status.HTTP_409_CONFLICT,
    }

    # We care for inheritance, so we need to check the error using isinstance(). A direct lookup
    # using e.g. exception_to_http_error_mapping.get(type(exc)) will not give correct results.
    for basetype, status_code in exception_to_http_error_mapping.items():
        if isinstance(exc, basetype):
            return JSONResponse(status_code=status_code, content={"errors": str(exc)})

    # catch-all
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"errors": str(exc)}
    )
