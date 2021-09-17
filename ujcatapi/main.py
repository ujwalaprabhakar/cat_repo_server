import logging
import sys
from typing import Callable

import sentry_sdk
import uvicorn  # type: ignore
from ai_event_pubsub.consumer import EventConsumer
from ai_event_pubsub.healthcheck import run_healthcheck
from elasticapm.contrib.starlette import ElasticAPM, make_apm_client  # type: ignore
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, Response
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware
from sentry_sdk.integrations.logging import LoggingIntegration

from ujcatapi import config
from ujcatapi.error_handler import exception_handler, validation_exception_handler
from ujcatapi.events.event_handlers import EVENT_HANDLERS
from ujcatapi.exceptions import UjcatapiError
from ujcatapi.libs import log_sanitizer
from ujcatapi.views import cat_view, status_view

logger = logging.getLogger(__name__)


def init_logging() -> None:
    logging.basicConfig(
        format="%(asctime)s %(levelname)-5.5s [%(name)s:%(lineno)s][%(threadName)s] %(message)s",
        level=config.LOG_LEVEL,
    )
    log_sanitizer.sanitize_formatters(logging.root.handlers)


def init_sentry(app: FastAPI) -> None:  # pragma: no cover
    if config.ENABLE_SENTRY:
        sentry_logging_integration = LoggingIntegration(
            level=logging.INFO,  # Capture info and above as context for future events
            event_level=logging.ERROR,  # Send errors and exceptions as events to Sentry
        )
        sentry_sdk.init(
            dsn=config.SENTRY_DSN,
            integrations=[sentry_logging_integration],
            environment=config.ENVIRONMENT,
            send_default_pii=True,
            before_send=log_sanitizer.sentry_event_log_sanitizer,
        )
        app.add_middleware(SentryAsgiMiddleware)


def init_apm(app: FastAPI) -> None:  # pragma: no cover
    if not config.ELASTIC_APM_ENABLED:
        return

    apm = make_apm_client(
        {
            "SERVICE_NAME": "ujcatapi",
            "SERVER_URL": config.ELASTIC_APM_SERVER_URL,
            "ENVIRONMENT": config.ENVIRONMENT,
        }
    )
    app.add_middleware(ElasticAPM, client=apm)


def init_event_consumer() -> EventConsumer:
    return EventConsumer(
        service_name="ujcatapi",
        environment_name=config.ENVIRONMENT,
        amqp_url=config.AMQP_URL,
        event_handler_map=EVENT_HANDLERS,
    )


def include_routers(app: FastAPI) -> None:
    app.include_router(status_view.router)
    app.include_router(cat_view.router, prefix="/v1")


def add_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(UjcatapiError, exception_handler)


def add_middlewares(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex="|".join(config.ALLOWED_ORIGINS_REGEXPES),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=[
            "Content-Type",
            "Date",
            "Content-Length",
            "Authorization",
            "X-Request-ID",
            "X-Correlation-ID",
        ],
        max_age=1728000,
    )

    @app.middleware("http")
    async def replace_content_type_header(request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        if response.headers.get("content-type") == "application/json":
            response.headers["content-type"] = "application/json; charset=utf-8"
        return response


init_logging()

app = FastAPI(
    title="Ujcatapi", description="Lionbridge AI Cat Management Service", version=config.VERSION
)
init_sentry(app)
init_apm(app)
include_routers(app)
add_exception_handlers(app)
add_middlewares(app)


@app.get("/")
async def root_view() -> RedirectResponse:
    return RedirectResponse(url="/docs", status_code=303)


if __name__ == "__main__":
    args = sys.argv[1:]

    if len(args) == 0 or args[0] == "api":
        uvicorn.run(
            "ujcatapi.main:app",
            host="0.0.0.0",
            port=10000,
            log_level="info",
            reload=config.ENABLE_RELOAD_UVICORN,
        )

    elif args[0] == "consumer":
        if not config.ENABLE_AMQP:
            logger.warning("AMQP is not enabled, consumer will not start")
            sys.exit(0)

        event_consumer = init_event_consumer()
        event_consumer.run()

    elif args[0] == "consumer-healthcheck":
        if not config.ENABLE_AMQP:
            logger.warning("AMQP is not enabled, consumer-healthcheck will not start")
            sys.exit(0)

        run_healthcheck(
            service_name="ujcatapi",
            environment_name=config.ENVIRONMENT,
            amqp_url=config.AMQP_URL,
        )
