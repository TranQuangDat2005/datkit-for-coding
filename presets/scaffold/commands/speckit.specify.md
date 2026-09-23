---
description: "Create a feature specification (preset override)"
scripts:
  sh: scripts/bash/create-new-feature.sh --json
  ps: scripts/powershell/create-new-feature.ps1 -Json
  py: scripts/python/create_new_feature.py --json
---

## User Input

```text
$ARGUMENTS
```

Given the feature description above:

1. **Create the feature files** by running the script (the CURRENT git branch
   name becomes the feature name; checkout a feature branch such as
   `003-user-auth` first):
   - `{SCRIPT}`
   - The JSON output contains FEATURE_NAME, FEATURE_DIR and SPEC_FILE paths.
   - If the script exits with code 3 and outputs
     `"ACTION": "ASK_USER_FOR_FEATURE_NAME"`, ask the user for a feature name
     (`003-user-auth`, `20260923-134500-user-auth`, or a bare kebab name such
     as `user-auth` which gets auto-numbered), then re-run with
     `--feature-name <name>` (`-FeatureName <name>` in PowerShell).

2. **Read the spec-template** to see the sections you need to fill.

3. **Write the specification** to SPEC_FILE, replacing the placeholders in each section
   (Overview, Requirements, Acceptance Criteria) with details from the user's description.
   Remove HTML comment blocks (`<!-- ... -->`) that only guide how to fill the template —
   the delivered spec is read by humans.
