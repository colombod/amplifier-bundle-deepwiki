"""Tests for detection pattern coverage.

Verifies that the expanded patterns catch high-confidence triggers
(import statements, package install commands, standalone SDK/API mentions)
while NOT matching generic technology mentions, stdlib imports, or
language-specific built-in modules.

Also verifies GITHUB_URL_RE matches issue and PR URLs.
"""

from __future__ import annotations

from amplifier_module_hooks_deepwiki_trigger import (
    GENERIC_API_PREFIXES,
    GITHUB_URL_RE,
    GO_IMPORT_RE,
    GO_STD_PACKAGES,
    IMPORT_RE,
    JS_BUILTIN_MODULES,
    JS_IMPORT_RE,
    LIBRARY_QUESTION_PATTERNS,
    PACKAGE_INSTALL_RE,
    RUST_STD_CRATES,
    RUST_USE_RE,
    SDK_API_RE,
    STDLIB_MODULES,
    _VALIDATED_PATTERNS,
)


def _any_pattern_matches(text: str) -> bool:
    """Check if text would trigger detection (mirrors _has_trigger_pattern).

    Replicates the hook's validated-match logic: general patterns are checked
    directly, but validated patterns are skipped in the blind iteration and
    instead handled via capturing-group variants with exclusion filtering.
    """
    # General library/framework patterns (skip validated ones)
    for pattern in LIBRARY_QUESTION_PATTERNS:
        if pattern in _VALIDATED_PATTERNS:
            continue
        if pattern.search(text):
            return True
    # Package install commands
    if PACKAGE_INSTALL_RE.search(text):
        return True
    # Python import statements — exclude stdlib modules
    for match in IMPORT_RE.finditer(text):
        module_name = match.group(1).lower()
        if module_name not in STDLIB_MODULES:
            return True
    # JS/TS import/require — exclude Node.js built-ins
    for match in JS_IMPORT_RE.finditer(text):
        pkg_raw = match.group(1) or match.group(2)
        pkg = pkg_raw.split("/")[0]
        if pkg.lower() not in JS_BUILTIN_MODULES:
            return True
    # Rust use statements — exclude std crates
    for match in RUST_USE_RE.finditer(text):
        crate_name = match.group(1).lower()
        if crate_name not in RUST_STD_CRATES:
            return True
    # Go import statements — exclude stdlib packages
    for match in GO_IMPORT_RE.finditer(text):
        pkg = match.group(1)
        pkg_base = pkg.split("/")[0]
        if pkg_base.lower() not in GO_STD_PACKAGES:
            return True
    # Standalone SDK/API mentions — exclude generic prefixes
    for match in SDK_API_RE.finditer(text):
        prefix = match.group(1).lower()
        if prefix not in GENERIC_API_PREFIXES:
            return True
    return False


# ---------------------------------------------------------------------------
# Python import/from statements
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
# Python pip/uv/poetry install commands
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
# Non-Python package manager install commands
# ---------------------------------------------------------------------------


class TestNonPythonPackageManagerPatterns:
    """Non-Python package manager commands should trigger detection."""

    def test_npm_install(self) -> None:
        assert _any_pattern_matches("npm install express")

    def test_yarn_add(self) -> None:
        assert _any_pattern_matches("yarn add react")

    def test_pnpm_add(self) -> None:
        assert _any_pattern_matches("pnpm add vue")

    def test_bun_add(self) -> None:
        assert _any_pattern_matches("bun add elysia")

    def test_cargo_add(self) -> None:
        assert _any_pattern_matches("cargo add serde")

    def test_go_get(self) -> None:
        assert _any_pattern_matches("go get github.com/gorilla/mux")

    def test_gem_install(self) -> None:
        assert _any_pattern_matches("gem install rails")

    def test_dotnet_add_package(self) -> None:
        assert _any_pattern_matches("dotnet add package Newtonsoft.Json")

    def test_npm_install_scoped_package(self) -> None:
        assert _any_pattern_matches("npm install @types/react")


