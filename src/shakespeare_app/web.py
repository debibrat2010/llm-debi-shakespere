from __future__ import annotations

import asyncio
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from openai import AuthenticationError, RateLimitError
from pydantic import BaseModel, Field

from shakespeare_app.translate import to_shakespeare

_TEMPLATES = Jinja2Templates(directory=str(Path(__file__).resolve().parent / "templates"))


def _message_for_rate_limit(exc: RateLimitError) -> str:
    body = exc.body
    code = None
    if isinstance(body, dict):
        err = body.get("error")
        if isinstance(err, dict):
            code = err.get("code")
    if code == "insufficient_quota":
        return (
            "Your OpenAI account has no usable quota (add billing or credits). "
            "Open https://platform.openai.com/account/billing then try again."
        )
    return (
        "OpenAI rate limit (429). Wait a moment and retry, or check "
        "https://platform.openai.com/account/limits"
    )

app = FastAPI(
    title="Bard",
    description="Modern English to Shakespearean-style English",
    version="0.1.0",
)


class TranslateBody(BaseModel):
    text: str = Field("", max_length=20000)


class TranslateResponse(BaseModel):
    translation: str


@app.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    return _TEMPLATES.TemplateResponse(
        request,
        "index.html",
        headers={"Cache-Control": "no-store"},
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/translate", response_model=TranslateResponse)
async def api_translate(body: TranslateBody) -> TranslateResponse:
    text = body.text.strip()
    if not text:
        return TranslateResponse(translation="")

    try:
        translation = await asyncio.to_thread(to_shakespeare, text)
    except AuthenticationError:
        raise HTTPException(
            status_code=401,
            detail=(
                "Missing or invalid OpenAI API key. Add OPENAI_API_KEY to a `.env` file "
                "in the project root (the folder that contains `pyproject.toml`), then restart the server."
            ),
        ) from None
    except RateLimitError as e:
        raise HTTPException(status_code=429, detail=_message_for_rate_limit(e)) from None
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e)) from e

    return TranslateResponse(translation=translation)
