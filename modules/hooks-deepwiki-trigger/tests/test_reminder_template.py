"""Tests for build_reminder() content.

Verifies that the contextual reminder function produces correct output
with all required elements (XML wrapper, web_search blocking, deepwiki
delegation, freshness verification, detected context).
"""

from __future__ import annotations

from amplifier_module_hooks_deepwiki_trigger import (
    TriggerMatch,
    build_reminder,
)


def _get_sample_reminder() -> str:
    """Get a sample reminder for testing."""
    return build_reminder(
        TriggerMatch(description="Detected: github.com/facebook/react")
    )


class TestReminderTemplateContent:
    """Verify build_reminder produces correct content."""

    def test_contains_explicit_web_search_blocking(self) -> None:
        """Template must contain explicit 'DO NOT use web_search' language."""
        template = _get_sample_reminder()
        assert "DO NOT use web_search" in template

    def test_contains_deepwiki_expert_delegation(self) -> None:
        """Template must direct to deepwiki:deepwiki-expert."""
        template = _get_sample_reminder()
        assert "deepwiki:deepwiki-expert" in template

    def test_contains_freshness_verification(self) -> None:
        """Template must mention freshness verification capability."""
        template = _get_sample_reminder()
        assert "freshness verification" in template

    def test_is_concise(self) -> None:
        """Template should be concise — 5 non-empty lines including XML tags."""
        template = _get_sample_reminder()
        # Expected: opening tag + description + 2 content lines + closing tag = 5
        lines = [line for line in template.strip().splitlines() if line.strip()]
        assert len(lines) == 5, f"Expected 5 non-empty lines, got {len(lines)}: {lines}"

    def test_has_system_reminder_xml_wrapper(self) -> None:
        """Template must be wrapped in system-reminder XML tags."""
        template = _get_sample_reminder()
        assert '<system-reminder source="hooks-deepwiki-trigger">' in template
        assert "</system-reminder>" in template

    def test_no_markdown_bold_formatting(self) -> None:
        """Reminder should not use markdown bold (**) formatting."""
        template = _get_sample_reminder()
        assert "**" not in template


class TestReminderContextualContent:
    """Verify build_reminder includes contextual detection info."""

    def test_includes_github_url_context(self) -> None:
        """Reminder for GitHub URLs should include the detected URL."""
        template = build_reminder(
            TriggerMatch(description="Detected: github.com/facebook/react")
        )
        assert "github.com/facebook/react" in template

    def test_includes_library_import_context(self) -> None:
        """Reminder for library imports should include the library name."""
        template = build_reminder(
            TriggerMatch(
                description="Library reference detected: fastapi (from import statement)"
            )
        )
        assert "fastapi" in template

    def test_includes_package_install_context(self) -> None:
        """Reminder for package installs should include the package name."""
        template = build_reminder(
            TriggerMatch(
                description="Package reference detected: express (from install command)"
            )
        )
        assert "express" in template

    def test_includes_sdk_api_context(self) -> None:
        """Reminder for SDK/API mentions should include the vendor name."""
        template = build_reminder(
            TriggerMatch(description="Library reference detected: Stripe API")
        )
        assert "Stripe API" in template
