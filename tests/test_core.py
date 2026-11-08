"""Behavioral regressions using synthetic values and reserved example domains."""

from copy import deepcopy
import json
from urllib.parse import quote

import pytest

from kayla_url_redact import (
    LIMIT_EXCEEDED,
    REDACTED,
    UNSUPPORTED,
    sanitize_text,
    sanitize_url,
    sanitize_value,
)


SECRET = "FAKE_CREDENTIAL_7319"
BASE = "https://shop.example/items/coat"
SEPARATORS = (" ", "\t", "\n", "\r", "\r\n")


@pytest.mark.parametrize("value", [
    BASE,
    "http://shop.example/",
    "https://shop.example:8443/items/coat",
    "https://shop.example/items/caf%C3%A9",
])
def test_url_without_query_is_preserved(value):
    assert sanitize_url(value) == value


@pytest.mark.parametrize("query", [
    "?token=" + SECRET,
    "?apiKey=" + SECRET,
    "?a=" + SECRET,
    "?a=1&b=2",
    "?li=12345&lpm=EXACT&pt=timeline",
    "?redirect=https%3A%2F%2Fnested.example%2F%3Ftoken%3D" + SECRET,
    "?a=1;token=" + SECRET,
    "?token=" + SECRET + "&token=another",
])
def test_url_removes_every_query_parameter_without_domain_exceptions(query):
    assert sanitize_url(BASE + query) == BASE


@pytest.mark.parametrize("value", [
    "",
    "shop.example/items/coat",
    "/items/coat",
    "//shop.example/items/coat",
    "ftp://shop.example/items/coat",
    "file:///tmp/example",
    "javascript:alert(1)",
    "https:///items/coat",
    "https://[broken/items/coat",
    "https://shop.example:invalid/items/coat",
    "https://shop.example:99999/items/coat",
    "https://user:" + SECRET + "@shop.example/items/coat",
    "https://user@shop.example/items/coat",
    "https://@shop.example/items/coat",
    BASE + "#" + SECRET,
    "https://shop.example/token/" + SECRET,
    "https://shop.example/password:" + SECRET,
    "https://shop.example/p;token=" + SECRET,
    "https://shop.example/%74oken/" + SECRET,
    "https://shop.example\\@other.example/items/coat",
    "https://shop.example/p%5C" + SECRET,
    "https://shop.example/p%00" + SECRET,
    "https://shop.example/p%0A" + SECRET,
    "https://shop.example/p%GG",
    "https://shop.example/p\ud800",
])
def test_url_rejects_unsafe_or_unsupported_forms(value):
    assert sanitize_url(value) is None


@pytest.mark.parametrize("separator", SEPARATORS + ("\u00a0", "\x00", "\x7f"))
def test_url_never_silently_normalizes_control_or_whitespace(separator):
    assert sanitize_url(BASE + "?token=" + separator + SECRET) is None


@pytest.mark.parametrize("shape", [
    BASE + "?token={sep}" + SECRET,
    BASE + "?a={sep}" + SECRET,
    BASE + "?token=prefix{sep}" + SECRET,
    BASE + "?li=1&token={sep}" + SECRET,
    BASE + "?li=123{sep}" + SECRET,
    BASE + "?{sep}a=" + SECRET,
    BASE + "{sep}?a=" + SECRET,
    "https://user:{sep}" + SECRET + "@shop.example/items/coat",
])
@pytest.mark.parametrize("separator", SEPARATORS)
def test_text_rejects_whole_field_instead_of_retaining_credential_tails(shape, separator):
    value = "before " + shape.format(sep=separator) + " after"
    assert sanitize_text(value) is None
    assert sanitize_value({"description": value}) == {"description": REDACTED}


@pytest.mark.parametrize("value", [
    "An ordinary coat\nwith a belt",
    "Text with a\ttab",
    "See " + BASE + " for details.",
    "Compare https://a.example/a and https://b.example/b",
    "café / 外套",
    "",
])
def test_ordinary_text_is_preserved(value):
    assert sanitize_text(value) == value


@pytest.mark.parametrize("value", [
    "See " + BASE + "?page=2 for details",
    "https://safe.example/a then " + BASE + "?a=\n" + SECRET,
    "prefix " + BASE + "?token=%2509" + SECRET,
    "prefix ftp://shop.example/" + SECRET,
    "prefix custom://shop.example/" + SECRET,
    "prefix //shop.example/" + SECRET,
    "password=" + SECRET,
    "Authorization: Bearer " + SECRET,
    "token: " + SECRET,
    "before\x00after",
    "before\udfffafter",
])
def test_text_rejects_unsafe_urls_assignments_and_invalid_text(value):
    assert sanitize_text(value) is None


@pytest.mark.parametrize("levels", [1, 2, 3, 4, 5])
def test_encoded_credential_urls_do_not_escape_text_checks(levels):
    value = BASE + "?token=" + SECRET
    for _ in range(levels):
        value = quote(value, safe="")
    assert sanitize_text("prefix " + value) is None


def test_encoding_beyond_the_supported_depth_is_rejected():
    value = BASE
    for _ in range(6):
        value = quote(value, safe="")
    assert sanitize_text(value) is None


def test_opaque_secrets_are_explicitly_outside_the_detection_contract():
    assert sanitize_text(SECRET) == SECRET
    assert sanitize_url("https://shop.example/" + SECRET) == "https://shop.example/" + SECRET


