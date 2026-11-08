# Changelog

## 0.1.0a1 — GitHub prerelease

Initial standalone alpha contract:

- Pure URL, text, and recursive JSON-value sanitization APIs with no third-party runtime dependencies.
- Removal of all URL query parameters; rejection of userinfo, fragments, credential-labelled paths, and inputs outside the URL policy.
- Whole-text rejection when an embedded URL is unsafe or needs rewriting, avoiding residual text after a partial URL match.
- Omission of sensitive or invalid dictionary keys; explicit markers for rejected strings, unsupported values, and whole-input traversal-limit failures.
- Default limits of 65,536 text characters, depth 16, and 10,000 value nodes, with cycle detection.
- Stdin-only `url`, `text`, and `json` CLI modes with JSON output and generic input-error reporting.
- Documentation of the limited threat model and extraction boundary.
- Owner-selected MIT License for the standalone package.
- Named security maintainer `Joe-lgtm-dev` and GitHub Private Vulnerability Reporting.

Distribution is through [GitHub Releases](https://github.com/Joe-lgtm-dev/kayla-url-redact/releases), not PyPI. The original production application is not integrated with this package. No independent security audit, third-party adoption, or CVP approval is claimed.
