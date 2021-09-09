from ujcatapi import dto
from ujcatapi.events.event_handlers import handle_cat_created


def test_handle_cat_created() -> None:
    data: dto.JSON = {
        "cat_id": "000000000000000000000101",
    }

    handle_cat_created(data)
