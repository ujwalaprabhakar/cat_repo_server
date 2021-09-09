from unittest import mock

from ujcatapi.events.common import fire_event


@mock.patch("ujcatapi.events.common.get_producer")
def test_fire_event(mock_get_producer: mock.Mock) -> None:
    mock_producer = mock.Mock()
    mock_get_producer.return_value = mock_producer

    fire_event("event_name", {"foo": "bar"})

    mock_producer.produce.assert_called_with("event_name", {"foo": "bar"})
