from ujcatapi.events import common


def fire_cat_created(cat_id: str) -> None:
    """
    Fired after a new Cat has been created, so that this
    service can do some background post-processing and so that other services can subscribe to
    info on new Cats.
    """
    common.fire_event("cat.created", {"cat_id": cat_id})
