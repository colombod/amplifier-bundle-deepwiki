"""Tests for PR review fixes #1, #2, #3, #4, #5, #8.

Each test class targets a specific fix from the PR review and should FAIL
before the corresponding fix is applied.
"""

from __future__ import annotations

import asyncio
from typing import Any

from amplifier_module_hooks_deepwiki_trigger import (
    DeepWikiTriggerHook,
    TriggerConfig,
)


def _run(coro):  # noqa: ANN001, ANN202
    """Helper to run async coroutines in sync tests."""
    return asyncio.run(coro)


def _make_data(messages: list[dict[str, Any]]) -> dict[str, Any]:
    """Build a provider:request data dict with only the contract fields."""
    return {
        "provider": "test-provider",
        "model": "test-model",
        "messages": messages,
    }


# ---------------------------------------------------------------------------
# Fix #1: session_id not in provider:request — use single state, not _states dict
# ---------------------------------------------------------------------------


class TestFix1SingleState:
    """Hook should use a single TriggerState, not a _states dict."""

    def test_no_states_dict(self) -> None:
        """Hook should NOT have a _states dict attribute."""
        hook = DeepWikiTriggerHook(TriggerConfig())
        assert not hasattr(hook, "_states"), (
            "Hook should not have _states dict — use single _state instead"
        )

    def test_has_single_state(self) -> None:
        """Hook should have a single _state attribute."""
        hook = DeepWikiTriggerHook(TriggerConfig())
        assert hasattr(hook, "_state"), "Hook should have a single _state attribute"

    def test_no_get_state_method(self) -> None:
        """Hook should NOT have _get_state method (no session lookup needed)."""
        hook = DeepWikiTriggerHook(TriggerConfig())
        assert not hasattr(hook, "_get_state"), (
            "Hook should not have _get_state — single state needs no lookup"
        )

    def test_works_without_session_id_in_data(self) -> None:
        """Hook must work when data has no session_id (the normal case)."""
        hook = DeepWikiTriggerHook(TriggerConfig())
        data = _make_data(
            [
                {"role": "user", "content": "Look at github.com/facebook/react"},
            ]
        )
        # Should not raise, and should detect the pattern
        result = _run(hook.on_provider_request("provider:request", data))
        assert result.action == "inject_context"


# ---------------------------------------------------------------------------
# Fix #2: _extract_text includes assistant messages — causes false positives
# ---------------------------------------------------------------------------


class TestFix2UserMessagesOnly:
    """Trigger patterns should only match on user-role messages."""

    def test_assistant_github_url_not_detected(self) -> None:
        """Assistant mentioning github.com should NOT trigger injection."""
        hook = DeepWikiTriggerHook(TriggerConfig())
        data = _make_data(
            [
                {"role": "user", "content": "Help me with my project"},
                {
                    "role": "assistant",
                    "content": "Check github.com/facebook/react for examples",
                },
            ]
        )
        result = _run(hook.on_provider_request("provider:request", data))
        assert result.action == "continue", (
            "Assistant-only GitHub URL should not trigger injection"
        )

    def test_assistant_import_not_detected(self) -> None:
        """Assistant showing code with 'import fastapi' should NOT trigger."""
        hook = DeepWikiTriggerHook(TriggerConfig())
        data = _make_data(
            [
                {"role": "user", "content": "How do I write a web server?"},
                {
                    "role": "assistant",
                    "content": "Here's an example:\nimport fastapi\nfrom fastapi import FastAPI",
                },
            ]
        )
        result = _run(hook.on_provider_request("provider:request", data))
        assert result.action == "continue", (
            "Assistant-only import statement should not trigger injection"
        )

    def test_user_github_url_still_detected(self) -> None:
        """User mentioning github.com should still trigger injection."""
        hook = DeepWikiTriggerHook(TriggerConfig())
        data = _make_data(
            [
                {"role": "user", "content": "Look at github.com/pallets/flask"},
            ]
        )
        result = _run(hook.on_provider_request("provider:request", data))
        assert result.action == "inject_context"

    def test_user_import_still_detected(self) -> None:
        """User's code with import should still trigger (if not stdlib)."""
        hook = DeepWikiTriggerHook(TriggerConfig())
        data = _make_data(
            [
                {"role": "user", "content": "import fastapi\napp = FastAPI()"},
            ]
        )
        result = _run(hook.on_provider_request("provider:request", data))
        assert result.action == "inject_context"


