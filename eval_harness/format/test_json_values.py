import json

import pytest

from eval_harness.format.json_values import (
    coerce_value,
    format_input,
    format_output,
    truncate,
)


def test_coerce_parsed_dict_unchanged():
    value = {"a": 1}
    assert coerce_value(value) == value


def test_coerce_json_string():
    assert coerce_value('[{"role": "user", "content": "hi"}]') == [
        {"role": "user", "content": "hi"}
    ]


def test_coerce_plain_string():
    assert coerce_value("hello") == "hello"


def test_coerce_none():
    assert coerce_value(None) == ""


def test_format_input_chat_transcript():
    messages = [
        {"role": "system", "content": "You are an expert."},
        {"role": "user", "content": "Hello"},
    ]
    result = format_input(messages)
    assert "[system]\nYou are an expert." in result
    assert "[user]\nHello" in result


def test_format_input_nested_object():
    value = {"args": [5, 1], "kwargs": {}}
    result = format_input(value)
    assert '"args"' in result
    assert "5" in result


def test_format_output_nested_eval():
    value = {
        "winner": "no_rag",
        "criteria": [{"criterion_name": "Correct Statement"}],
    }
    result = format_output(value)
    parsed = json.loads(result)
    assert parsed["winner"] == "no_rag"


def test_format_output_json_string():
    raw = '{"winner": "pass"}'
    result = format_output(raw)
    assert json.loads(result)["winner"] == "pass"


def test_format_input_plain_text():
    assert format_input("plain prompt") == "plain prompt"


def test_truncate():
    text = "x" * 100
    result = truncate(text, max_chars=50)
    assert len(result) <= 50
    assert "truncated" in result
