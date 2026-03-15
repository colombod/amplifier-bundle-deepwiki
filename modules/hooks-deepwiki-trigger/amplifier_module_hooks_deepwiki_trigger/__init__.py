"""DeepWiki Trigger Hook Module

Detects GitHub URLs and library/framework questions in user messages
and injects reminders to delegate to deepwiki:deepwiki-expert instead
of using web_search.

Detection Patterns:
- GitHub URLs: github.com/owner/repo in any format
- Library questions: "how does X work", "X architecture", "X internals"
- SDK/API integration: "implement with X", "integrate X", "using X SDK"
- Package install commands: pip, npm, yarn, pnpm, cargo, go get, gem, dotnet
- Import statements: Python, JavaScript/TypeScript, Rust, Go

Anti-Spam:
- Cooldown period after injection (configurable, default: 3 turns)
- Suppressed when deepwiki-expert was recently delegated to
- Maximum injection cap per session (configurable, default: 15)
- Only fires on provider:request (before LLM calls)

Config options:
    enabled: bool (default: True)
    cooldown_turns: int (default: 3) - Turns to wait before re-injecting
    scan_depth: int (default: 3) - Number of recent messages to scan
    max_injections: int (default: 15) - Max injections per session
    max_sessions: int (default: 64) - Max concurrent sessions before LRU eviction
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from collections import OrderedDict
from collections.abc import Callable
from typing import Any

from amplifier_core import HookResult

# ---------------------------------------------------------------------------
# Trigger match result
# ---------------------------------------------------------------------------


@dataclass
class TriggerMatch:
    """Describes what triggered detection."""

    description: str  # Human-readable, e.g. "Detected: github.com/facebook/react"


def build_reminder(match: TriggerMatch) -> str:
    """Build a contextual reminder based on what was detected."""
    return (
        '<system-reminder source="hooks-deepwiki-trigger">\n'
        f"{match.description}\n"
        "DO NOT use web_search \u2014 delegate to deepwiki:deepwiki-expert for\n"
        "source-level codebase analysis with freshness verification.\n"
        "</system-reminder>"
    )


# ---------------------------------------------------------------------------
# GitHub platform paths — owner-position segments that are NOT real user orgs
# ---------------------------------------------------------------------------

GITHUB_PLATFORM_PATHS: frozenset[str] = frozenset(
    {
        "settings",
        "features",
        "marketplace",
        "explore",
        "topics",
        "trending",
        "collections",
        "sponsors",
        "orgs",
        "login",
        "signup",
        "new",
        "notifications",
        "pulls",
        "issues",
        "codespaces",
    }
)

# Validates a single owner or repo path segment (alphanumeric, dash, dot, underscore)
_REPO_SEGMENT_RE = re.compile(r"^[a-zA-Z0-9_.-]+$")


def _is_valid_repo_format(text: str) -> tuple[bool, str | None]:
    """Validate and normalise a GitHub owner/repo reference.

    Accepts bare ``owner/repo`` strings, GitHub URLs (with or without scheme /
    www), and owner/repo with a ``.git`` suffix.  Rejects GitHub platform paths
    (e.g. ``settings``, ``explore``) used in the owner position.

    Returns:
        ``(True, "owner/repo")`` for valid inputs.
        ``(False, None)`` for invalid / unrecognised inputs.
    """
    # Step 1: strip whitespace; empty → invalid
    text = text.strip()
    if not text:
        return (False, None)

    # Step 2: strip scheme prefix
    if text.startswith("https://"):
        text = text[len("https://") :]
    elif text.startswith("http://"):
        text = text[len("http://") :]

    # Step 3: strip www. prefix
    if text.startswith("www."):
        text = text[len("www.") :]

    # Step 4: handle github.com host
    is_github_url = False
    if text.startswith("github.com/"):
        text = text[len("github.com/") :]
        is_github_url = True
    elif text == "github.com":
        # bare host with no path
        return (False, None)

    # Step 5: strip URL fragment and query string (applies to all forms)
    if "#" in text:
        text = text[: text.index("#")]
    if "?" in text:
        text = text[: text.index("?")]

    # Step 6: strip trailing slash — only for the extracted GitHub URL path.
    # A bare "owner/repo/" is treated as having three path segments (the third
    # being empty) and is therefore rejected as-is in the split check below.
    if is_github_url:
        text = text.rstrip("/")

    # Step 7: split and require exactly two segments
    parts = text.split("/")
    if len(parts) != 2:
        return (False, None)

    owner, repo = parts

    # Step 8: strip .git suffix from repo
    if repo.endswith(".git"):
        repo = repo[:-4]

    # Step 9: both segments must be non-empty
    if not owner or not repo:
        return (False, None)

    # Step 10: both segments must contain only valid characters
    if not _REPO_SEGMENT_RE.match(owner) or not _REPO_SEGMENT_RE.match(repo):
        return (False, None)

    # Step 11: owner must not be a GitHub platform path
    if owner.lower() in GITHUB_PLATFORM_PATHS:
        return (False, None)

    return (True, f"{owner}/{repo}")


# ---------------------------------------------------------------------------
# GitHub URL patterns - matches various formats
# ---------------------------------------------------------------------------

GITHUB_URL_RE = re.compile(
    r"(?:https?://)?(?:www\.)?github\.com/[\w.-]+/[\w.-]+",
    re.IGNORECASE,
)

# ---------------------------------------------------------------------------
# Sentinel patterns for LIBRARY_QUESTION_PATTERNS discoverability.
# The hook skips these during blind iteration and uses the capturing-group
# variants with exclusion filtering instead.
# ---------------------------------------------------------------------------

_IMPORT_PATTERN = re.compile(
    r"(?:^|\n)\s*(?:import|from) [\w]+",
    re.IGNORECASE,
)
_SDK_API_PATTERN = re.compile(
    r"[\w.-]+ (?:SDK|API)\b",
    re.IGNORECASE,
)
_JS_IMPORT_PATTERN = re.compile(
    r"""(?:import\s+.*?\s+from\s+['"][^'"]+['"]|require\s*\(\s*['"][^'"]+['"]\s*\))""",
)
_RUST_USE_PATTERN = re.compile(
    r"(?:^|\n)\s*use\s+[a-z_]\w*::",
)
_GO_IMPORT_PATTERN = re.compile(
    r'import\s+"[^"]+"',
)
_PACKAGE_INSTALL_PATTERN = re.compile(
    r"(?:pip install|pip3 install|uv add|poetry add|npm install|yarn add|pnpm add|bun add|cargo add|go get|gem install|dotnet add package) [\w._/@:-]+",
    re.IGNORECASE,
)

# Set of sentinel patterns skipped during blind iteration
_VALIDATED_PATTERNS: frozenset[re.Pattern[str]] = frozenset(
    {
        _IMPORT_PATTERN,
        _SDK_API_PATTERN,
        _JS_IMPORT_PATTERN,
        _RUST_USE_PATTERN,
        _GO_IMPORT_PATTERN,
        _PACKAGE_INSTALL_PATTERN,
    }
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
    # Python import statements: "import fastapi", "from langchain import ..."
    _IMPORT_PATTERN,
    # JS/TS import statements: import ... from 'pkg', require('pkg')
    _JS_IMPORT_PATTERN,
    # Rust use statements: use serde::Deserialize
    _RUST_USE_PATTERN,
    # Go import statements: import "github.com/..."
    _GO_IMPORT_PATTERN,
    # Package install commands (all languages)
    _PACKAGE_INSTALL_PATTERN,
    # Direct SDK/API mention: "X SDK", "X API" (standalone, high-confidence)
    _SDK_API_PATTERN,
]

# ---------------------------------------------------------------------------
# Capturing-group variants for validated matching in _has_trigger_pattern
# ---------------------------------------------------------------------------

# Python imports — (?=[.\s]|$) forces full-word match (prevents backtracking
# into a shorter capture; allows dotted paths like django.db), then negative
# lookahead excludes JS-style "import X from 'Y'" syntax.
IMPORT_RE = re.compile(
    r"(?:^|\n)\s*(?:import|from) ([\w]+)(?=[.\s]|$)(?!\s+from\s)",
    re.IGNORECASE,
)
# SDK/API mentions
SDK_API_RE = re.compile(
    r"([\w.-]+) (?:SDK|API)\b",
    re.IGNORECASE,
)
# Package install commands (captures package name)
PACKAGE_INSTALL_RE = re.compile(
    r"(?:pip install|pip3 install|uv add|poetry add|npm install|yarn add|pnpm add|bun add|cargo add|go get|gem install|dotnet add package) ([\w._/@:-]+)",
    re.IGNORECASE,
)
# JS/TS: import ... from 'package' or require('package')
# Excludes relative imports starting with . or /
JS_IMPORT_RE = re.compile(
    r"""(?:import\s+.*?\s+from\s+['"]([^'"./][^'"]*?)['"]|require\s*\(\s*['"]([^'"./][^'"]*?)['"]\s*\))""",
)
# Rust: use crate_name:: (captures top-level crate name)
RUST_USE_RE = re.compile(
    r"(?:^|\n)\s*use\s+([a-z_]\w*)::",
)
# Go: import "package" (single imports; grouped imports partially handled)
GO_IMPORT_RE = re.compile(
    r'import\s+"([^"]+)"',
)

