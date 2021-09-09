import logging
from typing import Any, NamedTuple

import pytest

from ujcatapi.libs.log_sanitizer import sanitize_formatters


@pytest.mark.parametrize(
    "text, replaced",
    [
        # Case: leaves nearby text intact
        (
            "stuff='123', password='12345', etc",
            "stuff='123', password='**** [hidden for privacy] ****', etc",
        ),
        # Cases: redacts email addresses, may include plus in local
        ("email='alice@admin.sammybridge.com'", "email='ali**@adm**.sam********.c**'"),
        ("email='bob@user.sammybridge.com'", "email='b**@us**.sam********.c**'"),
        ("email='bob-with-hyphens@bob.com'", "email='b**-wi**-hyp****@b**.c**'"),
        ("email='me@me.com'", "email='**@**.c**'"),
        ("email='a@a.com'", "email='*@*.c**'"),
        ("email='alice.has.lots.of.pii+1@a.com'", "email='ali**.h**.lo**.**.p**+*@*.c**'"),
        # Case: emails don't need to be matched to "email" keyword
        ("...,alice@admin.sammybridge.com,...", "...,ali**@adm**.sam********.c**,..."),
        # Case: preserves "s
        ('password="password"', 'password="**** [hidden for privacy] ****"'),
        # Case: preserves 's
        ("password='password'", "password='**** [hidden for privacy] ****'"),
        # Case: value may contain "s or 's
        ("password='p@^&*(\\')\"xyz'", "password='**** [hidden for privacy] ****'"),
        # Case: partial request params with stack strace
        (
            "{'jwt': '123.123.123456\nTraceback:",
            "{'jwt': '**** [hidden for privacy] ****\nTraceback:",
        ),
    ],
)
def test_sanitizes_string(text: str, replaced: str, caplog: Any) -> None:
    caplog.set_level(logging.INFO)
    logger = logging.getLogger()
    sanitize_formatters(logger.handlers)

    logger.info(text)

    assert replaced in caplog.text


def test_sanitizes_object(caplog: Any) -> None:
    caplog.set_level(logging.INFO)

    # mypy has a cache-related issue with defining classes inside functions,
    # workaround is to use inline syntax. cf. https://github.com/python/mypy/issues/7281
    DummyClass = NamedTuple(
        "DummyClass",
        [("test_field", str), ("password", str), ("password_reset_token", str), ("email", str)],
    )

    test_instance = DummyClass(
        test_field="test",
        password_reset_token="my_token",
        password="test_password\"'xyziuoahsodf123123",
        email="alice@admin.sammybridge.com",
    )

    logger = logging.getLogger()
    sanitize_formatters(logger.handlers)

    logger.info(str(test_instance))

    assert (
        "DummyClass(test_field='test', "
        "password='**** [hidden for privacy] ****', "
        "password_reset_token='**** [hidden for privacy] ****', "
        "email='ali**@adm**.sam********.c**')"
    ) in caplog.text


def test_sanitizes_dicts(caplog: Any) -> None:
    caplog.set_level(logging.INFO)

    test_dict_params = {
        "jwt": "abcd.efg.hijk",
        "access_token": "456",
        "email": "alice@admin.sammybridge.com",
        "credentials": {"password": "password"},
    }

    logger = logging.getLogger()
    sanitize_formatters(logger.handlers)

    logger.info(str(test_dict_params))

    assert (
        "{'jwt': '**** [hidden for privacy] ****', "
        "'access_token': '**** [hidden for privacy] ****', "
        "'email': 'ali**@adm**.sam********.c**', 'credentials': {'password': "
        "'**** [hidden for privacy] ****'}}"
    ) in caplog.text
