# Changelog

All notable changes to the DeepWiki bundle will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-02-04

### Added
- **Proactive trigger system** based on analysis of 650+ historical sessions
- New `context/proactive-triggers.md` with automatic trigger patterns:
  - GitHub URL detection (regex patterns)
  - "How does [library] work" question detection
  - External library/SDK implementation triggers
  - Decision matrix for when to use DeepWiki vs web_search
- Real failure examples from session history (Session 89aff774) demonstrating the cost of not using DeepWiki proactively
- Additional usage examples showing proactive delegation patterns
- Cost-benefit analysis showing 120-240x time savings from proactive research

### Changed
- **Enhanced agent description** with critical urgency markers (🚨)
- Strengthened language: "ALWAYS use IMMEDIATELY when you see" for key triggers
- Added real session failure example to agent description showing user having to prompt
- Updated `deepwiki-awareness.md` with automatic trigger checklist and decision tree
- Moved from reactive ("when users ask") to proactive ("use immediately when you see") language
- Added missed opportunity analysis from 10+ sessions where DeepWiki should have been used

### Context
This release addresses findings from session analysis showing DeepWiki was only used in 4.3% of sessions where it would have been valuable. The primary issue was defaulting to `web_search` instead of proactively using DeepWiki for GitHub repositories and library internals.

**Key insight:** Session 89aff774 showed user had to explicitly prompt "remember to use deepwiki for understanding API usage" - this prevented API implementation errors. This release makes that proactive behavior the default.

## [1.0.0] - Initial Release

### Added
- Initial DeepWiki MCP integration
- `deepwiki-expert` agent for repository understanding
- Progressive discovery methodology
- Basic usage documentation
- MCP tool awareness context
