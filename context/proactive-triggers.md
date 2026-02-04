# Proactive DeepWiki Usage - Triggers and Patterns

> **Purpose**: Guide AI agents to use DeepWiki proactively based on session analysis of 650+ historical sessions.

---

## The Problem: Reactive, Not Proactive Usage

**Session analysis findings:**
- **28 sessions** (4.3%) used deepwiki where it would have been valuable
- **100+ sessions** had GitHub URLs → deepwiki used in <5%
- **10+ clear misses** where deepwiki would have prevented implementation errors

**Default pattern observed:**
```
User mentions GitHub repo → AI uses web_search → Implements with assumptions → Errors
```

**Correct pattern:**
```
User mentions GitHub repo → AI delegates to deepwiki:deepwiki-expert → Gets accurate API → Implements correctly
```

---

## Real Failure Example (Session 89aff774)

**Context:** User implementing Azure AI Inference SDK integration

**What happened:**
1. AI started implementing with Azure AI Inference SDK
2. AI made assumptions about imports, method signatures, response structures
3. **User had to interrupt:** 
   > "remember to use deepwiki or perplexity or other searchs for understaind api usage or asking question on features you are consuming from other pacakges"
4. AI then delegated to deepwiki:deepwiki-expert
5. Got correct API details: proper imports, accurate signatures, real response structures
6. **Prevented implementation errors that would have required debugging**

**Lesson:** 30 seconds of research prevents hours of debugging incorrect API assumptions.

---

## Automatic Trigger Patterns

### 🔴 CRITICAL: GitHub Repository Mentions

**Pattern recognition:**
```regex
github\.com/[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+
(github.com/microsoft/amplifier-core)
```

**Action:** IMMEDIATELY delegate to `deepwiki:deepwiki-expert`

**Examples from missed sessions:**
- `"github.com/microsoft-amplifier/amplifier-support/issues/32"` → Should have researched Amplifier codebase
- `"https://github.com/colombod/amplifier-session-storage"` → Should have researched storage architecture
- `"amplifier-app-server repo"` → Should have researched module loading

### 🔴 CRITICAL: "How does [library] work" Questions

**Pattern recognition:**
```
"how does [X] work"
"how [X] works"
"understand how [X]"
"[X] architecture"
"[X] internals"
```

**Action:** Delegate to `deepwiki:deepwiki-expert` for open-source projects

**Examples from missed sessions:**
- "how does amplifier work" → Should have used deepwiki for architecture
- "amplifier session gets modules loaded" → Should have researched module system
- "open telemetry in amplifier" → Should have researched Amplifier patterns

### 🔴 CRITICAL: External Library/SDK Implementation

**Pattern recognition:**
```
"implementing with [X]"
"integrate [X]"
"using [Y] SDK"
"add [Z] library"
```

**Action:** Research BEFORE implementing

**Examples from missed sessions:**
- "ACP integration" → Should have researched amplifier-app-server
- "Cosmos DB integration" → Should have researched Azure Cosmos patterns
- "Azure AI Inference SDK" → User had to prompt (failure case)

### 🟡 MEDIUM: Library/Framework References

**Pattern recognition:**
- React, Vue, Angular, Django, FastAPI mentions
- Riot Games API, Perplexity API references
- Any third-party framework or tool name

**Action:** Consider delegating if understanding internal behavior is needed

---

## Decision Matrix

| Scenario | Use DeepWiki? | Why |
|----------|---------------|-----|
| GitHub URL in message | ✅ YES - IMMEDIATELY | Authoritative source for codebase understanding |
| "How does [OSS library] work?" | ✅ YES - IMMEDIATELY | Library internals is deepwiki's specialty |
| Implementing with external SDK | ✅ YES - BEFORE CODING | Prevent API assumption errors |
| Understanding Amplifier internals | ✅ YES | microsoft/amplifier repos on GitHub |
| General web documentation | ❌ NO - use web_search | Broader context, not codebase-specific |
| Historical facts/concepts | ❌ NO - use web_search | Not repository-specific |

---

## Cost-Benefit Analysis

**DeepWiki costs:**
- ~30 seconds per question
- Token usage (MCP overhead)

**DeepWiki prevents:**
- Hours debugging wrong API assumptions
- Multiple iteration cycles fixing imports
- Misunderstanding architecture/patterns
- Implementing incompatible integration patterns

**ROI calculation:**
```
Cost: 30 seconds research
Benefit: Prevent 1-2 hours debugging
ROI: 120-240x time savings
```

**Real example:** Session 89aff774 saved hours of Azure SDK debugging by spending 30 seconds on research.

---

## Missed Opportunities Analysis

