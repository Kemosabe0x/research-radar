# Context setup — lean RSSAgent chats

How to reduce skills/plugin overhead while keeping **backend (RSS + LLM) and UI (Next.js + shadcn)** skills available.

> **Automated setup (recommended):** run the project skill TUI once after clone:
> ```bash
> pip install -r requirements-dev.txt
> python scripts/setup-project-skills.py --apply
> ```
> See **[project-skills-workflow.md](./project-skills-workflow.md)** for architecture and presets. Manual steps below remain as reference.

**What project files already do**

| File | Effect |
|------|--------|
| `AGENTS.md` | Tells agents what to use / ignore (behavior) |
| `.cursor/rules/project-scope.mdc` | Always-on scope guard (~small) |
| `.cursor/skills/rssagent/SKILL.md` | One local skill for this repo's full workflow |
| `.cursor/skills-profile.yaml` | Declarative list of enabled global skills |
| `scripts/setup-project-skills.py` | TUI / CLI to sync global skills to the profile |

**What they do *not* do:** remove installed plugins or global skills from the session catalog. Prune at the source below.

---

## Step 1 — Cursor plugins (Settings → Plugins)

### Disable (largest wins, no UI impact)

| Plugin | Why disable |
|--------|-------------|
| **compound-engineering** | 40+ review personas and skills; very heavy |
| **superpowers** | Forces skill invocation on every turn |
| **sagemaker-ai** | ML training, not RSS/LLM app |
| **databases-on-aws** | Aurora DSQL unless you adopt DSQL |
| **docs-canvas** | Doc visualization, not core pipeline |
| **create-plugin** | Plugin authoring |
| **cursor-sdk** | Automating Cursor agents externally |
| **agent-compatibility** | Repo compatibility audits |
| **continual-learning** | Memory hooks across sessions |
| **cli-for-agent** | CLI agent tooling |
| **figma** | Design tooling (re-enable if doing Figma-to-code) |

### Keep enabled — backend + UI (recommended profile)

| Plugin | Why keep |
|--------|----------|
| **aws-serverless** | Lambda + EventBridge deployment |
| **vercel** | Next.js deploy, env vars, hosting |
| **shadcn** | UI components for dev portal / auth UI |
| **modern-web-guidance** | HTML/CSS/frontend best practices |
| **browse** | Browser automation for UI dev testing |
| **cursor-team-kit** | `fix-ci`, `review-and-ship` (optional; disable if still too heavy) |

---

## Step 2 — Global marketing skills (`~/.agents/skills/`)

You have **~72 skills** here. Many `~/.claude/skills/` entries are **symlinks into this folder**. Do **not** move the entire directory — that breaks every Claude symlink.

**Move only skills you do not need** (marketing + non-RSSAgent dev tools):

```bash
mkdir -p ~/.agents/skills-disabled

# Skills to KEEP in ~/.agents/skills (backend + UI for RSSAgent)
KEEP='gemini-api-dev|gemini-interactions-api|vertex-ai-api-dev|ai-sdk|ai-elements|cloudflare-deploy|cloudflare-email-service|wrangler|workers-best-practices|code-reviewer|next-best-practices|shadcn|shadcn-ui|vercel-react-best-practices|frontend-design|web-design-guidelines|web-perf|webapp-testing|brainstorming|managing-python-dependencies|openai-docs|codex-security-best-practices|accidental-data-loss-prevention'

for s in ~/.agents/skills/*; do
  name="$(basename "$s")"
  if echo "$name" | grep -qE "^($KEEP)$"; then
    echo "KEEP: $name"
  else
    echo "DISABLE: $name"
    mv "$s" ~/.agents/skills-disabled/
  fi
done
```

**Verify symlinks still resolve:**

```bash
for s in ~/.claude/skills/*; do [ -e "$s" ] || echo "BROKEN: $(basename "$s")"; done
```

If you already moved the whole folder (`mv skills skills-disabled`), restore kept skills first — see **Repair** in Step 4.

---

## Step 3 — Personal Codex skills (`~/.cursor/skills/`)

You have **~100** symlinked skills. For RSSAgent **backend + UI**, **keep**:

```
# LLM & Python backend
gemini-api-dev
gemini-interactions-api
vertex-ai-api-dev
managing-python-dependencies
openai-docs
codex-security-best-practices
accidental-data-loss-prevention

# Cloud deploy
workers-best-practices
wrangler
cloudflare-deploy
codex-vercel-deploy

# Next.js + UI (dev portal / auth UI planned)
next-best-practices
shadcn
shadcn-ui
vercel-react-best-practices
ai-sdk
frontend-design
web-design-guidelines
webapp-testing
codex-playwright
ui-ux-pro-max
```

**Archive the rest** (BigQuery, Figma codex skills, WinUI, Rails, media gen, etc.):

