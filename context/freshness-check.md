# Pre-Flight Freshness Protocol

> **Mandatory.** Execute this 4-step protocol BEFORE every DeepWiki query. Never skip it.
> The goal is to know how fresh DeepWiki's index is *before* trusting any answer.

---

## Step 1 — GitHub Ground Truth

Fetch the repository's latest release and last commit to the default branch.

### 1a. Detect API access method

Run `gh auth status` via bash.

- **If exit code 0** (authenticated): use `gh api` for both calls below.
- **If non-zero** (not installed, not authenticated, any error): silently fall back to `web_fetch`. This is the expected path for most users — do not warn about it.

### 1b. Fetch latest release

| Method | Command / URL |
|--------|---------------|
| `gh api` | `gh api repos/{owner}/{repo}/releases/latest` |
| `web_fetch` | `https://api.github.com/repos/{owner}/{repo}/releases/latest` |

Extract from the JSON response:
- `tag_name` — the release version tag (e.g., `v2.3.1`)
- `published_at` — the release date (ISO 8601)

**If HTTP 404:** The repository has no releases. Record "No releases found" and proceed — use commit data only for staleness.

### 1c. Fetch last commit to default branch

| Method | Command / URL |
|--------|---------------|
| `gh api` | `gh api repos/{owner}/{repo}/commits/main` |
| `web_fetch` | `https://api.github.com/repos/{owner}/{repo}/commits/main` |

Extract from the JSON response:
- `sha` — first 7 characters (short SHA)
- `commit.author.date` — the commit date (ISO 8601)
- `commit.message` — first line only (summary)

**Branch fallback:** If `main` returns 404 or 422, retry with `master`. If both fail, record "Default branch unknown".

### 1d. Record API method used

Note which path was used: `gh (authenticated)` or `web_fetch (unauthenticated)`.

### Failure handling

| Failure | Detection | Behavior |
|---------|-----------|----------|
| Rate limited | HTTP 403 + `rate limit` in body | Set risk to **UNKNOWN**, note "GitHub API rate limited", proceed |
| Repo not found | HTTP 404 on repo root | **Abort** — report "Repository not found on GitHub" to calling agent |
| Network error / timeout | `web_fetch` failure | If `gh` not yet tried, try `gh api`; otherwise set API method to `UNAVAILABLE` with reason |
| `gh` not installed | `gh auth status` non-zero | Silent fallback to `web_fetch` (expected) |

---

## Step 2 — DeepWiki Version Probe

Make one targeted `ask_question` call to determine what version DeepWiki's index covers:

> **Prompt:** "What is the latest version of this library/project covered in your documentation? What release or commit does your knowledge extend to?"

Extract whatever version identifier, release tag, or date DeepWiki reports. Record it verbatim.

### Failure handling

| Situation | Handling |
|-----------|----------|
| DeepWiki can't identify a version | Record "Unknown", fall back to commit recency comparison only |
| DeepWiki timeout | Skip the probe, compute risk from GitHub data only |
| Reported version doesn't match any known release tag | Record the reported version verbatim, note the mismatch in Gap Summary |

---

## Step 3 — Compute Staleness Risk

Compare GitHub ground truth (Step 1) against DeepWiki's reported coverage (Step 2) using this heuristic table:

