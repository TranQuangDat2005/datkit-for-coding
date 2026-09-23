#!/usr/bin/env bash
# Create Spec Kit feature files from the CURRENT Git branch.
#
# IMPORTANT:
# - This script DOES NOT create, switch, rename, merge, or delete Git branches.
# - Git branch management is external to this script.
# - The current Git branch name becomes the Spec Kit feature name.
#
# Example:
#   Current Git branch: 003-user-auth
#   FEATURE_NAME:       003-user-auth
#   FEATURE_DIR:        specs/003-user-auth

set -e

# Parse command line arguments
JSON_MODE=false
DRY_RUN=false
ALLOW_EXISTING=false

for arg in "$@"; do
    case "$arg" in
        --json)
            JSON_MODE=true
            ;;
        --dry-run)
            DRY_RUN=true
            ;;
        --allow-existing-feature|--allow-existing-branch)
            ALLOW_EXISTING=true
            ;;
        --help|-h)
            echo "Usage: $0 [--json] [--dry-run] [--allow-existing-feature]"
            echo ""
            echo "Purpose:"
            echo "  Read the current Git branch name and create the matching Spec Kit feature directory."
            echo ""
            echo "This script DOES NOT manage Git."
            echo "It never creates, switches, renames, merges, or deletes branches."
            echo ""
            echo "Expected branch examples:"
            echo "  003-user-auth"
            echo "  014-product-review"
            echo "  20260923-134500-payment-flow"
            echo ""
            echo "Options:"
            echo "  --json                    Output machine-readable JSON"
            echo "  --dry-run                 Compute names/paths without creating files"
            echo "  --allow-existing-feature  Reuse an existing feature directory"
            echo "  --allow-existing-branch   Deprecated alias for --allow-existing-feature"
            echo "  --help, -h                Show this help message"
            exit 0
            ;;
        *)
            # Unexpected positional/unknown arguments are ignored (parity with
            # the PowerShell variant).
            ;;
    esac
done

# Shared Spec Kit helpers.
SCRIPT_DIR="$(CDPATH="" cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

REPO_ROOT=$(get_repo_root) || exit 1

cd "$REPO_ROOT"

