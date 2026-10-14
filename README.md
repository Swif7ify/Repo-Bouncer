# Repo Bouncer

> Check the repo before the agent starts guessing.

[![Package build](https://github.com/Swif7ify/Repo-Bouncer/actions/workflows/package.yml/badge.svg)](https://github.com/Swif7ify/Repo-Bouncer/actions/workflows/package.yml)
[![MIT license](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Repo Bouncer is a local, read-only checkpoint for coding-agent prompts. Before an agent starts, it checks whether the request is clear enough to proceed, whether the repository has evidence worth inspecting, or whether an important decision should be asked first.

It is an early prototype with a Python CLI and prompt-submit adapters for **Codex** and **Claude Code**, plus setup packs for **Cursor**, **VS Code**, and **Antigravity**. Every integration uses the same heuristic advisor and bounded repository scanner. It makes no model/API calls and does not intentionally write project files.

## What it does

For each prompt it returns one of three recommendations:

- **Proceed** when the request looks clear enough to start.
- **Inspect** when the repository may already contain useful context.
- **Ask** when an important choice is missing, such as a deployment target or data-preservation expectation.

The advisor does not generate or install `AGENTS.md`, `CLAUDE.md`, or other project rules. It may suggest a short instruction file if none is present, but the suggestion is optional. See the [product overview](docs/OVERVIEW.md) for the intended role and current limits.

## Try the CLI

Requires Python 3.10 or newer. The package is not published to PyPI yet, so install from a checkout:

```powershell
python -m pip install -e .
repo-bouncer check --repo . "Make signup better"
repo-bouncer check --repo . --json "Improve the login flow"
```

The CLI is useful on its own and provides a stable JSON result for additional adapters. It does not install dependencies or change project settings. Python may create its normal `__pycache__` files if you run an editable source install from inside the scanned checkout.

## Use with an agent

- **Codex:** add this checkout as a local plugin marketplace with `codex plugin marketplace add .`, then install **Repo Bouncer** from `/plugins`.
- **Claude Code:** from the repository you want Claude to work in, start a session with `claude --plugin-dir "<path-to-this-checkout>"`. This loads the plugin for that session. The bundled hook uses `python3`; on Windows, update its interpreter in `hooks/hooks.json` to the Python 3.10+ launcher available on your PATH (for example, `py` with `-3` in `args`).
- **Cursor, VS Code, and Antigravity:** copy the matching files from [`integrations/`](integrations/) into the project you want to use them in. These hosts need the CLI installed and use repository instructions to run its preflight. Cursor and VS Code also have optional prompt-submit ask gates.

**Codex in the ChatGPT desktop app** uses the same local Codex plugin. A regular ChatGPT conversation does not automatically run against a local repository. Read [integration setup](docs/INTEGRATIONS.md) for host-specific steps and limitations. Read [security and data handling](docs/SECURITY.md) before enabling prompt hooks in a project.

An optional, opinionated [personal engineering profile](profiles/personal/) is available to copy into a project that supports `AGENTS.md`. It includes your defaults for TypeScript, modularity, backend documentation and tests, linting, and commit-message drafts. Review it before sharing it with a team.

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

This is an early prototype, not a mature prompt-understanding system or an industry standard. Routing is based on explainable patterns and repository evidence; review its decisions before relying on blocking behavior. The scan is bounded and may miss useful files. The CLI can be used by any agent that can run a local command, but automatic prompt-submit support requires a host-specific adapter.
