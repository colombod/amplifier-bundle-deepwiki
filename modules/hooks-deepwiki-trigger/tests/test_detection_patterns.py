"""Tests for detection pattern coverage.

Verifies that the expanded v1.3.0 patterns catch high-confidence triggers
(import statements, pip/uv install commands, standalone SDK/API mentions)
while NOT matching generic technology mentions or stdlib imports.

Also verifies GITHUB_URL_RE matches issue and PR URLs.
"""

from __future__ import annotations

from amplifier_module_hooks_deepwiki_trigger import (
    GENERIC_API_PREFIXES,
    GITHUB_URL_RE,
    IMPORT_RE,
    LIBRARY_QUESTION_PATTERNS,
    SDK_API_RE,
    STDLIB_MODULES,
    _IMPORT_PATTERN,
    _SDK_API_PATTERN,
)


def _any_pattern_matches(text: str) -> bool:
    """Check if text would trigger detection (mirrors _has_trigger_pattern).

    Replicates the hook's validated-match logic: general patterns are checked
    directly, but _IMPORT_PATTERN and _SDK_API_PATTERN are skipped in the
    blind iteration and instead handled via IMPORT_RE / SDK_API_RE with
    exclusion filtering (stdlib modules, generic API prefixes).
    """
    # General library/framework patterns (skip validated ones)
    for pattern in LIBRARY_QUESTION_PATTERNS:
        if pattern is _IMPORT_PATTERN or pattern is _SDK_API_PATTERN:
            continue
        if pattern.search(text):
            return True
    # Import statements — exclude stdlib modules
    for match in IMPORT_RE.finditer(text):
        module_name = match.group(1).lower()
        if module_name not in STDLIB_MODULES:
            return True
    # Standalone SDK/API mentions — exclude generic prefixes
    for match in SDK_API_RE.finditer(text):
        prefix = match.group(1).lower()
        if prefix not in GENERIC_API_PREFIXES:
            return True
    return False


# ---------------------------------------------------------------------------
# New pattern: import/from statements
# ---------------------------------------------------------------------------


class TestImportPatterns:
    """Import/from statements should trigger detection (high-confidence)."""

    def test_import_fastapi(self) -> None:
        assert _any_pattern_matches("import fastapi")

    def test_from_langchain_import_chains(self) -> None:
        assert _any_pattern_matches("from langchain import chains")

    def test_import_at_line_start_in_multiline(self) -> None:
        text = "Here's the code:\nimport requests\nprint('hello')"
        assert _any_pattern_matches(text)

    def test_from_at_line_start(self) -> None:
        assert _any_pattern_matches("from django.db import models")


# ---------------------------------------------------------------------------
# New pattern: pip/uv/poetry install commands
# ---------------------------------------------------------------------------


class TestPipUvInstallPatterns:
    """Package install commands should trigger detection (high-confidence)."""

    def test_pip_install_requests(self) -> None:
        assert _any_pattern_matches("pip install requests")

    def test_pip_install_azure_ai_inference(self) -> None:
        assert _any_pattern_matches("pip install azure-ai-inference")

    def test_uv_add_httpx(self) -> None:
        assert _any_pattern_matches("uv add httpx")

    def test_uv_add_openai(self) -> None:
        assert _any_pattern_matches("uv add openai")

    def test_poetry_add_package(self) -> None:
        assert _any_pattern_matches("poetry add sqlalchemy")

    def test_pip3_install(self) -> None:
        assert _any_pattern_matches("pip3 install torch")


# ---------------------------------------------------------------------------
# New pattern: standalone SDK/API mentions
# ---------------------------------------------------------------------------


class TestSdkApiPatterns:
    """Standalone "X SDK" / "X API" mentions should trigger (high-confidence)."""

    def test_azure_ai_sdk(self) -> None:
        assert _any_pattern_matches("Azure AI SDK")

    def test_stripe_api(self) -> None:
        assert _any_pattern_matches("Stripe API")

    def test_openai_sdk(self) -> None:
        assert _any_pattern_matches("OpenAI SDK")

    def test_github_api(self) -> None:
        assert _any_pattern_matches("GitHub API")


# ---------------------------------------------------------------------------
# False positive guards: these must NOT match new patterns
# ---------------------------------------------------------------------------


class TestFalsePositiveGuards:
    """Generic technology mentions must NOT trigger detection."""

    def test_we_use_react_no_match(self) -> None:
        assert not _any_pattern_matches("we use React")

    def test_built_with_python_no_match(self) -> None:
        assert not _any_pattern_matches("built with Python")

    def test_the_react_component_no_match(self) -> None:
        assert not _any_pattern_matches("the React component")

    def test_the_database_is_slow_no_match(self) -> None:
        assert not _any_pattern_matches("the database is slow")


# ---------------------------------------------------------------------------
# GITHUB_URL_RE: verify it matches issue and PR URLs
# ---------------------------------------------------------------------------


class TestGitHubUrlRegex:
    """GITHUB_URL_RE must match issue and PR URLs (not just repo root)."""

    def test_issue_url(self) -> None:
        text = "Check github.com/facebook/react/issues/123"
        assert GITHUB_URL_RE.search(text) is not None

    def test_pr_url(self) -> None:
        text = "See github.com/microsoft/vscode/pull/45"
        assert GITHUB_URL_RE.search(text) is not None

    def test_repo_root_url(self) -> None:
        text = "Look at github.com/pallets/flask"
        assert GITHUB_URL_RE.search(text) is not None

    def test_https_url(self) -> None:
        text = "https://github.com/django/django/issues/99"
        assert GITHUB_URL_RE.search(text) is not None


# ---------------------------------------------------------------------------
# False positive guards: stdlib imports must NOT trigger (PR comment #4)
# ---------------------------------------------------------------------------


class TestStdlibImportFalsePositives:
    """Stdlib import statements must NOT trigger detection."""

    def test_import_os_no_match(self) -> None:
        assert not _any_pattern_matches("import os")

    def test_from_sys_import_argv_no_match(self) -> None:
        assert not _any_pattern_matches("from sys import argv")

    def test_import_json_no_match(self) -> None:
        assert not _any_pattern_matches("import json")

    def test_from_collections_import_defaultdict_no_match(self) -> None:
        assert not _any_pattern_matches("from collections import defaultdict")


# ---------------------------------------------------------------------------
# False positive guards: generic API/SDK terms must NOT trigger (PR comment #5)
# ---------------------------------------------------------------------------


class TestGenericApiSdkFalsePositives:
    """Generic API/SDK terms without a specific vendor must NOT trigger."""

    def test_rest_api_no_match(self) -> None:
        assert not _any_pattern_matches("REST API")

    def test_our_internal_api_no_match(self) -> None:
        assert not _any_pattern_matches("our internal API")

    def test_the_web_api_no_match(self) -> None:
        assert not _any_pattern_matches("the web API")

    def test_graphql_api_no_match(self) -> None:
        assert not _any_pattern_matches("GraphQL API")


# ---------------------------------------------------------------------------
# False positive guards: non-library extend/configure (PR comment #3)
# ---------------------------------------------------------------------------


class TestNonLibraryVerbFalsePositives:
    """Non-library uses of extend/configure/customize must NOT trigger."""

    def test_extend_the_deadline_no_match(self) -> None:
        assert not _any_pattern_matches("extend the deadline")

    def test_configure_the_settings_no_match(self) -> None:
        assert not _any_pattern_matches("configure the settings")

    def test_customize_the_colors_no_match(self) -> None:
        assert not _any_pattern_matches("customize the colors")
