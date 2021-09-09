from typing import Any
from unittest import mock

from ujcatapi.events.cat_events import fire_cat_created


@mock.patch("ujcatapi.events.common.fire_event")
def test_fire_cat_created(mock_fire_event: mock.Mock, monkeypatch: Any) -> None:
    cat_id = "000000000000000000000001"

    with monkeypatch.context():
        monkeypatch.setattr("ujcatapi.config.ENABLE_AMQP", True)
        fire_cat_created(cat_id)

    mock_fire_event.assert_called_once_with(
        "cat.created",
        {"cat_id": "000000000000000000000001"},
    )
