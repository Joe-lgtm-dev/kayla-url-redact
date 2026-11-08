"""Conservative record filtering; not a universal secret detector or URL firewall."""

from ._core import (
    LIMIT_EXCEEDED,
    MAX_DEPTH,
    MAX_NODES,
    MAX_TEXT_LENGTH,
    REDACTED,
    UNSUPPORTED,
    sanitize_text,
    sanitize_url,
    sanitize_value,
)

__version__ = "0.1.0a1"
__all__ = [
    "sanitize_url", "sanitize_text", "sanitize_value", "REDACTED", "UNSUPPORTED",
    "LIMIT_EXCEEDED", "MAX_DEPTH", "MAX_NODES", "MAX_TEXT_LENGTH",
]
