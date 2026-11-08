# Development and verification

Use an isolated Python environment, then run from this checkout:

```console
python -m pip install -e ".[test]"
python -m pytest -q
python -m pip install "build>=1.2,<2" "twine>=6,<7"
python -m build
python -m twine check dist/*.whl dist/*.tar.gz
```

The default `build` command produces an sdist, then builds a wheel from that
sdist. Check the archive member lists before sharing either artifact. The
explicit `twine check` patterns exclude source ZIPs and verification reports
that may also be present in `dist/`.

To test the distribution, create a **second environment** containing pytest and
the built wheel. Do not install this checkout in editable mode into it:

```console
python -m pip install "pytest>=8,<10"
python -m pip install --no-deps dist/kayla_url_redact-0.1.0a1-py3-none-any.whl
python -I tools/verify_install.py
```

Use that second environment's interpreter for all three commands. The verifier
refuses imports from this checkout, runs the tests from a temporary directory
without `PYTHONPATH`, and exercises README examples and the installed console
entry point. The tests use synthetic values; they need no credentials, network
access, database, or original application imports. Installing development tools
may require network access.

The supplied CI workflow performs the same build and distribution checks on
Windows and Linux, with Python 3.11–3.14. It only reads repository contents and
does not publish packages or require publishing secrets. Action revisions are
pinned; compare upgrades with the upstream [checkout](https://github.com/actions/checkout)
and [setup-python](https://github.com/actions/setup-python) repositories before
changing them.

A local passing suite does not mean that the remote matrix has passed. Check
[GitHub Actions](https://github.com/Joe-lgtm-dev/kayla-url-redact/actions) at the
exact commit, and record actual interpreter versions when reporting validation.
Create the GitHub prerelease only after the checks for that commit complete;
these commands do not upload to PyPI. Release verification tasks are tracked in
the [release checklist](RELEASE_CHECKLIST.md).
