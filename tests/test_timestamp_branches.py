"""
Pytest tests for common.sh helpers and the bundled git extension scripts.

Core create-new-feature behavior (branch-based contract) is covered by
tests/test_create_new_feature_python_parity.py. This file keeps:

- static/regression guards over core common.sh helper removals,
- get_feature_paths / Get-FeaturePathsEnv resolution priority tests,
- static guards over create-new-feature.ps1 flags,
- the git extension (create-new-feature-branch) GIT_BRANCH_NAME override
  and description-quoting regression tests.
"""

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

from tests.conftest import requires_bash

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CREATE_FEATURE = PROJECT_ROOT / "scripts" / "bash" / "create-new-feature.sh"
CREATE_FEATURE_PS = PROJECT_ROOT / "scripts" / "powershell" / "create-new-feature.ps1"
EXT_CREATE_FEATURE = (
    PROJECT_ROOT / "extensions" / "git" / "scripts" / "bash" / "create-new-feature-branch.sh"
)
EXT_CREATE_FEATURE_PS = (
    PROJECT_ROOT / "extensions" / "git" / "scripts" / "powershell" / "create-new-feature-branch.ps1"
)
COMMON_SH = PROJECT_ROOT / "scripts" / "bash" / "common.sh"

HAS_PWSH = shutil.which("pwsh") is not None


def _has_pwsh() -> bool:
    """Check if pwsh is available."""
    return HAS_PWSH


@pytest.fixture
def git_repo(tmp_path: Path) -> Path:
    """Create a temp git repo with scripts and .specify dir."""
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"], cwd=tmp_path, check=True
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"], cwd=tmp_path, check=True
    )
    subprocess.run(
        ["git", "commit", "--allow-empty", "-m", "init", "-q"],
        cwd=tmp_path,
        check=True,
    )
    scripts_dir = tmp_path / "scripts" / "bash"
    scripts_dir.mkdir(parents=True)
    shutil.copy(CREATE_FEATURE, scripts_dir / "create-new-feature.sh")
    shutil.copy(COMMON_SH, scripts_dir / "common.sh")
    (tmp_path / ".specify" / "templates").mkdir(parents=True)
    return tmp_path


@pytest.fixture
def ext_git_repo(tmp_path: Path) -> Path:
    """Create a temp git repo with extension scripts (for GIT_BRANCH_NAME tests)."""
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "--allow-empty", "-m", "init", "-q"], cwd=tmp_path, check=True)
    # Extension script needs common.sh at .specify/scripts/bash/
    specify_scripts = tmp_path / ".specify" / "scripts" / "bash"
    specify_scripts.mkdir(parents=True)
    shutil.copy(COMMON_SH, specify_scripts / "common.sh")
    # Also install core scripts for compatibility
    core_scripts = tmp_path / "scripts" / "bash"
    core_scripts.mkdir(parents=True)
    shutil.copy(COMMON_SH, core_scripts / "common.sh")
    # Copy extension script
    ext_dir = tmp_path / ".specify" / "extensions" / "git" / "scripts" / "bash"
    ext_dir.mkdir(parents=True)
    shutil.copy(EXT_CREATE_FEATURE, ext_dir / "create-new-feature-branch.sh")
    # Also copy git-common.sh if it exists
    git_common = PROJECT_ROOT / "extensions" / "git" / "scripts" / "bash" / "git-common.sh"
    if git_common.exists():
        shutil.copy(git_common, ext_dir / "git-common.sh")
    (tmp_path / ".specify" / "templates").mkdir(parents=True, exist_ok=True)
    (tmp_path / "specs").mkdir(exist_ok=True)
    return tmp_path


