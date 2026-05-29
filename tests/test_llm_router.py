from rssagent.llm import router
from rssagent.llm.types import LLMResponse


def test_router_uses_fallback_provider_when_primary_fails(monkeypatch) -> None:
    monkeypatch.setattr(router, "TASK_PROVIDER_ENV", {"alert": "gemini"})

    def fake_call(provider: str, messages: list[dict[str, str]]) -> LLMResponse:
        if provider == "gemini":
            return LLMResponse(ok=False, provider="gemini", error="gemini unavailable")
        return LLMResponse(ok=True, provider="bedrock", model="stub", text="fallback ok")

    monkeypatch.setattr(router, "_call_provider", fake_call)

    result = router.complete("alert", [{"role": "user", "content": "hello"}])
    assert result.ok
    assert result.provider == "bedrock"
    assert result.text == "fallback ok"


def test_router_returns_error_when_all_providers_fail(monkeypatch) -> None:
    monkeypatch.setattr(router, "TASK_PROVIDER_ENV", {"alert": "gemini"})
    monkeypatch.setattr(
        router,
        "_call_provider",
        lambda provider, messages: LLMResponse(
            ok=False, provider=provider, error=f"{provider} down"
        ),
    )

    result = router.complete("alert", [{"role": "user", "content": "hello"}])
    assert not result.ok
    assert "down" in result.error
