# DeepWiki Integration

You have access to **DeepWiki** for understanding open-source projects on GitHub.

## Critical: Progressive Discovery Approach

**DeepWiki operations are content-intensive** - wiki content can exceed 400k characters.
Complex questions can timeout. Use progressive discovery:

```
Questions First ──▶ Build Understanding ──▶ Deep Dive (if needed)
```

**Start with simple questions, not content reads.**

## When to Delegate

Delegate to `deepwiki:deepwiki-expert` when users ask about:

- How open-source libraries/frameworks work internally
- Understanding unfamiliar GitHub repositories
- "How does [library] implement [feature]?"
- Finding extension points or integration patterns
- Architecture and design of OSS projects

## Available MCP Tools

| Tool | Speed | Purpose |
|------|-------|---------|
| `mcp_deepwiki_ask_question` | Fast | **Start here** - AI-powered answers |
| `mcp_deepwiki_read_wiki_structure` | Fast | Get documentation outline |
| `mcp_deepwiki_read_wiki_contents` | Slow | Full wiki (truncated to 50k chars) |

## Quick Usage Pattern

For any repository question, use this progressive approach:

```
1. ask_question: "What is [repo] and what are its main components?"
2. ask_question: "How does [specific feature] work?"
3. ask_question: "How do I extend/use [capability]?"
4. (only if needed) read_wiki_structure → read_wiki_contents
```

**Break down complex questions** - multiple simple questions avoid timeouts.

## Delegate to the Expert

**Use `deepwiki:deepwiki-expert`** rather than using tools directly. The expert 
agent knows the progressive discovery strategy and handles timeouts gracefully.

## Repository Format

DeepWiki uses `owner/repo` format:
- `facebook/react`
- `microsoft/vscode`
- `langchain-ai/langchain`
- `dotnet/interactive`

Only public GitHub repositories are accessible.
