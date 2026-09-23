<div align="center">
    <img src="./media/datkit-logo.svg" alt="Dat Kit Logo" width="180" height="180"/>
    <h1>🧰 Dat Kit</h1>
    <h3><em>Define what to build before building it — with any AI coding agent.</em></h3>
</div>

<p align="center">
    <strong>A spec-driven development toolkit for building high-quality software with any AI coding agent — a ready-to-use spec-driven process (or bring your own), endlessly extensible via extensions, presets, and bundles.</strong>
</p>

<p align="center">
    <a href="https://github.com/TranQuangDat2005/datkit-for-coding/stargazers"><img src="https://img.shields.io/github/stars/TranQuangDat2005/datkit-for-coding?style=social" alt="GitHub stars"/></a>
    <a href="https://github.com/TranQuangDat2005/datkit-for-coding/blob/main/LICENSE"><img src="https://img.shields.io/github/license/TranQuangDat2005/datkit-for-coding" alt="License"/></a>
    <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.11%2B-blue" alt="Python 3.11+"/></a>
    <a href="https://github.com/github/spec-kit"><img src="https://img.shields.io/badge/fork%20of-Spec%20Kit-2ea043" alt="Fork of Spec Kit"/></a>
</p>

> [!NOTE]
> **About Dat Kit**
>
> Dat Kit is an independent distribution based on [GitHub Spec Kit](https://github.com/github/spec-kit) (MIT). It keeps the full spec-driven workflow — commands, templates, extensions, presets, bundles — under its own name and version line, installed from this repository.
>
> Differences from upstream: the package is named `spec-datkit`, releases are cut from this repo, and the built-in `specify self upgrade` path is disabled (upgrading would pull the original upstream package). To update, reinstall from this repository — see [Get Started](#-get-started).

---

## Table of Contents

- [🤔 What is Spec-Driven Development?](#-what-is-spec-driven-development)
- [🐞 Bug Fixing with Dat Kit](#-bug-fixing-with-dat-kit)
- [💡 Assessing Ideas with Dat Kit](#-assessing-ideas-with-dat-kit)
- [⚡ Get Started](#-get-started)
- [🌍 Community](#-community)
- [🤖 Supported AI Coding Agent Integrations](#-supported-ai-coding-agent-integrations)
- [Available Slash Commands](#available-slash-commands)
- [🔧 Dat Kit CLI Reference](#-dat-kit-cli-reference)
- [🧩 Making Dat Kit Your Own: Extensions & Presets](#-making-dat-kit-your-own-extensions--presets)
- [📦 Bundles: Role-Based Setups](#-bundles-role-based-setups)
- [📚 Core Philosophy](#-core-philosophy)
- [🌟 Development Phases](#-development-phases)
- [🔧 Prerequisites](#-prerequisites)
- [📖 Learn More](#-learn-more)
- [💬 Support](#-support)
- [🙏 Acknowledgements](#-acknowledgements)
- [📄 License](#-license)

## 🤔 What is Spec-Driven Development?

Spec-Driven Development (SDD) is a methodology where **specifications guide AI coding agents** through a structured development process. Instead of prompting an AI to write code immediately, you first build clear, structured requirements — then let the agent work through them step by step.

Dat Kit gives you the complete scaffolding for this workflow: templates, slash commands, and scripts that work with your favorite AI coding agent.

### SDD Quickstart

```bash
# Install Dat Kit (requires uv: https://docs.astral.sh/uv/)
uv tool install spec-datkit --from git+https://github.com/TranQuangDat2005/datkit-for-coding.git

# Bootstrap a project for Spec-Driven Development
specify init my-project --integration copilot
cd my-project

# Create your project's principles, then work through the spec workflow
/speckit.constitution Create principles focused on code quality and testing standards
/speckit.specify Build a photo organizer app with drag-and-drop albums
/speckit.plan Use Vite with vanilla HTML, CSS, and JavaScript; store metadata in SQLite
/speckit.tasks
/speckit.implement
```

## 🐞 Bug Fixing with Dat Kit

Dat Kit includes a structured bug-fixing workflow (via the `bug` extension) that mirrors the SDD process: reproduce and assess the bug, write a failing test, then fix it.

### Bug Fix Quickstart

```bash
uv tool install spec-datkit --from git+https://github.com/TranQuangDat2005/datkit-for-coding.git
specify init my-project --integration copilot
cd my-project
specify extension add bug
```

Then use `/speckit.bug.assess`, `/speckit.bug.fix`, and `/speckit.bug.test` in your agent.

## 💡 Assessing Ideas with Dat Kit

Before committing to a feature, run it through the structured assessment workflow (via the `assess` extension): intake, research, shaping, and a clear go/no-go decision.

### Idea Assessment Quickstart

```bash
uv tool install spec-datkit --from git+https://github.com/TranQuangDat2005/datkit-for-coding.git
specify init my-project --integration copilot
cd my-project
specify extension add assess
```

Then use `/speckit.assess.intake` → `/speckit.assess.research` → `/speckit.assess.shape` → `/speckit.assess.decide`.

## ⚡ Get Started

### 1. Install the Dat Kit CLI

Requires **[uv](https://docs.astral.sh/uv/)** ([install uv](./docs/install/uv.md)) and Python 3.11+:

```bash
uv tool install spec-datkit --from git+https://github.com/TranQuangDat2005/datkit-for-coding.git
```

Try it without a persistent install:

```bash
uvx --from git+https://github.com/TranQuangDat2005/datkit-for-coding.git specify init my-project --integration copilot
```

Or with pipx:

```bash
pipx install git+https://github.com/TranQuangDat2005/datkit-for-coding.git
```

This installs the CLI under both the `specify` and `specdat` commands.

### 2. Initialize a project

```bash
specify init my-project --integration copilot
cd my-project
```

For CI or AI agent harnesses (no keyboard, or a PTY that cannot send arrow keys), pass `--non-interactive` so init never hangs on a picker. Combine with `--force` when initializing into a non-empty directory:

```bash
specify init my-project --non-interactive --ignore-agent-tools
specify init --here --force --non-interactive --integration claude
```

### 3. Establish project principles

Launch your coding agent in the project directory. Most agents expose Dat Kit as `/speckit.*` slash commands; Codex CLI and Command Code in skills mode use `$speckit-*` instead; GitHub Copilot CLI uses `/agents` to select the agent or address it directly in a prompt.

Use the **`/speckit.constitution`** command to create your project's governing principles and development guidelines that will guide all subsequent development.

```bash
/speckit.constitution Create principles focused on code quality, testing standards, user experience consistency, and performance requirements
```

### 4. Create the spec

Use the **`/speckit.specify`** command to describe what you want to build. Focus on the **what** and **why**, not the tech stack.

```bash
/speckit.specify Build an application that can help me organize my photos in separate photo albums. Albums are grouped by date and can be re-organized by dragging and dropping on the main page. Albums are never in other nested albums. Within each album, photos are previewed in a tile-like interface.
```

### 5. Create a technical implementation plan

Use the **`/speckit.plan`** command to provide your tech stack and architecture choices.

```bash
/speckit.plan The application uses Vite with minimal number of libraries. Use vanilla HTML, CSS, and JavaScript as much as possible. Images are not uploaded anywhere and metadata is stored in a local SQLite database.
```

### 6. Break down into tasks

Use **`/speckit.tasks`** to create an actionable task list from your implementation plan.

```bash
/speckit.tasks
```

### 7. Execute implementation

Use **`/speckit.implement`** to execute all tasks and build your feature according to the plan.

```bash
/speckit.implement
```

For detailed step-by-step instructions, see the [comprehensive guide](./spec-driven.md).

### Updating Dat Kit

`specify self check` reports the installed version (update checks against upstream GitHub releases are disabled in this build; `specify self upgrade` intentionally does nothing and exits with an error). To update, reinstall from this repository:

```bash
uv tool install --force spec-datkit --from git+https://github.com/TranQuangDat2005/datkit-for-coding.git
```

## 🌍 Community

Dat Kit resolves extension, preset, workflow, and bundle catalogs from the upstream [Spec Kit community](https://github.github.io/spec-kit/):

- [Extensions](https://github.github.io/spec-kit/community/extensions.html) — commands, hooks, and capabilities
- [Presets](https://github.github.io/spec-kit/community/presets.html) — template and terminology overrides
- [Bundles](https://github.github.io/spec-kit/community/bundles.html) — role and team stacks composed from existing components
- [Walkthroughs](https://github.github.io/spec-kit/community/walkthroughs.html) — end-to-end SDD scenarios

> [!NOTE]
> Community contributions are independently created and maintained by their respective authors. Review source code before installation and use at your own discretion.

For authoring your own components, see the [Extension Publishing Guide](extensions/EXTENSION-PUBLISHING-GUIDE.md), the [Presets Publishing Guide](presets/PUBLISHING.md), or the [Community Bundles guide](docs/community/bundles.md).

## 🤖 Supported AI Coding Agent Integrations

Dat Kit works with 30+ AI coding agents — both CLI tools and IDE-based assistants. See the full list with notes and usage details in the upstream [Supported AI Coding Agent Integrations](https://github.github.io/spec-kit/reference/integrations.html) guide.

Run `specify integration list` to see all available integrations in your installed version.

## Available Slash Commands

After running `specify init`, your AI coding agent will have access to these slash commands for structured development. For integrations that support skills mode, passing `--integration <agent> --integration-options="--skills"` installs agent skills instead of slash-command prompt files.

### Core Commands

Essential commands for the Spec-Driven Development workflow:

| Command                  | Agent Skill            | Description                                                                |
| ------------------------ | ---------------------- | -------------------------------------------------------------------------- |
| `/speckit.constitution`  | `speckit-constitution` | Create or update project governing principles and development guidelines   |
| `/speckit.specify`       | `speckit-specify`      | Define what you want to build (requirements and user stories)              |
| `/speckit.plan`          | `speckit-plan`         | Create technical implementation plans with your chosen tech stack          |
| `/speckit.tasks`         | `speckit-tasks`        | Generate actionable task lists for implementation                          |
| `/speckit.taskstoissues` | `speckit-taskstoissues`| Convert generated task lists into GitHub issues for tracking and execution |
| `/speckit.implement`     | `speckit-implement`    | Execute all tasks to build the feature according to the plan               |
| `/speckit.converge`      | `speckit-converge`     | Assess the codebase against spec/plan/tasks and append remaining work as new tasks |

### Optional Commands

Additional commands for enhanced quality and validation:

| Command              | Agent Skill            | Description                                                                                                                          |
| -------------------- | ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| `/speckit.clarify`   | `speckit-clarify`      | Clarify underspecified areas (recommended before `/speckit.plan`)                                                |
| `/speckit.analyze`   | `speckit-analyze`      | Cross-artifact consistency & coverage analysis (run after `/speckit.tasks`, before `/speckit.implement`)                             |
| `/speckit.checklist` | `speckit-checklist`    | Generate custom quality checklists that validate requirements completeness, clarity, and consistency (like "unit tests for English") |

## 🔧 Dat Kit CLI Reference

The CLI is available as both `specify` and `specdat`. For full command details, options, and examples, see the upstream [CLI Reference](https://github.github.io/spec-kit/reference/overview.html) — the command surface is identical.

```bash
specify init my-project --integration <agent>   # bootstrap a project
specify integration list                        # list available agents
specify extension search / add / remove         # manage extensions
specify preset search / add / remove            # manage presets
specify bundle search / info / install          # manage bundles
specify self check                              # show installed version
```

## 🧩 Making Dat Kit Your Own: Extensions & Presets

Dat Kit can be tailored to your needs through two complementary systems — **extensions** and **presets** — plus project-local overrides for one-off adjustments:

| Priority | Component Type                              | Location                         |
| -------: | ------------------------------------------- | -------------------------------- |
|      ⬆ 1 | Project-Local Overrides                     | `.specify/templates/overrides/`  |
|        2 | Presets — Customize core & extensions       | `.specify/presets/templates/`    |
|        3 | Extensions — Add new capabilities           | `.specify/extensions/templates/` |
|      ⬇ 4 | Dat Kit Core — Built-in SDD commands & templates | `.specify/templates/`        |

- **Templates** are resolved at **runtime** — Dat Kit walks the stack top-down and uses the first match.
- Project-local overrides (`.specify/templates/overrides/`) let you make one-off adjustments for a single project without creating a full preset.
- **Extension/preset commands** are applied at **install time** — when you run `specify extension add` or `specify preset add`, command files are written into agent directories (e.g., `.claude/commands/`).
- If multiple presets or extensions provide the same command, the highest-priority version wins. On removal, the next-highest-priority version is restored automatically.
- If no overrides or customizations exist, Dat Kit uses its core defaults.

### Extensions — Add New Capabilities

Use **extensions** when you need functionality that goes beyond the core. Extensions introduce new commands and templates — for example, adding domain-specific workflows, integrating with external tools, or adding entirely new development phases.

```bash
# Search available extensions
specify extension search

# Install an extension
specify extension add <extension-name>
```

See the upstream [Extensions reference](https://github.github.io/spec-kit/reference/extensions.html) for the full command guide. Browse the [community extensions](https://github.github.io/spec-kit/community/extensions.html) for what's available.

### Presets — Customize Existing Workflows

Use **presets** when you want to change *how* Dat Kit works without adding new capabilities. Presets override the templates and commands that ship with the core *and* with installed extensions — for example, enforcing a compliance-oriented spec format, using domain-specific terminology, or applying organizational standards to plans and tasks.

```bash
# Search available presets
specify preset search

# Install a preset
specify preset add <preset-name>
```

See the upstream [Presets reference](https://github.github.io/spec-kit/reference/presets.html) for the full command guide, including resolution order and priority stacking.

## 📦 Bundles: Role-Based Setups

Extensions and presets are individual building blocks. A **bundle** packages a curated set of them — extensions, presets, steps, and workflows — into a single, versioned, role-oriented setup so a whole team persona (product manager, business analyst, security researcher, developer, …) can be provisioned with one command.

```bash
# Discover bundles in the active catalog stack
specify bundle search [<query>]

# Inspect the exact component set a bundle will add (equals what install does)
specify bundle info <bundle-id>

# Install a bundle's full component set in one operation
specify bundle install <bundle-id>

# See what's installed, then update or remove non-destructively
specify bundle list
specify bundle update <bundle-id>     # or --all
specify bundle remove <bundle-id>     # removes only this bundle's components
```

Bundles resolve from a **priority-ordered catalog stack** (project > user > built-in). Four ready-to-read example bundle manifests live under [`examples/bundles/`](examples/bundles/).

Key guarantees: `info` shows exactly what `install` adds; installs are idempotent and confined to the project root; `remove` never touches components another installed bundle still needs; and all consume/author commands work **offline** against local or pinned sources.

### When to Use Which

| Goal | Use |
| --- | --- |
| Add a brand-new command or workflow | Extension |
| Customize the format of specs, plans, or tasks | Preset |
| Integrate an external tool or service | Extension |
| Enforce organizational or regulatory standards | Preset |
| Ship reusable domain-specific templates | Either — presets for template overrides, extensions for templates bundled with new commands |
| Provision a complete role-based setup in one command | Bundle |

## 📚 Core Philosophy

Spec-Driven Development is a structured process that emphasizes:

- **Intent-driven development** where specifications define the "*what*" before the "*how*"
- **Rich specification creation** using guardrails and organizational principles
- **Multi-step refinement** rather than one-shot code generation from prompts
- **Heavy reliance** on advanced AI model capabilities for specification interpretation

## 🌟 Development Phases

| Phase                                    | Focus                    | Key Activities                                                                                                                                                     |
| ---------------------------------------- | ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **0-to-1 Development** ("Greenfield")    | Generate from scratch    | <ul><li>Start with high-level requirements</li><li>Generate specifications</li><li>Plan implementation steps</li><li>Build production-ready applications</li></ul> |
| **Creative Exploration**                 | Parallel implementations | <ul><li>Explore diverse solutions</li><li>Support multiple technology stacks & architectures</li><li>Experiment with UX patterns</li></ul>                         |
| **Iterative Enhancement** ("Brownfield") | Brownfield modernization | <ul><li>Add features iteratively</li><li>Modernize legacy systems</li><li>Adapt processes</li></ul>                                                                |

For existing projects, keep Dat Kit tooling updates separate from feature artifact evolution: refresh managed project files when upgrading, and update `specs/` artifacts when intended behavior changes. The [Evolving Specs guide](./docs/guides/evolving-specs.md) describes the recommended brownfield loop.

## 🔧 Prerequisites

- **Linux/macOS/Windows**
- [Supported](#-supported-ai-coding-agent-integrations) AI coding agent.
- [uv](https://docs.astral.sh/uv/) for package management (recommended) or [pipx](https://pipx.pypa.io/) for persistent installation
- [Python 3.11+](https://www.python.org/downloads/)
- [Git](https://git-scm.com/downloads)

## 📖 Learn More

- **[Complete Spec-Driven Development Methodology](./spec-driven.md)** — deep dive into the full process
- **[Upstream Spec Kit docs](https://github.github.io/spec-kit/)** — reference documentation for the shared machinery (agents, extensions, presets, bundles)

## 💬 Support

For support with Dat Kit, please open a [GitHub issue](https://github.com/TranQuangDat2005/datkit-for-coding/issues/new) on this repository. Bug reports, feature requests, and questions about using Spec-Driven Development are all welcome.

## 🙏 Acknowledgements

Dat Kit is a fork of [GitHub Spec Kit](https://github.com/github/spec-kit) and builds on the work and research of [John Lam](https://github.com/jflam) and the Spec Kit maintainers and community. Upstream bug fixes and features are periodically merged into this repository.

## 📄 License

This project is licensed under the terms of the MIT open source license, as is the upstream Spec Kit code it contains. Please refer to the [LICENSE](./LICENSE) file for the full terms.
