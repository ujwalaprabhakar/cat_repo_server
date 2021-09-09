from starlette.testclient import TestClient

from ujcatapi.main import app

client = TestClient(app)


def test_root_view() -> None:
    response = client.get("/", allow_redirects=False)

    assert (response.status_code, response.headers["location"]) == (303, "/docs")


def test_docs_view() -> None:
    response = client.get("/docs")

    assert (response.status_code, response.headers["content-type"]) == (
        200,
        "text/html; charset=utf-8",
    )


def test_openapi_view() -> None:
    response = client.get("/openapi.json")

    assert (response.status_code, response.headers["content-type"]) == (
        200,
        "application/json; charset=utf-8",
    )
