# Project adoption and KAYLA dependency evidence

**Reported dependent repositories: 1.**

As of **2026-11-09**, the maintainer reports one consuming repository: **KAYLA
(ltk-workbench)**. Both the consumer and this package are maintained by
[Joe-lgtm-dev](https://github.com/Joe-lgtm-dev). This is **first-party downstream
use on a development branch**, not independent third-party adoption. The package
repository itself, its tests, CI jobs, branches, and installations are not counted
as additional consumers.

This public page is a maintainer-authored dependency disclosure. It is not a
GitHub dependency-graph count, independent audit, or access-program eligibility
determination. The consumer source remains private, so readers can inspect this
declaration and its evidence fingerprints but cannot independently inspect the
consumer implementation from these public materials alone.

## Consumer and integration

| Field | Reported value |
| --- | --- |
| Consumer | KAYLA / ltk-workbench |
| Consumer repository visibility | Private; source code is not published here |
| Maintainer relationship | Same maintainer as kayla-url-redact |
| Integration branch | `codex/kayla-redact-integration-20261109` |
| Consumer commit | `3157dae431c2fdd41ebdd998c4d3a014b600e813` |
| Package version | `0.1.0a1` |
| Runtime use | Scraper logging, including CLI exception reporting |
| Integration status | Committed, pushed to the private development branch, and executed locally |
| Shared-branch merge / production deployment | Not claimed |
| Independent third-party consumers | None verified or claimed |

The consumer imports the installed package and calls `sanitize_text()` from its
existing logging function. Rejected log messages become `[REDACTED]`. This is a
runtime call, not just a dependency declaration. There is no optional-import
fallback that silently disables filtering.

**Affiliate links are product data, not automatically credentials.** This
integration filters log output only. It does not change product URL storage,
catalogue sanitization, or customer-facing links. The dependency's conservative
logging policy is not applied to rewrite affiliate links in place.

## Public dependency declaration

The following dependency declaration is disclosed with the consumer owner's
permission; no KAYLA application source is included:

```text
kayla-url-redact @ https://github.com/Joe-lgtm-dev/kayla-url-redact/releases/download/v0.1.0a1/kayla_url_redact-0.1.0a1-py3-none-any.whl --hash=sha256:bfacda7c4102d09dbdb0837b21c3d4e3e1ba8ea9f16ef9d877cd8ae6946b45e0
```

The consumer installs this with pip's `--require-hashes` option. The release is
MIT-licensed and has no third-party runtime dependencies.

- [Public package release and downloadable artifacts](https://github.com/Joe-lgtm-dev/kayla-url-redact/releases/tag/v0.1.0a1)
- [Released package source](https://github.com/Joe-lgtm-dev/kayla-url-redact/tree/3fc0ceb4fbaa3a1f7196e7fd4c1a6d1a8c4e3945)
- [Named security maintainer and reporting policy](../SECURITY.md)
- [Machine-readable public evidence summary](evidence/kayla-dependency-20261109.json)

## Executed verification

The maintainer's local verification ran **497 tests: 0 failures, 0 errors, and
0 skips**, including **25 new integration tests**, against a clean literal-blob
export of the consumer commit above. Installed distribution provenance and
package file hashes were checked. A before/after test with a synthetic credential
confirmed that the original logger printed it and the integrated logger emitted
only `[ERROR] [REDACTED]`.

Integration tests exercised the real logging function, the actual CLI error path,
and normal operational messages. Three existing supported LTK affiliate-link
forms passed through the real parser and persistence function into an in-memory
database with their complete URLs retained, including applicable `li`, `lpm`,
and `pt` parameters. This does not establish compatibility with every affiliate
provider or verify real commission attribution. No live database or external
scraping was used for these tests.

The private consumer's full remote CI was **in progress when this disclosure
was prepared**. These local test results are not a claim that that full CI passed.
The public package's own CI is separate from consumer integration testing.

An initial local test attempt failed because three new test fixtures omitted
their required parent-post setup. The fixture was corrected before the passing
run; the failed evidence was retained. An initial ordinary Git archive also
failed a byte-comparison check before testing; the passing run used a new exact
Git-blob export. Neither failed attempt is represented as a pass.

## Evidence fingerprints and privacy

The linked JSON publishes selected non-sensitive metadata from the private test
receipt: source identifiers, dependency identity, result counts, and SHA256
fingerprints. It excludes local paths, application source, raw test logs,
customer data, and credentials. It is a derived summary, not the original receipt.

The original receipt, JUnit results, and source remain private. Their hashes bind
this statement to specific artifacts and allow comparison if those artifacts
are separately disclosed to an authorized reviewer; hashes alone do not prove
the artifacts' contents or correctness. No cryptographic third-party attestation
is claimed. Additional evidence can be considered through a separately agreed
private review process; access is not automatically granted by this page.

Whether one same-maintainer private development consumer satisfies an external
program's adoption criteria is for that program to decide.