# ---------------------------------------------------------------------------
# Fix #3: extend/customize/configure pattern too broad
# ---------------------------------------------------------------------------


class TestFix3RemoveBroadPattern:
    """The extend/customize/configure pattern should be removed entirely."""

    def test_configure_settings_no_match(self) -> None:
        """'configure the settings' must NOT trigger detection."""
        hook = DeepWikiTriggerHook(TriggerConfig())
        data = _make_data(
            [
                {"role": "user", "content": "configure the settings"},
            ]
        )
        result = _run(hook.on_provider_request("provider:request", data))
        assert result.action == "continue", (
            "'configure the settings' should not trigger — too generic"
        )

    def test_extend_the_deadline_no_match(self) -> None:
        """'extend the deadline' must NOT trigger detection."""
        hook = DeepWikiTriggerHook(TriggerConfig())
        data = _make_data(
            [
                {"role": "user", "content": "extend the deadline"},
            ]
        )
        result = _run(hook.on_provider_request("provider:request", data))
        assert result.action == "continue", (
            "'extend the deadline' should not trigger — too generic"
        )

    def test_customize_theme_no_match(self) -> None:
        """'customize the theme' must NOT trigger detection."""
        hook = DeepWikiTriggerHook(TriggerConfig())
        data = _make_data(
            [
                {"role": "user", "content": "customize the theme"},
            ]
        )
        result = _run(hook.on_provider_request("provider:request", data))
        assert result.action == "continue", (
            "'customize the theme' should not trigger — too generic"
        )


# ---------------------------------------------------------------------------
# Fix #4: import pattern matches stdlib modules
# ---------------------------------------------------------------------------


class TestFix4StdlibExclusion:
    """Import of stdlib modules should NOT trigger detection."""

    def test_import_os_no_match(self) -> None:
        hook = DeepWikiTriggerHook(TriggerConfig())
        data = _make_data(
            [
                {"role": "user", "content": "import os"},
            ]
        )
        result = _run(hook.on_provider_request("provider:request", data))
        assert result.action == "continue", "'import os' (stdlib) should not trigger"

    def test_import_sys_no_match(self) -> None:
        hook = DeepWikiTriggerHook(TriggerConfig())
        data = _make_data(
            [
                {"role": "user", "content": "import sys"},
            ]
        )
        result = _run(hook.on_provider_request("provider:request", data))
        assert result.action == "continue", "'import sys' (stdlib) should not trigger"

    def test_import_json_no_match(self) -> None:
        hook = DeepWikiTriggerHook(TriggerConfig())
        data = _make_data(
            [
                {"role": "user", "content": "import json"},
            ]
        )
        result = _run(hook.on_provider_request("provider:request", data))
        assert result.action == "continue", "'import json' (stdlib) should not trigger"

    def test_import_pathlib_no_match(self) -> None:
        hook = DeepWikiTriggerHook(TriggerConfig())
        data = _make_data(
            [
                {"role": "user", "content": "import pathlib"},
            ]
        )
        result = _run(hook.on_provider_request("provider:request", data))
        assert result.action == "continue", (
            "'import pathlib' (stdlib) should not trigger"
        )

    def test_from_collections_no_match(self) -> None:
        hook = DeepWikiTriggerHook(TriggerConfig())
        data = _make_data(
            [
                {"role": "user", "content": "from collections import defaultdict"},
            ]
        )
        result = _run(hook.on_provider_request("provider:request", data))
        assert result.action == "continue", (
            "'from collections' (stdlib) should not trigger"
        )

    def test_import_asyncio_no_match(self) -> None:
        hook = DeepWikiTriggerHook(TriggerConfig())
        data = _make_data(
            [
                {"role": "user", "content": "import asyncio"},
            ]
        )
        result = _run(hook.on_provider_request("provider:request", data))
        assert result.action == "continue", (
            "'import asyncio' (stdlib) should not trigger"
        )

    def test_import_fastapi_still_matches(self) -> None:
        """Third-party imports should still trigger."""
        hook = DeepWikiTriggerHook(TriggerConfig())
        data = _make_data(
            [
                {"role": "user", "content": "import fastapi"},
            ]
        )
        result = _run(hook.on_provider_request("provider:request", data))
        assert result.action == "inject_context", (
            "'import fastapi' (third-party) should still trigger"
        )

    def test_from_langchain_still_matches(self) -> None:
        """Third-party from-imports should still trigger."""
        hook = DeepWikiTriggerHook(TriggerConfig())
        data = _make_data(
            [
                {"role": "user", "content": "from langchain import chains"},
            ]
        )
        result = _run(hook.on_provider_request("provider:request", data))
        assert result.action == "inject_context", (
            "'from langchain' (third-party) should still trigger"
        )


