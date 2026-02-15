# Changelog

All notable changes to the DeepWiki bundle will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2026-02-15

### Added
- **Proactive freshness verification** — every DeepWiki query is now preceded by a mandatory pre-flight freshness check
- New `context/freshness-check.md` — single source of truth for the 4-step pre-flight protocol:
  1. GitHub Ground Truth (latest release + last commit via `gh api` or `web_fetch` fallback)
  2. DeepWiki Version Probe (`ask_question` to determine coverage version)
  3. Staleness Risk Computation (LOW / MODERATE / HIGH / UNKNOWN heuristic)
  4. Proceed to main query with freshness context
- Tiered GitHub API access: `gh` CLI (authenticated, higher rate limits) with automatic `web_fetch` fallback (unauthenticated)
- Structured **Freshness Assessment** output section — always first in every response, with machine-readable key-value fields

### Changed
- **Shifted from reactive to proactive staleness handling** — version mismatches are now caught before queries, not after errors
- Updated `agents/deepwiki-expert.md`:
  - Added freshness-check.md as agent context (@-mention)
  - Rewrote Standard Workflow to include pre-flight freshness as Step 2
  - Updated Output Contract to require Freshness Assessment as first section
  - Replaced inline version-mismatch section with brief reference to pre-flight protocol
  - Updated meta description to mention proactive freshness verification
- Updated `context/version-mismatch-handling.md`:
  - Removed reactive symptom-recognition section (superseded by pre-flight check)
  - Added Freshness Data Flow section (how freshness data reaches calling agents)
  - Updated communication templates to align with Freshness Assessment format
  - Preserved fallback strategy matrix for MODERATE/HIGH risk scenarios
- Updated `context/deepwiki-awareness.md`:
  - Version Awareness section now describes proactive verification
  - Notes that every response includes Freshness Assessment
- Updated `context/proactive-triggers.md`:
  - Version mismatch awareness section replaced with freshness verification reference
  - Summary workflow updated to show proactive freshness as default
- Updated `README.md` with corrected bundle structure diagram and freshness feature

### Context
This release addresses the limitation that version staleness was only detected reactively — after errors or inconsistencies surfaced during implementation. The pre-flight freshness protocol ensures every response comes with an objective assessment of data currency, enabling calling agents to make informed decisions about the information they receive.

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