# ---------------------------------------------------------------------------
# Exclusion sets
# ---------------------------------------------------------------------------

# Python standard library modules
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

# Node.js built-in modules
JS_BUILTIN_MODULES = frozenset(
    {
        "fs",
        "path",
        "os",
        "http",
        "https",
        "url",
        "util",
        "stream",
        "events",
        "crypto",
        "buffer",
        "child_process",
        "cluster",
        "net",
        "dns",
        "tls",
        "zlib",
        "readline",
        "assert",
        "querystring",
        "string_decoder",
        "timers",
        "vm",
        "worker_threads",
        "perf_hooks",
        "console",
        "process",
        "module",
    }
)

# Rust standard/built-in crate names
RUST_STD_CRATES = frozenset(
    {
        "std",
        "core",
        "alloc",
        "self",
        "super",
        "crate",
    }
)

# Go standard library packages (common ones)
GO_STD_PACKAGES = frozenset(
    {
        "fmt",
        "os",
        "io",
        "log",
        "net",
        "sync",
        "time",
        "math",
        "sort",
        "strings",
        "bytes",
        "errors",
        "context",
        "regexp",
        "strconv",
        "encoding",
        "testing",
        "reflect",
        "runtime",
        "flag",
        "path",
        "bufio",
        "crypto",
        "hash",
        "unicode",
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
        "backend",
        "client",
        "server",
        "frontend",
        "local",
        "remote",
        "new",
    }
)

