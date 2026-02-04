# Version Mismatch Handling Strategy

> **Critical awareness**: DeepWiki indexes repositories at specific points in time and may not reflect the latest package versions installed in your environment.

---

## The Version Mismatch Problem

**DeepWiki provides:** Architecture, design patterns, conceptual understanding
**DeepWiki may miss:** Latest API changes, recent features, current deprecations

**Root cause:** DeepWiki's AI-powered knowledge base is built from repository snapshots. Fast-moving projects (frequent releases, active development) can diverge significantly from their indexed state.

---

## Recognizing Version Mismatches

### 🔴 Strong Indicators (Immediate action required)

1. **Import/Module errors:**
   ```python
   # DeepWiki suggests:
   from azure.ai.inference import ChatCompletionsClient
   
   # Reality:
   ImportError: cannot import name 'ChatCompletionsClient'
   ```

2. **Method signature mismatches:**
   ```python
   # DeepWiki shows:
   client.complete(prompt="...")
   
   # Reality:
   TypeError: complete() got an unexpected keyword argument 'prompt'
   ```

3. **Missing features:**
   - User mentions feature X exists
   - DeepWiki doesn't document it
   - User likely has newer version

4. **Deprecation warnings:**
   ```python
   DeprecationWarning: Method 'old_method' is deprecated, use 'new_method'
   # But DeepWiki only shows old_method
   ```

### 🟡 Warning Signs (Investigate)

1. **Vague version references:**
   - DeepWiki answers lack specific version numbers
   - Documentation seems generic/old

2. **Release date clues:**
   - DeepWiki references "recent" features from 2+ years ago
   - Changelog mentions stop at old versions

3. **API inconsistencies:**
   - Response structures don't match
   - Parameter names differ slightly
   - Return types unexpected

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

## Communication Pattern

### When DeepWiki Information is Current

```markdown
**Source:** DeepWiki (architecture understanding)
**Validation:** APIs match official docs v[X.Y.Z]
**Confidence:** HIGH - proceeding with implementation
```

### When Version Mismatch Detected

```markdown
**⚠️ Version Mismatch Detected**

**DeepWiki showed:** [what DeepWiki suggested]
**Reality:** [what actually exists/errors encountered]
**Likely cause:** DeepWiki indexed v[X.X], you have v[Y.Y]

**Corrective actions taken:**
1. Fetched current API docs from [source]
2. Validated against official documentation
3. Adjusted implementation to match v[Y.Y]

**Recommendation:** Cross-reference DeepWiki's architectural insights with current API docs for [library] to ensure accuracy.
```

### When Uncertain

```markdown
**DeepWiki provided:** [architectural understanding]
**Uncertainty:** [what might have changed]
**Validation recommended:** 
- Check installed version: `pip show [package]`
- Verify API: [official docs URL]
- Test imports before full implementation
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

## Workflow Integration

### Standard Research Flow (No Mismatch)

```
User request
    ↓
DeepWiki (architecture + API)
    ↓
Implementation
    ↓
Success
```

### Enhanced Flow (Version-Aware)

```
User request
    ↓
DeepWiki (architecture understanding)
    ↓
Version check (if critical)
    ↓
Validate APIs (official docs)
    ↓
Implementation (combined knowledge)
    ↓
Success with confidence
```

### Recovery Flow (Mismatch Detected)

```
User request
    ↓
DeepWiki (gives outdated info)
    ↓
Implementation attempt
    ↓
Error (ImportError, TypeError, etc.)
    ↓
RECOGNIZE: Version mismatch
    ↓
Fetch current docs (web_fetch/perplexity)
    ↓
Correct implementation
    ↓
Success (+ report mismatch to user)
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
