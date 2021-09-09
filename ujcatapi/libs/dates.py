import datetime

UTC = datetime.timezone.utc


def get_utcnow() -> datetime.datetime:
    """Helper to addresses two issues:
    - the fact datetimes are timezone-naive by default
    - the fact we can't mock datetime.utcnow() because it is a built-in written in C
    """
    return datetime.datetime.now(tz=UTC)
