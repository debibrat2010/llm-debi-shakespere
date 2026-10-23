from unittest.mock import MagicMock, patch

import os
import pytest

from shakespeare_app.translate import TranslateConfig, to_shakespeare


def test_to_shakespeare_empty_returns_empty():
    assert to_shakespeare("", client=MagicMock()) == ""
    assert to_shakespeare("   \n  ", client=MagicMock()) == ""


def test_to_shakespeare_calls_openai_and_returns_content():
    fake_response = MagicMock()
    fake_response.choices = [MagicMock()]
    fake_response.choices[0].message.content = "  Hark, what news?  "

    client = MagicMock()
    client.chat.completions.create.return_value = fake_response

    cfg = TranslateConfig(model="gpt-test", temperature=0.5)
    out = to_shakespeare("Hello there", client=client, config=cfg)

    assert out == "Hark, what news?"
    client.chat.completions.create.assert_called_once()
    call_kw = client.chat.completions.create.call_args.kwargs
    assert call_kw["model"] == "gpt-test"
    assert call_kw["temperature"] == 0.5
    assert len(call_kw["messages"]) == 2
    assert "Hello there" in call_kw["messages"][1]["content"]


@patch.dict("os.environ", {"OPENAI_MODEL": "custom-model", "OPENAI_TEMPERATURE": "0.3"}, clear=False)
def test_load_config_from_env():
    from shakespeare_app.translate import load_config

    c = load_config()
    assert c.model == "custom-model"
    assert c.temperature == pytest.approx(0.3)


def test_load_config_default_model_openai_vs_ollama(monkeypatch):
    from shakespeare_app.translate import load_config

    monkeypatch.delenv("OPENAI_BASE_URL", raising=False)
    monkeypatch.delenv("OPENAI_MODEL", raising=False)
    assert load_config().model == "gpt-4o-mini"

    monkeypatch.setenv("OPENAI_BASE_URL", "http://localhost:11434/v1")
    monkeypatch.delenv("OPENAI_MODEL", raising=False)
    assert load_config().model == "llama3.2"


@patch("shakespeare_app.translate.OpenAI")
def test_build_client_ollama_placeholder_key(mock_openai):
    with patch.dict(
        os.environ,
        {"OPENAI_BASE_URL": "http://localhost:11434/v1", "OPENAI_API_KEY": ""},
        clear=False,
    ):
        from shakespeare_app.translate import _build_client

        _build_client()
    mock_openai.assert_called_once_with(
        base_url="http://localhost:11434/v1",
        api_key="ollama",
    )
