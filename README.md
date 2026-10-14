# Repo Bouncer

> Check the repo before the agent starts guessing.

[![Package build](https://github.com/Swif7ify/Repo-Bouncer/actions/workflows/package.yml/badge.svg)](https://github.com/Swif7ify/Repo-Bouncer/actions/workflows/package.yml)
[![MIT license](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Repo Bouncer is a local, repo-aware briefing step for coding-agent requests. It checks for project context, routes reported failures toward investigation, and helps an agent ask about subjective decisions—such as the direction of an open-ended UI redesign—before editing. The agent can inspect the project first, offer concrete options, or take responsibility with a “Use your judgment” choice.

It is an early prototype with a Python CLI and prompt-submit adapters for **Codex** and **Claude Code**, plus setup packs for **Cursor**, **VS Code**, and **Antigravity**. Every integration uses the same heuristic advisor and bounded repository scanner; the coding agent uses its own model to inspect context and conduct the brief. Repo Bouncer itself makes no model/API calls and does not intentionally write project files.

## What it does

For each prompt it returns one of three recommendations:

- **Proceed** when the request looks clear enough to start.
- **Inspect** when the repository may clarify the request. For open-ended design work, the result can include an interactive brief for the agent to ask after inspecting the current UI.
- **Ask** when a consequential choice needs an answer before any safe first step, with suggested choices and room for a custom response.

For subjective design requests, the agent is instructed to inspect the relevant UI first, ask one focused question with repo-informed options, and keep “Use your judgment” as the final choice. Clear bug reports are routed to investigation without a generic prompt interview. Codex and similar hooks pass numbered-text guidance; Antigravity can use its native question UI. See the [product overview](docs/OVERVIEW.md) for host limits and current behavior.

## Try the CLI

Requires Python 3.10 or newer. The package is not published to PyPI yet, so install from a checkout:

```powershell
python -m pip install -e .
repo-bouncer check --repo . "Make signup better"
repo-bouncer check --repo . --json "Improve the login flow"
```

The CLI is useful on its own and provides a stable JSON result for additional adapters. It does not install dependencies or change project settings. Python may create its normal `__pycache__` files if you run an editable source install from inside the scanned checkout.

## Use with an agent

- **Codex CLI:** add the local marketplace with `codex plugin marketplace add .`, then separately install the plugin with `codex plugin add repo-bouncer@repo-bouncer-local`. Review and trust its hook in Codex (`/hooks` in the CLI).
- **Claude Code:** from the repository you want Claude to work in, start a session with `claude --plugin-dir "<path-to-this-checkout>"`. This loads the plugin for that session. The bundled hook uses `python3`; on Windows, update its interpreter in `hooks/hooks.json` to the Python 3.10+ launcher available on your PATH (for example, `py` with `-3` in `args`).
- **Cursor, VS Code, and Antigravity:** copy the matching files from [`integrations/`](integrations/) into the project you want to use them in. These hosts need the CLI installed and use repository instructions to run its preflight. Cursor and VS Code also have optional prompt-submit ask gates.

**Codex in the ChatGPT desktop app** uses the same local Codex plugin. Install it separately from the **Plugins Directory** after adding the marketplace, review and trust its hook, then use a new local coding session with the target repository open. A regular ChatGPT conversation does not automatically run against a local repository. Read [integration setup](docs/INTEGRATIONS.md) for host-specific steps, a safe smoke test, and limitations. Read [security and data handling](docs/SECURITY.md) before enabling prompt hooks in a project.

An optional, opinionated [personal engineering profile](profiles/personal/) is available as persistent `AGENTS.md` instructions and a portable `engineering-defaults` Agent Skill. It includes your defaults for framework/dependency documentation research, TypeScript, modularity, backend OpenAPI and tests, database docs, linting, and commit-message drafts. It is opt-in and separate from Repo Bouncer's public prompt-routing rules; review it before sharing it with a team.

## Project documentation

- [Product overview and architecture](docs/OVERVIEW.md)
- [Agent and IDE integration setup](docs/INTEGRATIONS.md)
- [Security and data handling](docs/SECURITY.md)
- [Changelog](CHANGELOG.md)
- [Contributing](CONTRIBUTING.md)
- [Support](SUPPORT.md)
- [Security reporting policy](SECURITY.md)

## Contributing and community

Focused bug reports, documentation fixes, and small improvements are welcome. Read the [contribution guide](CONTRIBUTING.md) before opening a pull request. Use the GitHub issue forms for bug reports and feature proposals; do not include private prompts, source code, credentials, or other sensitive project data.

See the [GitHub contributors page](https://github.com/Swif7ify/Repo-Bouncer/graphs/contributors) for the people credited through repository history. Names are added there by GitHub from actual contributions; this repository does not invent or manually assign contributor credits.

## Current status

This is an early prototype, not a mature prompt-understanding system or an industry standard. Routing is based on explainable patterns and repository evidence; an agent must follow its instructions to inspect and ask well. Review its decisions before relying on blocking behavior. The scan is bounded and may miss useful files. The CLI can be used by any agent that can run a local command, but automatic prompt-submit support requires a host-specific adapter.