```bash
mkdir -p ~/.cursor/skills-archive
cd ~/.cursor/skills
KEEP='gemini-api-dev|gemini-interactions-api|vertex-ai-api-dev|managing-python-dependencies|openai-docs|codex-security-best-practices|accidental-data-loss-prevention|workers-best-practices|wrangler|cloudflare-deploy|codex-vercel-deploy|next-best-practices|shadcn|shadcn-ui|vercel-react-best-practices|ai-sdk|frontend-design|web-design-guidelines|webapp-testing|codex-playwright|ui-ux-pro-max'
for s in *; do
  echo "$s" | grep -qE "^($KEEP)$" || mv "$s" ../skills-archive/ 2>/dev/null || true
done
```

---

## Step 4 — Claude skills (`~/.claude/skills/`)

Claude Code (and some Cursor integrations) load skills from `~/.claude/skills/`. On your machine these are usually **symlinks** to `~/.agents/skills/<name>`. Step 2 must leave those targets in place.

**Do not use `[ -e "$s" ] || continue`** — broken symlinks skip silently and nothing moves.

### Before you start

1. **Quit Claude Code / close agent chats** that might be using skills (optional but avoids odd paths mid-move).
2. **See what you have:**

   ```bash
   ls -la ~/.claude/skills
   ```

   Symlinks show `@` in some listings (e.g. `shadcn@` → points elsewhere). The script below moves the symlink name itself, which is fine.

3. **Dry run** — list what *would* be archived without moving:

   ```bash
   KEEP='gemini-api-dev|gemini-interactions-api|ai-sdk|ai-elements|cloudflare-deploy|wrangler|workers-best-practices|code-reviewer|next-best-practices|shadcn|shadcn-ui|vercel-react-best-practices|frontend-design|web-design-guidelines|web-perf|webapp-testing|vertex-ai-api-dev|brainstorming|managing-python-dependencies|openai-docs'
   for s in ~/.claude/skills/*; do
     name="$(basename "$s")"
     echo "$name" | grep -qE "^($KEEP)$" || echo "ARCHIVE: $name"
   done
   ```

   Review the `ARCHIVE:` lines. If something you need is listed, add its folder name to `KEEP` before running the real move.

### Keep list (RSSAgent backend + UI)

| Skill folder | Why keep |
|--------------|----------|
| `gemini-api-dev` | Gemini API (if present) |
| `gemini-interactions-api` | Gemini Interactions API (if present) |
| `vertex-ai-api-dev` | Enterprise Gemini on GCP |
| `ai-sdk` | Streaming LLM in Next.js UI |
| `ai-elements` | Chat/message UI components (optional but useful for dashboard) |
| `cloudflare-deploy`, `wrangler`, `workers-best-practices` | Cloudflare deploy |
| `code-reviewer` | Pre-PR review |
| `next-best-practices` | Next.js App Router |
| `shadcn`, `shadcn-ui` | Component library |
| `vercel-react-best-practices` | React performance |
| `frontend-design`, `web-design-guidelines`, `web-perf` | UI layout, a11y, performance |
| `webapp-testing` | Playwright-style UI testing |
| `brainstorming` | Scope UI/features before building |
| `managing-python-dependencies`, `openai-docs` | Backend (if present) |

### Typical archive targets

Move these **out** of `~/.claude/skills/` unless you actively use them:

| Pattern / folder | Why archive |
|------------------|-------------|
| `stitch-design`, `stitch-loop`, `design-md`, `enhance-prompt`, `react-components` | Stitch design tooling |
| `canvas-design`, `web-artifacts-builder` | Standalone HTML artifacts, not this repo |
| `grill-me` | Interview/planning persona |
| `agents-sdk`, `durable-objects` | Cloudflare Agents app pattern (not RSSAgent core) |
| `cloudflare-email-service` | Only if you are not sending email from Workers |
| `supabase-postgres-best-practices` | Only if not using Supabase |
| `skill-creator` | Meta — re-enable when authoring skills |

### Run the archive (copy-paste)

Because entries are symlinks, **remove unwanted links** (move link into archive). Do not delete `~/.agents/skills/` targets here — Step 2 already disabled those.

```bash
mkdir -p ~/.claude/skills-archive

KEEP='gemini-api-dev|gemini-interactions-api|vertex-ai-api-dev|ai-sdk|ai-elements|cloudflare-deploy|wrangler|workers-best-practices|code-reviewer|next-best-practices|shadcn|shadcn-ui|vercel-react-best-practices|frontend-design|web-design-guidelines|web-perf|webapp-testing|brainstorming|managing-python-dependencies|openai-docs'

for s in ~/.claude/skills/*; do
  name="$(basename "$s")"
  if echo "$name" | grep -qE "^($KEEP)$"; then
    echo "KEEP: $name"
  else
    echo "REMOVE LINK: $name"
    mv "$s" ~/.claude/skills-archive/
  fi
done
```

Use the full path `~/.claude/skills/*` so the loop runs even if your cwd is wrong.

### Repair (if Step 2 moved the whole `~/.agents/skills/` folder)

Symptoms: archive loop prints nothing; `~/.claude/skills-archive` empty; all 29 symlinks still present.

