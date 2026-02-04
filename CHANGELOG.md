# Changelog

All notable changes to the DeepWiki bundle will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-02-04

### Fixed (Architecture)
- **Corrected context sink pattern violation** - Moved heavy analysis documents to agent-only loading
  - Removed `proactive-triggers.md` (9.4KB) from behavior context includes
  - Added `proactive-triggers.md` as @mention in agent (loads only when agent spawned)
  - Refactored `deepwiki-awareness.md` from 135 lines → 75 lines (thin awareness pointer)
  - Deduplicated version mismatch content (thin pointer in awareness, full guide in agent)
  - **Impact:** Root sessions now load ~3KB instead of ~14KB, following Foundation's context sink pattern

## [1.1.0] - 2026-02-04 (Original)

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
- **Version mismatch awareness system** addressing DeepWiki's potential staleness:
  - New `context/version-mismatch-handling.md` with comprehensive fallback strategies
  - Symptom recognition patterns (import errors, signature mismatches, missing features)
  - Validation workflow for critical implementations
  - Fallback strategy matrix (when to use DeepWiki vs web_fetch vs perplexity_research)
  - Official documentation URL patterns for common sources
  - Version-aware communication patterns for reporting mismatches

### Changed
- **Enhanced agent description** with critical urgency markers (🚨)
- Strengthened language: "ALWAYS use IMMEDIATELY when you see" for key triggers
- Added real session failure example to agent description showing user having to prompt
- Updated `deepwiki-awareness.md` with automatic trigger checklist and decision tree
- Moved from reactive ("when users ask") to proactive ("use immediately when you see") language
- Added missed opportunity analysis from 10+ sessions where DeepWiki should have been used
- **Enhanced agent with version mismatch section** including:
  - Symptoms recognition
  - Cross-reference workflow
  - Fallback strategy when mismatch detected
  - Example scenario showing mismatch detection and recovery
- **Updated proactive-triggers.md** with version awareness integration
- **Agent now loads version-mismatch-handling.md** for complete strategy reference

### Context
This release addresses two critical findings from session analysis:

1. **Underuse:** DeepWiki was only used in 4.3% of sessions where it would have been valuable. The primary issue was defaulting to `web_search` instead of proactively using DeepWiki for GitHub repositories and library internals.

2. **Version staleness:** DeepWiki indexes repositories at specific points in time and may not reflect the latest package versions installed in environments, leading to import errors, API mismatches, and implementation issues.

**Key insight from Session 89aff774:** User had to explicitly prompt "remember to use deepwiki for understanding API usage" - this prevented API implementation errors. This release makes that proactive behavior the default WHILE adding awareness that DeepWiki should be combined with current official docs for production implementations.

## [1.0.0] - Initial Release

### Added
- Initial DeepWiki MCP integration
- `deepwiki-expert` agent for repository understanding
- Progressive discovery methodology
- Basic usage documentation
- MCP tool awareness context
