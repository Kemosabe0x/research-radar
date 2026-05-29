from rssagent.urls import is_valid_http_url, normalize_http_url


def test_normalize_adds_https() -> None:
    assert normalize_http_url("example.com/feed") == "https://example.com/feed"


def test_normalize_keeps_https() -> None:
    url = "https://journals.example.com/rss"
    assert normalize_http_url(url) == url


def test_normalize_empty() -> None:
    assert normalize_http_url("") == ""
    assert normalize_http_url(None) == ""
    assert normalize_http_url("nan") == ""


def test_is_valid_http_url() -> None:
    assert is_valid_http_url("https://example.com/feed")
    assert not is_valid_http_url("not a url")
    assert not is_valid_http_url("ftp://example.com/feed")
