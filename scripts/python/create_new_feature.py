#!/usr/bin/env python3
"""Create Spec Kit feature files from the CURRENT Git branch.

IMPORTANT:
- This script DOES NOT create, switch, rename, merge, or delete Git branches.
- Git branch management is external to this script.
- The current Git branch name becomes the Spec Kit feature name.

Example:
  Current Git branch: 003-user-auth
  FEATURE_NAME:       003-user-auth
  FEATURE_DIR:        specs/003-user-auth
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

try:
    from common import (
        TemplateResolutionError,
        get_repo_root,
        persist_feature_json,
        resolve_template_content,
    )
except ImportError:  # pragma: no cover - direct execution from unusual cwd
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from common import (
        TemplateResolutionError,
        get_repo_root,
        persist_feature_json,
        resolve_template_content,
    )


def _json_line(payload: object) -> str:
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n"


# Spec Kit feature branches must carry their feature identifier.
#
# Supported:
#   sequential: NNN-short-name
#   timestamp:  YYYYMMDD-HHMMSS-short-name
#
# The suffix must be kebab-like: words separated by single hyphens.
_NAME_PART_PATTERN = r"[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*"
_TIMESTAMP_BRANCH_PATTERN = re.compile(
    rf"^(\d{{8}}-\d{{6}})-({_NAME_PART_PATTERN})$"
)
_SEQUENTIAL_BRANCH_PATTERN = re.compile(rf"^(\d{{3,}})-({_NAME_PART_PATTERN})$")


def _usage(argv0: str) -> str:
    return (
        f"Usage: {argv0} [--json] [--dry-run] [--allow-existing-feature] [--help]"
    )


def _help_text(argv0: str) -> str:
    return f"""{_usage(argv0)}

Purpose:
  Read the current Git branch name and create the matching Spec Kit feature directory.

This script DOES NOT manage Git.
It never creates, switches, renames, merges, or deletes branches.

Expected branch examples:
  003-user-auth
  014-product-review
  20260923-134500-payment-flow

Options:
  --json                   Output machine-readable JSON
  --dry-run                Compute names/paths without creating files
  --allow-existing-feature Reuse an existing feature directory
  --help, -h               Show this help message
