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

# Named patterns that need post-match validation in _has_trigger_pattern.
# They live in LIBRARY_QUESTION_PATTERNS for public API / test discoverability,
# but the hook skips them during blind iteration and uses the capturing-group
# variants (IMPORT_RE / SDK_API_RE) with exclusion filtering instead.
_IMPORT_PATTERN = re.compile(
    r"(?:^|\n)\s*(?:import|from) [\w]+",
    re.IGNORECASE,
)
_SDK_API_PATTERN = re.compile(
    r"[\w.-]+ (?:SDK|API)\b",
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
    # Import statements: "import fastapi", "from langchain import ..."
    _IMPORT_PATTERN,
    # pip/uv install: "pip install X", "uv add X"
    re.compile(
        r"(?:pip install|uv add|poetry add|pip3 install) [\w._-]+",
        re.IGNORECASE,
    ),
    # Direct SDK/API mention: "X SDK", "X API" (standalone, high-confidence)
    _SDK_API_PATTERN,
]

# Capturing-group variants for validated matching in _has_trigger_pattern
IMPORT_RE = re.compile(
    r"(?:^|\n)\s*(?:import|from) ([\w]+)",
    re.IGNORECASE,
)
SDK_API_RE = re.compile(
    r"([\w.-]+) (?:SDK|API)\b",
    re.IGNORECASE,
)

# Standard library modules excluded from import-pattern triggers
STDLIB_MODULES = frozenset(
    {
        "os",
        "sys",
        "re",
        "json",
        "collections",
        "typing",
        "pathlib",
        "dataclasses",
        "abc",
        "io",
        "math",
        "datetime",
        "time",
        "functools",
        "itertools",
        "operator",
        "copy",
        "enum",
        "contextlib",
        "logging",
        "unittest",
        "asyncio",
        "threading",
        "multiprocessing",
        "subprocess",
        "shutil",
        "tempfile",
        "glob",
        "fnmatch",
        "hashlib",
        "hmac",
        "secrets",
        "base64",
        "struct",
        "codecs",
        "csv",
        "configparser",
        "argparse",
        "textwrap",
        "string",
        "dis",
        "ast",
        "token",
        "tokenize",
        "inspect",
        "pdb",
        "traceback",
        "warnings",
        "types",
        "importlib",
        "pkgutil",
        "socket",
        "http",
        "urllib",
        "email",
        "html",
        "xml",
        "sqlite3",
        "zlib",
        "gzip",
        "zipfile",
        "tarfile",
        "pickle",
        "shelve",
        "marshal",
        "signal",
        "select",
        "ssl",
        "uuid",
        "pprint",
        "decimal",
        "fractions",
        "random",
        "statistics",
        "bisect",
        "heapq",
        "array",
        "queue",
        "weakref",
        "ctypes",
        "platform",
        "sysconfig",
        "site",
    }
)

# Generic prefixes excluded from standalone "X SDK" / "X API" triggers
GENERIC_API_PREFIXES = frozenset(
    {
        "rest",
        "web",
        "internal",
        "public",
        "private",
        "external",
        "graphql",
        "grpc",
        "soap",
        "custom",
        "our",
        "the",
        "this",
        "your",
        "my",
        "an",
        "a",
    }
)

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
        # TODO: If multi-session support is added later, replace with a dict
        # keyed by session_id and implement state eviction (e.g. LRU or TTL)
        # to prevent unbounded memory growth.
        self._state = TriggerState()

    async def on_provider_request(
        self, _event: str, data: dict[str, Any]
    ) -> HookResult:
        """Scan messages for GitHub/library patterns before each LLM call."""
        if not self.config.enabled:
            return HookResult(action="continue")

        state = self._state
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

        # Check for trigger patterns (user messages only — Fix #2)
        user_messages = [m for m in recent if m.get("role") == "user"]
        if self._has_trigger_pattern(user_messages):
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

        # Check general library/framework patterns (skip validated ones)
        for pattern in LIBRARY_QUESTION_PATTERNS:
            if pattern is _IMPORT_PATTERN or pattern is _SDK_API_PATTERN:
                continue  # Handled below with exclusion filtering
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
