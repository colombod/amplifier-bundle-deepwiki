# DeepWiki Bundle Usage Guide

This guide explains how to use the DeepWiki bundle for understanding open-source projects.

## Quick Start

### Option 1: Add to Your Existing Setup with `--app` (Recommended)

Layer DeepWiki onto every session without replacing your active bundle. The `--app`
flag registers it as an app bundle that is auto-composed on top of whatever primary
bundle you use:

```bash
amplifier bundle add git+https://github.com/colombod/amplifier-bundle-deepwiki@main --app

# Available immediately in every session — no `bundle use` needed
amplifier run "How does React's virtual DOM work?"
```

### Option 2: Use as Primary Bundle

Make DeepWiki your active bundle (it includes foundation capabilities):

```bash
# Add the bundle
amplifier bundle add git+https://github.com/colombod/amplifier-bundle-deepwiki@main

# Set as active bundle (scope with --local | --project | --global)
amplifier bundle use deepwiki

# Start using it
amplifier run "How does React's virtual DOM work?"
```

### Option 3: Compose into Your Own Bundle (Bundle Authors)

If you are *authoring* a bundle, include the DeepWiki behavior as a reusable capability:

```yaml
# your-bundle.md
---
bundle:
  name: my-bundle
  version: 1.0.0

includes:
  - bundle: git+https://github.com/microsoft/amplifier-foundation@main
  - bundle: git+https://github.com/colombod/amplifier-bundle-deepwiki@main#subdirectory=behaviors/deepwiki.yaml
---
```

## Available Capabilities

### DeepWiki Expert Agent

The bundle provides `deepwiki:deepwiki-expert`, a specialized agent for understanding 
open-source projects. It's automatically available for delegation.

**Triggers delegation:**
- "How does [library] work?"
- "Explain the architecture of [project]"
- "How can I extend [framework]?"
- "What's the best way to integrate with [library]?"

### MCP Tools

Three DeepWiki tools are available:

| Tool | Description |
|------|-------------|
| `mcp_deepwiki_read_wiki_structure` | Get documentation structure for a repo |
| `mcp_deepwiki_read_wiki_contents` | Read specific documentation sections |
| `mcp_deepwiki_ask_question` | Ask AI-powered questions about a repo |

## Usage Examples

### Understanding a Library

```
User: How does FastAPI handle dependency injection?

Amplifier: [Delegates to deepwiki:deepwiki-expert]
           [Agent explores FastAPI documentation]
           [Returns comprehensive explanation with code examples]
```

### Finding Extension Points

```
User: I want to add a custom memory provider to LangChain. 
      How should I approach this?

Amplifier: [Delegates to deepwiki:deepwiki-expert]
           [Agent explores LangChain's memory architecture]
           [Returns extension patterns with practical guidance]
```

### Architecture Deep Dive

```
User: Explain the overall architecture of VS Code

Amplifier: [Delegates to deepwiki:deepwiki-expert]
           [Agent explores VS Code documentation]
           [Returns architecture overview with key components]
```

## Repository Format

DeepWiki works with public GitHub repositories using `owner/repo` format:

- `facebook/react`
- `microsoft/vscode`
- `langchain-ai/langchain`
- `tiangolo/fastapi`

**Note:** Private repositories require a Devin.ai account and are not supported 
by this bundle's free MCP endpoint.

## Best Practices

1. **Be specific** - Ask about specific features or behaviors
2. **Provide context** - Mention why you need the information
3. **Follow up** - Ask clarifying questions if needed
4. **Trust the expert** - Let the agent explore systematically

## Troubleshooting

### "Repository not found"

- Verify the repository exists and is public
- Check the `owner/repo` format is correct
- Some very new or obscure repos may not be indexed yet

### Slow responses

- DeepWiki needs to analyze documentation, which takes time
- Complex questions exploring multiple sections take longer
- This is expected for comprehensive answers

### Incomplete answers

- Ask more specific follow-up questions
- Request the agent to explore specific documentation sections
- Break complex questions into smaller parts

## Limitations

- **Public repositories only** — DeepWiki indexes public GitHub repositories. Private repositories return a 404 and the agent bails out with alternative suggestions (`web_search`, check spelling).
- **DeepWiki indexing required** — Very new or obscure repositories may not yet be indexed by DeepWiki. If the repo exists on GitHub but DeepWiki has no data, the agent will note this and suggest alternatives.
- **No private repo support** — Private repos require a [Devin.ai](https://devin.ai) account and are not supported by this bundle's free MCP endpoint (`https://mcp.deepwiki.com/mcp`).
