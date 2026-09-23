"""Tests for the disabled self-upgrade / offline self-check behavior.

spec-datkit removes the upstream auto-upgrade path: `self upgrade` must
refuse without touching the network or launching an installer, and
`self check` must report the installed version without querying GitHub
Releases. These tests pin that contract.
"""

from unittest.mock import patch

from specify_cli import app

from tests.self_upgrade_helpers import runner, strip_ansi


class TestSelfUpgradeDisabled:
    """`self upgrade` always refuses, without side effects."""

    def test_upgrade_exits_1_with_disabled_message(self, clean_environ):
        result = runner.invoke(app, ["self", "upgrade"])

        output = strip_ansi(result.output)
        assert result.exit_code == 1
        assert "Self-upgrade is disabled in this spec-datkit build" in output

    def test_upgrade_never_resolves_latest_release(self, clean_environ):
        with patch(
            "specify_cli._version._fetch_latest_release_tag",
            side_effect=AssertionError("latest release lookup should not run"),
        ) as fetch_latest:
            result = runner.invoke(app, ["self", "upgrade"])

        assert result.exit_code == 1
        fetch_latest.assert_not_called()

    def test_upgrade_never_launches_installer(self, uv_tool_argv0, clean_environ):
        with patch(
            "specify_cli._version.subprocess.run",
            side_effect=AssertionError("installer subprocess should not run"),
        ) as mock_run:
            result = runner.invoke(app, ["self", "upgrade"])

        assert result.exit_code == 1
        mock_run.assert_not_called()

    def test_upgrade_with_tag_still_refuses(self, clean_environ):
        result = runner.invoke(app, ["self", "upgrade", "--tag", "v1.0.0"])

        output = strip_ansi(result.output)
        assert result.exit_code == 1
        assert "Self-upgrade is disabled in this spec-datkit build" in output

    def test_upgrade_dry_run_still_refuses(self, clean_environ):
        result = runner.invoke(app, ["self", "upgrade", "--dry-run"])

        assert result.exit_code == 1


class TestSelfCheckOffline:
    """`self check` reports the installed version without network access."""

    def test_check_prints_installed_version_and_disabled_note(self, clean_environ):
        with patch(
            "specify_cli._version._get_installed_version", return_value="1.0.0"
        ):
            result = runner.invoke(app, ["self", "check"])

        output = strip_ansi(result.output)
        assert result.exit_code == 0
        assert "Installed: 1.0.0" in output
        assert "disabled" in output

    def test_check_never_queries_github(self, clean_environ):
        with patch(
            "specify_cli._version._fetch_latest_release_tag",
            side_effect=AssertionError("latest release lookup should not run"),
        ) as fetch_latest:
            result = runner.invoke(app, ["self", "check"])

        assert result.exit_code == 0
        fetch_latest.assert_not_called()

    def test_check_reports_unknown_when_metadata_missing(self, clean_environ):
        with patch(
            "specify_cli._version._get_installed_version", return_value="unknown"
        ):
            result = runner.invoke(app, ["self", "check"])

        output = strip_ansi(result.output)
        assert result.exit_code == 0
        assert "Installed: unknown" in output