```bash
# 1. Restore kept skill folders from skills-disabled
KEEP='gemini-api-dev|gemini-interactions-api|vertex-ai-api-dev|ai-sdk|ai-elements|cloudflare-deploy|wrangler|workers-best-practices|code-reviewer|next-best-practices|shadcn|shadcn-ui|vercel-react-best-practices|frontend-design|web-design-guidelines|web-perf|webapp-testing|brainstorming|managing-python-dependencies|openai-docs|codex-security-best-practices|accidental-data-loss-prevention|cloudflare-email-service'
mkdir -p ~/.agents/skills
for s in ~/.agents/skills-disabled/*; do
  name="$(basename "$s")"
  echo "$name" | grep -qE "^($KEEP)$" && mv "$s" ~/.agents/skills/ && echo "RESTORED: $name"
done

# 2. Remove unwanted Claude symlinks (script above)
```

Then verify — **no output** means success:

```bash
for s in ~/.claude/skills/*; do [ -e "$s" ] || echo "BROKEN: $(basename "$s")"; done
```

### Verify

```bash
echo "=== Remaining ($(ls -1 ~/.claude/skills | wc -l | tr -d ' ') skills) ==="
ls -1 ~/.claude/skills

echo "=== Archived ($(ls -1 ~/.claude/skills-archive 2>/dev/null | wc -l | tr -d ' ') skills) ==="
ls -1 ~/.claude/skills-archive
```

You should see roughly **15–20 folders** left in `~/.claude/skills` and the rest in `skills-archive`.

### Restore one skill later

```bash
mv ~/.claude/skills-archive/stitch-design ~/.claude/skills/
```

### Restore everything

```bash
mv ~/.claude/skills-archive/* ~/.claude/skills/
rmdir ~/.claude/skills-archive 2>/dev/null || true
```

### If a skill lives only in `~/.cursor/skills/`

Claude and Cursor maintain **separate** skill directories. Archiving `~/.claude/skills` does not change `~/.cursor/skills`. For RSSAgent, run **both** Step 3 and Step 4, or Cursor may still see skills Claude no longer does (and vice versa).

### Troubleshooting

| Issue | Fix |
|-------|-----|
| `mv: Permission denied` | Don't use `sudo`. Fix ownership: `ls -la ~/.claude/skills` |
| Skill still appears in chat | Start a **new chat**; catalog is loaded at session start |
| Archive loop prints nothing, archive empty | Step 2 broke symlinks — run **Repair** above |
| `BROKEN:` names after verify | Restore that skill folder from `skills-disabled` to `~/.agents/skills/` |
| Broke symlink after move | `mv` link back from archive; restore target under `~/.agents/skills/` |


## Step 5 — MCP servers (Cursor Settings → MCP)

Disable MCP servers you won't use for this repo:

| MCP | RSSAgent need |
|-----|----------------|
| **plugin-shadcn-shadcn** | **Keep** — component install/docs |
| **plugin-vercel-vercel** | **Keep** — Next.js deploy |
| **plugin-browse-browser** | **Keep** — UI dev testing |
| **plugin-aws-serverless-aws-serverless-mcp** | **Keep** — Lambda/backend |
| **user-github-mcp-server** | **Keep** — PR/issue work |
| **user-google-developer-knowledge** | Optional — Gemini docs |
| **plugin-figma-figma** | Disable unless Figma-to-code |
| **plugin-databases-on-aws-aurora-dsql** | Disable |
| **user-colab** | Disable |

---

## Step 6 — Start a new chat

1. Open the **RSSAgent** workspace (so `project-scope.mdc` applies).
2. **New chat** — clears long history.
3. First message example:

   > Continue RSSAgent development. Follow `.cursor/skills/rssagent/SKILL.md` and `AGENTS.md`. Next: [your task].

Agents should load **rssagent** skill once instead of scanning dozens of global skills.

---

## Profiles

| Profile | Plugins | Global skills | Best for |
|---------|---------|---------------|----------|
| **Backend + UI** (recommended) | aws-serverless, vercel, shadcn, modern-web-guidance, browse | ~20 kept skills (see Step 3) | RSS/LLM + Next.js dev portal |
| **Backend only** | aws-serverless, vercel | ~10 LLM/cloud skills | Pipeline work, no UI touches |
| **Full** | Re-enable compound-engineering | Restore archives | Large refactors, formal review |

---

## Restore later

Everything is reversible:

```bash
mv ~/.agents/skills-disabled ~/.agents/skills
mv ~/.cursor/skills-archive/* ~/.cursor/skills/
# Re-enable plugins in Cursor Settings → Plugins
```

---

## Expected savings

| Source | Approx. skills removed |
|--------|------------------------|
| Marketing `~/.agents/skills` | ~72 |
| Codex skill archive | ~75–80 (UI skills kept) |
| Plugins (compound + sagemaker + figma + …) | ~60–100 catalog entries |
| MCP servers | Variable tool schema overhead |

Project-local **rssagent** skill adds one focused entry instead of relying on the global catalog.