@pytest.mark.parametrize("function", [sanitize_url, sanitize_text])
@pytest.mark.parametrize("value", [None, 1, True, [SECRET], {"value": SECRET}])
def test_string_apis_reject_wrong_types_without_echoing_the_value(function, value):
    with pytest.raises(TypeError) as failure:
        function(value)
    assert SECRET not in str(failure.value)


def test_type_errors_do_not_evaluate_custom_representations():
    class NoRepresentation:
        def __repr__(self):
            raise AssertionError("Input representation must not be evaluated")

        def __str__(self):
            raise AssertionError("Input string conversion must not be evaluated")

    for function in (sanitize_url, sanitize_text):
        with pytest.raises(TypeError):
            function(NoRepresentation())
    assert sanitize_value(NoRepresentation()) == UNSUPPORTED


@pytest.mark.parametrize("key", [
    "token", "access_token", "apiKey", "PASSWORD", "client_secret",
    "authorization", "cookie", "jwt", "signature", "credentials",
])
def test_sensitive_mapping_keys_and_values_are_omitted(key):
    result = sanitize_value({key: SECRET, "name": "coat"})
    assert result == {"name": "coat"}


def test_sensitive_mapping_key_itself_is_not_copied_into_metadata():
    key = "token_" + SECRET
    result = sanitize_value({key: "anything", "safe": 1})
    assert result == {"safe": 1}
    assert SECRET not in json.dumps(result)


@pytest.mark.parametrize("key", [1, None, ("tuple",), "space key", "bad/key", "x" * 129])
def test_invalid_mapping_keys_and_their_values_are_omitted(key):
    assert sanitize_value({key: SECRET, "safe": 1}) == {"safe": 1}


def test_supported_key_names_and_scalar_values_are_preserved():
    value = {"snake_case": [None, True, False, 12, -7, 1.25], "file.name": "ok", "hyphen-name": {}}
    assert sanitize_value(value) == value


def test_nested_values_are_sanitized_without_mutating_the_input():
    value = {
        "name": "coat",
        "items": [{"description": BASE + "?token=\t" + SECRET}, {"apiKey": SECRET, "value": 2}],
    }
    original = deepcopy(value)
    result = sanitize_value(value)
    assert result == {"name": "coat", "items": [{"description": REDACTED}, {"value": 2}]}
    assert value == original
    result["items"][1]["value"] = 3
    assert value == original


@pytest.mark.parametrize("value", [
    float("nan"), float("inf"), -float("inf"), b"bytes", (1, 2), {1, 2},
    pytest.param(1 << 20000, id="oversized-integer"),
])
def test_non_json_and_out_of_range_values_get_an_explicit_marker(value):
    assert sanitize_value(value) == UNSUPPORTED


def test_builtin_subclasses_are_not_allowed_to_execute_custom_methods():
    class HostileMapping(dict):
        def items(self):
            raise AssertionError("Mapping subclass methods must not execute")

    class HostileList(list):
        def __iter__(self):
            raise AssertionError("List subclass methods must not execute")

    assert sanitize_value(HostileMapping(safe=1)) == UNSUPPORTED
    assert sanitize_value(HostileList([1])) == UNSUPPORTED


def test_unsupported_types_do_not_invoke_metaclass_comparison_hooks():
    class HostileType(type):
        def __eq__(cls, other):
            raise AssertionError("Type comparison hooks must not execute")

    class Unsupported(metaclass=HostileType):
        pass

    assert sanitize_value(Unsupported()) == UNSUPPORTED


def test_repeated_reference_without_a_cycle_is_supported():
    child = {"name": "coat"}
    assert sanitize_value([child, child]) == [{"name": "coat"}, {"name": "coat"}]


@pytest.mark.parametrize("kind", ["list", "dict", "mixed"])
def test_cycles_fail_the_whole_value_with_a_bounded_marker(kind):
    if kind == "list":
        value = []
        value.append(value)
    elif kind == "dict":
        value = {}
        value["self"] = value
    else:
        value = {"children": []}
        value["children"].append(value)
    assert sanitize_value(value) == LIMIT_EXCEEDED


def test_depth_limit_fails_the_whole_value_not_a_partial_document():
    value = "leaf"
    for _ in range(18):
        value = [value]
    assert sanitize_value({"ordinary": 1, "deep": value}) == LIMIT_EXCEEDED


def test_node_limit_fails_the_whole_value():
    assert sanitize_value([None] * 10001) == LIMIT_EXCEEDED
    assert sanitize_value({"key" + str(i): i for i in range(10001)}) == LIMIT_EXCEEDED


def test_string_limit_is_applied_before_processing_the_value():
    at_limit = "a" * 65536
    assert sanitize_text(at_limit) == at_limit
    assert sanitize_value(at_limit) == at_limit
    too_long = at_limit + "a"
    assert sanitize_text(too_long) is None
    assert sanitize_url("https://shop.example/" + too_long) is None
    assert sanitize_value({"value": too_long}) == LIMIT_EXCEEDED


@pytest.mark.parametrize("value", [
    {"token": SECRET, "safe": [BASE, "ordinary", None]},
    {"value": BASE + "?token=\t" + SECRET},
    [float("inf"), 12, {"a/b": SECRET}],
    REDACTED,
    UNSUPPORTED,
    LIMIT_EXCEEDED,
])
def test_value_sanitization_is_idempotent_and_json_serializable(value):
    result = sanitize_value(value)
    assert sanitize_value(result) == result
    json.dumps(result, ensure_ascii=False, allow_nan=False).encode("utf-8")


def test_url_sanitization_is_idempotent():
    result = sanitize_url(BASE + "?token=" + SECRET)
    assert result == BASE
    assert sanitize_url(result) == result