# ---------------------------------------------------------------------------
# Fix #5: SDK/API standalone pattern matches generic terms
# ---------------------------------------------------------------------------


class TestFix5GenericApiExclusion:
    """Generic API/SDK prefixes like 'REST API', 'web API' should NOT trigger."""

    def test_rest_api_no_match(self) -> None:
        hook = DeepWikiTriggerHook(TriggerConfig())
        data = _make_data(
            [
                {"role": "user", "content": "Build a REST API"},
            ]
        )
        result = _run(hook.on_provider_request("provider:request", data))
        assert result.action == "continue", "'REST API' (generic) should not trigger"

    def test_web_api_no_match(self) -> None:
        hook = DeepWikiTriggerHook(TriggerConfig())
        data = _make_data(
            [
                {"role": "user", "content": "the web API is slow"},
            ]
        )
        result = _run(hook.on_provider_request("provider:request", data))
        assert result.action == "continue", "'web API' (generic) should not trigger"

    def test_internal_api_no_match(self) -> None:
        hook = DeepWikiTriggerHook(TriggerConfig())
        data = _make_data(
            [
                {"role": "user", "content": "our internal API needs work"},
            ]
        )
        result = _run(hook.on_provider_request("provider:request", data))
        assert result.action == "continue", (
            "'internal API' (generic) should not trigger"
        )

    def test_graphql_api_no_match(self) -> None:
        hook = DeepWikiTriggerHook(TriggerConfig())
        data = _make_data(
            [
                {"role": "user", "content": "Set up a GraphQL API"},
            ]
        )
        result = _run(hook.on_provider_request("provider:request", data))
        assert result.action == "continue", "'GraphQL API' (generic) should not trigger"

    def test_the_api_no_match(self) -> None:
        hook = DeepWikiTriggerHook(TriggerConfig())
        data = _make_data(
            [
                {"role": "user", "content": "the API returns 500"},
            ]
        )
        result = _run(hook.on_provider_request("provider:request", data))
        assert result.action == "continue", "'the API' (generic) should not trigger"

    def test_stripe_api_still_matches(self) -> None:
        """Named vendor API should still trigger."""
        hook = DeepWikiTriggerHook(TriggerConfig())
        data = _make_data(
            [
                {"role": "user", "content": "Use the Stripe API"},
            ]
        )
        result = _run(hook.on_provider_request("provider:request", data))
        assert result.action == "inject_context", (
            "'Stripe API' (specific vendor) should still trigger"
        )

    def test_openai_sdk_still_matches(self) -> None:
        """Named vendor SDK should still trigger."""
        hook = DeepWikiTriggerHook(TriggerConfig())
        data = _make_data(
            [
                {"role": "user", "content": "Install the OpenAI SDK"},
            ]
        )
        result = _run(hook.on_provider_request("provider:request", data))
        assert result.action == "inject_context", (
            "'OpenAI SDK' (specific vendor) should still trigger"
        )


# ---------------------------------------------------------------------------
# Fix #8: TODO comment for multi-session eviction
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Fix: max_injections cap — hook suppresses after hitting the limit
# ---------------------------------------------------------------------------


