# amplifier-bundle-deepwiki

AI-powered open-source project understanding via [DeepWiki](https://deepwiki.com/).

This Amplifier bundle helps developers understand how open-source libraries, frameworks, 
and tools work internally, making it easier to use, extend, and integrate with them.

## Features

- **AI-Powered Documentation Analysis** - Ask questions about any public GitHub repository
- **Architecture Understanding** - Explore how projects are structured and designed
- **Extension Guidance** - Find the right way to extend or customize libraries
- **Integration Patterns** - Learn how to integrate with open-source tools

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

This bundle integrates with the [DeepWiki MCP server](https://mcp.deepwiki.com/), 
which provides AI-powered access to documentation and knowledge about public 
GitHub repositories.

**Available tools:**
- `read_wiki_structure` - Explore documentation structure
- `read_wiki_contents` - Read specific documentation sections
- `ask_question` - Get AI-powered answers about repositories

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

- Only public GitHub repositories are supported
- Private repos require a [Devin.ai](https://devin.ai) account
- Very new or obscure repos may not be fully indexed

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

- [DeepWiki](https://deepwiki.com/) for the AI-powered documentation platform
- [Cognition](https://cognition.ai/) for the public MCP server
- [Amplifier](https://github.com/microsoft/amplifier) ecosystem
