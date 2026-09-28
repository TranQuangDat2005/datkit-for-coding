---
description: Create or update plan.md as the only planning artifact, using the active plan template, feature spec, and project context.
handoffs:
  - label: Create Tasks
    agent: speckit.tasks
    prompt: Break the plan into tasks
    send: true
  - label: Create Checklist
    agent: speckit.checklist
    prompt: Create a checklist for the following domain...

scripts:
  sh: scripts/bash/setup-plan.sh --json
  ps: scripts/powershell/setup-plan.ps1 -Json
  py: scripts/python/setup_plan.py --json
---

## User Input

```text
{ARGS}
```

You **MUST** consider the user input before proceeding (if not empty).

## Pre-Execution Checks

**Check for extension hooks (before planning)**:
- Check if `.specify/extensions.yml` exists in the project root.
- If it exists, read it and look for entries under the `hooks.before_plan` key
- If the YAML cannot be parsed or is invalid, do not skip silently: tell the user that `.specify/extensions.yml` could not be read (include the parser error) and that no hooks were checked, including any mandatory (`optional: false`) hooks registered there, then continue normally
- Filter out hooks where `enabled` is explicitly `false`. Treat hooks without an `enabled` field as enabled by default.
- For each remaining hook, do **not** attempt to interpret or evaluate hook `condition` expressions:
  - If the hook has no `condition` field, or it is null/empty, treat the hook as executable
  - If the hook defines a non-empty `condition`, skip the hook and leave condition evaluation to the HookExecutor implementation
- For each executable hook, output the following based on its `optional` flag:
  - **Optional hook** (`optional: true`):
    ```
    ## Extension Hooks

    **Optional Pre-Hook**: {extension}
    Command: `/{command}`
    Description: {description}

    Prompt: {prompt}
    To execute: `/{command}`
    ```
  - **Mandatory hook** (`optional: false`):
    ```
    ## Extension Hooks

    **Automatic Pre-Hook**: {extension}
    Executing: `/{command}`
    EXECUTE_COMMAND: {command}

    Wait for the result of the hook command before proceeding to the Outline.
    ```
    After emitting the block above you MUST actually invoke the hook and wait for it to finish before continuing. Run it the same way you would run the command yourself in this agent/session (the invocation may differ from the literal `{command}` id shown above, e.g. a skills-mode agent runs it as `/skill:speckit-...` or `$speckit-...`). Emitting the block alone does not run the hook.
- If no hooks are registered or `.specify/extensions.yml` does not exist, skip silently

## Outline

1. **Setup**: Run `{SCRIPT}` from repo root and parse JSON for FEATURE_SPEC, IMPL_PLAN, SPECS_DIR, BRANCH. For single quotes in args like "I'm Groot", use escape syntax: e.g 'I'\''m Groot' (or double-quote if possible: "I'm Groot").

2. **Load context**:
   - Read FEATURE_SPEC and `.specify/memory/constitution.md`.
   - Read project-level `AGENTS.md` if present.
   - Read project constraint/context files explicitly referenced by `AGENTS.md` or the constitution when they are relevant to planning.
   - Load IMPL_PLAN template (already copied).
   - Treat project-wide technology, conventions, approved dependencies, forbidden patterns, and architectural constraints as inherited context. Do not ask for or duplicate information that is already defined there.
   - If project-level context conflicts, the constitution is authoritative. Surface any unresolved conflict instead of silently choosing.

