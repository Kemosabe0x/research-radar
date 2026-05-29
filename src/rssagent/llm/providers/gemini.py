"""Gemini provider integration (REST)."""

from __future__ import annotations

import logging
from typing import Sequence

import requests

from rssagent import config
from rssagent.llm.types import LLMResponse

logger = logging.getLogger(__name__)

GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


def _message_to_part(message: dict[str, str]) -> dict[str, object]:
    role = message.get("role", "user").lower()
    # Gemini expects "user" / "model". "system" can be modeled as user text.
    gemini_role = "model" if role == "assistant" else "user"
    return {
        "role": gemini_role,
        "parts": [{"text": message.get("content", "")}],
    }


def complete(messages: Sequence[dict[str, str]], *, model: str | None = None) -> LLMResponse:
    """Send a simple completion request to Gemini."""
    if not config.GEMINI_API_KEY:
        return LLMResponse(ok=False, provider="gemini", error="GEMINI_API_KEY is unset")

    selected_model = model or config.GEMINI_MODEL
    payload = {
        "contents": [_message_to_part(msg) for msg in messages if msg.get("content")],
        "generationConfig": {"temperature": 0.4},
    }

    try:
        response = requests.post(
            GEMINI_ENDPOINT.format(model=selected_model),
            params={"key": config.GEMINI_API_KEY},
            json=payload,
            timeout=config.LLM_REQUEST_TIMEOUT,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        logger.warning("Gemini request failed: %s", exc)
        return LLMResponse(
            ok=False,
            provider="gemini",
            model=selected_model,
            error=f"request failed: {exc}",
        )

    data = response.json()
    try:
        text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception:  # noqa: BLE001
        return LLMResponse(
            ok=False,
            provider="gemini",
            model=selected_model,
            error="missing text in Gemini response",
        )

    if not text:
        return LLMResponse(
            ok=False,
            provider="gemini",
            model=selected_model,
            error="empty completion text",
        )

    return LLMResponse(ok=True, text=text, provider="gemini", model=selected_model)
