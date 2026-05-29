"""Types shared by LLM providers and router."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LLMResponse:
    """Normalized model completion result."""

    ok: bool
    text: str = ""
    provider: str = ""
    model: str = ""
    error: str = ""
