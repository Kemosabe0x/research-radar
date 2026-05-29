---
name: rssagent
description: RSSAgent ingestion, multi-provider LLM pipeline, and Next.js UI for sports-science journal monitoring, alerts, and conditional article generation. Use when working on RSS feeds, feedparser, SQLite dedupe, journal CSV, webhooks, Gemini or Bedrock LLM routing, synthesis, digests, shadcn dashboard, or deployment of this repo.
---

# RSSAgent

Single source of truth for implementation in this repo. Read `AGENTS.md` for contributor rules. Do not load marketing, Figma, or unrelated skills.

## Pipeline

```
Journals - Journal List.csv
  → poll RSS (feedparser) or fallback scraper (BeautifulSoup)
  → SQLite seen_articles (dedupe by article_link)
  → Alert path: every new item → fast customized message
  → Generate path: conditional → synthesize → write markdown
  → Web UI: Next.js + shadcn (dev dashboard / auth portal TBD)
```

**Never block alerts on LLM calls.** Generation is async or scheduled.

## Codebase

| File | Notes |
|------|--------|
| `deepseek.py` | Best reference monitor (logging, webhook, fallback) |
| `gemini.py` | Legacy duplicate — consolidate, do not extend |
| `Journals - Journal List.csv` | Master list (scripts wrongly say `Master Journal List`) |

Fix CSV filename mismatch when touching ingestion.

## LLM router (target layout)

```
src/
  ingest/       # RSS loop, scraper, db
  llm/
    router.py   # task → provider + model
    providers/
      gemini.py
      bedrock.py
  output/       # alert + markdown writers
web/            # Next.js + shadcn UI (TBD)
content/
  articles/
  digests/
```

UI reads from an API layer — keep RSS polling in Python, not in the frontend.

### Tasks → models

| Task | Latency | Provider default |
|------|---------|------------------|
| `alert` | Low | Gemini (fast/cheap) |
| `synthesize` | Medium | Gemini or Bedrock Claude |
| `generate` | High | Best writing model available |

Router interface:

```python
def complete(task: str, messages: list[dict], **kwargs) -> str:
    """Resolve provider from env; fail gracefully if secondary unset."""
```

### Env vars (document in `.env.example`, never commit values)

```
GEMINI_API_KEY=
AWS_REGION=
AWS_ACCESS_KEY_ID=          # or use IAM role on Lambda
AWS_SECRET_ACCESS_KEY=
BEDROCK_MODEL_ID=             # e.g. anthropic.claude-3-5-sonnet-...
NOTIFICATION_WEBHOOK_URL=
LLM_PROVIDER_ALERT=gemini
LLM_PROVIDER_SYNTHESIZE=gemini
LLM_PROVIDER_GENERATE=bedrock
```

## Outputs

**Alert** — webhook or stdout: journal, title, link, 1–2 sentence context.

**Per-article markdown** — `content/articles/{slug}.md`:

```yaml
---
title:
sources: [{journal, url, published}]
provider:
model:
generated_at:
---
```

**Digest markdown** — `content/digests/{period}.md` (same frontmatter pattern).

Generation thresholds are TBD (volume caps, priority journals, spend limits). Stub with config file; do not hardcode until decided.

## Ingestion rules

- `time.sleep(2)` (or `REQUEST_DELAY`) between journal requests
- Log with `logging`, not bare `print` in production paths
- Handle `feed.bozo` warnings; skip entries without links
- Public repo: no paywalled full text in git; links + metadata only

## Implementation order

1. Align CSV filename; consolidate `deepseek.py` / `gemini.py`
2. Add `.env.example`, `requirements.txt`, package layout
3. Router skeleton — Gemini live, Bedrock stub with graceful skip
4. Alert path wired to router (`task="alert"`)
5. Conditional generation hook + markdown writers
6. Next.js dev UI (feed list, alerts, generated articles)
7. Deploy: backend (VPS | Lambda | Workers) + UI (Vercel)

## External skills (only when needed)

Load these **instead of** guessing API details — do not load marketing or design skills.

| Need | Skill |
|------|--------|
| Gemini API | `gemini-interactions-api` or `gemini-api-dev` |
| Vertex Gemini | `vertex-ai-api-dev` |
| OpenAI fallback | `openai-docs` |
| Python deps | `managing-python-dependencies` |
| Lambda deploy | `aws-lambda`, `aws-serverless-deployment` |
| Workers deploy | `wrangler`, `workers-best-practices`, `cloudflare-deploy` |
| Vercel / Next.js | `next-best-practices`, `codex-vercel-deploy` |
| shadcn components | `shadcn`, `shadcn-ui` |
| React perf | `vercel-react-best-practices` |
| UI testing | `webapp-testing`, `codex-playwright` |
| Security review | `codex-security-best-practices` |

## Verification

- [ ] Subset CSV poll completes without crash
- [ ] Duplicate links not re-alerted
- [ ] Alert fires without waiting on generation
- [ ] Router works with Gemini; Bedrock skips cleanly if unset
- [ ] No secrets in diff
