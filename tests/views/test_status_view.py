from starlette.testclient import TestClient

from ujcatapi import config
from ujcatapi.main import app

client = TestClient(app)


def test_status_view() -> None:
    response = client.get("/status")
    assert (response.status_code, response.json()) == (
        200,
        {
            "service": "ujcatapi",
            "version": config.VERSION,
            "links": [{"href": "/docs", "rel": "documentation", "type": "GET"}],
            "feature_flags": {"ENABLE_FOO": config.ENABLE_FOO, "ENABLE_BAR": config.ENABLE_BAR},
        },
    )


def test_status_view_response_content_type() -> None:
    response = client.get("/status")
    assert response.headers["content-type"] == "application/json; charset=utf-8"