| Condition | Risk Level |
|-----------|------------|
| DeepWiki version matches latest release AND last commit < 7 days ago | **LOW** |
| DeepWiki version is 1+ minor versions behind OR last commit is 7–30 days more recent than DeepWiki coverage | **MODERATE** |
| DeepWiki version is 1+ major versions behind OR last commit is 30+ days more recent than DeepWiki coverage | **HIGH** |
| GitHub data unavailable OR DeepWiki version unknown (can't compare) | **UNKNOWN** |

**Edge cases:**
- **No releases:** Base risk entirely on commit recency. < 7 days = LOW, 7–30 = MODERATE, 30+ = HIGH.
- **Monorepo:** Report repo-level freshness. Note in Gap Summary that the assessment is repo-wide and may not reflect the specific sub-project.
- **Very active repo** (multiple commits per day): If last commit is < 24 hours old but DeepWiki version is behind, lean toward MODERATE or HIGH depending on release gap.

---

## Step 4 — Proceed to Main Query

Execute the caller's original question against DeepWiki with the freshness context now established.

- **LOW risk:** Answer normally. Freshness Assessment is informational.
- **MODERATE risk:** Answer with a caveat noting potential gaps. Suggest verifying recent API changes if the query is implementation-focused.
- **HIGH risk:** Answer with a prominent warning. Recommend cross-referencing with official docs for anything implementation-critical. Use fallback strategy matrix from `version-mismatch-handling.md`.
- **UNKNOWN risk:** Answer with a note that freshness could not be verified. Recommend treating information as potentially stale.

---

## Output Format

Every response MUST begin with this Freshness Assessment section:

```
## Freshness Assessment
- **Repository:** {owner}/{repo}
- **Latest Release:** {tag} ({date}) — or "No releases found"
- **Last Commit to Main:** {short SHA} ({date}) — "{commit message summary}"
- **DeepWiki Reported Coverage:** {version/date DeepWiki claims to cover}
- **Staleness Risk:** LOW | MODERATE | HIGH | UNKNOWN
- **Gap Summary:** {human-readable description of the version/time delta}
- **API Method:** gh (authenticated) | web_fetch (unauthenticated) | UNAVAILABLE ({reason})
```

This section appears even when risk is LOW. Callers should never have to guess whether freshness was checked.

---

## Example Outputs

### LOW Risk

```
## Freshness Assessment
- **Repository:** tiangolo/fastapi
- **Latest Release:** v0.115.0 (2025-12-01)
- **Last Commit to Main:** a3f2c7b (2025-12-03) — "docs: fix typo in security section"
- **DeepWiki Reported Coverage:** v0.115.0
- **Staleness Risk:** LOW
- **Gap Summary:** DeepWiki covers the latest release. Last commit is 2 days after release (docs-only change).
- **API Method:** gh (authenticated)
```

### MODERATE Risk

```
## Freshness Assessment
- **Repository:** langchain-ai/langchain
- **Latest Release:** v0.3.5 (2025-11-20)
- **Last Commit to Main:** e9c1d44 (2025-12-05) — "feat: add streaming support for new provider"
- **DeepWiki Reported Coverage:** v0.3.3
- **Staleness Risk:** MODERATE
- **Gap Summary:** DeepWiki is 2 minor versions behind (v0.3.3 vs v0.3.5). 15 days of commits not covered. New streaming features may not be reflected.
- **API Method:** web_fetch (unauthenticated)
```

### HIGH Risk

```
## Freshness Assessment
- **Repository:** microsoft/semantic-kernel
- **Latest Release:** v2.1.0 (2025-11-28)
- **Last Commit to Main:** f7b3a12 (2025-12-04) — "refactor: new plugin architecture"
- **DeepWiki Reported Coverage:** v1.8.0
- **Staleness Risk:** HIGH
- **Gap Summary:** DeepWiki is a major version behind (v1.8.0 vs v2.1.0). Significant API changes likely. Architecture information may be outdated.
- **API Method:** gh (authenticated)
```

### UNKNOWN Risk

```
## Freshness Assessment
- **Repository:** some-org/some-repo
- **Latest Release:** v4.2.0 (2025-11-15)
- **Last Commit to Main:** c8d2e91 (2025-12-01) — "fix: resolve race condition in worker pool"
- **DeepWiki Reported Coverage:** Unknown (could not determine version)
- **Staleness Risk:** UNKNOWN
- **Gap Summary:** DeepWiki could not identify its coverage version. Freshness cannot be assessed — treat information as potentially stale.
- **API Method:** web_fetch (unauthenticated)
```
