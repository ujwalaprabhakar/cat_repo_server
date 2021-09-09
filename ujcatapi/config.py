import logging
import os
from typing import List

logger = logging.getLogger(__name__)


def _get_boolean_env_variable(name: str) -> bool:
    return os.getenv(name) == "true"


def _get_comma_separated_env_variable(name: str) -> List[str]:
    return [element.strip() for element in os.getenv(name, "").split(",") if element.strip() != ""]


VERSION = "1.8.8"
LOG_LEVEL = int(os.getenv("LOG_LEVEL", logging.NOTSET))
ENVIRONMENT = os.getenv("ENVIRONMENT")

ENABLE_RELOAD_UVICORN = _get_boolean_env_variable("ENABLE_RELOAD_UVICORN")

ENABLE_MONGODB = _get_boolean_env_variable("ENABLE_MONGODB")
MONGODB_URL = os.environ["MONGODB_URL"]
MONGO_MAX_POOL_SIZE = int(os.getenv("MONGO_MAX_POOL_SIZE", 100))
DEFAULT_LOCALE = "en_US"

ENABLE_AMQP = _get_boolean_env_variable("ENABLE_AMQP")
AMQP_URL = os.environ["AMQP_URL"]

ENABLE_SENTRY = _get_boolean_env_variable("ENABLE_SENTRY")
SENTRY_DSN = os.getenv("SENTRY_DSN")

ELASTIC_APM_ENABLED = _get_boolean_env_variable("ELASTIC_APM_ENABLED")
ELASTIC_APM_SERVER_URL = os.getenv("ELASTIC_APM_SERVER_URL")

# ====== Feature flags ======
ENABLE_FOO = _get_boolean_env_variable("ENABLE_FOO")
ENABLE_BAR = _get_boolean_env_variable("ENABLE_BAR")
