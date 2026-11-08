# kayla-url-redact

A small Python library for removing URL queries and rejecting selected credential-bearing inputs before they enter logs or evidence exports.

Version `0.1.0a1` is an alpha distributed through [GitHub prereleases](https://github.com/Joe-lgtm-dev/kayla-url-redact/releases). The source repository is [Joe-lgtm-dev/kayla-url-redact](https://github.com/Joe-lgtm-dev/kayla-url-redact). It requires Python 3.11 or later and has no third-party runtime dependencies. The package makes no network requests and does not read a database or call a model.

**This is a bounded redaction policy, not a guarantee that an output is safe to publish.** Unlabelled secrets in paths, hostnames, and ordinary text can remain. Review outputs against your application's data policy.

## Install

Clone the source repository, then create an isolated environment:

```console
git clone https://github.com/Joe-lgtm-dev/kayla-url-redact.git
cd kayla-url-redact
python -m venv .venv
```

Activate that environment using your shell's usual command, then install:

```console
python -m pip install .
```

Alternatively, download the wheel from [GitHub Releases](https://github.com/Joe-lgtm-dev/kayla-url-redact/releases) and install the local file:

```console
python -m pip install ./kayla_url_redact-0.1.0a1-py3-none-any.whl
```

This standalone package is licensed under the [MIT License](LICENSE). It is not published on PyPI; use this repository or its GitHub release artifacts rather than assuming the package name on PyPI belongs to this project. The security maintainer is [Joe-lgtm-dev](https://github.com/Joe-lgtm-dev). Report vulnerabilities through the [private reporting form](https://github.com/Joe-lgtm-dev/kayla-url-redact/security/advisories/new); see [SECURITY.md](SECURITY.md) for scope and alpha support.

## Python API

```python
from kayla_url_redact import sanitize_text, sanitize_url, sanitize_value

assert sanitize_url("https://shop.example/items/42?ref=demo") == (
    "https://shop.example/items/42"
)
assert sanitize_url("https://user:FAKE@example.com/item") is None

assert sanitize_text("An ordinary product title") == "An ordinary product title"
assert sanitize_text("See https://shop.example/items/42?ref=demo") is None

assert sanitize_value({
    "message": "See https://shop.example/items/42?ref=demo",
    "api_key": "SYNTHETIC_EXAMPLE",
    "items": [True, None],
}) == {
    "message": "[REDACTED]",
    "items": [True, None],
}
```

| Function | Result and policy |
| --- | --- |
| `sanitize_url(value: str) -> str \| None` | Accept a conforming HTTP(S) URL and remove its entire query. Reject userinfo, fragments, credential-labelled paths, and other inputs outside the URL policy. No query-key allowlist is retained. |
| `sanitize_text(value: str) -> str \| None` | Preserve accepted ordinary text. Reject the whole string if an embedded URL is unsafe or would need rewriting, or if a suspected credential assignment is detected. Do not splice a cleaned URL into the original surrounding text. |
| `sanitize_value(value) -> JSON value` | Return a new JSON-compatible value. Replace a rejected string with `"[REDACTED]"`; omit sensitive or invalid dictionary keys; replace unsupported types and numbers with `"[UNSUPPORTED]"`. A cycle or resource-limit violation replaces the entire result with `"[LIMIT_EXCEEDED]"`. |

URL mode and text mode intentionally differ: URL mode may remove a query, while text mode rejects the entire containing string. This avoids retaining a suffix that a partial URL match failed to inspect.

The direct URL and text APIs require an exact built-in `str`; other input types raise `TypeError`. An oversized URL or text value returns `None`.

The default limits are 65,536 characters per text value, depth 16 with the root at depth 0, and 10,000 traversal nodes. Dictionary keys also consume the node budget, including omitted keys. In `sanitize_value`, an oversized string, excessive depth/node count, or cycle replaces the entire result with `"[LIMIT_EXCEEDED]"`. It does not modify the caller's containers.

The recursive API accepts exact built-in JSON types: `str`, `dict`, `list`, `bool`, `int`, `float`, and `None`. Other types, including tuples and custom subclasses, become `"[UNSUPPORTED]"`. Non-finite floats and integers exceeding 4,096 bits also become `"[UNSUPPORTED]"`.

The marker strings are ordinary JSON strings, not authenticated audit records. Sensitive keys are omitted without preserving their names in a redaction list. Callers must decide how omitted fields and marker values affect their own schema.

## CLI

```console
python -m kayla_url_redact url
python -m kayla_url_redact text
python -m kayla_url_redact json
```

Supply a UTF-8 payload through standard input, limited to 1 MiB (1,048,576 bytes). The only positional argument is the mode; the CLI does not accept payloads as arguments or open a supplied filename. Input is not stripped: a newline appended by a shell is part of the input and causes URL mode to reject the URL. Avoid placing real credentials in shell command history when producing the input stream.

| Mode | Standard input | Standard output |
| --- | --- | --- |
| `url` | A URL as raw text | A JSON string containing the result, or `"[REDACTED]"` for a rejected URL. |
| `text` | Raw text | A JSON string containing the result, or `"[REDACTED]"` for rejected text. |
| `json` | One JSON value | The JSON encoding of `sanitize_value`'s result. |

For example, this portable synthetic input producer sends a URL without adding a newline:

```console
python -c "import sys; sys.stdout.write('https://shop.example/item?ref=demo')" | python -m kayla_url_redact url
```

Expected output:

```json
"https://shop.example/item"
```

Policy rejection is represented in the result with exit status 0; the CLI maps the direct APIs' `None` result to `"[REDACTED]"`. Invalid invocation, invalid UTF-8, input over the byte cap, malformed JSON, duplicate JSON keys, or another input-processing error produces a generic error on standard error and exit status 2 without echoing the original input. Nonstandard JSON constants such as `NaN` and `Infinity` are input errors. Do not add raw input to your own error logs.

## Limits of protection

- This is not a general secret scanner. Unknown labels, opaque tokens, personal data, and application-specific identifiers may pass through.
- It does not authorize destinations or provide SSRF protection. A retained URL may still name a local, private, or otherwise inappropriate destination. The library does not resolve DNS or follow redirects.
- It does not escape HTML, JavaScript, SQL, Markdown, terminal controls for every consumer, or other output formats. Apply the encoding and validation required by the eventual sink.
- Removing a query can change the URL's meaning or make it unusable. A returned URL is not proof that a resource exists, is public, or may be redistributed.
- Conservative matching may reject benign inputs or omit useful dictionary keys. Preserve required business data through a separately reviewed schema rather than weakening redaction ad hoc.

## Project status

For local test/build commands and verification of installed wheels, see
[Development](docs/DEVELOPMENT.md). The CI workflow targets Windows and Linux on
Python 3.11–3.14. Check [GitHub Actions](https://github.com/Joe-lgtm-dev/kayla-url-redact/actions) for the result at the commit you intend to use.

The original production application does not import this package. This extraction does not include source data, private review history, database schemas, or catalogue-specific provenance rules. See [Extraction notes](docs/EXTRACTION.md), [Security policy](SECURITY.md), and the [Release checklist](docs/RELEASE_CHECKLIST.md).

No independent security audit, CVE, CVP approval, or third-party adoption is claimed.
