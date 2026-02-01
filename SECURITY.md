# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |

## Security Considerations

### Data Privacy

This bundle connects to the public DeepWiki MCP server at `https://mcp.deepwiki.com/mcp`.

**What is sent:**
- GitHub repository identifiers (e.g., `owner/repo`)
- Natural language questions about repositories
- Documentation section requests

**What is NOT sent:**
- Your local files or code
- API keys or credentials
- Personal information

### Third-Party Service

DeepWiki is operated by [Cognition](https://cognition.ai/). By using this bundle, 
you agree to their terms of service and privacy policy.

### Network Security

- All communication uses HTTPS
- No authentication required for public repositories
- No credentials are stored by this bundle

## Reporting a Vulnerability

If you discover a security vulnerability in this bundle:

1. **Do NOT** open a public issue
2. Email the maintainer directly with details
3. Allow reasonable time for a fix before public disclosure

## Best Practices

- Only query public repositories you have rights to analyze
- Do not attempt to extract sensitive information from repositories
- Review DeepWiki's usage policies for rate limits and acceptable use
