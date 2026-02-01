# DeepWiki Integration

You have access to **DeepWiki** for understanding open-source projects on GitHub.

## When to Delegate

Delegate to `deepwiki:deepwiki-expert` when users ask about:

- How open-source libraries/frameworks work internally
- Understanding unfamiliar GitHub repositories
- "How does [library] implement [feature]?"
- Finding extension points or integration patterns
- Architecture and design of OSS projects

## Available MCP Tools

The DeepWiki MCP server provides three tools:

| Tool | Purpose |
|------|---------|
| `mcp_deepwiki_read_wiki_structure` | Explore documentation structure |
| `mcp_deepwiki_read_wiki_contents` | Read specific documentation sections |
| `mcp_deepwiki_ask_question` | Ask AI-powered questions about any public repo |

## Usage Note

**Delegate to the expert agent** rather than using DeepWiki tools directly. 
The `deepwiki:deepwiki-expert` agent carries comprehensive knowledge about 
effective query patterns and can synthesize multiple sources into coherent answers.

## Repository Format

DeepWiki uses `owner/repo` format for GitHub repositories:
- `facebook/react`
- `microsoft/vscode`
- `langchain-ai/langchain`