# Git is used only to READ repository/branch state.
inside_git_status=0
inside_git_output=$(git rev-parse --is-inside-work-tree 2>/dev/null) || inside_git_status=$?
inside_git="${inside_git_output%%$'\n'*}"
inside_git="${inside_git#"${inside_git%%[![:space:]]*}"}"
inside_git="${inside_git%"${inside_git##*[![:space:]]}"}"

if [ "$inside_git_status" -ne 0 ] || [ "$inside_git" != "true" ]; then
    echo "Spec Kit could not read a Git repository. Select/open the project repository first." >&2
    exit 1
fi

branch_status=0
branch_output=$(git branch --show-current 2>/dev/null) || branch_status=$?
current_branch="${branch_output%%$'\n'*}"
current_branch="${current_branch#"${current_branch%%[![:space:]]*}"}"
current_branch="${current_branch%"${current_branch##*[![:space:]]}"}"

if [ "$branch_status" -ne 0 ] || [ -z "$current_branch" ]; then
    echo "Spec Kit could not determine the current Git branch. Checkout a feature branch first." >&2
    exit 1
fi

# Keep branch name and feature directory basename identical.
# Branch names containing '/' or '\' are rejected instead of rewritten.
case "$current_branch" in
    */*|*\\*)
        echo "Current Git branch '$current_branch' contains a path separator. Spec Kit requires a single feature name such as '003-user-auth' so the branch name and feature directory basename remain identical." >&2
        exit 1
        ;;
esac

# Spec Kit feature branches must carry their feature identifier.
#
# Supported:
#   sequential: NNN-short-name
#   timestamp:  YYYYMMDD-HHMMSS-short-name
#
# The suffix must be kebab-like: words separated by single hyphens.
NUMBERING_MODE=""
FEATURE_NUM=""
name_part_pattern='[A-Za-z0-9]+(-[A-Za-z0-9]+)*'
timestamp_branch_pattern="^([0-9]{8}-[0-9]{6})-($name_part_pattern)$"
sequential_branch_pattern="^([0-9]{3,})-($name_part_pattern)$"

if [[ "$current_branch" =~ $timestamp_branch_pattern ]]; then
    NUMBERING_MODE="timestamp"
    FEATURE_NUM="${BASH_REMATCH[1]}"
elif [[ "$current_branch" =~ $sequential_branch_pattern ]]; then
    NUMBERING_MODE="sequential"
    FEATURE_NUM="${BASH_REMATCH[1]}"
else
    echo "Current Git branch '$current_branch' is not a Spec Kit feature branch. Expected '003-user-auth' or 'YYYYMMDD-HHMMSS-user-auth'." >&2
    exit 1
fi

FEATURE_NAME="$current_branch"
BRANCH_NAME="$current_branch"

SPECS_DIR="$REPO_ROOT/specs"
FEATURE_DIR="$SPECS_DIR/$FEATURE_NAME"
SPEC_FILE="$FEATURE_DIR/spec.md"

feature_dir_exists=false
spec_exists=false
if [ -d "$FEATURE_DIR" ]; then
    feature_dir_exists=true
fi
if [ -f "$SPEC_FILE" ]; then
    spec_exists=true
fi

if [ "$feature_dir_exists" = true ] && [ "$ALLOW_EXISTING" != true ]; then
    echo "Feature directory '$FEATURE_DIR' already exists. Use --allow-existing-feature only when intentionally reopening the same feature." >&2
    exit 1
fi

if [ "$DRY_RUN" != true ]; then
    SPEC_TEMPLATE_CONTENT=""
    SPEC_TEMPLATE_FOUND=false
    if [ "$spec_exists" != true ]; then
        if SPEC_TEMPLATE_CONTENT=$(resolve_template_content "spec-template" "$REPO_ROOT"; status=$?; printf x; exit "$status"); then
            SPEC_TEMPLATE_CONTENT="${SPEC_TEMPLATE_CONTENT%x}"
            SPEC_TEMPLATE_FOUND=true
        else
            resolve_status=$?
            if [ "$resolve_status" -ne 1 ]; then
                exit "$resolve_status"
            fi
        fi
    fi

    mkdir -p "$SPECS_DIR"
    mkdir -p "$FEATURE_DIR"

    if [ "$spec_exists" != true ]; then
        if [ "$SPEC_TEMPLATE_FOUND" = true ]; then
            printf '%s' "$SPEC_TEMPLATE_CONTENT" > "$SPEC_FILE"
        else
            echo "[specify] Warning: spec-template was not found; created an empty spec.md." >&2
            touch "$SPEC_FILE"
        fi
    fi

    # Downstream Spec Kit commands resolve the active feature from feature.json.
    _persist_feature_json "$REPO_ROOT" "$FEATURE_DIR"

    # Convenience values for commands executed in this shell process.
    SPECIFY_FEATURE="$FEATURE_NAME"
    SPECIFY_FEATURE_DIRECTORY="$FEATURE_DIR"
    export SPECIFY_FEATURE SPECIFY_FEATURE_DIRECTORY
fi

if $JSON_MODE; then
    if has_jq; then
        if [ "$DRY_RUN" = true ]; then
            jq -cn \
                --arg feature_name "$FEATURE_NAME" \
                --arg branch_name "$BRANCH_NAME" \
                --arg feature_num "$FEATURE_NUM" \
                --arg feature_dir "$FEATURE_DIR" \
                --arg spec_file "$SPEC_FILE" \
                --arg numbering_mode "$NUMBERING_MODE" \
                '{FEATURE_NAME:$feature_name,BRANCH_NAME:$branch_name,FEATURE_NUM:$feature_num,FEATURE_DIR:$feature_dir,SPEC_FILE:$spec_file,NUMBERING_MODE:$numbering_mode,DRY_RUN:true}'
        else
            jq -cn \
                --arg feature_name "$FEATURE_NAME" \
                --arg branch_name "$BRANCH_NAME" \
                --arg feature_num "$FEATURE_NUM" \
                --arg feature_dir "$FEATURE_DIR" \
                --arg spec_file "$SPEC_FILE" \
                --arg numbering_mode "$NUMBERING_MODE" \
                '{FEATURE_NAME:$feature_name,BRANCH_NAME:$branch_name,FEATURE_NUM:$feature_num,FEATURE_DIR:$feature_dir,SPEC_FILE:$spec_file,NUMBERING_MODE:$numbering_mode}'
        fi
    else
        if [ "$DRY_RUN" = true ]; then
            printf '{"FEATURE_NAME":"%s","BRANCH_NAME":"%s","FEATURE_NUM":"%s","FEATURE_DIR":"%s","SPEC_FILE":"%s","NUMBERING_MODE":"%s","DRY_RUN":true}\n' \
                "$(json_escape "$FEATURE_NAME")" "$(json_escape "$BRANCH_NAME")" "$(json_escape "$FEATURE_NUM")" "$(json_escape "$FEATURE_DIR")" "$(json_escape "$SPEC_FILE")" "$(json_escape "$NUMBERING_MODE")"
        else
            printf '{"FEATURE_NAME":"%s","BRANCH_NAME":"%s","FEATURE_NUM":"%s","FEATURE_DIR":"%s","SPEC_FILE":"%s","NUMBERING_MODE":"%s"}\n' \
                "$(json_escape "$FEATURE_NAME")" "$(json_escape "$BRANCH_NAME")" "$(json_escape "$FEATURE_NUM")" "$(json_escape "$FEATURE_DIR")" "$(json_escape "$SPEC_FILE")" "$(json_escape "$NUMBERING_MODE")"
        fi
    fi
else
    echo "FEATURE_NAME: $FEATURE_NAME"
    echo "BRANCH_NAME: $BRANCH_NAME"
    echo "FEATURE_NUM: $FEATURE_NUM"
    echo "FEATURE_DIR: $FEATURE_DIR"
    echo "SPEC_FILE: $SPEC_FILE"
    echo "NUMBERING_MODE: $NUMBERING_MODE"
fi
