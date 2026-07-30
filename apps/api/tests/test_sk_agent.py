from types import SimpleNamespace

from app.agent.sk_agent import extract_token_counts


def test_extract_token_counts_from_completion_usage_object():
    usage = SimpleNamespace(prompt_tokens=527, completion_tokens=243)
    metadata = {"usage": usage}

    assert extract_token_counts(metadata) == (527, 243)


def test_extract_token_counts_from_flat_dict():
    metadata = {"prompt_tokens": 100, "completion_tokens": 50}

    assert extract_token_counts(metadata) == (100, 50)


def test_extract_token_counts_from_none():
    assert extract_token_counts(None) == (0, 0)
