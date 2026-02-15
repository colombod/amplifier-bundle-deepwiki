# Version Mismatch Handling Strategy

> **Context:** The pre-flight freshness protocol (`context/freshness-check.md`) proactively verifies DeepWiki's index freshness before every query. This file defines what to do when staleness risk is MODERATE or HIGH.

---

## How Freshness Verification Works

The expert agent runs a mandatory pre-flight check before every DeepWiki query:
1. Fetches the repo's latest release + last commit from GitHub
2. Probes DeepWiki for its coverage version
3. Computes a staleness risk: LOW / MODERATE / HIGH / UNKNOWN

**When risk is LOW:** No special action. Answer normally.
**When risk is MODERATE or HIGH:** Use the fallback strategies in this file to supplement DeepWiki answers with current information.
**When risk is UNKNOWN:** Treat information as potentially stale and recommend verification.

---

## Validation Workflow

### Step 1: Check Version Context

**When using DeepWiki, ALWAYS ask about version first:**

```
Primary question: "What is [library] and how does [feature] work?"
Follow-up: "What version of [library] is this documentation based on?"
```

**Look for:**
- Explicit version numbers in response
- "Last updated" or indexing dates
- Release tags mentioned

### Step 2: Cross-Reference Installation

**If user is implementing with an installed package:**

```bash
# Python packages
pip show [package-name]  # Check installed version

# Node packages  
npm list [package-name]  # Check installed version

# System packages
dpkg -l | grep [package]  # Debian/Ubuntu
rpm -qa | grep [package]  # RedHat/CentOS
```

**Compare:**
- DeepWiki version vs installed version
- If >1 major version apart → HIGH RISK of mismatch
- If >6 months of releases between → MEDIUM RISK

### Step 3: Verify Critical APIs

**Before implementing production code, validate:**

1. **Official documentation:**
   ```
   web_fetch("https://docs.[official-domain]/[library]/api-reference")
   ```

2. **Package changelogs:**
   ```
   web_search("[library] changelog version [X.Y.Z]")
   ```

3. **Migration guides:**
   ```
   web_search("[library] migration guide v[old] to v[new]")
   ```

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

### Recommended Patterns

#### Pattern 1: Architecture + Current API (Most Common)
```
1. DeepWiki ──▶ Understand architecture, design patterns, concepts
2. web_fetch ──▶ Get current API reference from official docs
3. Implement ──▶ Using DeepWiki's design + current API reality
```

**Use when:** Implementing with established library, need both concepts and current API

#### Pattern 2: Deep Research + Validation
```
1. DeepWiki ──▶ Get comprehensive understanding
2. web_search ──▶ Find version-specific information
3. web_fetch ──▶ Verify from official sources
4. Implement ──▶ With confidence in accuracy
```

**Use when:** Critical production code, high cost of errors

#### Pattern 3: Fast Track for Simple Tasks
```
1. DeepWiki ──▶ Quick answer to specific question
2. (Skip validation if low risk)
3. Implement ──▶ Test and adjust if needed
```

**Use when:** Exploratory work, prototypes, non-critical code

#### Pattern 4: Version Mismatch Recovery
```
1. DeepWiki ──▶ Gives outdated information
2. RECOGNIZE mismatch ──▶ Import/method errors
3. perplexity_research ──▶ "How does [feature] work in [library] v[X.Y.Z]?"
4. web_fetch ──▶ Official docs for current version
5. Implement ──▶ With corrected information
```

**Use when:** DeepWiki information doesn't match reality

---

## Official Documentation URLs

**Common sources for validation:**

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

## Communication Patterns

These templates supplement the Freshness Assessment section that always appears first in every response.

### When Staleness Risk is LOW

No additional version caveat needed. The Freshness Assessment header provides the verification data. Answer normally.

### When Staleness Risk is MODERATE

Include after the relevant answer section:

```markdown
> **⚠️ Freshness note:** DeepWiki's index is slightly behind the latest release.
> Recent changes (especially in the last {N} days) may not be reflected.
> For implementation-critical APIs, verify against official docs: {url}
```

### When Staleness Risk is HIGH

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

### When Staleness Risk is UNKNOWN

Include:

```markdown
> **ℹ️ Freshness unverified:** Could not determine DeepWiki's coverage version.
> Information may be current or stale — treat accordingly.
> Recommend verifying implementation-critical details against official docs: {url}
```

---

## Best Practices Summary

### ✅ DO

- **Ask about version** when querying DeepWiki
- **Validate critical APIs** from official sources before implementing
- **Report mismatches** when you encounter them
- **Combine sources** - DeepWiki for architecture, official docs for current API
- **Test imports early** - catch version issues before deep implementation
- **Use perplexity_research** for version-specific questions DeepWiki can't answer

### ❌ DON'T

- **Assume DeepWiki is current** - always verify for production code
- **Ignore import errors** - they're often version mismatch indicators
- **Skip validation** for critical/production implementations
- **Abandon DeepWiki** entirely - it's still excellent for architecture/design
- **Guess at APIs** - when in doubt, fetch official docs

---

## Freshness Data Flow

### How freshness data reaches the calling agent

The expert agent includes a structured **Freshness Assessment** as the first section of every response. This gives the calling agent:

1. **Objective data** — latest release tag, last commit SHA/date, DeepWiki coverage version
2. **Risk rating** — LOW / MODERATE / HIGH / UNKNOWN
3. **Gap summary** — human-readable explanation of the delta
4. **API method** — so the caller knows the reliability of the freshness data itself

The calling agent can use this information to:
- Decide whether to trust the answer as-is (LOW risk)
- Add caveats when presenting to the user (MODERATE risk)
- Supplement with additional research (HIGH risk)
- Flag uncertainty (UNKNOWN risk)

### Workflow (always proactive)

```
Caller's question
    ↓
Pre-flight freshness check (Steps 1-3)
    ↓
Freshness Assessment assembled
    ↓
DeepWiki query (with staleness context)
    ↓
If MODERATE/HIGH → supplement with fallback strategies (see matrix above)
    ↓
Response with Freshness Assessment header + answer sections
```

---

## Remember

**DeepWiki is authoritative for:**
- ✅ Architecture and design patterns
- ✅ Conceptual understanding
- ✅ Extension points and integration patterns
- ✅ Historical context and evolution

**DeepWiki may lag behind for:**
- ⚠️ Current API signatures
- ⚠️ Latest features (released in last 6 months)
- ⚠️ Deprecation status
- ⚠️ Version-specific behavior

**The solution isn't to avoid DeepWiki - it's to combine it with current sources for complete, accurate information.**
