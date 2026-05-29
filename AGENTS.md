# AGENTS.md — RSSAgent

Guidance for AI agents and human contributors working on this public repository.

## Project Summary

**RSSAgent** monitors 150+ sports-science journals and industry blogs via RSS (with optional HTML fallback scraping), deduplicates articles in SQLite, and notifies users when new research appears.

The next layer adds a **multi-provider LLM pipeline** that interprets feed data and generates written content — without replacing the real-time alert path.

A **web UI** is planned (auth portal or dev testing dashboard) for browsing feeds, alerts, and generated articles — likely **Next.js + shadcn/ui**, deployed via Vercel or similar.

## Architecture (Target)

```
CSV journal list
    → RSS / fallback scraper
    → SQLite (seen articles)
    → Alert path (every new item → customized notification)
    → Generation path (conditional — rules TBD)
           → Provider router (Gemini primary; AWS Bedrock/Claude optional)
           → Synthesis model (summarize, cluster, rank)
           → Generation model (articles, digests)
           → Output (markdown files, optional webhook payload)
```

### Two paths, one ingestion pipeline

| Path | Trigger | Purpose |
|------|---------|---------|
| **Alert** | Every unseen article | Fast, customized user notification (title, journal, link, short context) |
| **Generate** | Conditional (TBD) | Deeper synthesis and long-form content when volume/quality thresholds are met |

Do not block alerts on LLM latency or cost. Generation runs asynchronously or on a separate schedule.

### Output formats (both supported)

1. **Per-article markdown** — one file per generated piece under something like `content/articles/`
2. **Digest markdown** — periodic rollups (e.g. weekly) under `content/digests/`

Use frontmatter (title, source URLs, journal, published date, model, provider) so outputs are traceable in a public repo.

### Multi-provider LLM design

- **Primary:** Google Gemini (`google-genai` / Interactions API) — default for alerts, synthesis, and generation.
- **Secondary:** AWS Bedrock (e.g. Claude) when AWS credits or model choice favors it.
- **Principle:** Separate **synthesis** (compress, classify, dedupe themes) from **generation** (prose, digests). Each stage may use a different model/provider via a thin router — no provider logic scattered across the codebase.

```python
# Target pattern (illustrative)
router.complete(task="alert", ...)      # fast, cheap model
router.complete(task="synthesize", ...) # reasoning-oriented model
router.complete(task="generate", ...)   # writing-oriented model
```

Configuration via environment variables only — never commit keys. See `.env.example` (to be added with LLM work).

### Deployment options (in scope)

- **Local / VPS cron** — current `schedule`-based runner
- **AWS Lambda + EventBridge** — serverless polling
- **Cloudflare Workers + Cron Triggers** — edge scheduling, optional Workers AI

Pick one hosting path per deployment; keep provider code host-agnostic.

### Web UI (planned)

- **Stack:** Next.js App Router, shadcn/ui, TypeScript — follow `next-best-practices` and `vercel-react-best-practices`.
- **Purpose:** Dev testing dashboard first; optional auth-gated portal later (Clerk/Auth0/etc. TBD).
- **Data:** UI reads from API layer over SQLite/generated content — do not embed Python RSS loop in the frontend.
- **Location (TBD):** e.g. `apps/web/` or `web/` in a monorepo layout.

## Repository Layout

| Path | Role |
|------|------|
| `Journals - Journal List.csv` | Master journal database |
| `deepseek.py` | Reference RSS monitor (logging, webhook, fallback scraper) |
| `gemini.py` | Legacy duplicate — consolidate into main module over time |
| `journal_tracker.db` | Local SQLite (gitignored) |
| `content/` | Generated markdown (structure TBD) |
| `web/` or `apps/web/` | Next.js UI (TBD) |

**Known fix:** Scripts reference `Journals - Master Journal List.csv` but the file is `Journals - Journal List.csv`. Align names when touching ingestion code.

## Public Repository Rules

- No API keys, webhook URLs, or `.env` in git.
- Gitignore: `*.db`, `.env`, `__pycache__/`, `.venv/`, local drafts if desired.
- Prefer `os.environ.get(...)` with documented vars in `.env.example`.
- Respect publisher terms: store links and metadata; do not commit full paywalled text unless licensing allows.
- Rate-limit requests (`time.sleep` between feeds); handle 403/429 gracefully.

