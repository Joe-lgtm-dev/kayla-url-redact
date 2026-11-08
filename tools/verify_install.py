"""Run tests and README examples against a normally installed distribution.

Run with the interpreter whose environment contains the built wheel and pytest.
The script refuses source/editable imports and runs the suite outside the repo.
"""

from pathlib import Path
import os
import re
import shutil
import subprocess
import sys
import sysconfig
import tempfile

import kayla_url_redact


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    installed = Path(kayla_url_redact.__file__).resolve()
    if installed.is_relative_to(root):
        raise RuntimeError("Install the wheel into a separate environment first")
    print(f"Verifying installed package: {installed}", flush=True)
    for example in re.findall(r"```python\n(.*?)```", root.joinpath("README.md").read_text(encoding="utf-8"), re.S):
        exec(compile(example, "README.md", "exec"), {})
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    with tempfile.TemporaryDirectory(prefix="kayla-redaction-tests-") as directory:
        target = Path(directory)
        shutil.copytree(root / "tests", target / "tests", ignore=shutil.ignore_patterns("__pycache__"))
        subprocess.run(
            [sys.executable, "-I", "-m", "pytest", "-q", "-p", "no:cacheprovider", "tests"],
            cwd=target, env=environment, check=True,
        )
        suffix = ".exe" if os.name == "nt" else ""
        command = Path(sysconfig.get_path("scripts")) / ("kayla-url-redact" + suffix)
        smoke = subprocess.run(
            [str(command), "url"], input=b"https://shop.example/item?ref=demo",
            capture_output=True, cwd=target, env=environment, check=True,
        )
        assert smoke.stdout.strip() == b'"https://shop.example/item"'
        assert smoke.stderr == b""
    print("README examples and installed console entry point passed.")


if __name__ == "__main__":
    main()
