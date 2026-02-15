"""Tests for REMINDER_TEMPLATE content.

These tests parse the source file directly to avoid requiring amplifier_core
to be installed, since we're only testing a string constant.
"""

from __future__ import annotations

import ast
from pathlib import Path

MODULE_PATH = (
    Path(__file__).resolve().parent.parent
    / "amplifier_module_hooks_deepwiki_trigger"
    / "__init__.py"
)


def _extract_reminder_template() -> str:
    """Extract REMINDER_TEMPLATE value from the module source via AST parsing."""
    source = MODULE_PATH.read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id == "REMINDER_TEMPLATE"
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
        ):
            return node.value.value
    raise AssertionError("REMINDER_TEMPLATE not found in module source")


class TestReminderTemplateContent:
    """Verify REMINDER_TEMPLATE has the correct content after the v1.3.0 update."""

    def test_contains_explicit_web_search_blocking(self) -> None:
        """Template must contain explicit 'DO NOT use web_search' language."""
        template = _extract_reminder_template()
        assert "DO NOT use web_search" in template

    def test_contains_deepwiki_expert_delegation(self) -> None:
        """Template must direct to deepwiki:deepwiki-expert."""
        template = _extract_reminder_template()
        assert "deepwiki:deepwiki-expert" in template

    def test_contains_freshness_verification(self) -> None:
        """Template must mention freshness verification capability."""
        template = _extract_reminder_template()
        assert "freshness verification" in template

    def test_is_concise(self) -> None:
        """Template should be shorter — 4 content lines inside the XML tags."""
        template = _extract_reminder_template()
        # Strip the outer XML tags and count non-empty content lines
        lines = [line for line in template.strip().splitlines() if line.strip()]
        # Expected: opening tag + 3 content lines + closing tag = 5 non-empty lines
        assert len(lines) == 5, f"Expected 5 non-empty lines, got {len(lines)}: {lines}"

    def test_has_system_reminder_xml_wrapper(self) -> None:
        """Template must be wrapped in system-reminder XML tags."""
        template = _extract_reminder_template()
        assert '<system-reminder source="hooks-deepwiki-trigger">' in template
        assert "</system-reminder>" in template

    def test_no_markdown_bold_formatting(self) -> None:
        """New template should not use markdown bold (**) formatting."""
        template = _extract_reminder_template()
        assert "**" not in template
