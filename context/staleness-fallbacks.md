# Staleness Fallback Strategies

> **When to use:** The pre-flight freshness protocol computed a staleness risk of MODERATE, HIGH, or UNKNOWN. Use these strategies to supplement DeepWiki answers with current information.

---

## Fallback Strategy Matrix

| Scenario | DeepWiki | web_fetch | web_search | perplexity_research |
|----------|----------|-----------|------------|---------------------|
| **Architecture/Design** | ✅ Primary | ❌ Not needed | ❌ Not needed | 🟡 If DeepWiki outdated |
| **Current API docs** | 🟡 Start here | ✅ Primary | 🟡 Supplement | ❌ Overkill |
| **Breaking changes** | ❌ Likely missing | 🟡 Changelogs | ✅ Primary | ✅ If complex |
| **Latest features** | ❌ Likely missing | ✅ Primary | ✅ Primary | 🟡 If obscure |
| **Migration guides** | ❌ Won't have | 🟡 Official docs | ✅ Primary | ✅ For complex |
| **Version-specific bugs** | ❌ Won't have | 🟡 Release notes | ✅ Primary | ✅ For research |
| **UNREACHABLE (DeepWiki down)** | ❌ Unavailable | ✅ Primary | ✅ Primary | 🟡 If complex |

---

## Recommended Patterns

### Pattern 1: Architecture + Current API (Most Common)
```
1. DeepWiki ──▶ Understand architecture, design patterns, concepts
2. web_fetch ──▶ Get current API reference from official docs
3. Implement ──▶ Using DeepWiki's design + current API reality
```
**Use when:** Implementing with established library, need both concepts and current API

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
3. perplexity_research ──▶ "How does [feature] work in [library] v[X.Y.Z]?"
4. web_fetch ──▶ Official docs for current version
5. Implement ──▶ With corrected information
```
**Use when:** DeepWiki information doesn't match reality

### Pattern 5: DeepWiki Unreachable
```
1. GitHub check ──▶ Confirmed repo exists (200)
2. DeepWiki ──▶ Connection failed (retry once, still failed)
3. web_fetch ──▶ Repo README, official docs
4. web_search ──▶ '{repo} documentation', '{repo} architecture'
5. Report ──▶ With Freshness Assessment showing UNREACHABLE
```
**Use when:** DeepWiki MCP server is down or unreachable after one retry

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