class TestMaxInjectionsCap:
    """Hook should stop injecting after total_injections reaches max_injections."""

    def test_suppressed_after_max_injections(self) -> None:
        """After max_injections triggers, further matches should be suppressed."""
        hook = DeepWikiTriggerHook(TriggerConfig(cooldown_turns=0, max_injections=2))
        data = _make_data(
            [
                {"role": "user", "content": "Look at github.com/facebook/react"},
            ]
        )
        # First two should inject
        r1 = _run(hook.on_provider_request("provider:request", data))
        assert r1.action == "inject_context", "1st injection should fire"
        r2 = _run(hook.on_provider_request("provider:request", data))
        assert r2.action == "inject_context", "2nd injection should fire"
        # Third should be suppressed by the cap
        r3 = _run(hook.on_provider_request("provider:request", data))
        assert r3.action == "continue", (
            "3rd injection should be suppressed by max_injections cap"
        )

    def test_no_provider_request_count_field(self) -> None:
        """TriggerState should NOT have provider_request_count (dead state removed)."""
        from amplifier_module_hooks_deepwiki_trigger import TriggerState

        state = TriggerState()
        assert not hasattr(state, "provider_request_count"), (
            "provider_request_count is dead state and should be removed"
        )


# ---------------------------------------------------------------------------
# Fix #8: TODO comment for multi-session eviction
# ---------------------------------------------------------------------------


class TestFix8TodoComment:
    """Source should contain a TODO about multi-session state eviction."""

    def test_todo_comment_exists(self) -> None:
        """There should be a TODO comment about state eviction for multi-session."""
        import inspect

        source = inspect.getsource(DeepWikiTriggerHook)
        assert "TODO" in source and "eviction" in source.lower(), (
            "Missing TODO comment about state eviction for multi-session support"
        )


# ---------------------------------------------------------------------------
# Fix #9: Wire _is_valid_repo_format into GitHub URL detection
# ---------------------------------------------------------------------------


class TestFix9GithubUrlValidationGate:
    """GitHub URL detection must reject platform paths via _is_valid_repo_format."""

    def test_settings_tokens_url_not_detected(self) -> None:
        """'github.com/settings/tokens' is a platform path and must NOT trigger."""
        hook = DeepWikiTriggerHook(TriggerConfig())
        data = _make_data(
            [
                {
                    "role": "user",
                    "content": "Go to github.com/settings/tokens to create a token",
                },
            ]
        )
        result = _run(hook.on_provider_request("provider:request", data))
        assert result.action == "continue", (
            "github.com/settings/tokens (platform path) should not trigger injection"
        )

    def test_valid_repo_url_still_detected(self) -> None:
        """'github.com/facebook/react' is a valid repo and must still trigger."""
        hook = DeepWikiTriggerHook(TriggerConfig())
        data = _make_data(
            [
                {"role": "user", "content": "Look at github.com/facebook/react"},
            ]
        )
        result = _run(hook.on_provider_request("provider:request", data))
        assert result.action == "inject_context", (
            "github.com/facebook/react (valid repo) should still trigger injection"
        )

    def test_explore_url_not_detected(self) -> None:
        """'github.com/explore/topic' is a platform path and must NOT trigger."""
        hook = DeepWikiTriggerHook(TriggerConfig())
        data = _make_data(
            [
                {"role": "user", "content": "Browse github.com/explore/trending"},
            ]
        )
        result = _run(hook.on_provider_request("provider:request", data))
        assert result.action == "continue", (
            "github.com/explore/trending (platform path) should not trigger injection"
        )


# ---------------------------------------------------------------------------
# LRU eviction for multi-session state management
# ---------------------------------------------------------------------------


