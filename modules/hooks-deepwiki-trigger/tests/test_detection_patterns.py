"""Tests for LIBRARY_QUESTION_PATTERNS and GITHUB_URL_RE detection coverage.

Verifies that the expanded v1.3.0 patterns catch high-confidence triggers
(import statements, pip/uv install commands, standalone SDK/API mentions)
while NOT matching generic technology mentions.

Also verifies GITHUB_URL_RE matches issue and PR URLs.
"""

from __future__ import annotations

import sys
import types
from unittest.mock import MagicMock


def _setup_amplifier_core_mock() -> None:
    """Mock amplifier_core so the module can be imported without the real package."""
    if "amplifier_core" not in sys.modules:
        mock_module = types.ModuleType("amplifier_core")
        mock_module.HookResult = MagicMock(name="HookResult")  # type: ignore[attr-defined]
        sys.modules["amplifier_core"] = mock_module


# Must mock before importing the module under test
_setup_amplifier_core_mock()

from amplifier_module_hooks_deepwiki_trigger import (  # noqa: E402
    GITHUB_URL_RE,
    LIBRARY_QUESTION_PATTERNS,
)


def _any_pattern_matches(text: str) -> bool:
    """Check if any LIBRARY_QUESTION_PATTERNS matches the given text."""
    return any(p.search(text) for p in LIBRARY_QUESTION_PATTERNS)


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
