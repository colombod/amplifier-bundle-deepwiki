# DeepWiki Integration

For GitHub repos and library internals, prefer a **source-grounded understanding
capability** over generic web search — source-grounded analysis gives correct imports,
signatures, and architecture instead of shallow snippets. In this bundle that capability
is `deepwiki:deepwiki-expert`; delegate to it for any GitHub repo or library question.
(If other agents with deep-search or web-content capability are composed alongside this
bundle, route to whichever best fits the question.)

**Escalation order for understanding a repo:**
1. **`deepwiki:deepwiki-expert`** — source-grounded, indexed analysis (primary).
2. **Clone & inspect locally** — if DeepWiki is unindexed, stale, or insufficient,
   read the actual source (a shallow `git clone` + inspect) for ground truth, rather
   than guessing from web snippets.
3. **Web search/fetch** — reserve for questions *about* the repo (releases, changelogs,
   migration guides, issues, community usage), not for reading its code.

## Triggers (delegate immediately)

| Pattern | Example |
|---------|---------|
| GitHub URL | `github.com/owner/repo`, any format |
| "How does X work" | Library internals, architecture |
| Implementing with SDK/library | Research API BEFORE coding |
| Framework reference | React, Django, FastAPI, etc. |

## Why Not web_search

Real failure (Session 89aff774): User implementing Azure AI Inference SDK → AI guessed at API → wrong assumptions → user interrupted. After deepwiki: correct imports, signatures, structures. 30 seconds of deepwiki research prevents hours of debugging.

## Delegate to the Expert

Use `deepwiki:deepwiki-expert` rather than MCP tools directly. The expert has freshness verification, progressive discovery, and fallback strategies.

## Quick Reference

- Repo format: `owner/repo` (e.g., `facebook/react`) — public repos only
- Tools: `mcp_deepwiki_ask_question` (fast), `read_wiki_structure`, `read_wiki_contents`
