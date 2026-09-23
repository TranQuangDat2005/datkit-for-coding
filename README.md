<div align="center">
    <img src="./media/datkit-logo.svg" alt="Dat Kit Logo" width="180" height="180"/>
    <h1>🧰 Dat Kit</h1>
    <h3><em>Define what to build before building it — with any AI coding agent.</em></h3>
</div>

<p align="center">
    <strong>A spec-driven development toolkit for building high-quality software with any AI coding agent — a ready-to-use workflow, endlessly extensible via extensions, presets, and bundles.</strong>
</p>

<p align="center">
    <a href="https://github.com/TranQuangDat2005/datkit-for-coding/stargazers"><img src="https://img.shields.io/github/stars/TranQuangDat2005/datkit-for-coding?style=social" alt="GitHub stars"/></a>
    <a href="https://github.com/TranQuangDat2005/datkit-for-coding/blob/main/LICENSE"><img src="https://img.shields.io/github/license/TranQuangDat2005/datkit-for-coding" alt="License"/></a>
    <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.11%2B-blue" alt="Python 3.11+"/></a>
</p>

---

## Table of Contents

- [✨ Highlights](#-highlights)
- [🤔 What is Spec-Driven Development?](#-what-is-spec-driven-development)
- [⚡ Get Started](#-get-started)
- [Available Slash Commands](#available-slash-commands)
- [🤖 Supported AI Coding Agents](#-supported-ai-coding-agents)
- [🔧 CLI Reference](#-cli-reference)
- [🧩 Extensions, Presets & Bundles](#-extensions-presets--bundles)
- [📚 Core Philosophy](#-core-philosophy)
- [🌟 Development Phases](#-development-phases)
- [🔧 Prerequisites](#-prerequisites)
- [🔄 Updating Dat Kit](#-updating-dat-kit)
- [💬 Support](#-support)
- [📄 License](#-license)
- [🙏 Acknowledgements](#-acknowledgements)

## ✨ Highlights

- **Spec-driven, not prompt-driven** — structured requirements, plans, and tasks guide your agent step by step instead of one-shot code generation
- **Works with 30+ AI coding agents** — CLI tools and IDE assistants alike
- **Batteries included** — templates, slash commands, and helper scripts ship inside the package and work offline
- **Extensible** — add capabilities with extensions, reshape workflows with presets, provision whole team setups with bundles
- **Cross-platform** — Linux, macOS, and Windows

## 🤔 What is Spec-Driven Development?

Spec-Driven Development (SDD) is a methodology where **specifications guide AI coding agents** through a structured development process. Instead of prompting an AI to write code immediately, you first build clear, structured requirements — then let the agent work through them step by step:

1. **Constitution** — establish the governing principles for your project
2. **Specify** — describe *what* you want to build and *why* (not the tech stack)
3. **Plan** — choose the technical implementation approach
4. **Tasks** — break the plan into an actionable task list
5. **Implement** — execute the tasks and build the feature

Dat Kit gives you the complete scaffolding for this workflow: templates, slash commands, and scripts that integrate with your favorite AI coding agent.

## ⚡ Get Started

### 1. Install Dat Kit

Requires **[uv](https://docs.astral.sh/uv/)** and Python 3.11+:

```bash
uv tool install spec-datkit --from git+https://github.com/TranQuangDat2005/datkit-for-coding.git
```

Try it without a persistent install:

```bash
uvx --from git+https://github.com/TranQuangDat2005/datkit-for-coding.git specdat init my-project --integration copilot
```

Or with pipx:

```bash
pipx install git+https://github.com/TranQuangDat2005/datkit-for-coding.git
```

The CLI is installed under both the `specdat` and `specify` commands — this guide uses `specdat`.

### 2. Initialize a project

```bash
specdat init my-project --integration copilot
cd my-project
```

For CI or AI agent harnesses (no keyboard, or a PTY that cannot send arrow keys), pass `--non-interactive` so init never hangs on a picker. Combine with `--force` when initializing into a non-empty directory:

```bash
specdat init my-project --non-interactive --ignore-agent-tools
specdat init --here --force --non-interactive --integration claude
```

### 3. Establish project principles

Launch your coding agent in the project directory. Most agents expose Dat Kit as `/speckit.*` slash commands; some agents in skills mode use `$speckit-*` instead; GitHub Copilot CLI uses `/agents` to select the agent or address it directly in a prompt.

Use **`/speckit.constitution`** to create your project's governing principles and development guidelines:

```bash
/speckit.constitution Create principles focused on code quality, testing standards, user experience consistency, and performance requirements
```

### 4. Create the spec

Use **`/speckit.specify`** to describe what you want to build. Focus on the **what** and **why**, not the tech stack:

```bash
/speckit.specify Build an application that can help me organize my photos in separate photo albums. Albums are grouped by date and can be re-organized by dragging and dropping on the main page. Albums are never in other nested albums. Within each album, photos are previewed in a tile-like interface.
```

### 5. Create a technical implementation plan

Use **`/speckit.plan`** to provide your tech stack and architecture choices:

```bash
/speckit.plan The application uses Vite with minimal number of libraries. Use vanilla HTML, CSS, and JavaScript as much as possible. Images are not uploaded anywhere and metadata is stored in a local SQLite database.
```

### 6. Break down into tasks

```bash
/speckit.tasks
```

### 7. Execute implementation

```bash
/speckit.implement
```

## Available Slash Commands

After running `specify init`, your AI coding agent has access to these slash commands. For integrations that support skills mode, passing `--integration <agent> --integration-options="--skills"` installs agent skills instead of slash-command prompt files.

### Core Commands

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

| Command              | Agent Skill         | Description                                                                                                                          |
| -------------------- | ------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| `/speckit.clarify`   | `speckit-clarify`   | Clarify underspecified areas (recommended before `/speckit.plan`)                                                                    |
| `/speckit.analyze`   | `speckit-analyze`   | Cross-artifact consistency & coverage analysis (run after `/speckit.tasks`, before `/speckit.implement`)                              |
| `/speckit.checklist` | `speckit-checklist` | Generate custom quality checklists that validate requirements completeness, clarity, and consistency (like "unit tests for English")  |

## 🤖 Supported AI Coding Agents

Dat Kit works with 30+ AI coding agents — both CLI tools and IDE-based assistants.

Run `specdat integration list` to see all available integrations in your installed version.

## 🔧 CLI Reference

```bash
specdat init my-project --integration <agent>   # bootstrap a project
specdat integration list                        # list available agents
specdat extension search / add / remove         # manage extensions
specdat preset search / add / remove            # manage presets
specdat bundle search / info / install          # manage bundles
specdat check                                   # verify agent prerequisites
specdat self check                              # show installed version
```

The CLI is available as both `specdat` and `specify`.

## 🧩 Extensions, Presets & Bundles

Dat Kit can be tailored through three complementary systems:

| Priority | Component Type                                  | Location                         |
| -------: | ----------------------------------------------- | -------------------------------- |
|      ⬆ 1 | Project-Local Overrides                         | `.specify/templates/overrides/`  |
|        2 | Presets — customize core & extensions           | `.specify/presets/templates/`    |
|        3 | Extensions — add new capabilities               | `.specify/extensions/templates/` |
|      ⬇ 4 | Dat Kit Core — built-in SDD commands & templates | `.specify/templates/`           |

- **Templates** are resolved at **runtime** — Dat Kit walks the stack top-down and uses the first match
- **Extension/preset commands** are applied at **install time** — command files are written into agent directories (e.g., `.claude/commands/`)
- If multiple presets or extensions provide the same command, the highest-priority version wins; on removal, the next-highest-priority version is restored automatically

### Extensions — add new capabilities

```bash
specdat extension search
specdat extension add <extension-name>
```

### Presets — customize existing workflows

```bash
specdat preset search
specdat preset add <preset-name>
```

### Bundles — role-based setups in one command

```bash
specdat bundle search [<query>]
specdat bundle info <bundle-id>
specdat bundle install <bundle-id>
specdat bundle list
specdat bundle update <bundle-id>     # or --all
specdat bundle remove <bundle-id>
```

### When to Use Which

| Goal | Use |
| --- | --- |
| Add a brand-new command or workflow | Extension |
| Customize the format of specs, plans, or tasks | Preset |
| Integrate an external tool or service | Extension |
| Enforce organizational or regulatory standards | Preset |
| Provision a complete role-based setup in one command | Bundle |

## 📚 Core Philosophy

- **Intent-driven development** where specifications define the "*what*" before the "*how*"
- **Rich specification creation** using guardrails and organizational principles
- **Multi-step refinement** rather than one-shot code generation from prompts
- **Heavy reliance** on advanced AI model capabilities for specification interpretation

## 🌟 Development Phases

| Phase                                    | Focus                    | Key Activities                                                                                                                                                     |
| ---------------------------------------- | ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **0-to-1 Development** ("Greenfield")    | Generate from scratch    | Start with high-level requirements → generate specifications → plan implementation steps → build production-ready applications                                     |
| **Creative Exploration**                 | Parallel implementations | Explore diverse solutions, multiple technology stacks & architectures, experiment with UX patterns                                                                |
| **Iterative Enhancement** ("Brownfield") | Brownfield modernization | Add features iteratively, modernize legacy systems, adapt processes                                                                                                |

## 🔧 Prerequisites

- **Linux/macOS/Windows**
- An [AI coding agent](#-supported-ai-coding-agents)
- [uv](https://docs.astral.sh/uv/) (recommended) or [pipx](https://pipx.pypa.io/)
- [Python 3.11+](https://www.python.org/downloads/)
- [Git](https://git-scm.com/downloads)

## 🔄 Updating Dat Kit

`specdat self check` reports the installed version. To update, reinstall from this repository:

```bash
uv tool install --force spec-datkit --from git+https://github.com/TranQuangDat2005/datkit-for-coding.git
```

## 💬 Support

Please open a [GitHub issue](https://github.com/TranQuangDat2005/datkit-for-coding/issues/new) on this repository. Bug reports, feature requests, and questions about using Dat Kit are all welcome.

## 📄 License

This project is licensed under the terms of the MIT open source license. Please refer to the [LICENSE](./LICENSE) file for the full terms.

## 🙏 Acknowledgements

Dat Kit (`spec-datkit`) is a **rebuild based on the original work** — [**GitHub Spec Kit**](https://github.com/github/spec-kit), a spec-driven development toolkit by GitHub, Inc. (MIT License). The original copyright notice and license terms are retained in the [LICENSE](./LICENSE) file, and the attribution statement is provided in the [NOTICE](./NOTICE) file, as required by the MIT License.
