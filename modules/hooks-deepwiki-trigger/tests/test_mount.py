"""Tests for mount() contract compliance.

The hook contract requires mount() to return a cleanup callable (or None),
NOT a metadata dict. The cleanup callable should call unregister() when invoked.
"""

from __future__ import annotations

import asyncio
import unittest
from unittest.mock import MagicMock

from amplifier_module_hooks_deepwiki_trigger import mount


class TestMountReturnsCleanupCallable(unittest.TestCase):
    """mount() must return a cleanup callable per the hook contract."""

    def _run_async(self, coro):  # noqa: ANN001, ANN202
        return asyncio.run(coro)

    def _make_coordinator(self) -> MagicMock:
        """Create a mock coordinator whose hooks.register() returns an unregister callable."""
        coordinator = MagicMock()
        unregister_fn = MagicMock(name="unregister")
        coordinator.hooks.register.return_value = unregister_fn
        return coordinator

    def test_mount_returns_callable_not_dict(self) -> None:
        """mount() must return a callable, not a dict."""
        coordinator = self._make_coordinator()
        result = self._run_async(mount(coordinator, {}))

        self.assertNotIsInstance(
            result,
            dict,
            "mount() must NOT return a dict — it should return a cleanup callable",
        )
        self.assertTrue(
            callable(result),
            f"mount() must return a callable cleanup function, got {type(result).__name__}",
        )

    def test_cleanup_calls_unregister(self) -> None:
        """The cleanup callable returned by mount() must call the unregister handle."""
        coordinator = self._make_coordinator()
        unregister_fn = coordinator.hooks.register.return_value

        cleanup = self._run_async(mount(coordinator, {}))
        assert cleanup is not None, (
            "mount() returned None instead of a cleanup callable"
        )

        # Before calling cleanup, unregister should not have been called
        unregister_fn.assert_not_called()

        # Call cleanup — it should invoke the unregister handle
        cleanup()

        unregister_fn.assert_called_once()

    def test_mount_registers_hook(self) -> None:
        """mount() must still register the hook on provider:request."""
        coordinator = self._make_coordinator()
        self._run_async(mount(coordinator, {}))

        coordinator.hooks.register.assert_called_once()
        call_args = coordinator.hooks.register.call_args
        self.assertEqual(call_args[0][0], "provider:request")
        self.assertEqual(call_args[1].get("name"), "deepwiki-trigger")


if __name__ == "__main__":
    unittest.main()
