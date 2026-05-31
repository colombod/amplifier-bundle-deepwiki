# Staleness Fallback Strategies

> **When to use:** The pre-flight freshness protocol computed a staleness risk of MODERATE, HIGH, or UNKNOWN. Use these strategies to supplement DeepWiki answers with current information.

---

## Escalation Ladder

> **Tool scope:** This agent has `tool-mcp` (DeepWiki), `tool-web` (`web_fetch` + `web_search`), and `tool-bash`.

When DeepWiki is stale, unindexed, or insufficient, escalate in this order — **read code from the source before reading about it from the web:**

1. **DeepWiki** (`tool-mcp`) — source-grounded, indexed analysis. Primary for architecture, design, and "how does it work" questions.
2. **Clone & inspect locally** (`tool-bash`) — for code-level ground truth, shallow-clone into a temp dir and read the actual source:
   ```bash
   tmp=$(mktemp -d) && git clone --depth 1 https://github.com/<owner>/<repo>.git "$tmp"
   # then inspect with shell tools: find "$tmp" -name '*.py', grep -rn "<symbol>" "$tmp", cat "$tmp/<file>"
   ```
   This beats web search for imports, signatures, and implementation detail — it *is* the truth, at the cloned ref. Clean up the temp dir when done.
3. **Web search / fetch** (`tool-web`) — reserve for questions *about* the repo that aren't answerable from its source tree: releases, changelogs, migration guides, open issues, security advisories, and community usage. Use `web_search` to discover and `web_fetch` to read authoritative pages.

(If the calling environment also provides a deep-research capability such as `perplexity_research`, it can substitute for `web_search` on complex multi-source questions — but never assume it is available.)

### Strategy Matrix

| Scenario | DeepWiki | Clone & inspect | web_fetch / web_search |
|----------|----------|-----------------|------------------------|
| **Architecture/Design** | ✅ Primary | 🟡 If DeepWiki outdated | ❌ Not needed |
| **Imports / signatures / impl detail** | 🟡 Start here | ✅ Primary (ground truth) | ❌ Shallow |
| **Current API for a specific version** | 🟡 Start here | ✅ Clone at the tag | 🟡 Official docs |
| **Breaking changes** | ❌ Likely missing | 🟡 Diff tags/changelog file | ✅ Releases/changelog page |
| **Latest features** | ❌ Likely missing | 🟡 Clone `main` | ✅ Release notes |
| **Migration guides** | ❌ Won't have | 🟡 Repo docs/ dir | ✅ Official guide |
| **Open issues / community usage** | ❌ Won't have | ❌ Not in source | ✅ Primary |
| **UNREACHABLE (DeepWiki down)** | ❌ Unavailable | ✅ Primary | ✅ For meta-questions |

---

## Recommended Patterns

### Pattern 1: Architecture + Real Source (Most Common)
```
1. DeepWiki ──▶ Understand architecture, design patterns, concepts
2. git clone --depth 1 ──▶ Read the actual API surface / signatures from source
3. web_fetch ──▶ Only if you need official prose docs the source doesn't carry
4. Implement ──▶ Using DeepWiki's design + the real, current source
```
**Use when:** Implementing with an established library; need both concepts and exact, current API. Prefer reading the cloned source over web snippets for signatures.

### Pattern 2: Deep Research + Validation
```
1. DeepWiki ──▶ Get comprehensive understanding
2. web_search ──▶ Find version-specific information
3. web_fetch ──▶ Verify from official sources
4. Implement ──▶ With confidence in accuracy
```
**Use when:** Critical production code, high cost of errors

### Pattern 3: Fast Track
```
1. DeepWiki ──▶ Quick answer to specific question
2. (Skip validation if low risk)
3. Implement ──▶ Test and adjust if needed
```
**Use when:** Exploratory work, prototypes, non-critical code