# Signals that deepwiki was already used or is about to be used
DEEPWIKI_ALREADY_USED_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"deepwiki", re.IGNORECASE),
    re.compile(r"mcp_deepwiki", re.IGNORECASE),
    re.compile(r"deepwiki-expert", re.IGNORECASE),
]


@dataclass
class TriggerConfig:
    """Configuration for the deepwiki trigger hook."""

    enabled: bool = True
    cooldown_turns: int = 3
    scan_depth: int = 3
    max_injections: int = 15
    max_sessions: int = 64


@dataclass
class TriggerState:
    """Tracks injection state per session."""

    turns_since_injection: int = 999  # Start high so first match triggers
    turns_since_deepwiki_use: int = 999
    total_injections: int = 0


class DeepWikiTriggerHook:
    """Hook that detects GitHub/library patterns and injects deepwiki reminders."""

    def __init__(self, config: TriggerConfig) -> None:
        self.config = config
        self._state: OrderedDict[str, TriggerState] = OrderedDict()

    def _get_or_create_state(self, session_id: str) -> TriggerState:
        """Get or create per-session state with LRU eviction."""
        if session_id in self._state:
            self._state.move_to_end(session_id)
            return self._state[session_id]
        state = TriggerState()
        self._state[session_id] = state
        if len(self._state) > self.config.max_sessions:
            self._state.popitem(last=False)
        return state

    async def __call__(self, event: str, data: dict[str, Any]) -> HookResult:
        """HookHandler protocol entry point."""
        return await self.on_provider_request(event, data)

    async def on_provider_request(
        self, _event: str, data: dict[str, Any]
    ) -> HookResult:
        """Scan messages for GitHub/library patterns before each LLM call."""
        if not self.config.enabled:
            return HookResult(action="continue")

        session_id = data.get("session_id", "__default__")
        state = self._get_or_create_state(session_id)

        # Increment turn counters
        state.turns_since_injection += 1
        state.turns_since_deepwiki_use += 1

        # Injection cap — stop after max_injections for the session
        if state.total_injections >= self.config.max_injections:
            return HookResult(action="continue")

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
        match = self._has_trigger_pattern(user_messages)
        if match is not None:
            state.turns_since_injection = 0
            state.total_injections += 1
            return HookResult(
                action="inject_context",
                context_injection=build_reminder(match),
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

    def _has_trigger_pattern(
        self, messages: list[dict[str, Any]]
    ) -> TriggerMatch | None:
        """Check if recent messages contain GitHub URLs or library questions.

        Returns a TriggerMatch describing what was detected, or None.
        """
        text = self._extract_text(messages)

        # Check for GitHub URLs (with format validation)
        m = GITHUB_URL_RE.search(text)
        if m:
            valid, _repo = _is_valid_repo_format(m.group(0))
            if valid:
                return TriggerMatch(description=f"Detected: {m.group(0)}")

        # Check general library/framework patterns (skip validated ones)
        for pattern in LIBRARY_QUESTION_PATTERNS:
            if pattern in _VALIDATED_PATTERNS:
                continue  # Handled below with exclusion filtering
            m = pattern.search(text)
            if m:
                return TriggerMatch(
                    description=f"Library reference detected: {m.group(0)}"
                )

        # Package install commands
        m = PACKAGE_INSTALL_RE.search(text)
        if m:
            return TriggerMatch(
                description=f"Package reference detected: {m.group(1)} (from install command)"
            )

        # Python import statements — exclude stdlib modules
        for m in IMPORT_RE.finditer(text):
            module_name = m.group(1).lower()
            if module_name not in STDLIB_MODULES:
                return TriggerMatch(
                    description=f"Library reference detected: {m.group(1)} (from import statement)"
                )

        # JS/TS import/require — exclude Node.js built-ins
        for m in JS_IMPORT_RE.finditer(text):
            pkg_raw = m.group(1) or m.group(2)
            pkg = pkg_raw.split("/")[0]
            if pkg.lower() not in JS_BUILTIN_MODULES:
                return TriggerMatch(
                    description=f"Library reference detected: {pkg_raw} (from import statement)"
                )

        # Rust use statements — exclude std crates
        for m in RUST_USE_RE.finditer(text):
            crate_name = m.group(1)
            if crate_name.lower() not in RUST_STD_CRATES:
                return TriggerMatch(
                    description=f"Library reference detected: {crate_name} (from use statement)"
                )

        # Go import statements — exclude stdlib packages
        for m in GO_IMPORT_RE.finditer(text):
            pkg = m.group(1)
            pkg_base = pkg.split("/")[0]
            if pkg_base.lower() not in GO_STD_PACKAGES:
                return TriggerMatch(
                    description=f"Library reference detected: {pkg} (from import statement)"
                )

        # Standalone SDK/API mentions — exclude generic prefixes
        for m in SDK_API_RE.finditer(text):
            prefix = m.group(1).lower()
            if prefix not in GENERIC_API_PREFIXES:
                return TriggerMatch(
                    description=f"Library reference detected: {m.group(0)}"
                )

        return None

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
        max_injections: int (default: 15) - Max injections per session
        max_sessions: int (default: 64) - Max concurrent sessions before LRU eviction

    Returns:
        Cleanup callable that unregisters the hook handler.
    """
    config = config or {}

    trigger_config = TriggerConfig(
        enabled=config.get("enabled", True),
        cooldown_turns=config.get("cooldown_turns", 3),
        scan_depth=config.get("scan_depth", 3),
        max_injections=config.get("max_injections", 15),
        max_sessions=config.get("max_sessions", 64),
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
