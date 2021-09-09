import datetime

from ujcatapi.libs.dates import get_utcnow

UTC = datetime.timezone.utc


def test_get_utcnow() -> None:
    assert (get_utcnow() - datetime.datetime.now(tz=UTC)) < datetime.timedelta(seconds=1)
