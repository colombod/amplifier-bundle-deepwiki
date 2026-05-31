# Changelog

All notable changes to the DeepWiki bundle will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.5.0] - 2026-05-31

### Changed — Setup Docs & Delegation Wording
- **README/USAGE setup instructions** — added the recommended `--app` layering path
  (`amplifier bundle add … --app`) so users can add DeepWiki on top of their existing
  bundle without `bundle use`. Both docs now present three clear options: `--app`
  layering (recommended), primary bundle (with `--local/--project/--global` scopes),
  and `includes:` composition for bundle authors.
- **Behavior renamed** `deepwiki-behavior` → `deepwiki-research` — a meaningful name
  that stays distinct from the root bundle name `deepwiki` (avoids self-referential
  registry entries flagged by `validate-bundle-repo`). Referenced by file path
  everywhere, so no external consumers are affected.
- **Capability-based delegation wording** — replaced the brittle, absolute
  "DO NOT use web_search" language with "prefer a source-grounded understanding
  capability," and noted that composed deep-search/web agents are valid routes. This
  reverses the v1.3.0/v1.4.0 hard prohibition in favor of portable, composition-aware
  guidance.
- **Clone-first fallback ladder** — when DeepWiki is stale/unindexed/insufficient, the
  expert now reads the actual source (shallow `git clone` + inspect) for code-level
  ground truth *before* web search; web search/fetch is reserved for questions *about*
  the repo (releases, changelogs, issues, community usage). Updated
  `context/deepwiki-awareness.md`, `context/staleness-fallbacks.md`, and the agent
  workflow/tool-scope accordingly.
- **Removed stale `perplexity_research` references** from agent context (the agent
  never had that tool); now framed as an optional capability only if composed.

### Added
- `model_role: research` on the `deepwiki-expert` agent for correct model routing.
- `AGENTS.md` — in-repo authoring/test/validation guidance.
- `bundle.dot` / `bundle.png` — repository architecture diagram (via `generate-bundle-docs`).
- `.amplifier/dtu/` — reusable Digital Twin Universe profile + README for end-to-end testing.
- Regeneration comment in `context/architecture.dot`.

### Fixed
- Removed a ghost `context/proactive-triggers.md` reference from the README structure
  diagram (the file was deleted in v1.4.0).
- Removed dead `__call__` method from the trigger hook (`mount()` registers
  `on_provider_request` directly). All 155 hook tests still pass.

### Validation
- `validate-bundle-repo` (v3.6.0): PASS — 0 errors; context-sink architecture exemplary.
- End-to-end verified in a Digital Twin Universe: bundle loads from local source,
  `--app` layering works without `bundle use`, hook mounts, expert agent registers,
  and the DeepWiki MCP server exposes its 3 tools.

## [1.4.0] - 2026-02-15

### Changed — Context Consolidation (46% token reduction)
- **Deleted `context/proactive-triggers.md`** — ~90% of its content was design justification or guidance for the root session, not the running agent. The hook module already handles proactive triggering at runtime. (-2,125 tokens)
- **Replaced `context/version-mismatch-handling.md` with `context/staleness-fallbacks.md`** — Stripped redundant freshness re-explanations, "Best Practices" filler, "Freshness Data Flow" (wrong audience), and "Remember" sections. Kept only: Fallback Strategy Matrix, 4 Recommended Patterns, Official Documentation URLs, Communication Templates. (-1,150 tokens)
- **Thinned `agents/deepwiki-expert.md` body** — Converted from content-heavy document to thin workflow orchestrator. Removed duplicated progressive discovery diagram, tool table, timeout handling, and Freshness Assessment template (all now single-sourced in @-included context files). (-675 tokens)
- **Consolidated `context/deepwiki-usage.md`** — Removed duplicated Progressive Discovery intro, repo format examples (already in awareness.md), and Response Quality Checklist (overlaps output contract). Kept Tool-Specific Guidance, exploration strategies, timeout handling. (-675 tokens)
- **Trimmed `context/freshness-check.md`** — Reduced examples from 4 to 2 (LOW + HIGH risk). Added Fast-Path for Simple Questions to skip full pre-flight for stable, well-known projects. (-275 tokens)
- **Agent context budget:** ~10,750 tokens → ~5,850 tokens (46% reduction)

### Changed — Hook Module Improvements
- **Multi-language package manager detection** — Added patterns for `npm install`, `yarn add`, `pnpm add`, `bun add`, `cargo add`, `go get`, `gem install`, `dotnet add package` alongside existing Python package managers
- **Multi-language import detection** — Added JS/TS (`import from`, `require()`), Rust (`use crate::`), and Go (`import "pkg"`) import patterns with per-language stdlib exclusion sets
- **Contextual reminder template** — Hook now reports WHAT was detected (e.g., "Detected: github.com/facebook/react" or "Library reference: fastapi (from import)") instead of generic "GitHub repository or library detected"
- **Injection cap** — Added `max_injections: 15` config to prevent reminder fatigue in long sessions. `total_injections` counter now enforced (was tracked but never read)
- **Expanded generic exclusions** — Added `backend`, `client`, `server`, `frontend`, `local`, `remote`, `new` to `GENERIC_API_PREFIXES` to reduce false positives
- **Removed dead state** — Deleted unused `provider_request_count` from `TriggerState`
- **113 tests pass** including 38 new tests covering multi-language patterns, expanded exclusions, contextual reminders, and injection cap

### Closed
- **Issue #2** (skill distribution via `@namespace:path`) — Closed as won't-fix. Analysis showed skills don't fit this bundle's delegation pattern: the root agent doesn't need to learn DeepWiki methodology (it just delegates), and the expert agent already has full context via @-mentions. The "upstream blocker" was also moot — `git+https://` URLs in tool config work today, and `skills.sources` in bundle frontmatter is silently dropped by the Bundle pipeline.

## [1.3.0] - 2026-02-15

### Improved
- Awareness context rewritten: shorter, opens with competing-path blocking against web_search
- Hook injection template: explicit "DO NOT use web_search" language
- Hook detection patterns: expanded to catch SDK/API integration, import/pip references, GitHub issue/PR URLs
- Hook mount(): returns cleanup callable per hook contract

### Noted
- Skill file distribution deferred to v1.4.0 (issue #2) pending upstream tool-skills enhancement — **Closed in v1.4.0** (skills don't fit delegation pattern)

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
