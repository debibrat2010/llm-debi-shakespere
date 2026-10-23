# Shakespeare OpenAI

Small Python app that rewrites modern English into Shakespearean-style English using an **OpenAI-compatible** chat API (OpenAI cloud, or **free local Ollama**).

## Requirements

- Python 3.9+ (3.11+ recommended)
- Either:
  - an [OpenAI API key](https://platform.openai.com/api-keys) with billing/credits, **or**
  - [Ollama](https://ollama.com) for **free, on-device** models (no OpenAI bill).

## Setup

```bash
cd /Users/debi/llm-debi-shakespere
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
```

Edit `.env` in the **project root** (same folder as `pyproject.toml`). The app loads that file even if you start `bard-web` or `bard` from another directory.

**Option A — OpenAI (paid usage):** set `OPENAI_API_KEY`. Optional: `OPENAI_MODEL` (default `gpt-4o-mini`), `OPENAI_TEMPERATURE` (default `0.7`, clamped 0–2).

**Option B — Ollama (free, local):** install Ollama, run `ollama pull llama3.2`, then in `.env` set:

```bash
OPENAI_BASE_URL=http://localhost:11434/v1
OPENAI_MODEL=llama3.2
```

You can omit `OPENAI_API_KEY` for Ollama (the app sends a harmless placeholder). Do **not** set `OPENAI_BASE_URL` if you want normal OpenAI cloud.

## Run

After activating the venv:

```bash
bard "I do not know why you are upset."
```

Or pipe:

```bash
echo "Where is the library?" | bard
python -m shakespeare_app <<< "Good morning everyone"
```

### Web UI

```bash
bard-web
```

Open **http://127.0.0.1:8765** in your browser. The server binds to loopback by default so it is not exposed on your LAN.

Optional environment variables: `BARD_HOST`, `BARD_PORT`, `BARD_RELOAD` (set to `1` for auto-reload while developing).

## Test (no API calls)

```bash
pytest -q
```

## Project layout

| Path | Role |
|------|------|
| `src/shakespeare_app/env.py` | Load `.env` from project root (next to `pyproject.toml`) |
| `src/shakespeare_app/prompts.py` | System instruction and user template |
| `src/shakespeare_app/translate.py` | `to_shakespeare()` and config from env |
| `src/shakespeare_app/cli.py` | `bard` CLI entrypoint |
| `src/shakespeare_app/web.py` | FastAPI app: `/`, `/api/translate`, `/health` |
| `src/shakespeare_app/web_cli.py` | `bard-web` (uvicorn) |
| `src/shakespeare_app/templates/index.html` | Web UI page |
| `tests/test_translate.py` | Mocked unit tests |
| `tests/test_web.py` | HTTP tests (mocked translate) |

## Notes

- The model is instructed to preserve meaning and avoid fake-archaic overload; tweak `prompts.py` to taste.
- OpenAI’s API is usage-based; `insufficient_quota` means add billing/credits at [OpenAI billing](https://platform.openai.com/account/billing), or switch to **Ollama** (see Setup).
- Local models are free but quality varies; `llama3.2` is a solid default on a Mac.
