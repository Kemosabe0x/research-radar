from rssagent.generation import should_generate_for_article


def test_should_generate_for_priority_journal(monkeypatch) -> None:
    monkeypatch.setattr("rssagent.config.PRIORITY_GENERATION_JOURNALS", ("Priority Journal",))

    result = should_generate_for_article("Priority Journal")
    assert result.should_generate
    assert "priority" in result.reason


def test_should_not_generate_when_daily_cap_reached(monkeypatch) -> None:
    monkeypatch.setattr("rssagent.config.PRIORITY_GENERATION_JOURNALS", tuple())
    monkeypatch.setattr("rssagent.generation.count_generated_today", lambda: 3)
    monkeypatch.setattr("rssagent.config.GENERATE_DAILY_CAP", 3)

    result = should_generate_for_article("Other Journal")
    assert not result.should_generate
    assert "cap" in result.reason


def test_should_generate_when_threshold_met(monkeypatch) -> None:
    monkeypatch.setattr("rssagent.config.PRIORITY_GENERATION_JOURNALS", tuple())
    monkeypatch.setattr("rssagent.generation.count_generated_today", lambda: 0)
    monkeypatch.setattr("rssagent.generation.count_recent_articles", lambda hours: 7)
    monkeypatch.setattr("rssagent.config.GENERATE_MIN_NEW_ARTICLES", 5)
    monkeypatch.setattr("rssagent.config.GENERATE_WINDOW_HOURS", 24)
    monkeypatch.setattr("rssagent.config.GENERATE_DAILY_CAP", 3)

    result = should_generate_for_article("Other Journal")
    assert result.should_generate
    assert "threshold" in result.reason
