# DeepWiki Integration

You have access to **DeepWiki** for understanding open-source projects on GitHub.

## 🚨 CRITICAL: Use Proactively, Not Reactively

**Session analysis shows deepwiki was only used in 4.3% of sessions where it would have been valuable.**
The default pattern is web_search → this is WRONG for GitHub repositories and library internals.

**Real failure from Session 89aff774:**
- User implementing Azure AI Inference SDK
- AI guessed at API structure → incorrect assumptions
- User had to interrupt: "remember to use deepwiki for understanding API usage"
- After deepwiki: Correct imports, signatures, structures → prevented implementation errors

**Cost-benefit:** 30 seconds of deepwiki research prevents hours of debugging wrong APIs.

## When to Delegate (Immediate Triggers)

Delegate to `deepwiki:deepwiki-expert` IMMEDIATELY when you see:

1. **GitHub URLs** (any format: `github.com/owner/repo`, full URLs)
2. **"How does [library] work"** questions about open-source projects
3. **Library internals** questions (architecture, design patterns, implementation)
4. **Before implementing with external SDKs/libraries** (research FIRST, implement SECOND)
5. **Open-source framework references** (React, Django, FastAPI, Amplifier, etc.)

## Decision Tree

```
See GitHub URL? ──YES──▶ Delegate to deepwiki:deepwiki-expert
      │
      NO
      ↓
"How does X work?" ──YES──▶ Delegate to deepwiki:deepwiki-expert
      │
      NO
      ↓
Implementing with ──YES──▶ Delegate to deepwiki:deepwiki-expert FIRST
external library?
      │
      NO
      ↓
General web info? ──YES──▶ Use web_search (broader context)
```

## Version Awareness

**Every response includes a Freshness Assessment.** The expert agent proactively verifies DeepWiki's index freshness before every query by checking the repo's latest release and last commit against DeepWiki's reported coverage. Staleness risk is rated LOW / MODERATE / HIGH / UNKNOWN.

The expert agent:
- Runs a pre-flight freshness check (GitHub API + DeepWiki version probe) before answering
- Includes a structured Freshness Assessment as the first section of every response
- Applies fallback strategies when staleness risk is MODERATE or HIGH

## Available MCP Tools

| Tool | Speed | Purpose |
|------|-------|---------|
| `mcp_deepwiki_ask_question` | Fast | **Start here** - AI-powered answers |
| `mcp_deepwiki_read_wiki_structure` | Fast | Get documentation outline |
| `mcp_deepwiki_read_wiki_contents` | Slow | Full wiki (truncated to 50k chars) |

## Delegate to the Expert

**Use `deepwiki:deepwiki-expert`** rather than using tools directly. The expert agent has:
- Full trigger patterns and session analysis
- Progressive discovery strategy (avoids timeouts)
- Complete version mismatch handling strategies
- Fallback patterns for when DeepWiki is outdated

## Repository Format

DeepWiki uses `owner/repo` format:
- `facebook/react`
- `microsoft/vscode`
- `langchain-ai/langchain`
- `dotnet/interactive`

Only public GitHub repositories are accessible.
