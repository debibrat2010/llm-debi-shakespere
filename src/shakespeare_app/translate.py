from __future__ import annotations

import os
from dataclasses import dataclass

from openai import OpenAI

from shakespeare_app.env import load_project_env
from shakespeare_app.prompts import SYSTEM_INSTRUCTION, USER_TEMPLATE

_env_loaded = False


def _ensure_env() -> None:
    global _env_loaded
    if not _env_loaded:
        load_project_env()
        _env_loaded = True


@dataclass(frozen=True)
class TranslateConfig:
    model: str
    temperature: float = 0.7


def load_config() -> TranslateConfig:
    using_alt = bool((os.environ.get("OPENAI_BASE_URL") or "").strip())
    default_model = "llama3.2" if using_alt else "gpt-4o-mini"
    model = os.environ.get("OPENAI_MODEL", default_model).strip()
    temp_raw = os.environ.get("OPENAI_TEMPERATURE", "0.7").strip()
    try:
        temperature = float(temp_raw)
    except ValueError:
        temperature = 0.7
    temperature = max(0.0, min(2.0, temperature))
    return TranslateConfig(model=model, temperature=temperature)


def _build_client() -> OpenAI:
    """OpenAI-compatible servers (e.g. local Ollama) use ``OPENAI_BASE_URL``; key may be a placeholder."""
    base_url = (os.environ.get("OPENAI_BASE_URL") or "").strip() or None
    api_key = (os.environ.get("OPENAI_API_KEY") or "").strip() or None
    if base_url:
        return OpenAI(base_url=base_url, api_key=api_key or "ollama")
    if api_key:
        return OpenAI(api_key=api_key)
    return OpenAI()


def to_shakespeare(text: str, *, client: OpenAI | None = None, config: TranslateConfig | None = None) -> str:
    """Rewrite *text* into Shakespearean-style English via the Chat Completions API."""
    stripped = text.strip()
    if not stripped:
        return ""

    _ensure_env()

    cfg = config or load_config()
    api = client or _build_client()

    response = api.chat.completions.create(
        model=cfg.model,
        temperature=cfg.temperature,
        messages=[
            {"role": "system", "content": SYSTEM_INSTRUCTION},
            {"role": "user", "content": USER_TEMPLATE.format(text=stripped)},
        ],
    )
    choice = response.choices[0].message.content
    return (choice or "").strip()
