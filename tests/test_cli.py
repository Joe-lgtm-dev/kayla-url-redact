"""Exercise the installed module through real processes with synthetic stdin."""

import json
import subprocess
import sys

import pytest


SECRET = "FAKE_CREDENTIAL_7319"


def run_cli(tmp_path, mode, payload=b"", *extra):
    return subprocess.run(
        [sys.executable, "-m", "kayla_url_redact", mode, *extra],
        input=payload,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=tmp_path,
        timeout=15,
        check=False,
    )


def output(result):
    assert result.returncode == 0, result.stderr.decode("utf-8", errors="replace")
    assert result.stderr == b""
    return json.loads(result.stdout.decode("utf-8"))


def test_url_cli_strips_query_and_emits_a_json_string(tmp_path):
    result = run_cli(tmp_path, "url", ("https://shop.example/p?token=" + SECRET).encode())
    assert output(result) == "https://shop.example/p"
    assert SECRET.encode() not in result.stdout + result.stderr


def test_url_cli_does_not_silently_strip_input_newlines(tmp_path):
    assert output(run_cli(tmp_path, "url", b"https://shop.example/p\n")) == "[REDACTED]"


def test_text_cli_preserves_utf8_and_newlines(tmp_path):
    value = "A café\n外套\n"
    assert output(run_cli(tmp_path, "text", value.encode("utf-8"))) == value


def test_text_cli_rejects_the_whole_field(tmp_path):
    value = "before https://shop.example/p?token=\t" + SECRET + " after"
    result = run_cli(tmp_path, "text", value.encode())
    assert output(result) == "[REDACTED]"
    assert SECRET.encode() not in result.stdout + result.stderr


def test_json_cli_sanitizes_nested_values(tmp_path):
    payload = {"items": [{"token": SECRET, "name": "coat"}], "note": "https://shop.example/p?a=" + SECRET}
    result = run_cli(tmp_path, "json", json.dumps(payload).encode())
    assert output(result) == {"items": [{"name": "coat"}], "note": "[REDACTED]"}
    assert SECRET.encode() not in result.stdout + result.stderr


@pytest.mark.parametrize("value", [None, True, 12, "ordinary", [1, 2]])
def test_json_cli_accepts_top_level_json_scalars_and_arrays(tmp_path, value):
    assert output(run_cli(tmp_path, "json", (" \n" + json.dumps(value) + "\n ").encode())) == value


@pytest.mark.parametrize("payload", [
    b"",
    ("{\"name\":\"" + SECRET).encode(),
    ("{\"name\":\"safe\",\"name\":\"" + SECRET + "\"}").encode(),
    ("{\"nested\":{\"a\":\"safe\",\"a\":\"" + SECRET + "\"}}").encode(),
    ("{} \"" + SECRET + "\"").encode(),
    b"NaN",
    b"Infinity",
    b"-Infinity",
    b"\xff" + SECRET.encode(),
])
def test_invalid_json_is_rejected_without_echoing_input_or_traceback(tmp_path, payload):
    result = run_cli(tmp_path, "json", payload)
    assert result.returncode == 2
    assert result.stdout == b""
    assert result.stderr
    assert SECRET.encode() not in result.stderr
    assert b"Traceback" not in result.stderr


@pytest.mark.parametrize("mode", ["url", "text", "json"])
def test_input_size_cap_is_checked_for_every_mode(tmp_path, mode):
    payload = SECRET.encode() + b"x" * (1024 * 1024 + 1)
    result = run_cli(tmp_path, mode, payload)
    assert result.returncode == 2
    assert result.stdout == b""
    assert result.stderr
    assert SECRET.encode() not in result.stderr
    assert b"Traceback" not in result.stderr


@pytest.mark.parametrize("mode", ["url", "text"])
def test_non_utf8_stdin_is_rejected_without_a_decoder_traceback(tmp_path, mode):
    result = run_cli(tmp_path, mode, b"\xff" + SECRET.encode())
    assert result.returncode == 2
    assert result.stdout == b""
    assert result.stderr
    assert SECRET.encode() not in result.stderr
    assert b"Traceback" not in result.stderr


def test_argument_errors_do_not_echo_secrets(tmp_path):
    for result in (
        run_cli(tmp_path, SECRET),
        run_cli(tmp_path, "url", b"", SECRET),
    ):
        assert result.returncode == 2
        assert result.stdout == b""
        assert result.stderr
        assert SECRET.encode() not in result.stderr
        assert b"Traceback" not in result.stderr


def test_help_is_available_without_reading_input(tmp_path):
    result = run_cli(tmp_path, "--help")
    assert result.returncode == 0
    assert b"url" in result.stdout and b"text" in result.stdout and b"json" in result.stdout
    assert result.stderr == b""