### Session a075ff7d (ACP Implementation)
- **Trigger:** "amplifier-app-server repo", "ACP integration"
- **What happened:** 76 web_fetch calls, 31 web_search calls, 0 deepwiki calls
- **Should have:** Researched Amplifier module loading architecture via deepwiki

### Session 7c48906a (Amplifier Support Issue)
- **Trigger:** "github.com/microsoft-amplifier/amplifier-support/issues/32"
- **What happened:** Web searches for context
- **Should have:** Researched Amplifier codebase to understand issue context

### Session fc4a6dfb (Cosmos DB Integration)
- **Trigger:** "https://github.com/colombod/amplifier-session-storage"
- **What happened:** Web searches for Azure Cosmos documentation
- **Should have:** Researched amplifier-session-storage repo architecture

### Session b8e71370 (OpenTelemetry Module)
- **Trigger:** "open telemetry in amplifier", module design discussions
- **What happened:** Web searches for OpenTelemetry general docs
- **Should have:** Researched Amplifier's module architecture patterns

### Session 062c562f (League of Legends Bundle)
- **Trigger:** "https://developer.riotgames.com/docs/lol"
- **What happened:** Web searches and fetch operations
- **Should have:** Used deepwiki for Riot Games API structure

---

## Implementation Checklist

Before implementing with any external library/SDK, verify:

- [ ] Have I seen a GitHub URL or repository reference?
- [ ] Am I implementing with an external package/SDK?
- [ ] Is the user asking "how does [library] work"?
- [ ] Do I understand the internal API structure?
- [ ] Have I delegated to deepwiki:deepwiki-expert?

**If NO to last question and YES to any others → Delegate to deepwiki:deepwiki-expert NOW**

---

## Success Pattern

**From Session 89aff774 (after user prompt):**

1. User mentioned Azure AI Inference SDK
2. AI delegated to deepwiki:deepwiki-expert
3. Got accurate information:
   - Correct import paths
   - Proper method signatures  
   - Actual response structures
   - Client lifecycle management
4. Implemented correctly on first try
5. No debugging cycle needed

**This is the pattern we want PROACTIVELY, not after user prompts.**

---

## Anti-Patterns to Avoid

❌ **"I'll just try web_search first"**
- GitHub repos need authoritative source (deepwiki), not web summaries

❌ **"I'll implement and see what breaks"**
- Wastes time debugging wrong assumptions that research would have prevented

❌ **"The API seems straightforward"**
- Assumptions about APIs cause 80% of integration bugs

❌ **"I can figure it out from error messages"**
- Error messages don't teach you the correct architecture/patterns

✅ **"Let me research this first with deepwiki:deepwiki-expert"**
- Correct approach: understand before implementing

---

## Version Mismatch Awareness

**CRITICAL: DeepWiki may be out of sync with installed package versions.**

**Why this matters:**
- DeepWiki indexes repositories at specific points in time
- Fast-moving projects diverge quickly from indexed state
- Outdated information leads to import errors, signature mismatches, missing features

**Recognize version mismatches:**
- Import/module not found errors
- Method signature mismatches (unexpected parameters)
- Deprecation warnings for APIs DeepWiki recommends
- User mentions features DeepWiki doesn't show

**When version mismatch suspected:**

1. **Ask DeepWiki:** "What version is this documentation for?"
2. **Cross-reference:** Use `web_fetch` for current official docs
3. **Use perplexity_research:** For version-specific questions
4. **Combine sources:** DeepWiki (architecture) + official docs (current API)

**Fallback strategy matrix:**
```
Architecture/Design     → DeepWiki (PRIMARY)
Current API docs        → web_fetch official docs (PRIMARY)
Breaking changes        → web_search + perplexity_research
Latest features         → web_fetch + web_search
Version-specific bugs   → perplexity_research
```

**Communication pattern:**
When mismatch detected, report to user:
- What DeepWiki showed vs reality
- Likely version difference
- Fallback sources used
- Recommendation to verify with official docs

See `context/version-mismatch-handling.md` for complete strategy.

---

## Summary: The New Default

**Old default:**
```
Implement → Error → Debug → Research → Fix
```

**New default with version awareness:**
```
Research (deepwiki) → Validate version → Cross-reference if needed → Implement correctly
```

**Trigger checklist:**
- GitHub URL? → deepwiki
- "How does X work?" (OSS) → deepwiki
- External SDK/library? → deepwiki BEFORE coding + validate version
- General web info? → web_search
- Version mismatch suspected? → deepwiki + web_fetch + perplexity_research

**Remember:** You're reading this file in your context RIGHT NOW. These patterns should guide your behavior automatically.
