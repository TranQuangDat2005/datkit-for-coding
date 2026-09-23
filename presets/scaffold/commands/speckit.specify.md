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

2. **Read the spec-template** to see the sections you need to fill.

3. **Write the specification** to SPEC_FILE, replacing the placeholders in each section
   (Overview, Requirements, Acceptance Criteria) with details from the user's description.
