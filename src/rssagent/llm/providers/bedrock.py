"""Bedrock provider integration with graceful fallback."""

from __future__ import annotations

import json
import logging
from typing import Sequence

from rssagent import config
from rssagent.llm.types import LLMResponse

logger = logging.getLogger(__name__)


def complete(messages: Sequence[dict[str, str]], *, model: str | None = None) -> LLMResponse:
    """Send a completion request to Bedrock when boto3 + model are available."""
    selected_model = model or config.BEDROCK_MODEL_ID
    if not selected_model:
        return LLMResponse(
            ok=False,
            provider="bedrock",
            error="BEDROCK_MODEL_ID is unset",
        )

    try:
        import boto3  # type: ignore
    except Exception as exc:  # noqa: BLE001
        return LLMResponse(
            ok=False,
            provider="bedrock",
            model=selected_model,
            error=f"boto3 unavailable: {exc}",
        )

    prompt = "\n".join(
        f"{msg.get('role', 'user').upper()}: {msg.get('content', '')}" for msg in messages
    )
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 512,
        "temperature": 0.4,
        "messages": [{"role": "user", "content": prompt}],
    }

    try:
        client = boto3.client("bedrock-runtime", region_name=config.AWS_REGION)
        response = client.invoke_model(
            modelId=selected_model,
            body=json.dumps(body),
            contentType="application/json",
            accept="application/json",
        )
        payload = json.loads(response["body"].read())
    except Exception as exc:  # noqa: BLE001
        logger.warning("Bedrock request failed: %s", exc)
        return LLMResponse(
            ok=False,
            provider="bedrock",
            model=selected_model,
            error=f"request failed: {exc}",
        )

    try:
        text = payload["content"][0]["text"].strip()
    except Exception:  # noqa: BLE001
        return LLMResponse(
            ok=False,
            provider="bedrock",
            model=selected_model,
            error="missing text in Bedrock response",
        )

    if not text:
        return LLMResponse(
            ok=False,
            provider="bedrock",
            model=selected_model,
            error="empty completion text",
        )
    return LLMResponse(ok=True, text=text, provider="bedrock", model=selected_model)
