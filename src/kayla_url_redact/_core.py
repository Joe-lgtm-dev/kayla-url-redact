"""Pure, bounded filtering adapted from KAYLA's internal sanitization logic.

The checks recognize URL structure and credential labels, not the sensitivity of
arbitrary bytes. Opaque secrets in ordinary prose, hostnames, or unlabelled paths
can survive. Nothing in this module authorizes fetching or rendering a URL.
"""

from __future__ import annotations

import math
import re
from urllib.parse import unquote, urlsplit, urlunsplit

MAX_TEXT_LENGTH = 65_536
MAX_DEPTH = 16
MAX_NODES = 10_000
REDACTED = "[REDACTED]"
UNSUPPORTED = "[UNSUPPORTED]"
LIMIT_EXCEEDED = "[LIMIT_EXCEEDED]"

_LABEL = (
    r"token|secret|password|passwd|credential|signature|api[ _-]?key|"
    r"access[ _-]?(?:key|token)|authorization|session|cookie|bearer|jwt|sig|auth|pwd"
)
_SECRET_KEY = re.compile(
    r"token|secret|password|passwd|credential|signature|api[ _-]?key|"
    r"access[ _-]?(?:key|token)|authorization|session|cookie|bearer|jwt|^sig$|^auth$|^pwd$",
    re.IGNORECASE | re.ASCII,
)
_SECRET_PATH = re.compile(
    rf"(?:^|[/;?&=])(?:{_LABEL})(?:[/;?&=:]|$)", re.IGNORECASE | re.ASCII
)
_SECRET_ASSIGNMENT = re.compile(
    rf"(?:^|[\s/;?&])(?:{_LABEL})\s*[=:]", re.IGNORECASE | re.ASCII
)
# Match unsupported schemes too: their contents must not evade HTTP(S) checks.
_URL = re.compile(
    r"(?<![a-z0-9+.-])(?:[a-z][a-z0-9+.-]*:)?//[^\s\"'<>]+", re.IGNORECASE | re.ASCII
)
_KEY = re.compile(r"[A-Za-z0-9_.-]{1,128}\Z")
_BAD_ESCAPE = re.compile(r"%(?![0-9a-fA-F]{2})")


class _LimitExceeded(Exception):
    """Internal control flow, with no input payload attached."""


def _decoded(value: str) -> str:
    for _ in range(5):
        decoded = unquote(value, errors="strict")
        if decoded == value:
            return value
        value = decoded
    if unquote(value, errors="strict") != value:
        raise ValueError("encoding depth exceeded")
    return value


def _control(char: str) -> bool:
    point = ord(char)
    return point < 32 or 127 <= point <= 159 or 0xD800 <= point <= 0xDFFF


def sanitize_url(value: str) -> str | None:
    """Return an HTTP(S) URL with *all* query parameters removed, or ``None``.

    Userinfo, fragments, labelled credential paths, ambiguous encoded delimiters,
    controls, whitespace, and unsupported URL forms are rejected. URLs are never
    fetched. An accepted value is not a guarantee that its host/path is public.
    """
    if type(value) is not str:
        raise TypeError("sanitize_url expects a built-in str")
    if not value or len(value) > MAX_TEXT_LENGTH:
        return None
    if any(_control(c) or c.isspace() or c in "\\\"'<>" for c in value):
        return None
    if _BAD_ESCAPE.search(value):
        return None
    try:
        parts = urlsplit(value)
        decoded = _decoded(value)
        path = _decoded(parts.path)
        # Reading .port also validates malformed and out-of-range ports.
        _ = parts.port
        if (
            parts.scheme.lower() not in {"http", "https"}
            or not parts.hostname
            or parts.username is not None
            or parts.password is not None
            or "#" in value
            or "%" in parts.netloc
            or any(c in "?#@\\" for c in path)
            or _SECRET_PATH.search(path)
            or any(_control(c) or c.isspace() or c in "\\\"'<>" for c in decoded)
        ):
            return None
        if "?" not in value:
            return value
        return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))
    except (UnicodeError, ValueError):
        return None


def sanitize_text(value: str) -> str | None:
    """Keep original text, or reject the *whole* field when a check fails.

    Never replace a URL token while preserving an unchecked whitespace suffix.
    Ordinary prose without recognizable URL or credential patterns can pass even
    when it contains a secret. This API is deliberately not a general DLP tool.
    """
    if type(value) is not str:
        raise TypeError("sanitize_text expects a built-in str")
    if len(value) > MAX_TEXT_LENGTH:
        return None
    try:
        decoded = _decoded(value)
    except (UnicodeError, ValueError):
        return None
    if any(_control(c) and c not in "\t\r\n" for c in decoded):
        return None
    if _SECRET_ASSIGNMENT.search(decoded):
        return None
    # Inspect both representations, since decoding can introduce URL delimiters.
    for representation in (value, decoded):
        for match in _URL.finditer(representation):
            token = match.group()
            tail = representation[match.end():]
            if sanitize_url(token) != token:
                return None
            if token.endswith(":"):
                return None
            if tail[:1].isspace() and (
                "?" in token or re.match(r"\s*[?&#=]", tail)
            ):
                return None
    return value


def sanitize_value(value: object) -> object:
    """Return a fresh JSON-compatible tree of exact built-in JSON types.

    Sensitive/invalid dictionary keys are omitted, with no raw-key side channel.
    Unsafe strings and unsupported values become fixed marker strings. A cycle,
    excessive depth/node count, or oversized string replaces the entire result
    with ``LIMIT_EXCEEDED``. Marker strings are data, not authenticity claims.
    """
    remaining = MAX_NODES
    active: set[int] = set()

    def consume() -> None:
        nonlocal remaining
        remaining -= 1
        if remaining < 0:
            raise _LimitExceeded

    def visit(item: object, depth: int) -> object:
        consume()
        if depth > MAX_DEPTH:
            raise _LimitExceeded
        kind = type(item)
        if kind is str:
            if len(item) > MAX_TEXT_LENGTH:
                raise _LimitExceeded
            safe = sanitize_text(item)
            return safe if safe is not None else REDACTED
        if item is None or kind is bool:
            return item
        if kind is int:
            return item if item.bit_length() <= 4096 else UNSUPPORTED
        if kind is float:
            return item if math.isfinite(item) else UNSUPPORTED
        if kind is not dict and kind is not list:
            return UNSUPPORTED
        identity = id(item)
        if identity in active:
            raise _LimitExceeded
        active.add(identity)
        try:
            if kind is list:
                return [visit(child, depth + 1) for child in item]
            result = {}
            for key, child in item.items():
                consume()  # Sensitive/invalid keys also consume the shared budget.
                if type(key) is not str or _KEY.fullmatch(key) is None:
                    continue
                if _SECRET_KEY.search(key):
                    continue
                result[key] = visit(child, depth + 1)
            return result
        finally:
            active.remove(identity)

    try:
        return visit(value, 0)
    except _LimitExceeded:
        return LIMIT_EXCEEDED
