import asyncio
import functools
from typing import Any, Callable, Generator

import pytest
from fastapi import Request

import ujcatapi


@pytest.fixture(scope="session")
def event_loop(request: Request) -> Generator:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


def async_test(f: Callable) -> Callable:
    @pytest.mark.asyncio
    @functools.wraps(f)
    async def mock_resetting_async_test(*args: Any, **kwargs: Any) -> None:
        for arg in args:
            arg.reset_mock()
        return await f(*args, **kwargs)

    return mock_resetting_async_test


@pytest.fixture(scope="session", autouse=True)
def assert_is_test_db() -> None:
    assert ujcatapi.config.MONGODB_URL.endswith("_test")


@pytest.fixture(autouse=True)
def mock_config(monkeypatch: Any) -> None:
    """
    Patch all env vars and config here that is relevant for tests.
    Make sure that running tests does NOT depend on the Docker .env file or deploy/vars.
    """
    monkeypatch.setattr("ujcatapi.config.ENABLE_FOO", "true")
    monkeypatch.setattr("ujcatapi.config.ENABLE_BAR", "false")


@pytest.fixture(autouse=True)
def prevent_actual_requests(monkeypatch: Any) -> None:
    def mock_request(*args: Any, **kwargs: Any) -> None:
        raise Exception(
            "Executing actual remote requests is not permitted in tests. "
            "See ujcatapi.tests.conftest.prevent_actual_requests for more information."
        )

    async def mock_async_request(*args: Any, **kwargs: Any) -> None:
        raise Exception(
            "Executing actual remote requests is not permitted in tests. "
            "See ujcatapi.tests.conftest.prevent_actual_requests for more information."
        )

    monkeypatch.setattr("urllib3.connectionpool.HTTPConnectionPool.urlopen", mock_request)
    monkeypatch.setattr("httpx.Client.request", mock_request)
    monkeypatch.setattr("httpx.AsyncClient.request", mock_async_request)
