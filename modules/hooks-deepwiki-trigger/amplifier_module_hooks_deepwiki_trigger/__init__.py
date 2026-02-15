"""DeepWiki Trigger Hook Module

Detects GitHub URLs and library/framework questions in user messages
and injects reminders to delegate to deepwiki:deepwiki-expert instead
of using web_search.

Detection Patterns:
- GitHub URLs: github.com/owner/repo in any format
- Library questions: "how does X work", "X architecture", "X internals"
- SDK/API integration: "implement with X", "integrate X", "using X SDK"

Anti-Spam:
- Cooldown period after injection (configurable, default: 3 turns)
- Suppressed when deepwiki-expert was recently delegated to
- Only fires on provider:request (before LLM calls)

Config options:
    enabled: bool (default: True)
    cooldown_turns: int (default: 3) - Turns to wait before re-injecting
    scan_depth: int (default: 3) - Number of recent messages to scan
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from collections.abc import Callable
from typing import Any

from amplifier_core import HookResult

# GitHub URL patterns - matches various formats
GITHUB_URL_RE = re.compile(
    r"(?:https?://)?(?:www\.)?github\.com/[\w.-]+/[\w.-]+",
    re.IGNORECASE,
)

# Library/framework question patterns
LIBRARY_QUESTION_PATTERNS: list[re.Pattern[str]] = [
    # "How does X work" / "how X works"
    re.compile(r"how does [\w./-]+ work", re.IGNORECASE),
    re.compile(r"how [\w./-]+ works", re.IGNORECASE),
    # Architecture / internals questions
    re.compile(
        r"[\w./-]+ (?:architecture|internals|source code|codebase)",
        re.IGNORECASE,
    ),
    # SDK/API integration: "implement with X SDK", "integrate X", "using X API"
    re.compile(
        r"(?:implement|integrat|using|connect)\w* (?:with |to )?(?:the )?[\w.-]+ (?:SDK|API|library|package|framework)",
        re.IGNORECASE,
    ),
    # Extend/customize patterns
    re.compile(
        r"(?:extend|customize|configure) [\w.-]+",
        re.IGNORECASE,
    ),
    # Import statements: "import fastapi", "from langchain import ..."
    re.compile(
        r"(?:^|\n)\s*(?:import|from) [\w]+",
        re.IGNORECASE,
    ),
    # pip/uv install: "pip install X", "uv add X"
    re.compile(
        r"(?:pip install|uv add|poetry add|pip3 install) [\w._-]+",
        re.IGNORECASE,
    ),
    # Direct SDK/API mention: "X SDK", "X API" (standalone, high-confidence)
    re.compile(
        r"[\w.-]+ (?:SDK|API)\b",
        re.IGNORECASE,
    ),
]

# Signals that deepwiki was already used or is about to be used
DEEPWIKI_ALREADY_USED_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"deepwiki", re.IGNORECASE),
    re.compile(r"mcp_deepwiki", re.IGNORECASE),
    re.compile(r"deepwiki-expert", re.IGNORECASE),
]

REMINDER_TEMPLATE = """<system-reminder source="hooks-deepwiki-trigger">
GitHub repository or library detected in conversation.
DO NOT use web_search — delegate to deepwiki:deepwiki-expert for
source-level codebase analysis with freshness verification.
</system-reminder>"""


@dataclass
class TriggerConfig:
    """Configuration for the deepwiki trigger hook."""

    enabled: bool = True
    cooldown_turns: int = 3
    scan_depth: int = 3


@dataclass
class TriggerState:
    """Tracks injection state per session."""

    turns_since_injection: int = 999  # Start high so first match triggers
    turns_since_deepwiki_use: int = 999
    total_injections: int = 0
    provider_request_count: int = 0


class DeepWikiTriggerHook:
    """Hook that detects GitHub/library patterns and injects deepwiki reminders."""

    def __init__(self, config: TriggerConfig) -> None:
        self.config = config
        self._states: dict[str, TriggerState] = {}

    def _get_state(self, session_id: str) -> TriggerState:
        if session_id not in self._states:
            self._states[session_id] = TriggerState()
        return self._states[session_id]

    async def on_provider_request(
        self, _event: str, data: dict[str, Any]
    ) -> HookResult:
        """Scan messages for GitHub/library patterns before each LLM call."""
        if not self.config.enabled:
            return HookResult(action="continue")

        session_id = data.get("session_id", "default")
        state = self._get_state(session_id)
        state.provider_request_count += 1

        # Increment turn counters
        state.turns_since_injection += 1
        state.turns_since_deepwiki_use += 1

        # Cooldown check — don't spam
        if state.turns_since_injection < self.config.cooldown_turns:
            return HookResult(action="continue")

        messages = data.get("messages", [])
        if not messages:
            return HookResult(action="continue")

        # Scan recent messages
        recent = messages[-self.config.scan_depth :]

        # Check if deepwiki was already mentioned/used recently
        if self._deepwiki_recently_used(recent):
            state.turns_since_deepwiki_use = 0
            return HookResult(action="continue")

        # Skip if deepwiki was used very recently (within cooldown)
        if state.turns_since_deepwiki_use < self.config.cooldown_turns:
            return HookResult(action="continue")

        # Check for trigger patterns
        if self._has_trigger_pattern(recent):
            state.turns_since_injection = 0
            state.total_injections += 1
            return HookResult(
                action="inject_context",
                context_injection=REMINDER_TEMPLATE,
                context_injection_role="user",
                ephemeral=True,
                suppress_output=True,
            )

        return HookResult(action="continue")

    def _extract_text(self, messages: list[dict[str, Any]]) -> str:
        """Extract text content from messages."""
        parts: list[str] = []
        for msg in messages:
            content = msg.get("content", "")
            if isinstance(content, str):
                parts.append(content)
            elif isinstance(content, list):
                # Handle structured content blocks
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "text":
                        parts.append(block.get("text", ""))
        return "\n".join(parts)

    def _has_trigger_pattern(self, messages: list[dict[str, Any]]) -> bool:
        """Check if recent messages contain GitHub URLs or library questions."""
        text = self._extract_text(messages)

        # Check for GitHub URLs
        if GITHUB_URL_RE.search(text):
            return True

        # Check for library/framework question patterns
        for pattern in LIBRARY_QUESTION_PATTERNS:
            if pattern.search(text):
                return True

        return False

    def _deepwiki_recently_used(self, messages: list[dict[str, Any]]) -> bool:
        """Check if deepwiki was already mentioned or delegated to recently."""
        text = self._extract_text(messages)
        return any(p.search(text) for p in DEEPWIKI_ALREADY_USED_PATTERNS)


async def mount(
    coordinator: Any, config: dict[str, Any] | None = None
) -> Callable[[], None] | None:
    """Mount the deepwiki trigger hook module.

    Config options:
        enabled: bool (default: True) - Enable/disable the trigger
        cooldown_turns: int (default: 3) - LLM calls between re-injections
        scan_depth: int (default: 3) - Recent messages to scan for patterns

    Returns:
        Cleanup callable that unregisters the hook handler.
    """
    config = config or {}

    trigger_config = TriggerConfig(
        enabled=config.get("enabled", True),
        cooldown_turns=config.get("cooldown_turns", 3),
        scan_depth=config.get("scan_depth", 3),
    )

    hook = DeepWikiTriggerHook(trigger_config)

    # Register on provider:request — fires before every LLM call
    unregister = coordinator.hooks.register(
        "provider:request",
        hook.on_provider_request,
        priority=30,  # After skills visibility (20), before most other hooks
        name="deepwiki-trigger",
    )

    def cleanup() -> None:
        """Unregister the deepwiki trigger hook."""
        unregister()

    return cleanup
