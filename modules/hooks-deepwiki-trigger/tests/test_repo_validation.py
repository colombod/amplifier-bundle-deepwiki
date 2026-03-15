"""Tests for _is_valid_repo_format().

Verifies that the function correctly validates and normalizes owner/repo
strings, returning (True, 'owner/repo') for valid inputs and (False, None)
for invalid ones.

Test classes:
- TestValidFormats: Well-formed owner/repo strings that should be accepted
- TestInvalidFormats: Malformed inputs that should be rejected
- TestPlatformPathRejection: GitHub platform paths used as owner (rejected)
- TestEdgeCases: URL fragments, query params, whitespace, etc.
"""

from __future__ import annotations

from amplifier_module_hooks_deepwiki_trigger import _is_valid_repo_format


class TestValidFormats:
    """Well-formed owner/repo strings should return (True, 'owner/repo')."""

    def test_simple_owner_repo(self) -> None:
        """Simple owner/repo is valid."""
        result = _is_valid_repo_format("facebook/react")
        assert result == (True, "facebook/react")

    def test_hyphenated_names(self) -> None:
        """Hyphenated owner and repo names are valid."""
        result = _is_valid_repo_format("my-org/my-repo")
        assert result == (True, "my-org/my-repo")

    def test_dotted_owner(self) -> None:
        """Dotted owner name is valid."""
        result = _is_valid_repo_format("my.org/repo")
        assert result == (True, "my.org/repo")

    def test_git_suffix_stripped(self) -> None:
        """Bare owner/repo with .git suffix: suffix is stripped."""
        result = _is_valid_repo_format("facebook/react.git")
        assert result == (True, "facebook/react")

    def test_https_github_url(self) -> None:
        """Full HTTPS GitHub URL is parsed to owner/repo."""
        result = _is_valid_repo_format("https://github.com/facebook/react")
        assert result == (True, "facebook/react")

    def test_url_without_scheme(self) -> None:
        """GitHub URL without scheme (github.com/owner/repo) is valid."""
        result = _is_valid_repo_format("github.com/facebook/react")
        assert result == (True, "facebook/react")

    def test_url_with_www(self) -> None:
        """GitHub URL with www. prefix is valid."""
        result = _is_valid_repo_format("www.github.com/facebook/react")
        assert result == (True, "facebook/react")

    def test_github_url_with_git_suffix(self) -> None:
        """GitHub URL with .git suffix: suffix is stripped."""
        result = _is_valid_repo_format("https://github.com/facebook/react.git")
        assert result == (True, "facebook/react")

    def test_underscored_names(self) -> None:
        """Underscored owner and repo names are valid."""
        result = _is_valid_repo_format("my_org/my_repo")
        assert result == (True, "my_org/my_repo")


class TestInvalidFormats:
    """Malformed inputs should return (False, None)."""

    def test_single_segment(self) -> None:
        """Single segment (no slash) is invalid."""
        result = _is_valid_repo_format("facebook")
        assert result == (False, None)

    def test_three_segments(self) -> None:
        """Three-segment path (a/b/c) is invalid."""
        result = _is_valid_repo_format("a/b/c")
        assert result == (False, None)

    def test_empty_owner(self) -> None:
        """Empty owner (leading slash) is invalid."""
        result = _is_valid_repo_format("/repo")
        assert result == (False, None)

    def test_empty_repo(self) -> None:
        """Empty repo (trailing slash) is invalid."""
        result = _is_valid_repo_format("owner/")
        assert result == (False, None)

    def test_special_chars_in_repo(self) -> None:
        """Special character (!) in repo name is invalid."""
        result = _is_valid_repo_format("owner/repo!")
        assert result == (False, None)

    def test_special_chars_in_owner(self) -> None:
        """Space in owner name is invalid."""
        result = _is_valid_repo_format("my org/repo")
        assert result == (False, None)

    def test_empty_string(self) -> None:
        """Empty string is invalid."""
        result = _is_valid_repo_format("")
        assert result == (False, None)


class TestPlatformPathRejection:
    """GitHub platform paths used as owner should be rejected."""

    def test_settings_rejected(self) -> None:
        """'settings' as owner (GitHub platform path) is rejected."""
        result = _is_valid_repo_format("settings/profile")
        assert result == (False, None)

    def test_marketplace_rejected(self) -> None:
        """'marketplace' as owner (GitHub platform path) is rejected."""
        result = _is_valid_repo_format("marketplace/app")
        assert result == (False, None)

    def test_explore_rejected(self) -> None:
        """'explore' as owner (GitHub platform path) is rejected."""
        result = _is_valid_repo_format("explore/topic")
        assert result == (False, None)

    def test_login_rejected(self) -> None:
        """'login' as owner (GitHub platform path) is rejected."""
        result = _is_valid_repo_format("login/page")
        assert result == (False, None)

    def test_notifications_rejected(self) -> None:
        """'notifications' as owner (GitHub platform path) is rejected."""
        result = _is_valid_repo_format("notifications/repo")
        assert result == (False, None)

    def test_issues_rejected(self) -> None:
        """'issues' as owner (GitHub platform path) is rejected."""
        result = _is_valid_repo_format("issues/repo")
        assert result == (False, None)

    def test_codespaces_rejected(self) -> None:
        """'codespaces' as owner (GitHub platform path) is rejected."""
        result = _is_valid_repo_format("codespaces/repo")
        assert result == (False, None)

    def test_platform_path_in_github_url_rejected(self) -> None:
        """GitHub URL with platform path as owner is rejected."""
        result = _is_valid_repo_format("https://github.com/settings/profile")
        assert result == (False, None)

    def test_case_insensitive_platform_path_rejected(self) -> None:
        """Platform path matching is case-insensitive (SETTINGS is rejected)."""
        result = _is_valid_repo_format("SETTINGS/repo")
        assert result == (False, None)


class TestEdgeCases:
    """Edge case inputs should be handled correctly."""

    def test_trailing_slash_on_bare_repo_rejected(self) -> None:
        """Bare owner/repo with trailing slash is rejected."""
        result = _is_valid_repo_format("facebook/react/")
        assert result == (False, None)

    def test_url_fragment_stripped_and_accepted(self) -> None:
        """URL fragment (#readme) is stripped before validation."""
        result = _is_valid_repo_format("facebook/react#readme")
        assert result == (True, "facebook/react")

    def test_query_params_stripped_and_accepted(self) -> None:
        """Query parameters (?tab=repositories) are stripped before validation."""
        result = _is_valid_repo_format("facebook/react?tab=repositories")
        assert result == (True, "facebook/react")

    def test_github_url_with_trailing_slash_accepted(self) -> None:
        """GitHub URL with trailing slash is accepted (slash stripped)."""
        result = _is_valid_repo_format("https://github.com/facebook/react/")
        assert result == (True, "facebook/react")

    def test_github_com_alone_rejected(self) -> None:
        """'github.com' alone (no path) is rejected."""
        result = _is_valid_repo_format("github.com")
        assert result == (False, None)

    def test_github_com_single_segment_rejected(self) -> None:
        """'github.com/facebook' (single segment path) is rejected."""
        result = _is_valid_repo_format("github.com/facebook")
        assert result == (False, None)

    def test_whitespace_stripped(self) -> None:
        """Leading/trailing whitespace is stripped before validation."""
        result = _is_valid_repo_format("  facebook/react  ")
        assert result == (True, "facebook/react")
