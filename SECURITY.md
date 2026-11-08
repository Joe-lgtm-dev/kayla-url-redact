# Security policy

## Maintainer and support

[Joe-lgtm-dev](https://github.com/Joe-lgtm-dev) is the security maintainer for [kayla-url-redact](https://github.com/Joe-lgtm-dev/kayla-url-redact). Responsibilities include triaging private reports, reproducing issues with synthetic inputs, assessing impact against the documented policy, maintaining regression tests and fixes, and documenting security-relevant release changes.

Security support is best effort and limited to the latest alpha release. The initial alpha is `0.1.0a1`; older alpha versions do not receive a separate maintenance branch. There is no guaranteed response or resolution time.

## Report a vulnerability

GitHub Private Vulnerability Reporting is enabled. Use the repository's [private reporting form](https://github.com/Joe-lgtm-dev/kayla-url-redact/security/advisories/new): sign in to GitHub and submit a private report. See [GitHub's reporting-feature documentation](https://docs.github.com/en/code-security/how-tos/report-and-fix-vulnerabilities/configure-vulnerability-reporting/configure-for-a-repository) for how the channel works.

Do not post real credentials, personal data, private URLs, production payloads, or private project history in a public issue. A private reporting form is not a reason to send unnecessary sensitive data: use synthetic examples wherever possible.

## Useful report contents

A report should include:

- The package version and Python version.
- A minimal reproducer containing only synthetic values.
- The expected behavior, actual result, and affected API or CLI mode.
- The input shape and relevant encoding or whitespace, without live secrets.
- Whether the result is a policy bypass, an exception, resource exhaustion, or an error-output disclosure.

Do not include exploit traffic against a live service. This package can be evaluated with local synthetic inputs; it has no network integration.

## Scope

Relevant issues include credential-labelled input surviving contrary to the documented policy, residual text retained after an unsafe embedded URL, sensitive dictionary keys copied into results, failures of cycle or resource limits, caller-container mutation, and raw input appearing in CLI errors.

The documented policy is intentionally limited. Unlabelled secrets in paths, hosts, and ordinary text may remain. The package is not a general secret scanner, URL destination authorizer, SSRF defense, or HTML/XSS sanitizer. A successful return value does not certify that data can be published.

## Release handling

The maintainer evaluates reports against this policy and records relevant fixes in regression tests and the changelog. Security fixes are delivered through a new GitHub prerelease; users should move to the latest alpha rather than relying on a backport. The package is licensed under MIT and is not published on PyPI.

This alpha has not received an independent security audit. Maintainer assignment and the reporting channel do not certify that outputs are safe to disclose or establish external access-program eligibility.
