"""Read stdin only; never echo input in error messages or accept payload arguments."""

from __future__ import annotations

import json
import sys

from . import REDACTED, sanitize_text, sanitize_url, sanitize_value

MAX_STDIN_BYTES = 1_048_576
_USAGE = "Usage: kayla-url-redact {url,text,json} < input\n"


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def _reject_constant(_: str) -> None:
    raise ValueError("non-JSON constant")


def main() -> int:
    arguments = sys.argv[1:]
    if arguments in (["--help"], ["-h"]):
        sys.stdout.write(_USAGE)
        return 0
    if len(arguments) != 1 or arguments[0] not in {"url", "text", "json"}:
        sys.stderr.write(_USAGE)
        return 2
    try:
        raw = sys.stdin.buffer.read(MAX_STDIN_BYTES + 1)
        if len(raw) > MAX_STDIN_BYTES:
            raise ValueError("input too large")
        value = raw.decode("utf-8", errors="strict")
        mode = arguments[0]
        if mode == "json":
            payload = json.loads(value, object_pairs_hook=_unique_object,
                                 parse_constant=_reject_constant)
            result = sanitize_value(payload)
        else:
            result = (sanitize_url if mode == "url" else sanitize_text)(value)
            if result is None:
                result = REDACTED
        output = (json.dumps(result, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")
        sys.stdout.buffer.write(output)
        return 0
    except (OSError, UnicodeError, ValueError, RecursionError):
        sys.stderr.write("Input could not be processed.\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
