# Extraction notes

## Purpose and origin

This package isolates a small URL and text-redaction concern from an existing first-party catalogue-ingestion implementation. The original helpers were named `sanitized_url`, `sanitize_text`, and `sanitize_value`.

The motivating failure mode is general: a URL matcher can stop at whitespace before a credential value. Replacing only the matched URL token can leave the unexamined suffix in the surrounding text. The extracted text policy therefore rejects the whole field when an embedded URL is unsafe or requires rewriting.

The source helpers and their existing regression tests were read to understand this behavior. Public examples and tests for this package must be independently synthetic. Private source payloads, reviews, logs, database contents, and historical evidence are not part of this extraction.

## Deliberate API differences

| Area | Original application behavior | Standalone package contract |
| --- | --- | --- |
| URL helper name | `sanitized_url` | `sanitize_url` |
| Query policy | Selected catalogue relation parameters could survive under bounded grammars. | Remove all query parameters. No domain-specific `li`, `pt`, or `lpm` exceptions. |
| Text handling | Whole-field rejection protects against residual credential suffixes. | Retain whole-field rejection; accepted ordinary text is preserved. Never repair a substring and concatenate the original suffix. |
| Rejected strings | Application-specific typed markers. | The JSON string `"[REDACTED]"` inside `sanitize_value`; direct text and URL APIs return `None`. |
| Dictionary keys | Application-specific bookkeeping could retain redacted key names. | Omit sensitive or invalid keys without echoing them into result metadata. |
| Unsupported values | Application-specific marker objects. | The JSON string `"[UNSUPPORTED]"` for non-JSON types and non-finite numbers. |
| Traversal failures | Application-specific depth and node-limit handling. | A cycle or resource-limit violation returns `"[LIMIT_EXCEEDED]"` for the entire input. No partially retained tree. |
| Integration | Catalogue observations, identity bindings, persistence, and replay. | Pure sanitization functions and a stdin-only CLI. No persistence or catalogue identity logic. |

Defaults are a text length limit of 65,536 characters, a depth limit of 16, and a traversal-node limit of 10,000. Dictionary keys consume that budget too. The CLI additionally caps UTF-8 stdin at 1 MiB, does not strip input, and rejects duplicate JSON keys. Direct URL/text API rejection returns `None`; the CLI represents it as the JSON string `"[REDACTED]"` with exit status 0. Input-processing errors use generic stderr and exit status 2. All behavior must be demonstrated with the standalone package's own tests; source-project test results do not establish that this extraction works.

## Boundary around the original application

The production application remains on its existing implementation and does not import this package. The extraction does not change source selection, catalogue schemas, identity or ownership decisions, existing evidence, or production storage. A future integration would require a separate compatibility review because the query policy and result markers differ.

The package has no network, database, model, or application-framework dependency. It must not import private source modules to work or to run its tests. CLI errors must be generic and must not echo the input.

## What this does not establish

This work does not establish that the original application is free of security defects, that every secret can be recognized, or that every returned value is safe for public release. Opaque secrets can remain in unlabelled text, hostnames, and paths. Destination validation and output-context escaping belong to callers.

No accepted vulnerability disclosure, CVE, bug-bounty result, external adoption, or approval under an AI provider's verification program is claimed. Naming a maintainer documents responsibility; it does not by itself establish adoption or external program eligibility.

## Distribution status

Version `0.1.0a1` is a Python 3.11-or-later alpha distributed under MIT through [Joe-lgtm-dev/kayla-url-redact](https://github.com/Joe-lgtm-dev/kayla-url-redact) and its GitHub prereleases. It is not published on PyPI. The security maintainer is `Joe-lgtm-dev`; use the repository's [private vulnerability-reporting form](https://github.com/Joe-lgtm-dev/kayla-url-redact/security/advisories/new). See the [security policy](../SECURITY.md) and [release checklist](RELEASE_CHECKLIST.md).
