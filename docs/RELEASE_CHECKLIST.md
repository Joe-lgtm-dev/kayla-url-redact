# Release checklist

Use this checklist for GitHub prereleases of this standalone MIT package. The initial version is `0.1.0a1`; distribution is through [Joe-lgtm-dev/kayla-url-redact](https://github.com/Joe-lgtm-dev/kayla-url-redact), with no PyPI publication. Unchecked items are release-verification tasks, not claims that checks have passed.

## Ownership and public policy

- [x] Obtain the owner's license decision: MIT for the standalone package.
- [ ] Verify that the MIT license and matching package metadata are included in the release artifacts.
- [ ] Confirm the right to distribute every included file and dependency artifact.
- [x] Name the owner-approved security maintainer: `Joe-lgtm-dev`; responsibilities are documented in `SECURITY.md`.
- [x] Enable GitHub Private Vulnerability Reporting and verify the repository setting reports `enabled: true`.
- [ ] Verify that the private reporting link works and the maintainer's notification settings are configured. Do not claim notification delivery has been tested without an actual check.
- [x] Document best-effort support for the latest alpha, with no separate older-alpha maintenance branch or guaranteed response time.
- [x] Confirm the owner-approved public repository and distribution account: `Joe-lgtm-dev/kayla-url-redact`.

## Package and behavior

- [ ] Confirm version `0.1.0a1`, Python `>=3.11`, and the import name `kayla_url_redact` agree across package metadata, code, and documentation.
- [ ] Install from a clean local checkout or built distribution in an isolated environment. Verify the package works without the original application repository.
- [ ] Run the standalone suite and record the exact tested commit and relevant Python versions. Do not borrow CI results from the source application.
- [ ] Verify the URL API removes every query and rejects userinfo, fragments, credential-labelled paths, and malformed inputs covered by its policy.
- [ ] Verify whole-text rejection with multiple URLs, raw and encoded whitespace, and credential-like assignments. Check that no repaired substring is spliced into an original suffix.
- [ ] Verify accepted ordinary text is preserved and ordinary safe URLs remain usable under the documented contract.
- [ ] Verify sensitive and invalid dictionary keys are omitted without repeating their names in metadata.
- [ ] Verify non-JSON types, custom subclasses, non-finite numbers, and integers exceeding 4,096 bits produce `"[UNSUPPORTED]"`; rejected strings produce `"[REDACTED]"`.
- [ ] Verify cycles and default text/depth/node limits produce the documented bounded behavior, including whole-input `"[LIMIT_EXCEEDED]"` results for recursive traversal failures.
- [ ] Verify inputs are not mutated and no network, database, model, or source-project imports are required.
- [ ] Exercise all three CLI modes with stdin, correct JSON output, rejected strings, the 1 MiB cap, trailing newlines, invalid UTF-8, duplicate JSON keys, malformed JSON, invalid invocation, and generic errors that never echo synthetic secret input.
- [ ] Recheck README examples against the final implementation.

## Distribution contents

- [ ] Inspect source and built archives. Include only the standalone package, its synthetic tests, and intended project files.
- [ ] Exclude private history, original payloads, logs, database files, credentials, local environments, and unrelated application assets.
- [ ] Check that build metadata and error output contain no private filesystem paths or source-project information intended to remain private.
- [ ] Review the stated limitations: unknown secrets may survive; the package provides no SSRF, HTML/XSS, destination authorization, or general secret-scanning guarantee.
- [ ] Verify that the original production application remains independent of this package unless a separate integration has been authorized and tested.
- [ ] Run the public repository's own CI at the exact release commit before claiming a verified release.

## Publication and evidence

- [x] Obtain owner authorization for a public GitHub repository and GitHub prerelease; no PyPI publication.
- [ ] Verify the license, security policy, reporting channel, built artifacts, and exact release commit before creating the prerelease.
- [ ] Update the changelog and documentation to describe what was actually released.
- [ ] Claim external adoption only when it exists and can be verified. Link real downstream references, not invented consumers, stars, or self-created dependency records.
- [ ] Keep any verification-program application separate from software publication. Do not claim CVP approval, a CVE, accepted disclosure, or public security recognition without the corresponding evidence.

## Relevant platform documentation

- [GitHub: licensing a repository](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository)
- [GitHub: adding a security policy](https://docs.github.com/en/code-security/how-tos/report-and-fix-vulnerabilities/configure-vulnerability-reporting/add-security-policy)
- [GitHub: repository security advisories](https://docs.github.com/en/code-security/concepts/vulnerability-reporting-and-management/repository-security-advisories)
- [GitHub: configuring private vulnerability reporting](https://docs.github.com/en/code-security/how-tos/report-and-fix-vulnerabilities/configure-vulnerability-reporting/configure-for-a-repository)
- [GitHub: dependency graph and dependents](https://docs.github.com/en/code-security/concepts/supply-chain-security/dependency-graph)
