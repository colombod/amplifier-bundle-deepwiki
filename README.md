# amplifier-bundle-deepwiki

AI-powered open-source project understanding via [DeepWiki](https://deepwiki.com/).

This Amplifier bundle helps developers understand how open-source libraries, frameworks, 
and tools work internally, making it easier to use, extend, and integrate with them.

---

## External Service Dependency

> **This bundle uses the [DeepWiki MCP Server](https://mcp.deepwiki.com/mcp)**
> 
> DeepWiki is an AI-powered documentation platform by [Cognition](https://cognition.ai/) 
> (creators of [Devin](https://devin.ai/)). It provides intelligent analysis of public 
> GitHub repositories.
> 
> - **MCP Endpoint:** `https://mcp.deepwiki.com/mcp`
> - **Web Interface:** [deepwiki.com](https://deepwiki.com/)
> - **Protocol:** [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
> 
> By using this bundle, you are consuming DeepWiki's public MCP API. Please respect 
> their service and rate limits.

---

## Features

- **AI-Powered Documentation Analysis** - Ask questions about any public GitHub repository
- **Architecture Understanding** - Explore how projects are structured and designed
- **Extension Guidance** - Find the right way to extend or customize libraries
- **Integration Patterns** - Learn how to integrate with open-source tools
- **Progressive Discovery** - Efficient question-first exploration strategy

## Installation

```bash
# Add the bundle
amplifier bundle add git+https://github.com/colombod/amplifier-bundle-deepwiki@main

# Set as active
amplifier bundle use deepwiki
```

## Usage

### Interactive Session

```bash
amplifier
```

Then ask questions about open-source projects:

```
> How does React's reconciliation algorithm work?
> What's the architecture of the FastAPI framework?
> How can I add a custom provider to LangChain?
> What are the command and event patterns in dotnet/interactive?
```

### Single Query

```bash
amplifier run "Explain how Express.js middleware works"
```

### Compose into Your Bundle

Add DeepWiki capabilities to your existing bundle:

```yaml
includes:
  - bundle: git+https://github.com/colombod/amplifier-bundle-deepwiki@main#subdirectory=behaviors/deepwiki.yaml
```

## How It Works

This bundle integrates with the **DeepWiki MCP Server** using the 
[Model Context Protocol](https://modelcontextprotocol.io/).

### MCP Tools Provided

| Tool | Description |
|------|-------------|
| `mcp_deepwiki_read_wiki_structure` | Get documentation structure for a repository |
| `mcp_deepwiki_read_wiki_contents` | Read full wiki content (can be 400k+ chars) |
| `mcp_deepwiki_ask_question` | AI-powered Q&A about any public repository |

### Progressive Discovery Strategy

The bundle implements a **questions-first approach** for efficient exploration:

```
1. Start with simple questions (fastest)
2. Build understanding progressively  
3. Deep dive into content only when needed
```

This avoids the overhead of reading massive wiki content (400k+ chars) when 
targeted questions can get you answers faster.

## Bundle Structure

```
amplifier-bundle-deepwiki/
├── bundle.md                    # Thin root bundle
├── behaviors/
│   └── deepwiki.yaml            # Reusable behavior (MCP config + agent)
├── agents/
│   └── deepwiki-expert.md       # Context-sink expert agent
├── context/
│   ├── deepwiki-awareness.md    # Thin awareness for delegation
│   └── deepwiki-usage.md        # Detailed usage patterns
└── docs/
    └── USAGE.md                 # Human documentation
```

## Requirements

- [Amplifier](https://github.com/microsoft/amplifier) CLI installed
- Internet connection (for DeepWiki MCP server)
- A configured LLM provider (Anthropic, OpenAI, etc.)

## Limitations

- **Public repositories only** - DeepWiki indexes public GitHub repos
- **Private repos** - Require a [Devin.ai](https://devin.ai) account
- **Indexing delay** - Very new or obscure repos may not be fully indexed yet
- **Complex queries** - May timeout; break into smaller questions

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## License

MIT License - see [LICENSE](LICENSE) for details.

---

## Acknowledgments

This bundle would not be possible without:

- **[DeepWiki](https://deepwiki.com/)** - AI-powered documentation platform that 
  provides the knowledge base for understanding open-source projects
  
- **[Cognition](https://cognition.ai/)** - The team behind DeepWiki and Devin, 
  who provide the public MCP server at `https://mcp.deepwiki.com/mcp`
  
- **[Model Context Protocol](https://modelcontextprotocol.io/)** - The open protocol 
  that enables this integration
  
- **[Amplifier](https://github.com/microsoft/amplifier)** - The modular AI agent 
  framework that makes this bundle possible
