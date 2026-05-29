"""Task-aware LLM router with graceful provider fallback."""

from __future__ import annotations

from collections.abc import Sequence

from rssagent import config
from rssagent.llm.providers import bedrock, gemini
from rssagent.llm.types import LLMResponse

TASK_PROVIDER_ENV = {
    "alert": config.LLM_PROVIDER_ALERT,
    "synthesize": config.LLM_PROVIDER_SYNTHESIZE,
    "generate": config.LLM_PROVIDER_GENERATE,
}


def _providers_for_task(task: str) -> list[str]:
    preferred = TASK_PROVIDER_ENV.get(task, "gemini").strip().lower()
    fallback = "bedrock" if preferred == "gemini" else "gemini"
    return [preferred, fallback]


def _call_provider(provider: str, messages: Sequence[dict[str, str]]) -> LLMResponse:
    if provider == "gemini":
        return gemini.complete(messages)
    if provider == "bedrock":
        return bedrock.complete(messages)
    return LLMResponse(ok=False, provider=provider, error=f"unknown provider: {provider}")


def complete(task: str, messages: Sequence[dict[str, str]]) -> LLMResponse:
    """Resolve provider by task and fall back when the first choice fails."""
    last_error = "no provider attempted"
    for provider in _providers_for_task(task):
        result = _call_provider(provider, messages)
        if result.ok:
            return result
        last_error = result.error or "unknown provider error"

    return LLMResponse(ok=False, provider="", error=last_error)
