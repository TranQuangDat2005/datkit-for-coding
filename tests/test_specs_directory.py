"""Tests for the specs_directory setting in .specify/init-options.json.

Single source of truth for the project's specs directory: scripts must read
``specs_directory`` from init-options.json instead of hard-coding ``specs/``.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts" / "python"


def _load_module(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS_DIR / filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _load_common():
    return _load_module("cnf_common", "common.py")


def _load_create_new_feature():
    _load_module("cnf_common", "common.py")
    return _load_module("create_new_feature", "create_new_feature.py")


def _write_init_options(repo_root: Path, payload: dict) -> None:
    specify_dir = repo_root / ".specify"
    specify_dir.mkdir(parents=True, exist_ok=True)
    (specify_dir / "init-options.json").write_text(
        json.dumps(payload), encoding="utf-8"
    )


def _init_git_repo(repo_root: Path, branch: str = "001-user-auth") -> None:
    import subprocess as sp

    sp.run(["git", "init", "-q"], cwd=repo_root, check=True)
    sp.run(["git", "config", "user.email", "test@example.com"], cwd=repo_root, check=True)
    sp.run(["git", "config", "user.name", "Test"], cwd=repo_root, check=True)
    sp.run(["git", "checkout", "-q", "-b", branch], cwd=repo_root, check=True)


class TestResolveSpecsDirectory:
    @pytest.mark.parametrize(
        ("payload", "expected"),
        [
            ({}, "specs"),
            ({"specs_directory": "backend/specs"}, "backend/specs"),
            ({"specs_directory": " backend/specs "}, "backend/specs"),
            ({"specs_directory": "backend\\specs"}, "backend/specs"),
            ({"specs_directory": "backend/specs/"}, "backend/specs"),
            ({"specs_directory": ""}, "specs"),
            ({"specs_directory": "   "}, "specs"),
            ({"specs_directory": None}, "specs"),
            ({"specs_directory": 42}, "specs"),
            ({"specs_directory": "/abs/specs"}, "specs"),
            ({"specs_directory": "C:/abs/specs"}, "specs"),
            ({"specs_directory": "../outside/specs"}, "specs"),
            ({"specs_directory": "a/../b"}, "specs"),
            ({"other": "value"}, "specs"),
        ],
    )
    def test_resolution(self, tmp_path: Path, payload: dict, expected: str) -> None:
        common = _load_common()
        if payload:
            _write_init_options(tmp_path, payload)
        assert common.resolve_specs_directory(tmp_path) == expected

    def test_missing_file_defaults_to_specs(self, tmp_path: Path) -> None:
        common = _load_common()
        assert common.resolve_specs_directory(tmp_path) == "specs"

    def test_malformed_json_defaults_to_specs(self, tmp_path: Path) -> None:
        common = _load_common()
        specify_dir = tmp_path / ".specify"
        specify_dir.mkdir()
        (specify_dir / "init-options.json").write_text("{broken", encoding="utf-8")
        assert common.resolve_specs_directory(tmp_path) == "specs"


class TestCreateNewFeatureUsesConfiguredDirectory:
    def test_creates_feature_under_configured_specs_directory(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        _init_git_repo(tmp_path)
        _write_init_options(
            tmp_path,
            {
                "here": True,
                "specs_directory": "k-market-internal-management-system-backend/specs",
            },
        )
        monkeypatch.chdir(tmp_path)

        module = _load_create_new_feature()
        exit_code = module.main(["--json", "--dry-run"])
        assert exit_code == 0

    def test_script_creates_files_in_custom_directory(self, tmp_path: Path) -> None:
        _init_git_repo(tmp_path)
        custom_rel = "backend/specs"
        _write_init_options(tmp_path, {"specs_directory": custom_rel})

        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "create_new_feature.py"), "--json"],
            cwd=tmp_path,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        assert result.returncode == 0, result.stderr

        payload = None
        for line in result.stdout.splitlines():
            if line.startswith("{"):
                payload = json.loads(line)
                break
        assert payload is not None
        assert payload["FEATURE_DIR"].replace("\\", "/").endswith(
            f"{custom_rel}/001-user-auth"
        )

        feature_json = json.loads(
            (tmp_path / ".specify" / "feature.json").read_text(encoding="utf-8")
        )
        assert feature_json["feature_directory"] == f"{custom_rel}/001-user-auth"
        assert (tmp_path / custom_rel / "001-user-auth" / "spec.md").is_file()

    def test_default_directory_unchanged(self, tmp_path: Path) -> None:
        _init_git_repo(tmp_path)
        # An initialized project always carries .specify; without it the
        # script's repo-root resolver would walk up to the outer repo.
        _write_init_options(tmp_path, {"here": True})

        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "create_new_feature.py"), "--json"],
            cwd=tmp_path,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        assert result.returncode == 0, result.stderr

        assert (tmp_path / "specs" / "001-user-auth" / "spec.md").is_file()
        feature_json = json.loads(
            (tmp_path / ".specify" / "feature.json").read_text(encoding="utf-8")
        )
        assert feature_json["feature_directory"] == "specs/001-user-auth"
