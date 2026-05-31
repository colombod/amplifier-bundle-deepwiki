# amplifier-bundle-deepwiki

DeepWiki integration bundle: an MCP-backed context-sink expert agent plus a
pattern-detection trigger hook that nudges the model toward DeepWiki research.

## Architecture (at a glance)

- `bundle.md` — thin root bundle; includes foundation + the deepwiki behavior.
- `behaviors/deepwiki.yaml` — the reusable behavior: MCP server config (`tool-mcp`),
  the trigger hook, the expert agent, and a single thin awareness context file.
  Its `bundle.name` is `deepwiki-research` (intentionally distinct from the root
  bundle name `deepwiki` — do NOT rename it to `deepwiki`; a behavior name that
  collides with the root name causes self-referential registry entries, which the
  `validate-bundle-repo` recipe flags).
- `agents/deepwiki-expert.md` — context-sink expert. Heavy knowledge (usage,
  freshness-check, staleness-fallbacks) is @-mentioned in the agent BODY only, so it
  loads in the agent sub-session, never the root session.
- `context/` — `deepwiki-awareness.md` is the only file injected into root sessions
  (kept under ~500 tokens). The rest are agent-only deep context.
- `modules/hooks-deepwiki-trigger/` — the trigger hook Python module.

## Agent Tool Scope

The expert agent has only `tool-mcp` (DeepWiki), `tool-web` (`web_fetch` +
`web_search`), and `tool-bash`. Do NOT reference tools it lacks (e.g.
`perplexity_research`) as required steps in agent-loaded context.

## Test Commands

```bash
cd modules/hooks-deepwiki-trigger
uv run pytest -q          # 155 tests; all must pass before shipping
```

## Validation Gate

```bash
amplifier tool invoke recipes operation=execute \
  recipe_path=foundation:recipes/validate-bundle-repo.yaml \
  context='{"repo_path": "<abs path to this repo>", "validate_all": "true"}'
```

Target: PASS (0 errors). The two agent-file warnings about "missing bundle.name /
description" are validator detection mismatches on `meta:`-keyed agent files, not
real defects — agent identity lives under `meta.description`, not `bundle.*`.

## Authoring Conventions

- Root-injected context: only `context/deepwiki-awareness.md` (thin, ≤ ~500 tokens).
- `context/proactive-triggers.md` does NOT exist (deleted in v1.4.0) — do not recreate
  or re-reference it.
- Regenerate the architecture diagram after structural changes:
  `dot -Tsvg context/architecture.dot -o context/architecture.svg`
- Keep README installation guidance in sync: `--app` layering (recommended),
  `bundle use` (primary), and `includes:` composition (bundle authors).

## DTU Testing

Reusable Digital Twin Universe profiles for end-to-end testing live in
`.amplifier/dtu/` in this repo. See `.amplifier/dtu/README.md`.
