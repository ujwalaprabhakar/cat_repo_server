import re
from logging import Formatter, Handler, LogRecord
from typing import Any, List, Optional, Pattern

SENSITIVE_FIELDS = [
    "access_token",
    "client_secret",
    "first_name",
    "id_token",
    "jwt",
    "last_name",
    "password",
    "password_reset_token",
    "refresh_token",
    "reset_password_url",
    "secret",
]

HIDDEN_FIELD_DISPLAY_VALUE = "**** [hidden for privacy] ****"

SEPARATOR_PATTERN = r"(\s*(?:=|:)\s*)"

LEFT_PAREN = r"('|\")"
NON_GREEDY_VALUE = r"(?:.*?)"
MATCHING_RIGHT_PAREN_UNESCAPED_OR_END = r"((?:(?<!\\)\3)|\Z|\n)"

VALUE_PATTERN = f"{LEFT_PAREN}{NON_GREEDY_VALUE}{MATCHING_RIGHT_PAREN_UNESCAPED_OR_END}"

EMAIL_PATTERN = re.compile(r"([\w_\.+-]+@[\w_\.-]+)")
EMAIL_REPLACEMENT = r"(?=\w{3,})(?<=\w{3})\w|(?!\w{3})\w"
EMAIL_SUBSTITUTION = "*"


def _get_sensitive_field_regex(field: str) -> Pattern:
    return re.compile(f"({field}|'{field}'|\"{field}\"){SEPARATOR_PATTERN}{VALUE_PATTERN}")


SENSITIVE_FIELD_PATTERNS = [_get_sensitive_field_regex(field) for field in SENSITIVE_FIELDS]


FIELD_CAP = r"\1"
SEPARATOR_CAP = r"\2"
LEFT_PAREN_CAP = r"\3"
RIGHT_PAREN_CAP = r"\4"

FIELD_SUBSTITUTION_PATTERN = (
    f"{FIELD_CAP}{SEPARATOR_CAP}{LEFT_PAREN_CAP}{HIDDEN_FIELD_DISPLAY_VALUE}{RIGHT_PAREN_CAP}"
)


def _sanitize_string(msg: str) -> str:
    """
    Replaces PII from string input, which could be an email address or a string
    representation of a Python object. The string representation may also be
    truncated to a certain length, thus the value pattern above also captures
    values when hitting end-of-string.
    """
    for email in EMAIL_PATTERN.findall(msg):
        msg = msg.replace(email, re.sub(EMAIL_REPLACEMENT, EMAIL_SUBSTITUTION, email))
    for field_pattern in SENSITIVE_FIELD_PATTERNS:
        msg = field_pattern.sub(FIELD_SUBSTITUTION_PATTERN, msg)
    return msg


def _sanitize_object(obj: object) -> object:
    if isinstance(obj, str):
        return _sanitize_string(obj)
    if isinstance(obj, dict):
        return {
            key: HIDDEN_FIELD_DISPLAY_VALUE
            if key in SENSITIVE_FIELDS
            else _sanitize_object(obj=value)
            for key, value in obj.items()
        }
    return obj


class LogSanitizerException(Exception):
    pass


class SanitizedFormatter(Formatter):
    """
    Custom formatter object which sanitizes logs before they are passed to a Handler.
    https://docs.python.org/3/howto/logging-cookbook.html#customized-exception-formatting
    This approach is also based on:
    https://relaxdiego.com/2014/07/logging-in-python.html
    """

    def __init__(self, orig_formatter: Optional[Formatter]):
        self.orig_formatter = orig_formatter

    def format(self, record: LogRecord) -> str:
        if not self.orig_formatter:
            raise LogSanitizerException()
        msg = self.orig_formatter.format(record)
        return _sanitize_string(msg=msg)

    def __getattr__(self, attr: str) -> Any:
        return getattr(self.orig_formatter, attr)


def sanitize_formatters(handlers: List[Handler]) -> None:
    for h in handlers:
        h.setFormatter(fmt=SanitizedFormatter(orig_formatter=h.formatter))


def sentry_event_log_sanitizer(event: Any, hint: Any) -> Any:
    log_params = event["logentry"]["params"]
    for index, param in enumerate(log_params):
        log_params[index] = _sanitize_object(obj=param)
    return event