# ---------------------------------------------------------------------------
# JS/TS import/require statements
# ---------------------------------------------------------------------------


class TestJsImportPatterns:
    """JS/TS import/require statements should trigger detection."""

    def test_import_from_single_quotes(self) -> None:
        assert _any_pattern_matches("import React from 'react'")

    def test_import_from_double_quotes(self) -> None:
        assert _any_pattern_matches('import React from "react"')

    def test_named_import_from(self) -> None:
        assert _any_pattern_matches("import { useState } from 'react'")

    def test_require(self) -> None:
        assert _any_pattern_matches("const express = require('express')")

    def test_require_double_quotes(self) -> None:
        assert _any_pattern_matches('const app = require("express")')

    def test_relative_import_no_match(self) -> None:
        assert not _any_pattern_matches("import foo from './foo'")

    def test_relative_require_no_match(self) -> None:
        assert not _any_pattern_matches("require('./local')")

    def test_node_fs_no_match(self) -> None:
        assert not _any_pattern_matches("import fs from 'fs'")

    def test_node_path_no_match(self) -> None:
        assert not _any_pattern_matches("import path from 'path'")

    def test_node_crypto_no_match(self) -> None:
        assert not _any_pattern_matches("const crypto = require('crypto')")


# ---------------------------------------------------------------------------
# Rust use statements
# ---------------------------------------------------------------------------


class TestRustUsePatterns:
    """Rust use statements should trigger detection."""

    def test_use_serde(self) -> None:
        assert _any_pattern_matches("use serde::Deserialize;")

    def test_use_tokio(self) -> None:
        assert _any_pattern_matches("use tokio::runtime;")

    def test_use_in_multiline(self) -> None:
        text = "fn main() {\n    use reqwest::Client;\n}"
        assert _any_pattern_matches(text)

    def test_use_std_no_match(self) -> None:
        assert not _any_pattern_matches("use std::collections::HashMap;")

    def test_use_core_no_match(self) -> None:
        assert not _any_pattern_matches("use core::fmt;")

    def test_use_crate_no_match(self) -> None:
        assert not _any_pattern_matches("use crate::models;")

    def test_use_self_no_match(self) -> None:
        assert not _any_pattern_matches("use self::utils;")


# ---------------------------------------------------------------------------
# Go import statements
# ---------------------------------------------------------------------------


class TestGoImportPatterns:
    """Go import statements should trigger detection."""

    def test_import_third_party(self) -> None:
        assert _any_pattern_matches('import "github.com/gorilla/mux"')

    def test_import_non_std_package(self) -> None:
        assert _any_pattern_matches('import "gin"')

    def test_import_fmt_no_match(self) -> None:
        assert not _any_pattern_matches('import "fmt"')

    def test_import_os_no_match(self) -> None:
        assert not _any_pattern_matches('import "os"')

    def test_import_net_no_match(self) -> None:
        assert not _any_pattern_matches('import "net"')


# ---------------------------------------------------------------------------
# Standalone SDK/API mentions
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
# Expanded GENERIC_API_PREFIXES false positive guards
# ---------------------------------------------------------------------------


class TestExpandedGenericApiPrefixes:
    """Newly added generic API/SDK prefixes must NOT trigger detection."""

    def test_backend_api_no_match(self) -> None:
        assert not _any_pattern_matches("backend API")

    def test_client_sdk_no_match(self) -> None:
        assert not _any_pattern_matches("client SDK")

    def test_server_api_no_match(self) -> None:
        assert not _any_pattern_matches("server API")

    def test_frontend_sdk_no_match(self) -> None:
        assert not _any_pattern_matches("frontend SDK")

    def test_local_api_no_match(self) -> None:
        assert not _any_pattern_matches("local API")

    def test_remote_api_no_match(self) -> None:
        assert not _any_pattern_matches("remote API")

    def test_new_api_no_match(self) -> None:
        assert not _any_pattern_matches("new API")


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
