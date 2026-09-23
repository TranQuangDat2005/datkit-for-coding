"""Parity tests for the create-new-feature variants (branch-based contract)."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

import pytest

from tests.conftest import requires_bash
from tests.parity_helpers import (
    HAS_POWERSHELL,
    bash_cmd,
    break_wrap_layer,
    install_composition_stack,
    install_scripts,
    json_stdout,
    make_repo,
    normalize_repo_paths,
    ps_cmd,
    py_cmd,
    run,
)

SCRIPT = "create-new-feature"
TEMPLATE_BODY = "# Spec Template\n\nBody.\n"

requires_powershell = pytest.mark.skipif(
    not HAS_POWERSHELL, reason="no PowerShell available"
)


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True, text=True)


def _setup_repo(tmp_path: Path, name: str = "proj", branch: str = "003-user-auth") -> Path:
    repo = make_repo(tmp_path, name)
    _git(repo, "init", "-b", branch)
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test")
    _git(repo, "commit", "--allow-empty", "-m", "init")
    install_scripts(repo, SCRIPT)
    templates = repo / ".specify" / "templates"
    templates.mkdir(parents=True)
    (templates / "spec-template.md").write_text(TEMPLATE_BODY, encoding="utf-8")
    return repo


def _normalized_error_text(stderr: str, repo: Path) -> str:
    stderr = re.sub(r"\x1b\[[0-9;]*m", "", stderr)
    stderr = re.sub(r"(?m)^\s*\|\s?", "", stderr)
    stderr = normalize_repo_paths(stderr, repo)
    return " ".join(stderr.split()).replace("\\", "/")


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    return _setup_repo(tmp_path)


@pytest.fixture
def repo_pair(tmp_path: Path) -> tuple[Path, Path]:
    return _setup_repo(tmp_path, "proj-a"), _setup_repo(tmp_path, "proj-b")


def _norm_value(value: object) -> object:
    if isinstance(value, str):
        return value.replace("\\", "/")
    return value


def _normalized_payload(result: subprocess.CompletedProcess[str]) -> dict[str, object]:
    data = json_stdout(result)
    assert isinstance(data, dict)
    return {k: _norm_value(v) for k, v in data.items()}


def _assert_json_shape(payload: dict[str, object], branch: str) -> None:
    if re.match(r"^\d{8}-\d{6}-", branch):
        num, mode = branch[:15], "timestamp"
    else:
        num, mode = branch.split("-")[0], "sequential"
    assert payload["FEATURE_NAME"] == branch
    assert payload["BRANCH_NAME"] == branch
    assert payload["FEATURE_NUM"] == num
    assert payload["NUMBERING_MODE"] == mode
    assert str(payload["FEATURE_DIR"]).replace("\\", "/").endswith(f"specs/{branch}")
    assert str(payload["SPEC_FILE"]).replace("\\", "/").endswith(f"specs/{branch}/spec.md")


# -- Happy path ---------------------------------------------------------


@requires_bash
def test_python_full_run_matches_bash(repo_pair: tuple[Path, Path]) -> None:
    repo_a, repo_b = repo_pair
    bash = run(bash_cmd(repo_a, SCRIPT, "--json"), repo_a)
    py = run(py_cmd(repo_b, SCRIPT, "--json"), repo_b)

    assert bash.returncode == py.returncode == 0
    assert bash.stderr == py.stderr == ""
    payload = _normalized_payload(bash)
    assert payload == _normalized_payload(py)
    _assert_json_shape(payload, "003-user-auth")
    for repo in (repo_a, repo_b):
        spec = repo / "specs" / "003-user-auth" / "spec.md"
        assert spec.read_text(encoding="utf-8") == TEMPLATE_BODY
        feature_json = json.loads(
            (repo / ".specify" / "feature.json").read_text(encoding="utf-8")
        )
        assert feature_json == {"feature_directory": "specs/003-user-auth"}


@requires_powershell
def test_powershell_full_run_matches(repo: Path) -> None:
    ps = run(ps_cmd(repo, SCRIPT, "-Json"), repo)

    assert ps.returncode == 0
    payload = _normalized_payload(ps)
    _assert_json_shape(payload, "003-user-auth")
    spec = repo / "specs" / "003-user-auth" / "spec.md"
    assert spec.read_text(encoding="utf-8") == TEMPLATE_BODY
    feature_json = json.loads(
        (repo / ".specify" / "feature.json").read_text(encoding="utf-8")
    )
    assert feature_json == {"feature_directory": "specs/003-user-auth"}


@requires_bash
def test_all_variants_timestamp_branch_match(repo_pair: tuple[Path, Path]) -> None:
    repo_a, repo_b = repo_pair
    for repo in (repo_a, repo_b):
        _git(repo, "checkout", "-b", "20260923-134500-pay")

    bash = run(bash_cmd(repo_a, SCRIPT, "--json"), repo_a)
    py = run(py_cmd(repo_b, SCRIPT, "--json"), repo_b)
    results = [bash, py]
    if HAS_POWERSHELL:
        results.append(run(ps_cmd(repo_a, SCRIPT, "-Json"), repo_a))

    assert all(result.returncode == 0 for result in results)
    for result in results:
        _assert_json_shape(_normalized_payload(result), "20260923-134500-pay")


@requires_powershell
def test_powershell_timestamp_branch(repo: Path) -> None:
    _git(repo, "checkout", "-b", "20260923-134500-pay")
    ps = run(ps_cmd(repo, SCRIPT, "-Json"), repo)

    assert ps.returncode == 0
    _assert_json_shape(_normalized_payload(ps), "20260923-134500-pay")


def test_python_dry_run_creates_nothing(repo: Path) -> None:
    py = run(py_cmd(repo, SCRIPT, "--json", "--dry-run"), repo)

    assert py.returncode == 0
    payload = _normalized_payload(py)
    assert payload["DRY_RUN"] is True
    assert not (repo / "specs").exists()
    assert not (repo / ".specify" / "feature.json").exists()


@requires_bash
def test_all_variants_dry_run_match(repo: Path) -> None:
    bash = run(bash_cmd(repo, SCRIPT, "--json", "--dry-run"), repo)
    py = run(py_cmd(repo, SCRIPT, "--json", "--dry-run"), repo)

    assert bash.returncode == py.returncode == 0
    assert _normalized_payload(bash) == _normalized_payload(py)
    assert not (repo / "specs").exists()
    assert not (repo / ".specify" / "feature.json").exists()


# -- Branch validation ----------------------------------------------------


@pytest.mark.parametrize(
    "branch",
    [
        "main",
        "003userauth",
        "003-",
        "003-user--auth",
        "003_user-auth",
        "12-user-auth",
    ],
    ids=[
        "no_number",
        "no_separator",
        "empty_suffix",
        "double_hyphen",
        "underscore",
        "two_digit_number",
    ],
)
def test_python_reject_invalid_branch(repo: Path, branch: str) -> None:
    _git(repo, "checkout", "-b", branch)
    expected = (
        f"Current Git branch '{branch}' is not a Spec Kit feature branch. "
        "Expected '003-user-auth' or 'YYYYMMDD-HHMMSS-user-auth'."
    )

    py = run(py_cmd(repo, SCRIPT, "--json"), repo)
    assert py.returncode == 1
    assert expected in _normalized_error_text(py.stderr, repo)


@requires_bash
@pytest.mark.parametrize(
    "branch", ["main", "003userauth", "003-user--auth", "12-user-auth"]
)
def test_bash_reject_invalid_branch(repo: Path, branch: str) -> None:
    _git(repo, "checkout", "-b", branch)
    expected = (
        f"Current Git branch '{branch}' is not a Spec Kit feature branch. "
        "Expected '003-user-auth' or 'YYYYMMDD-HHMMSS-user-auth'."
    )

    bash = run(bash_cmd(repo, SCRIPT, "--json"), repo)
    assert bash.returncode == 1
    assert expected in _normalized_error_text(bash.stderr, repo)


@requires_powershell
def test_powershell_reject_invalid_branch(repo: Path) -> None:
    _git(repo, "checkout", "-b", "main")
    expected = (
        "Current Git branch 'main' is not a Spec Kit feature branch. "
        "Expected '003-user-auth' or 'YYYYMMDD-HHMMSS-user-auth'."
    )

    ps = run(ps_cmd(repo, SCRIPT, "-Json"), repo)
    assert ps.returncode == 1
    assert expected in _normalized_error_text(ps.stderr, repo)


def test_python_reject_path_separator_branch(repo: Path) -> None:
    _git(repo, "checkout", "-b", "feature/003-user-auth")
    expected = "Current Git branch 'feature/003-user-auth' contains a path separator."

    py = run(py_cmd(repo, SCRIPT, "--json"), repo)
    assert py.returncode == 1
    assert expected in _normalized_error_text(py.stderr, repo)


def test_python_reject_detached_head(repo: Path) -> None:
    head = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=repo, check=True, capture_output=True, text=True
    ).stdout.strip()
    _git(repo, "checkout", "--detach", head)

    py = run(py_cmd(repo, SCRIPT, "--json"), repo)
    assert py.returncode == 1
    assert "could not determine the current Git branch" in _normalized_error_text(
        py.stderr, repo
    )


def test_python_reject_non_git_directory(tmp_path: Path) -> None:
    repo = make_repo(tmp_path, "plain")
    install_scripts(repo, SCRIPT)
    (repo / ".specify" / "templates").mkdir(parents=True, exist_ok=True)
    (repo / ".specify" / "templates" / "spec-template.md").write_text(
        TEMPLATE_BODY, encoding="utf-8"
    )

    py = run(py_cmd(repo, SCRIPT, "--json"), repo)
    assert py.returncode == 1
    assert "could not read a Git repository" in _normalized_error_text(py.stderr, repo)


# -- Existing feature directory -------------------------------------------


def test_python_existing_dir_without_flag_fails(repo: Path) -> None:
    assert run(py_cmd(repo, SCRIPT, "--json"), repo).returncode == 0

    py = run(py_cmd(repo, SCRIPT, "--json"), repo)
    assert py.returncode == 1
    stderr = _normalized_error_text(py.stderr, repo)
    assert "Feature directory" in stderr
    assert "already exists" in stderr


def test_python_allow_existing_feature_preserves_spec(repo: Path) -> None:
    assert run(py_cmd(repo, SCRIPT, "--json"), repo).returncode == 0
    spec = repo / "specs" / "003-user-auth" / "spec.md"
    spec.write_text("# user edits\n", encoding="utf-8")

    py = run(py_cmd(repo, SCRIPT, "--json", "--allow-existing-feature"), repo)
    assert py.returncode == 0
    assert spec.read_text(encoding="utf-8") == "# user edits\n"


@requires_powershell
def test_powershell_allow_existing_feature_preserves_spec(repo: Path) -> None:
    assert run(ps_cmd(repo, SCRIPT, "-Json"), repo).returncode == 0
    spec = repo / "specs" / "003-user-auth" / "spec.md"
    spec.write_text("# user edits\n", encoding="utf-8")

    ps = run(ps_cmd(repo, SCRIPT, "-Json", "-AllowExistingFeature"), repo)
    assert ps.returncode == 0
    assert spec.read_text(encoding="utf-8") == "# user edits\n"


def test_python_legacy_allow_existing_branch_alias(repo: Path) -> None:
    assert run(py_cmd(repo, SCRIPT, "--json"), repo).returncode == 0

    py = run(py_cmd(repo, SCRIPT, "--json", "--allow-existing-branch"), repo)
    assert py.returncode == 0


@requires_bash
def test_bash_legacy_allow_existing_branch_alias(repo: Path) -> None:
    assert run(bash_cmd(repo, SCRIPT, "--json"), repo).returncode == 0

    bash = run(bash_cmd(repo, SCRIPT, "--json", "--allow-existing-branch"), repo)
    assert bash.returncode == 0


# -- Template materialization ---------------------------------------------


def test_python_missing_template_warning(repo: Path) -> None:
    (repo / ".specify" / "templates" / "spec-template.md").unlink()

    py = run(py_cmd(repo, SCRIPT, "--json"), repo)
    assert py.returncode == 0
    assert "spec-template was not found" in _normalized_error_text(py.stderr, repo)
    spec = repo / "specs" / "003-user-auth" / "spec.md"
    assert spec.read_text(encoding="utf-8") == ""


@requires_bash
def test_python_missing_template_warning_matches_bash(repo_pair: tuple[Path, Path]) -> None:
    repo_a, repo_b = repo_pair
    (repo_a / ".specify" / "templates" / "spec-template.md").unlink()
    (repo_b / ".specify" / "templates" / "spec-template.md").unlink()

    bash = run(bash_cmd(repo_a, SCRIPT, "--json"), repo_a)
    py = run(py_cmd(repo_b, SCRIPT, "--json"), repo_b)

    assert bash.returncode == py.returncode == 0
    assert "spec-template was not found" in _normalized_error_text(bash.stderr, repo_a)
    assert "spec-template was not found" in _normalized_error_text(py.stderr, repo_b)


def test_python_materialize_composed_spec_template(repo: Path) -> None:
    composed = install_composition_stack(repo, "spec-template", "# Core\n")

    py = run(py_cmd(repo, SCRIPT, "--json"), repo)
    assert py.returncode == 0
    spec = repo / "specs" / "003-user-auth" / "spec.md"
    assert spec.read_text(encoding="utf-8") == composed


@requires_bash
def test_bash_materialize_composed_spec_template(repo: Path) -> None:
    composed = install_composition_stack(repo, "spec-template", "# Core\n")

    bash = run(bash_cmd(repo, SCRIPT, "--json"), repo)
    assert bash.returncode == 0
    spec = repo / "specs" / "003-user-auth" / "spec.md"
    assert spec.read_text(encoding="utf-8") == composed


def test_python_fail_for_broken_spec_composition(repo: Path) -> None:
    install_composition_stack(repo, "spec-template", "# Core\n")
    break_wrap_layer(repo, "spec-template")

    py = run(py_cmd(repo, SCRIPT, "--json"), repo)
    assert py.returncode == 1
    assert "wrap" in _normalized_error_text(py.stderr, repo).lower()


# -- Output shape -----------------------------------------------------------


def test_python_json_key_order(repo: Path) -> None:
    py = run(py_cmd(repo, SCRIPT, "--json"), repo)
    assert py.returncode == 0
    keys = list(json.loads(py.stdout).keys())
    assert keys == [
        "FEATURE_NAME",
        "BRANCH_NAME",
        "FEATURE_NUM",
        "FEATURE_DIR",
        "SPEC_FILE",
        "NUMBERING_MODE",
    ]


def test_python_text_mode_fields(repo: Path) -> None:
    py = run(py_cmd(repo, SCRIPT), repo)
    assert py.returncode == 0
    lines = py.stdout.strip().splitlines()
    fields = [line.split(":")[0] for line in lines]
    assert fields == [
        "FEATURE_NAME",
        "BRANCH_NAME",
        "FEATURE_NUM",
        "FEATURE_DIR",
        "SPEC_FILE",
        "NUMBERING_MODE",
    ]
    assert lines[0] == "FEATURE_NAME: 003-user-auth"
    assert lines[2] == "FEATURE_NUM: 003"
    assert lines[5] == "NUMBERING_MODE: sequential"


def test_python_persists_relative_feature_json(repo: Path) -> None:
    assert run(py_cmd(repo, SCRIPT, "--json"), repo).returncode == 0
    feature_json = json.loads(
        (repo / ".specify" / "feature.json").read_text(encoding="utf-8")
    )
    assert feature_json == {"feature_directory": "specs/003-user-auth"}


def test_python_ignores_stale_feature_json(tmp_path: Path) -> None:
    """The active branch — not .specify/feature.json — selects the feature."""
    repo = _setup_repo(tmp_path)
    _git(repo, "checkout", "-b", "007-other-feature")
    (repo / ".specify" / "feature.json").write_text(
        json.dumps({"feature_directory": "specs/099-stale-feature"}), encoding="utf-8"
    )

    py = run(py_cmd(repo, SCRIPT, "--json"), repo)
    assert py.returncode == 0
    payload = _normalized_payload(py)
    assert payload["FEATURE_NAME"] == "007-other-feature"
    feature_json = json.loads(
        (repo / ".specify" / "feature.json").read_text(encoding="utf-8")
    )
    assert feature_json == {"feature_directory": "specs/007-other-feature"}


def test_python_help_exits_zero(repo: Path) -> None:
    py = run(py_cmd(repo, SCRIPT, "--help"), repo)
    assert py.returncode == 0
