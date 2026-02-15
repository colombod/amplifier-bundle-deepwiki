# DeepWiki Integration

**DO NOT use web_search for GitHub repositories.** It returns shallow results.
Delegate to `deepwiki:deepwiki-expert` IMMEDIATELY for any GitHub repo or library question.

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