"""


@dataclass(frozen=True)
class Args:
    json_mode: bool = False
    dry_run: bool = False
    allow_existing: bool = False


def _parse_args(argv: list[str], argv0: str) -> Args:
    json_mode = False
    dry_run = False
    allow_existing = False

    for arg in argv:
        if arg == "--json":
            json_mode = True
        elif arg == "--dry-run":
            dry_run = True
        elif arg in {"--allow-existing-feature", "--allow-existing-branch"}:
            # --allow-existing-branch is a deprecated alias kept for back-compat.
            allow_existing = True
        elif arg in {"--help", "-h"}:
            sys.stdout.write(_help_text(argv0))
            raise SystemExit(0)
        else:
            print(f"Error: Unexpected argument '{arg}'", file=sys.stderr)
            print(_usage(argv0), file=sys.stderr)
            raise SystemExit(1)

    return Args(
        json_mode=json_mode,
        dry_run=dry_run,
        allow_existing=allow_existing,
    )


def _run_git(
    arguments: list[str], repo_root: Path
) -> subprocess.CompletedProcess | None:
    """Run a read-only git command from the repo root; None if git is unavailable."""
    try:
        return subprocess.run(
            ["git", *arguments],
            capture_output=True,
            check=False,
            cwd=str(repo_root),
        )
    except OSError:
        return None


def _is_inside_git_work_tree(repo_root: Path) -> bool:
    completed = _run_git(["rev-parse", "--is-inside-work-tree"], repo_root)
    if completed is None or completed.returncode != 0:
        return False
    lines = completed.stdout.decode("utf-8", errors="replace").splitlines()
    return bool(lines) and lines[0].strip() == "true"


def _get_current_branch(repo_root: Path) -> str:
    completed = _run_git(["branch", "--show-current"], repo_root)
    if completed is None or completed.returncode != 0:
        return ""
    lines = completed.stdout.decode("utf-8", errors="replace").splitlines()
    return lines[0].strip() if lines else ""


def main(argv: list[str] | None = None) -> int:
    argv0 = sys.argv[0]
    args = _parse_args(list(argv if argv is not None else sys.argv[1:]), argv0)

    repo_root = get_repo_root(Path(__file__))

    # Git is used only to READ repository/branch state.
    if not _is_inside_git_work_tree(repo_root):
        print(
            "Spec Kit could not read a Git repository. "
            "Select/open the project repository first.",
            file=sys.stderr,
        )
        return 1

    current_branch = _get_current_branch(repo_root)
    if not current_branch:
        print(
            "Spec Kit could not determine the current Git branch. "
            "Checkout a feature branch first.",
            file=sys.stderr,
        )
        return 1

    # Keep branch name and feature directory basename identical.
    # Branch names containing '/' or '\' are rejected instead of rewritten.
    if "/" in current_branch or "\\" in current_branch:
        print(
            f"Current Git branch '{current_branch}' contains a path separator. "
            "Spec Kit requires a single feature name such as '003-user-auth' "
            "so the branch name and feature directory basename remain identical.",
            file=sys.stderr,
        )
        return 1

    # The timestamp pattern is checked first so '20260923-134500-user-auth'
    # (whose leading '20260923' also satisfies \d{3,}) is not mistaken for a
    # sequential feature number.
    timestamp_match = _TIMESTAMP_BRANCH_PATTERN.match(current_branch)
    sequential_match = _SEQUENTIAL_BRANCH_PATTERN.match(current_branch)

    if timestamp_match is not None:
        numbering_mode = "timestamp"
        feature_num = timestamp_match.group(1)
    elif sequential_match is not None:
        numbering_mode = "sequential"
        feature_num = sequential_match.group(1)
    else:
        print(
            f"Current Git branch '{current_branch}' is not a Spec Kit feature "
            "branch. Expected '003-user-auth' or 'YYYYMMDD-HHMMSS-user-auth'.",
            file=sys.stderr,
        )
        return 1

    feature_name = current_branch
    branch_name = current_branch

    specs_dir = repo_root / "specs"
    feature_dir = specs_dir / feature_name
    spec_file = feature_dir / "spec.md"

    feature_dir_exists = feature_dir.is_dir()
    spec_exists = spec_file.is_file()

    if feature_dir_exists and not args.allow_existing:
        print(
            f"Feature directory '{feature_dir}' already exists. "
            "Use --allow-existing-feature only when intentionally reopening "
            "the same feature.",
            file=sys.stderr,
        )
        return 1

    if not args.dry_run:
        template_content: str | None = None

        if not spec_exists:
            try:
                template_content = resolve_template_content(
                    "spec-template", repo_root
                )
            except TemplateResolutionError as exc:
                print(f"Error: {exc}", file=sys.stderr)
                return 1

        specs_dir.mkdir(parents=True, exist_ok=True)
        feature_dir.mkdir(parents=True, exist_ok=True)

        if not spec_exists:
            if template_content is not None:
                spec_file.write_bytes(template_content.encode("utf-8"))
            else:
                print(
                    "[specify] Warning: spec-template was not found; "
                    "created an empty spec.md.",
                    file=sys.stderr,
                )
                spec_file.touch()

        # Downstream Spec Kit commands resolve the active feature from feature.json.
        persist_feature_json(repo_root, f"specs/{feature_name}")

        # Convenience values for commands executed in this Python process.
        os.environ["SPECIFY_FEATURE"] = feature_name
        os.environ["SPECIFY_FEATURE_DIRECTORY"] = str(feature_dir)

    if args.json_mode:
        payload: dict[str, object] = {
            "FEATURE_NAME": feature_name,
            "BRANCH_NAME": branch_name,
            "FEATURE_NUM": feature_num,
            "FEATURE_DIR": str(feature_dir),
            "SPEC_FILE": str(spec_file),
            "NUMBERING_MODE": numbering_mode,
        }
        if args.dry_run:
            payload["DRY_RUN"] = True
        sys.stdout.write(_json_line(payload))
    else:
        print(f"FEATURE_NAME: {feature_name}")
        print(f"BRANCH_NAME: {branch_name}")
        print(f"FEATURE_NUM: {feature_num}")
        print(f"FEATURE_DIR: {feature_dir}")
        print(f"SPEC_FILE: {spec_file}")
        print(f"NUMBERING_MODE: {numbering_mode}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
