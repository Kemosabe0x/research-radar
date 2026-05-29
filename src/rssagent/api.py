"""Lightweight read API for articles, digestion status, and generated content."""

from __future__ import annotations

import argparse
import json
import logging
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from rssagent import config
from rssagent.db import get_article_by_link, get_recent_articles, setup_database
from rssagent.generation import enqueue_article_processing

logger = logging.getLogger(__name__)


def _parse_frontmatter(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    if not text.startswith("---\n"):
        return {"path": str(path.relative_to(config.REPO_ROOT)), "title": path.stem}

    _, _, rest = text.partition("---\n")
    fm_text, _, body = rest.partition("\n---\n")
    data: dict[str, object] = {}
    for line in fm_text.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip()
    data["path"] = str(path.relative_to(config.REPO_ROOT))
    data["preview"] = body.strip()[:280]
    return data


def _list_markdown(directory: Path) -> list[dict[str, object]]:
    if not directory.exists():
        return []
    docs = sorted(directory.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
    return [_parse_frontmatter(path) for path in docs]


class ApiHandler(BaseHTTPRequestHandler):
    server_version = "RSSAgentAPI/0.1"

    def _send_json(self, payload: object, status: HTTPStatus = HTTPStatus.OK) -> None:
        encoded = json.dumps(payload, ensure_ascii=True).encode("utf-8")
        self.send_response(status.value)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.end_headers()
        self.wfile.write(encoded)

    def do_OPTIONS(self) -> None:  # noqa: N802
        self._send_json({"ok": True})

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        if path == "/health":
            self._send_json({"ok": True})
            return

        if path == "/api/articles":
            limit = int(query.get("limit", ["50"])[0])
            self._send_json({"items": get_recent_articles(limit=limit)})
            return

        if path == "/api/generated/articles":
            self._send_json({"items": _list_markdown(config.ARTICLES_DIR)})
            return

        if path == "/api/generated/digests":
            self._send_json({"items": _list_markdown(config.DIGESTS_DIR)})
            return

        self._send_json({"error": "not found"}, status=HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path != "/api/articles/digest":
            self._send_json({"error": "not found"}, status=HTTPStatus.NOT_FOUND)
            return

        length = int(self.headers.get("Content-Length", "0"))
        payload = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
        link = str(payload.get("article_link", "")).strip()
        if not link:
            self._send_json(
                {"error": "article_link is required"},
                status=HTTPStatus.BAD_REQUEST,
            )
            return

        article = get_article_by_link(link)
        if not article:
            self._send_json({"error": "article not found"}, status=HTTPStatus.NOT_FOUND)
            return

        enqueue_article_processing(
            journal_name=article["journal_name"],
            title=article["article_title"],
            link=article["article_link"],
            published_date=article.get("published_date", "") or "",
        )
        self._send_json({"ok": True, "status": "queued"})


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="RSSAgent read API")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8787)
    return parser.parse_args()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    setup_database()
    args = _parse_args()
    server = ThreadingHTTPServer((args.host, args.port), ApiHandler)
    logger.info("RSSAgent API listening on http://%s:%s", args.host, args.port)
    server.serve_forever()

