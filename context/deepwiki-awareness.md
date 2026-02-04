# DeepWiki Integration

You have access to **DeepWiki** for understanding open-source projects on GitHub.

## 🚨 CRITICAL: Use Proactively, Not Reactively

**Session analysis shows deepwiki was only used in 4.3% of sessions where it would have been valuable.**
The default pattern is web_search → this is WRONG for GitHub repositories and library internals.

**Real failure from Session 89aff774:**
- User implementing Azure AI Inference SDK
- AI guessed at API structure → incorrect assumptions
- User had to interrupt: "remember to use deepwiki for understanding API usage"
- After deepwiki: Correct imports, signatures, structures → prevented implementation errors

**Cost-benefit:** 30 seconds of deepwiki research prevents hours of debugging wrong APIs.

## Automatic Triggers - Use IMMEDIATELY When You See

### 🔴 Strong Triggers (ALWAYS delegate to deepwiki:deepwiki-expert)

1. **GitHub URLs in ANY format:**
   - `github.com/owner/repo`
   - `https://github.com/microsoft/amplifier`
   - Repository references in conversation
   
2. **"How does [library] work"** questions:
   - "How does Amplifier's module loading work?"
   - "What's the architecture of FastAPI?"
   - "How does React reconciliation work?"

3. **Library internals questions:**
   - Architecture, design patterns, internal APIs
   - Module structure, component hierarchy
   - Implementation details

4. **API integration tasks:**
   - Implementing with external packages/SDKs
   - "How do I use [library] for [task]?"
   - Before writing code that calls external APIs

5. **Open-source project references:**
   - React, Vue, Django, FastAPI, Amplifier mentions
   - Any third-party framework or tool
   - Developer tools and libraries

### Decision Tree

```
See GitHub URL? ──YES──▶ Delegate to deepwiki:deepwiki-expert
      │
      NO
      ↓
"How does X work?" ──YES──▶ Delegate to deepwiki:deepwiki-expert
      │
      NO
      ↓
Implementing with ──YES──▶ Delegate to deepwiki:deepwiki-expert FIRST
external library?
      │
      NO
      ↓
General web info? ──YES──▶ Use web_search (broader context)
```

## When to Delegate

**Delegate to `deepwiki:deepwiki-expert` BEFORE implementing** when users ask about:

- How open-source libraries/frameworks work internally
- Understanding unfamiliar GitHub repositories
- "How does [library] implement [feature]?"
- Finding extension points or integration patterns
- Architecture and design of OSS projects
- External package API usage patterns

## Available MCP Tools

| Tool | Speed | Purpose |
|------|-------|---------|
| `mcp_deepwiki_ask_question` | Fast | **Start here** - AI-powered answers |
| `mcp_deepwiki_read_wiki_structure` | Fast | Get documentation outline |
| `mcp_deepwiki_read_wiki_contents` | Slow | Full wiki (truncated to 50k chars) |

## ⚠️ Critical: Version Mismatch Awareness

**DeepWiki indexes repositories at specific points in time.** It may not reflect the latest package versions installed in your environment.

**Symptoms of version mismatch:**
- Import/module errors (can't find what DeepWiki shows)
- Method signature mismatches (parameters don't match)
- Missing features (user mentions features DeepWiki doesn't show)
- Deprecation warnings for APIs DeepWiki recommends

**When you suspect version mismatch:**

1. **Ask DeepWiki about version:** "What version is this documentation for?"
2. **Cross-reference with official docs:** Use `web_fetch` on official documentation
3. **Use perplexity_research:** For version-specific questions
4. **Validate before implementing:** Check APIs match reality

**Fallback strategy:**
```
DeepWiki (architecture/patterns) + web_fetch (current API docs) = Accurate implementation
```

See `@deepwiki:context/version-mismatch-handling.md` (loaded in deepwiki-expert agent) for complete handling strategy.

## Quick Usage Pattern

For any repository question, use this progressive approach:

```
1. ask_question: "What is [repo] and what are its main components?"
2. ask_question: "How does [specific feature] work?"
3. ask_question: "How do I extend/use [capability]?"
4. (only if needed) read_wiki_structure → read_wiki_contents
```

**Break down complex questions** - multiple simple questions avoid timeouts.

## Delegate to the Expert

**Use `deepwiki:deepwiki-expert`** rather than using tools directly. The expert 
agent knows the progressive discovery strategy and handles timeouts gracefully.

## Repository Format

DeepWiki uses `owner/repo` format:
- `facebook/react`
- `microsoft/vscode`
- `langchain-ai/langchain`
- `dotnet/interactive`

Only public GitHub repositories are accessible.