class TestLRUEviction:
    """Hook evicts oldest sessions when max_sessions is exceeded (LRU policy)."""

    def test_eviction_drops_oldest_session(self) -> None:
        """Adding a 3rd session when max_sessions=2 drops the oldest (session-1)."""
        hook = DeepWikiTriggerHook(TriggerConfig(max_sessions=2))
        for sid in ("session-1", "session-2", "session-3"):
            data = _make_data(
                [{"role": "user", "content": "Look at github.com/facebook/react"}]
            )
            data["session_id"] = sid
            _run(hook.on_provider_request("provider:request", data))
        assert "session-1" not in hook._state, "session-1 should have been evicted"
        assert "session-2" in hook._state, "session-2 should still be present"
        assert "session-3" in hook._state, "session-3 should still be present"

    def test_access_refreshes_lru_position(self) -> None:
        """Re-accessing session-1 before adding session-3 keeps session-1, evicts session-2."""
        hook = DeepWikiTriggerHook(TriggerConfig(max_sessions=2))
        # Add session-1 and session-2
        for sid in ("session-1", "session-2"):
            data = _make_data(
                [{"role": "user", "content": "Look at github.com/facebook/react"}]
            )
            data["session_id"] = sid
            _run(hook.on_provider_request("provider:request", data))
        # Re-access session-1 (refreshes its LRU position)
        data = _make_data(
            [{"role": "user", "content": "Look at github.com/facebook/react"}]
        )
        data["session_id"] = "session-1"
        _run(hook.on_provider_request("provider:request", data))
        # Add session-3 — should evict session-2 (the LRU)
        data = _make_data(
            [{"role": "user", "content": "Look at github.com/facebook/react"}]
        )
        data["session_id"] = "session-3"
        _run(hook.on_provider_request("provider:request", data))
        assert "session-1" in hook._state, (
            "session-1 was recently accessed, should survive"
        )
        assert "session-2" not in hook._state, (
            "session-2 should have been evicted (LRU)"
        )
        assert "session-3" in hook._state, "session-3 should be present"

    def test_eviction_preserves_active_session_tracking(self) -> None:
        """Evicting session-1 does not reset session-2's injection count."""
        hook = DeepWikiTriggerHook(TriggerConfig(max_sessions=2, max_injections=2))
        # session-1: first access (becomes the LRU once session-2 is added)
        data1 = _make_data(
            [{"role": "user", "content": "Look at github.com/facebook/react"}]
        )
        data1["session_id"] = "session-1"
        _run(hook.on_provider_request("provider:request", data1))
        # session-2: first injection
        data2 = _make_data(
            [{"role": "user", "content": "Look at github.com/facebook/react"}]
        )
        data2["session_id"] = "session-2"
        r1 = _run(hook.on_provider_request("provider:request", data2))
        assert r1.action == "inject_context", "1st injection for session-2 should fire"
        # session-3: evicts session-1 (the LRU)
        data3 = _make_data(
            [{"role": "user", "content": "Look at github.com/facebook/react"}]
        )
        data3["session_id"] = "session-3"
        _run(hook.on_provider_request("provider:request", data3))
        # session-2's 2nd injection should still fire (count preserved through eviction)
        data2b = _make_data(
            [{"role": "user", "content": "Look at github.com/facebook/react"}]
        )
        data2b["session_id"] = "session-2"
        r2 = _run(hook.on_provider_request("provider:request", data2b))
        assert r2.action == "inject_context", (
            "session-2's 2nd injection should still fire after session-1 was evicted"
        )

    def test_no_session_id_uses_default(self) -> None:
        """When data has no session_id, hook uses '__default__' key in _state."""
        hook = DeepWikiTriggerHook(TriggerConfig(max_sessions=2))
        data = _make_data(
            [{"role": "user", "content": "Look at github.com/facebook/react"}]
        )
        # No session_id in data
        _run(hook.on_provider_request("provider:request", data))
        assert "__default__" in hook._state, (
            "When no session_id present, hook should use '__default__' key in _state"
        )


# ---------------------------------------------------------------------------
# max_injections config
# ---------------------------------------------------------------------------


class TestMaxInjectionsConfig:
    """TriggerConfig.max_injections stores and applies the configured cap."""

    def test_config_value_is_stored(self) -> None:
        """TriggerConfig(max_injections=42) stores value 42."""
        config = TriggerConfig(max_injections=42)
        assert config.max_injections == 42, "max_injections should be stored as 42"

    def test_config_overrides_default_behaviorally(self) -> None:
        """max_injections=1 allows exactly 1 injection; 2nd call returns continue."""
        hook = DeepWikiTriggerHook(TriggerConfig(max_injections=1))
        data = _make_data(
            [{"role": "user", "content": "Look at github.com/facebook/react"}]
        )
        r1 = _run(hook.on_provider_request("provider:request", data))
        assert r1.action == "inject_context", "1st injection should fire"
        r2 = _run(hook.on_provider_request("provider:request", data))
        assert r2.action == "continue", (
            "2nd injection should be suppressed (max_injections=1)"
        )