@pytest.fixture
def ext_ps_git_repo(tmp_path: Path) -> Path:
    """Create a temp git repo with PowerShell extension scripts."""
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "--allow-empty", "-m", "init", "-q"], cwd=tmp_path, check=True)
    # Install core PS scripts
    ps_dir = tmp_path / "scripts" / "powershell"
    ps_dir.mkdir(parents=True)
    common_ps = PROJECT_ROOT / "scripts" / "powershell" / "common.ps1"
    shutil.copy(common_ps, ps_dir / "common.ps1")
    # Also install at .specify/scripts/powershell/ for extension resolution
    specify_ps = tmp_path / ".specify" / "scripts" / "powershell"
    specify_ps.mkdir(parents=True)
    shutil.copy(common_ps, specify_ps / "common.ps1")
    # Copy extension script
    ext_ps = tmp_path / ".specify" / "extensions" / "git" / "scripts" / "powershell"
    ext_ps.mkdir(parents=True)
    shutil.copy(EXT_CREATE_FEATURE_PS, ext_ps / "create-new-feature-branch.ps1")
    git_common_ps = PROJECT_ROOT / "extensions" / "git" / "scripts" / "powershell" / "git-common.ps1"
    if git_common_ps.exists():
        shutil.copy(git_common_ps, ext_ps / "git-common.ps1")
    (tmp_path / ".specify" / "templates").mkdir(parents=True, exist_ok=True)
    (tmp_path / "specs").mkdir(exist_ok=True)
    return tmp_path


@pytest.fixture
def ps_git_repo(tmp_path: Path) -> Path:
    """Create a temp git repo with PowerShell scripts and a BOM-prefixed template."""
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"], cwd=tmp_path, check=True
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"], cwd=tmp_path, check=True
    )
    subprocess.run(
        ["git", "commit", "--allow-empty", "-m", "init", "-q"],
        cwd=tmp_path,
        check=True,
    )
    ps_dir = tmp_path / "scripts" / "powershell"
    ps_dir.mkdir(parents=True)
    shutil.copy(CREATE_FEATURE_PS, ps_dir / "create-new-feature.ps1")
    common_ps = PROJECT_ROOT / "scripts" / "powershell" / "common.ps1"
    shutil.copy(common_ps, ps_dir / "common.ps1")
    templates_dir = tmp_path / ".specify" / "templates"
    templates_dir.mkdir(parents=True)
    # Write a BOM-prefixed template to ensure the WriteAllText fix is actually exercised.
    # If WriteAllText regresses, the output file will contain the BOM.
    bom = b"\xef\xbb\xbf"
    template_content = "# Feature Spec\n\nDescribe the feature here.\n"
    (templates_dir / "spec-template.md").write_bytes(bom + template_content.encode("utf-8"))
    return tmp_path


@pytest.fixture
def no_git_dir(tmp_path: Path) -> Path:
    """Create a temp directory without git, but with scripts."""
    scripts_dir = tmp_path / "scripts" / "bash"
    scripts_dir.mkdir(parents=True)
    shutil.copy(CREATE_FEATURE, scripts_dir / "create-new-feature.sh")
    shutil.copy(COMMON_SH, scripts_dir / "common.sh")
    (tmp_path / ".specify" / "templates").mkdir(parents=True)
    return tmp_path


def run_script(cwd: Path, *args: str) -> subprocess.CompletedProcess:
    """Run create-new-feature.sh with given args."""
    cmd = ["bash", "scripts/bash/create-new-feature.sh", *args]
    return subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
    )


def source_and_call(func_call: str, env: dict | None = None) -> subprocess.CompletedProcess:
    """Source common.sh and call a function."""
    cmd = f'source "{COMMON_SH}" && {func_call}'
    return subprocess.run(
        ["bash", "-c", cmd],
        capture_output=True,
        text=True,
        env={**os.environ, **(env or {})},
    )


# ── No-git Tests ─────────────────────────────────────────────────────────────


@requires_bash
class TestNoGitRejected:
    def test_no_git_rejected(self, no_git_dir: Path):
        """Without a git repository the branch-based script refuses to run."""
        result = run_script(no_git_dir)
        assert result.returncode != 0
        assert "could not read a Git repository" in result.stderr


