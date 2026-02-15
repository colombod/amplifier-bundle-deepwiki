"""Shared test fixtures for hooks-deepwiki-trigger tests."""

import sys
import types
from typing import Any

import pytest


def _install_amplifier_core_mock() -> None:
    """Mock amplifier_core module so tests can import the hook without the real package."""
    if "amplifier_core" not in sys.modules:

        class MockHookResult:
            """Lightweight stand-in that stores kwargs as attributes."""

            def __init__(self, **kwargs: Any) -> None:
                for k, v in kwargs.items():
                    setattr(self, k, v)

        mod = types.ModuleType("amplifier_core")
        models = types.ModuleType("amplifier_core.models")
        models.HookResult = MockHookResult  # type: ignore[attr-defined]
        mod.models = models  # type: ignore[attr-defined]
        mod.HookResult = MockHookResult  # type: ignore[attr-defined]
        sys.modules["amplifier_core"] = mod
        sys.modules["amplifier_core.models"] = models


# Run at import time so test modules can do module-level imports.
# (pytest loads conftest.py before any test modules in the same directory.)
_install_amplifier_core_mock()


@pytest.fixture(autouse=True)
def mock_amplifier_core() -> None:
    """Ensure amplifier_core mock is present before every test."""
    _install_amplifier_core_mock()