### Pattern 4: Version Mismatch Recovery
```
1. DeepWiki ──▶ Gives outdated information
2. RECOGNIZE mismatch ──▶ Import/method errors
3. git clone --depth 1 --branch v[X.Y.Z] ──▶ Read the real signatures at that exact tag
4. web_fetch ──▶ Official docs only if source lacks prose explanation
5. Implement ──▶ With corrected, source-verified information
```
**Use when:** DeepWiki information doesn't match reality. The cloned tag is the source of truth for the version's actual API.

### Pattern 5: DeepWiki Unreachable
```
1. GitHub check ──▶ Confirmed repo exists (200)
2. DeepWiki ──▶ Connection failed (retry once, still failed)
3. git clone --depth 1 ──▶ Read README + actual source for architecture/API ground truth
4. web_fetch / web_search ──▶ Fill gaps the source can't answer (releases, community usage)
5. Report ──▶ With Freshness Assessment showing UNREACHABLE
```
**Use when:** DeepWiki MCP server is down or unreachable after one retry. Cloning the source is the strongest substitute for DeepWiki's analysis.

---

## Official Documentation URLs

### Python Packages
- **Official docs:** `web_fetch("https://[library].readthedocs.io/en/stable/")`
- **PyPI changelog:** `web_fetch("https://pypi.org/project/[library]/#history")`
- **GitHub releases:** `web_fetch("https://github.com/[owner]/[repo]/releases")`

### Microsoft/Azure
- **Azure docs:** `web_fetch("https://learn.microsoft.com/azure/[service]/")`
- **Python SDK:** `web_fetch("https://learn.microsoft.com/python/api/overview/azure/")`
- **.NET docs:** `web_fetch("https://learn.microsoft.com/dotnet/")`

### JavaScript/Node
- **npm docs:** `web_fetch("https://www.npmjs.com/package/[package]")`
- **Official sites:** `web_fetch("https://[framework].dev/docs")`

### Language-Specific
- **Python:** `web_fetch("https://docs.python.org/3/")`
- **Node.js:** `web_fetch("https://nodejs.org/docs/latest/api/")`
- **.NET:** `web_fetch("https://learn.microsoft.com/dotnet/api/")`

---

## Communication Templates

These templates supplement the Freshness Assessment that always appears first in every response.

### LOW Risk
No additional caveat needed. The Freshness Assessment header provides the verification data.

### MODERATE Risk
Include after the relevant answer section:

```markdown
> **⚠️ Freshness note:** DeepWiki's index is slightly behind the latest release.
> Recent changes (especially in the last {N} days) may not be reflected.
> For implementation-critical APIs, verify against official docs: {url}
```

### HIGH Risk
Include prominently:

```markdown
> **🔴 Staleness warning:** DeepWiki's index is significantly behind (covers {old_version}, latest is {new_version}).
> Architecture and design pattern information is likely still accurate, but API details may have changed.
>
> **Corrective actions taken:**
> 1. Fetched current API docs from {source}
> 2. Cross-referenced DeepWiki's architectural insights with current documentation
>
> **Recommendation:** Treat API-specific details from DeepWiki as directional. Verify all imports, method signatures, and response structures against official docs.
```

### UNKNOWN Risk
Include:

```markdown
> **ℹ️ Freshness unverified:** Could not determine DeepWiki's coverage version.
> Information may be current or stale — treat accordingly.
> Recommend verifying implementation-critical details against official docs: {url}
```

### UNREACHABLE
Include:

```markdown
> **🔴 DeepWiki unreachable:** The DeepWiki MCP server is currently unavailable.
> The repository `{owner}/{repo}` has been verified as public on GitHub.
>
> **Fallback actions taken:**
> 1. Fetched repository README and available documentation via `web_fetch`
> 2. Searched for '{repo} documentation' via `web_search`
>
> **Recommendation:** Retry the DeepWiki delegation later for comprehensive codebase analysis.
> The information below is based on publicly available documentation only.
```