3. **Execute plan workflow**: IMPL_PLAN is an exact copy of the active `plan-template`. Follow its structure to:
   - Keep every heading from the template: do not add, remove, rename, or reorder sections; fill placeholders in place and never rewrite the template's own text. Sections that do not apply keep their heading with "N/A" and a one-line reason.
   - Fill **feature-specific** Technical Context using the inherited project context.
   - Do not repeat the project-wide tech stack unless this feature changes, extends, or depends on a specific part of it.
   - Mark only unresolved **feature-specific technical decisions** as "NEEDS CLARIFICATION".
   - Fill Constitution Check section from constitution.
   - Evaluate gates (ERROR if violations unjustified).
   - Resolve feature-specific technical decisions directly inside `plan.md`. Research only unresolved feature-specific unknowns or new technical choices; record decisions, rationale, and relevant alternatives in the existing template sections.
   - Record relevant data design, interface details, and validation approach directly in the appropriate `plan.md` sections.
   - Record remaining decisions requiring human input under Questions for Human. Keep the plan in DRAFT — REVIEW while these remain unresolved; do not invent answers or proceed to task generation.
   - Do not generate `research.md`, `data-model.md`, `contracts/`, `quickstart.md`, or `tasks.md`. The only planning artifact is `plan.md`; leave existing supplementary artifacts unchanged.
   - Re-evaluate Constitution Check before completing `plan.md`.
   - Comment cleanup: remove HTML comment blocks (`<!-- ... -->`) that only guide how to fill the template (yours or copied from the template) from `plan.md`. Deliverables are read by humans; keep only comments that carry real content.

## Mandatory Post-Execution Hooks

**You MUST complete this section before reporting completion to the user.**

Check if `.specify/extensions.yml` exists in the project root.
- If it does not exist, or no hooks are registered under `hooks.after_plan`, skip to the Completion Report.
- If it exists, read it and look for entries under the `hooks.after_plan` key.
- If the YAML cannot be parsed or is invalid, do not skip silently: tell the user that `.specify/extensions.yml` could not be read (include the parser error) and that no hooks were checked, including any mandatory (`optional: false`) hooks registered there, then continue to the Completion Report.
- Filter out hooks where `enabled` is explicitly `false`. Treat hooks without an `enabled` field as enabled by default.
- For each remaining hook, do **not** attempt to interpret or evaluate hook `condition` expressions:
  - If the hook has no `condition` field, or it is null/empty, treat the hook as executable
  - If the hook defines a non-empty `condition`, skip the hook and leave condition evaluation to the HookExecutor implementation
- For each executable hook, output the following based on its `optional` flag:
  - **Mandatory hook** (`optional: false`) — **You MUST emit `EXECUTE_COMMAND:` for each mandatory hook**:
    ```
    ## Extension Hooks

    **Automatic Hook**: {extension}
    Executing: `/{command}`
    EXECUTE_COMMAND: {command}
    ```
    After emitting the block above you MUST actually invoke the hook and wait for it to finish before continuing. Run it the same way you would run the command yourself in this agent/session (the invocation may differ from the literal `{command}` id shown above, e.g. a skills-mode agent runs it as `/skill:speckit-...` or `$speckit-...`). Emitting the block alone does not run the hook.
  - **Optional hook** (`optional: true`):
    ```
    ## Extension Hooks

    **Optional Hook**: {extension}
    Command: `/{command}`
    Description: {description}

    Prompt: {prompt}
    To execute: `/{command}`
    ```

## Completion Report

Command ends after `plan.md` is completed.

Report:

- branch
- IMPL_PLAN path

If Questions for Human contains unresolved decisions, state that the plan is a draft awaiting human input.

Do not generate additional planning artifacts.

## Key rules

- Use absolute paths for filesystem operations; use project-relative paths for references in documentation.
- Project-wide tech stack and conventions belong to project context (`AGENTS.md`, constitution, and referenced constraints); the plan should record only feature-specific technical decisions, additions, impacts, or deviations.
- Do not introduce a new framework, library, storage technology, architectural pattern, or external service when the project context already defines an approved approach unless the feature requires it and the plan explicitly justifies the deviation.
- Do not silently override project-level context. Surface conflicts or missing feature-specific decisions as NEEDS CLARIFICATION.
- ERROR on unjustified gate failures. Record unresolved human decisions in Questions for Human and report the plan as awaiting input.

## Done When

- [ ] `plan.md` completed using the active plan template
- [ ] Constitution checks completed
- [ ] All resolvable technical decisions recorded in `plan.md`
- [ ] Remaining human decisions recorded under Questions for Human
- [ ] No additional planning artifacts generated
- [ ] Extension hooks dispatched or skipped according to the rules in Mandatory Post-Execution Hooks above
- [ ] Completion reported with branch and plan path