## Project skill (prefer this)

Load **`.cursor/skills/rssagent/SKILL.md`** for ingestion, LLM router, alerts, and generation work in this repo. It replaces scanning many global skills.

For plugin/skill pruning to reduce chat context, see **`docs/project-skills-workflow.md`** (automated) and **`docs/context-setup.md`** (manual plugins).

## Agent Skills — Use These

Focus agent skills on this stack. Ignore unrelated domains unless the user explicitly expands scope.

### Core (always relevant)

| Skill | Use for |
|-------|---------|
| `gemini-api-dev`, `gemini-interactions-api` | Gemini integration |
| `vertex-ai-api-dev` | Enterprise Gemini on GCP |
| `openai-docs`, `codex-openai-docs` | Optional OpenAI provider |
| `managing-python-dependencies` | Python deps and venv |
| `ce-debug`, `systematic-debugging` | RSS, scraping, LLM failures |
| `verification-before-completion` | Run checks before claiming done |
| `codex-security-best-practices` | Secrets, input handling, public repo safety |
| `accidental-data-loss-prevention` | SQLite and destructive ops |
| `ce-plan`, `ce-work`, `writing-plans` | Multi-step features |
| `ce-compound` | Document solutions under `docs/solutions/` |
| `ce-code-review`, `ce-commit` | PRs and commits when asked |

### Cloud & deployment (keep enabled)

| Skill | Use for |
|-------|---------|
| `aws-lambda`, `aws-serverless-deployment` | Lambda cron, packaging |
| `api-gateway` | HTTP triggers if needed |
| `workers-best-practices`, `wrangler`, `cloudflare-deploy` | Workers cron, edge deploy |
| `codex-vercel-deploy` | Vercel deploy for UI/API |

### Web UI (keep enabled)

| Skill | Use for |
|-------|---------|
| `next-best-practices` | Next.js App Router, RSC, routing |
| `shadcn`, `shadcn-ui` | Component library |
| `vercel-react-best-practices` | React performance patterns |
| `ai-sdk` | Streaming LLM output in UI if needed |
| `frontend-design`, `web-design-guidelines` | Dashboard layout and a11y |
| `webapp-testing`, `codex-playwright` | UI dev testing and E2E |
| `modern-web-guidance` | CSS/layout/modern web APIs (plugin) |

### Other optional

| Skill | Use for |
|-------|---------|
| `notebook-guidance`, `ml-best-practices` | Feed analysis experiments |
| `copywriting` | Article voice and digest tone |
| `loop` | Dev-time monitored polling |

## Agent Skills — Ignore Unless Asked

Do **not** load or suggest skills from these domains for routine RSSAgent work:

- Marketing & growth (SEO, ads, email sequences, CRO, launch, etc.)
- Figma / Stitch / design-to-code
- BigQuery, Dataform, dbt, GCP data pipelines
- SageMaker training / HyperPod
- WinUI, Rails, ASP.NET, Chrome extensions
- Sora, speech, image generation, video marketing
- Notion, Linear, Slack research, Riffrec
- MCP/plugin authoring (unless building an MCP server for RSSAgent)
- Cursor meta (statusline, skill-installer, session reports)

## Coding Conventions

- Python 3.10+; type hints on new public functions.
- Logging over bare `print` in production paths (`deepseek.py` pattern).
- Small, focused diffs; match existing style in the file you edit.
- Provider clients live behind a single router module — no inline API calls in RSS loop code.
- Tests for provider router and dedupe logic when added; mock external APIs.

## Conditional Generation (TBD)

Generation rules are not finalized. When implementing, prefer configurable thresholds, for example:

- Minimum new articles in a topic window before a digest
- Priority journals always eligible for per-article generation
- Daily cap on LLM spend
- User opt-in flags in config

Document chosen rules in `docs/solutions/` via `ce-compound` once decided.

## Verification Checklist

Before marking LLM or ingestion work complete:

1. RSS cycle runs against a small CSV subset without errors.
2. Duplicate articles are not re-alerted.
3. Alerts fire without waiting on generation.
4. Provider router works with at least Gemini; AWS path fails gracefully if unset.
5. No secrets in diff; `.env.example` updated if new vars added.