# ── check_feature_branch Tests ───────────────────────────────────────────────


@requires_bash
class TestCoreCommonRemovesGitHelpers:
    def test_check_feature_branch_removed(self):
        result = source_and_call('declare -F check_feature_branch >/dev/null')
        assert result.returncode != 0

    def test_has_git_removed(self):
        result = source_and_call('declare -F has_git >/dev/null')
        assert result.returncode != 0


# ── find_feature_dir_by_prefix Tests ─────────────────────────────────────────


@requires_bash
class TestFindFeatureDirByPrefixRemoved:
    def test_find_feature_dir_by_prefix_removed(self):
        """Directory scanning helper is removed from core common.sh."""
        result = source_and_call('declare -F find_feature_dir_by_prefix >/dev/null')
        assert result.returncode != 0


# ── get_feature_paths + single-prefix integration ───────────────────────────


class TestGetFeaturePathsSinglePrefix:
    @requires_bash
    def test_bash_specify_feature_prefixed_requires_explicit_feature_context(
        self, tmp_path: Path
    ):
        """SPECIFY_FEATURE alone no longer triggers path lookup in bash."""
        (tmp_path / ".specify").mkdir()
        (tmp_path / "specs" / "001-target-spec").mkdir(parents=True)
        cmd = (
            f'cd "{tmp_path}" && export SPECIFY_FEATURE="feat/001-other" && '
            f'source "{COMMON_SH}" && get_feature_paths'
        )
        result = subprocess.run(
            ["bash", "-c", cmd],
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0
        assert "Feature directory not found" in result.stderr

    @pytest.mark.skipif(not _has_pwsh(), reason="pwsh not installed")
    def test_ps_specify_feature_prefixed_requires_explicit_feature_context(
        self, git_repo: Path
    ):
        """PowerShell also requires feature.json or SPECIFY_FEATURE_DIRECTORY."""
        common_ps = PROJECT_ROOT / "scripts" / "powershell" / "common.ps1"
        spec_dir = git_repo / "specs" / "001-ps-prefix-spec"
        spec_dir.mkdir(parents=True)
        ps_cmd = f'. "{common_ps}"; $r = Get-FeaturePathsEnv; Write-Output "FEATURE_DIR=$($r.FEATURE_DIR)"'
        result = subprocess.run(
            ["pwsh", "-NoProfile", "-Command", ps_cmd],
            cwd=git_repo,
            capture_output=True,
            text=True,
            env={**os.environ, "SPECIFY_FEATURE": "feat/001-other"},
        )
        assert result.returncode != 0
        assert "Feature directory not found" in (result.stderr + result.stdout)


# ── get_current_branch Tests ─────────────────────────────────────────────────


@requires_bash
class TestGetCurrentBranch:
    def test_env_var(self):
        """Test 12: get_current_branch returns SPECIFY_FEATURE env var."""
        result = source_and_call("get_current_branch", env={"SPECIFY_FEATURE": "my-custom-branch"})
        assert result.stdout.strip() == "my-custom-branch"


# ── Allow Existing Feature (PowerShell static guards) ────────────────────────


class TestAllowExistingFeaturePowerShell:
    def test_powershell_supports_allow_existing_feature_flag(self):
        """Static guard: PS script exposes -AllowExistingFeature with legacy alias."""
        contents = CREATE_FEATURE_PS.read_text(encoding="utf-8")
        assert "[switch]$AllowExistingFeature" in contents
        assert "[Alias('AllowExistingBranch')]" in contents

    def test_powershell_reuses_existing_feature_dir(self):
        """Static guard: PS script guards existing feature directories."""
        contents = CREATE_FEATURE_PS.read_text(encoding="utf-8")
        assert "Feature directory '$featureDir' already exists" in contents
        assert "-not $AllowExistingFeature" in contents

    @pytest.mark.skipif(
        os.name != "nt" or shutil.which("powershell.exe") is None,
        reason="Windows PowerShell not installed",
    )
    def test_ps_spec_file_written_without_bom(self, ps_git_repo: Path):
        """spec.md generated from a BOM-prefixed template must not contain a UTF-8 BOM.

        Branch-based contract: the feature is derived from the current git branch,
        so a valid feature branch must be checked out before invoking the script.
        """
        subprocess.run(
            ["git", "checkout", "-b", "001-bom-check"],
            cwd=ps_git_repo,
            check=True,
            capture_output=True,
        )
        script = ps_git_repo / "scripts" / "powershell" / "create-new-feature.ps1"
        result = subprocess.run(
            [
                "powershell.exe",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(script),
            ],
            cwd=ps_git_repo,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stderr

        spec_file = ps_git_repo / "specs" / "001-bom-check" / "spec.md"
        assert spec_file.is_file(), (
            f"spec.md was not created.\nstdout: {result.stdout}\nstderr: {result.stderr}"
        )

        raw = spec_file.read_bytes()
        assert not raw.startswith(b"\xef\xbb\xbf"), (
            f"spec.md must not start with a UTF-8 BOM — got first 3 bytes: {raw[:3]!r}"
        )
        # Verify template content was copied (not just an empty New-Item fallback)
        assert "Feature Spec" in raw.decode("utf-8"), (
            "spec.md does not contain template content — WriteAllText path was not exercised"
        )


# ── Git Extension Static Guards ──────────────────────────────────────────────


class TestGitExtensionParity:
    def test_bash_extension_surfaces_checkout_errors(self):
        """Static guard: git extension bash script preserves checkout stderr."""
        contents = EXT_CREATE_FEATURE.read_text(encoding="utf-8")
        assert 'switch_branch_error=$(git checkout -q "$BRANCH_NAME" 2>&1)' in contents
        assert "Failed to switch to existing branch '$BRANCH_NAME'" in contents

    def test_powershell_extension_surfaces_checkout_errors(self):
        """Static guard: git extension PowerShell script preserves checkout stderr."""
        contents = EXT_CREATE_FEATURE_PS.read_text(encoding="utf-8")
        assert "$switchBranchError = git checkout -q $branchName 2>&1 | Out-String" in contents
        assert "exists but could not be checked out.`n$($switchBranchError.Trim())" in contents


# ── GIT_BRANCH_NAME Override Tests ──────────────────────────────────────────


@requires_bash
class TestGitBranchNameOverrideBash:
    """Tests for GIT_BRANCH_NAME env var override in extension create-new-feature-branch.sh."""

    def _run_ext(self, ext_git_repo: Path, env_extras: dict, *extra_args: str):
        script = ext_git_repo / ".specify" / "extensions" / "git" / "scripts" / "bash" / "create-new-feature-branch.sh"
        cmd = ["bash", str(script), "--json", *extra_args, "ignored"]
        return subprocess.run(cmd, cwd=ext_git_repo, capture_output=True, text=True,
                              env={**os.environ, **env_extras})

    def test_exact_name_no_prefix(self, ext_git_repo: Path):
        """GIT_BRANCH_NAME is used verbatim with no numeric prefix added."""
        result = self._run_ext(ext_git_repo, {"GIT_BRANCH_NAME": "my-exact-branch"})
        assert result.returncode == 0, result.stderr
        data = json.loads(result.stdout)
        assert data["BRANCH_NAME"] == "my-exact-branch"
        assert data["FEATURE_NUM"] == "my-exact-branch"

    def test_sequential_prefix_extraction(self, ext_git_repo: Path):
        """FEATURE_NUM extracted from sequential-style prefix (digits before dash)."""
        result = self._run_ext(ext_git_repo, {"GIT_BRANCH_NAME": "042-custom-branch"})
        assert result.returncode == 0, result.stderr
        data = json.loads(result.stdout)
        assert data["BRANCH_NAME"] == "042-custom-branch"
        assert data["FEATURE_NUM"] == "042"

    def test_timestamp_prefix_extraction(self, ext_git_repo: Path):
        """FEATURE_NUM extracted as full YYYYMMDD-HHMMSS for timestamp-style names."""
        result = self._run_ext(ext_git_repo, {"GIT_BRANCH_NAME": "20260407-143022-my-feature"})
        assert result.returncode == 0, result.stderr
        data = json.loads(result.stdout)
        assert data["BRANCH_NAME"] == "20260407-143022-my-feature"
        assert data["FEATURE_NUM"] == "20260407-143022"

    def test_overlong_name_rejected(self, ext_git_repo: Path):
        """GIT_BRANCH_NAME exceeding 244 bytes is rejected with an error."""
        long_name = "a" * 245
        result = self._run_ext(ext_git_repo, {"GIT_BRANCH_NAME": long_name})
        assert result.returncode != 0
        assert "244" in result.stderr

    def test_dry_run_with_override(self, ext_git_repo: Path):
        """GIT_BRANCH_NAME works with --dry-run (no branch created)."""
        result = self._run_ext(ext_git_repo, {"GIT_BRANCH_NAME": "dry-run-override"}, "--dry-run")
        assert result.returncode == 0, result.stderr
        data = json.loads(result.stdout)
        assert data["BRANCH_NAME"] == "dry-run-override"
        assert data.get("DRY_RUN") is True
        branches = subprocess.run(
            ["git", "branch", "--list", "dry-run-override"],
            cwd=ext_git_repo, capture_output=True, text=True,
        )
        assert "dry-run-override" not in branches.stdout


@pytest.mark.skipif(not _has_pwsh(), reason="pwsh not installed")
class TestGitBranchNameOverridePowerShell:
    """Tests for GIT_BRANCH_NAME env var override in extension create-new-feature-branch.ps1."""

    def _run_ext(self, ext_ps_git_repo: Path, env_extras: dict):
        script = ext_ps_git_repo / ".specify" / "extensions" / "git" / "scripts" / "powershell" / "create-new-feature-branch.ps1"
        return subprocess.run(
            ["pwsh", "-NoProfile", "-File", str(script), "-Json", "ignored"],
            cwd=ext_ps_git_repo, capture_output=True, text=True,
            env={**os.environ, **env_extras},
        )

    def test_exact_name_no_prefix(self, ext_ps_git_repo: Path):
        """GIT_BRANCH_NAME is used verbatim with no numeric prefix added."""
        result = self._run_ext(ext_ps_git_repo, {"GIT_BRANCH_NAME": "ps-exact-branch"})
        assert result.returncode == 0, result.stderr
        data = json.loads(result.stdout)
        assert data["BRANCH_NAME"] == "ps-exact-branch"
        assert data["FEATURE_NUM"] == "ps-exact-branch"

    def test_sequential_prefix_extraction(self, ext_ps_git_repo: Path):
        """FEATURE_NUM extracted from sequential-style prefix."""
        result = self._run_ext(ext_ps_git_repo, {"GIT_BRANCH_NAME": "099-ps-numbered"})
        assert result.returncode == 0, result.stderr
        data = json.loads(result.stdout)
        assert data["BRANCH_NAME"] == "099-ps-numbered"
        assert data["FEATURE_NUM"] == "099"

    def test_timestamp_prefix_extraction(self, ext_ps_git_repo: Path):
        """FEATURE_NUM extracted as full YYYYMMDD-HHMMSS for timestamp-style names."""
        result = self._run_ext(ext_ps_git_repo, {"GIT_BRANCH_NAME": "20260407-143022-ps-feature"})
        assert result.returncode == 0, result.stderr
        data = json.loads(result.stdout)
        assert data["BRANCH_NAME"] == "20260407-143022-ps-feature"
        assert data["FEATURE_NUM"] == "20260407-143022"

    def test_overlong_name_rejected(self, ext_ps_git_repo: Path):
        """GIT_BRANCH_NAME exceeding 244 bytes is rejected."""
        long_name = "a" * 245
        result = self._run_ext(ext_ps_git_repo, {"GIT_BRANCH_NAME": long_name})
        assert result.returncode != 0
        assert "244" in result.stderr


# ── Feature Directory Resolution Tests ───────────────────────────────────────


class TestFeatureDirectoryResolution:
    """Tests for SPECIFY_FEATURE_DIRECTORY and .specify/feature.json resolution."""

    @requires_bash
    def test_env_var_overrides_branch_lookup(self, git_repo: Path):
        """SPECIFY_FEATURE_DIRECTORY env var takes priority over branch-based lookup."""
        custom_dir = git_repo / "my-custom-specs" / "my-feature"
        custom_dir.mkdir(parents=True)

        result = subprocess.run(
            ["bash", "-c", f'source "{COMMON_SH}" && get_feature_paths'],
            cwd=git_repo,
            capture_output=True,
            text=True,
            env={**os.environ, "SPECIFY_FEATURE_DIRECTORY": str(custom_dir)},
        )
        assert result.returncode == 0, result.stderr
        assert str(custom_dir) in result.stdout
        for line in result.stdout.splitlines():
            if line.startswith("FEATURE_DIR="):
                val = line.split("=", 1)[1].strip("'\"")
                assert val == str(custom_dir)
                break
        else:
            pytest.fail("FEATURE_DIR not found in output")

    @requires_bash
    def test_feature_json_overrides_branch_lookup(self, git_repo: Path):
        """feature.json feature_directory takes priority over branch-based lookup."""
        custom_dir = git_repo / "specs" / "custom-feature"
        custom_dir.mkdir(parents=True)

        feature_json = git_repo / ".specify" / "feature.json"
        feature_json.write_text(
            json.dumps({"feature_directory": str(custom_dir)}) + "\n",
            encoding="utf-8",
        )

        result = subprocess.run(
            ["bash", "-c", f'source "{COMMON_SH}" && get_feature_paths'],
            cwd=git_repo,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stderr
        for line in result.stdout.splitlines():
            if line.startswith("FEATURE_DIR="):
                val = line.split("=", 1)[1].strip("'\"")
                assert val == str(custom_dir)
                break
        else:
            pytest.fail("FEATURE_DIR not found in output")

    @requires_bash
    def test_env_var_takes_priority_over_feature_json(self, git_repo: Path):
        """Env var wins over feature.json."""
        env_dir = git_repo / "specs" / "env-feature"
        env_dir.mkdir(parents=True)
        json_dir = git_repo / "specs" / "json-feature"
        json_dir.mkdir(parents=True)

        feature_json = git_repo / ".specify" / "feature.json"
        feature_json.write_text(
            json.dumps({"feature_directory": str(json_dir)}) + "\n",
            encoding="utf-8",
        )

        result = subprocess.run(
            ["bash", "-c", f'source "{COMMON_SH}" && get_feature_paths'],
            cwd=git_repo,
            capture_output=True,
            text=True,
            env={**os.environ, "SPECIFY_FEATURE_DIRECTORY": str(env_dir)},
        )
        assert result.returncode == 0, result.stderr
        for line in result.stdout.splitlines():
            if line.startswith("FEATURE_DIR="):
                val = line.split("=", 1)[1].strip("'\"")
                assert val == str(env_dir)
                break
        else:
            pytest.fail("FEATURE_DIR not found in output")

    @requires_bash
    def test_errors_without_env_var_or_feature_json(self, git_repo: Path):
        """Without env var or feature.json, get_feature_paths now errors."""
        spec_dir = git_repo / "specs" / "001-test-feat"
        spec_dir.mkdir(parents=True)

        result = subprocess.run(
            ["bash", "-c", f'source "{COMMON_SH}" && get_feature_paths'],
            cwd=git_repo,
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0
        assert "Feature directory not found" in result.stderr

    @pytest.mark.skipif(not _has_pwsh(), reason="pwsh not installed")
    def test_ps_env_var_overrides_branch_lookup(self, git_repo: Path):
        """PowerShell: SPECIFY_FEATURE_DIRECTORY env var takes priority."""
        common_ps = PROJECT_ROOT / "scripts" / "powershell" / "common.ps1"
        custom_dir = git_repo / "my-custom-specs" / "ps-feature"
        custom_dir.mkdir(parents=True)

        ps_cmd = f'. "{common_ps}"; $r = Get-FeaturePathsEnv; Write-Output "FEATURE_DIR=$($r.FEATURE_DIR)"'
        result = subprocess.run(
            ["pwsh", "-NoProfile", "-Command", ps_cmd],
            cwd=git_repo,
            capture_output=True,
            text=True,
            env={**os.environ, "SPECIFY_FEATURE_DIRECTORY": str(custom_dir)},
        )
        assert result.returncode == 0, result.stderr
        for line in result.stdout.splitlines():
            if line.startswith("FEATURE_DIR="):
                val = line.split("=", 1)[1].strip("'\"")
                assert val == str(custom_dir)
                break
        else:
            pytest.fail("FEATURE_DIR not found in PowerShell output")

    @pytest.mark.skipif(not _has_pwsh(), reason="pwsh not installed")
    def test_ps_feature_json_overrides_branch_lookup(self, git_repo: Path):
        """PowerShell: feature.json takes priority over branch-based lookup."""
        common_ps = PROJECT_ROOT / "scripts" / "powershell" / "common.ps1"
        custom_dir = git_repo / "specs" / "ps-json-feature"
        custom_dir.mkdir(parents=True)

        feature_json = git_repo / ".specify" / "feature.json"
        feature_json.write_text(
            json.dumps({"feature_directory": str(custom_dir)}) + "\n",
            encoding="utf-8",
        )

        ps_cmd = f'. "{common_ps}"; $r = Get-FeaturePathsEnv; Write-Output "FEATURE_DIR=$($r.FEATURE_DIR)"'
        result = subprocess.run(
            ["pwsh", "-NoProfile", "-Command", ps_cmd],
            cwd=git_repo,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stderr
        for line in result.stdout.splitlines():
            if line.startswith("FEATURE_DIR="):
                val = line.split("=", 1)[1].strip("'\"")
                assert val == str(custom_dir)
                break
        else:
            pytest.fail("FEATURE_DIR not found in PowerShell output")


# ── Extension Description Quoting Tests (issue #2339) ────────────────────────


@requires_bash
class TestExtensionDescriptionQuoting:
    """Descriptions with quotes, apostrophes, and backslashes must not break the
    extension script. Regression tests for
    https://github.com/github/spec-kit/issues/2339
    """

    @pytest.mark.parametrize(
        "description",
        [
            "Add user's profile page",
            'Fix the "login" bug',
            "Handle path\\with\\backslashes",
            'It\'s a "complex" feature\\here',
        ],
        ids=["apostrophe", "double-quotes", "backslashes", "mixed"],
    )
    def test_ext_script_handles_special_chars(self, ext_git_repo: Path, description: str):
        """Extension create-new-feature-branch.sh succeeds with special characters in description."""
        script = (
            ext_git_repo
            / ".specify"
            / "extensions"
            / "git"
            / "scripts"
            / "bash"
            / "create-new-feature-branch.sh"
        )
        result = subprocess.run(
            ["bash", str(script), "--dry-run", "--short-name", "feat", description],
            cwd=ext_git_repo,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, (
            f"Script failed for description {description!r}: {result.stderr}"
        )
