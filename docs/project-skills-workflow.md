# Project-level skills workflow

Cursor does **not** (today) offer a native “enable only these skills for this workspace” toggle. The session still receives metadata for globally installed skills and plugins. To reduce context, use a **layered approach**:

```
┌─────────────────────────────────────────────────────────┐
│ 1. Project skill (.cursor/skills/rssagent/)  ← git     │  Always-on workflow doc
│ 2. skills-profile.yaml                       ← git     │  Declarative enabled list
│ 3. cursor-project-skills (external CLI)    ← install │  Syncs your machine
│ 4. AGENTS.md + project-scope.mdc             ← git     │  Agent behavior
│ 5. Disable heavy Cursor plugins              ← manual  │  Biggest catalog wins
└─────────────────────────────────────────────────────────┘
```

## Tool: [Cursor-Project-Skills](https://github.com/YOUR_USER/Cursor-Project-Skills)

Standalone package: **`cursor-project-skills`**. This repo keeps RSSAgent-specific presets in `.cursor/skills-profile.yaml` only.

```bash
pip install -e /path/to/Cursor-Project-Skills   # or from GitHub after publish

cd /path/to/RSSAgent
cursor-project-skills dry-run --preset backend-ui
cursor-project-skills apply --preset backend-ui

# Interactive TUI
cursor-project-skills apply

# Legacy wrapper (same CLI if package installed)
python scripts/setup-project-skills.py
```

Then **open a new Cursor chat** in this workspace.

Upstream docs: [Cursor-Project-Skills/docs/workflow.md](https://github.com/YOUR_USER/Cursor-Project-Skills/blob/main/docs/workflow.md)

## What the CLI does

| Location | Enabled skill | Disabled skill |
|----------|---------------|----------------|
| `~/.agents/skills/` | stays | → `~/.agents/skills-disabled/` |
| `~/.cursor/skills/` | stays | → `~/.cursor/skills-archive/` |
| `~/.claude/skills/` | symlink kept/created | → `~/.claude/skills-archive/` |

**Never touched:** `.cursor/skills/*` inside the repo (e.g. `rssagent`).

**Updates:** `.cursor/skills-profile.yaml` → `enabled:` list on `apply`.

## Presets (RSSAgent)

| Preset | Use when |
|--------|----------|
| `backend-ui` | RSS + LLM + Next.js/shadcn (default) |
| `backend-only` | Python pipeline only, no UI |

Edit `.cursor/skills-profile.yaml` to change presets.

## Best practices

### Do (project-level)

- **One project skill** with architecture + conventions (`.cursor/skills/rssagent/`)
- **Commit** `skills-profile.yaml` so teammates share the same intended set
- **Run setup after clone** — skill paths are per-machine
- **Use `disable-model-invocation: true`** on optional project skills so they load only when named

### Do (global)

- Disable heavy **plugins** (compound-engineering, superpowers, sagemaker) in Cursor Settings
- Keep marketing skills in `skills-disabled`, not `~/.agents/skills/`

### Don’t

- Don’t `mv ~/.agents/skills ~/.agents/skills-disabled` wholesale — breaks Claude symlinks
- Don’t rely on AGENTS.md alone to shrink the skills catalog
- Don’t expect changes mid-chat — start a **new chat**

## Restore

```bash
cursor-project-skills restore-all
```

## New project template

1. Install `cursor-project-skills`.
2. `cursor-project-skills init` in the repo.
3. Add `.cursor/skills/<project>/SKILL.md`, `AGENTS.md`, rules as needed.

Example presets: [Cursor-Project-Skills/profiles/examples](https://github.com/YOUR_USER/Cursor-Project-Skills/tree/main/profiles/examples).

## Limitations

- **Plugin skills** are not managed by the CLI — disable plugins manually.
- **Cursor built-in skills** (`~/.cursor/skills-cursor/`) cannot be archived.
- Tool is **local-only**; it does not modify Cursor settings JSON.

For manual plugin steps, see [context-setup.md](./context-setup.md).
