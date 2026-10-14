# Repo Bouncer

> Check the repo before the agent starts guessing.

Repo Bouncer is a local, read-only checkpoint for coding-agent prompts. Before an agent starts, it checks whether the request is clear enough to proceed, whether the repository has evidence worth inspecting, or whether an important decision should be asked first.

It is a small prototype with a Python CLI and prompt-submit adapters for **Codex** and **Claude Code**. Both integrations use the same heuristic advisor and bounded repository scanner. It makes no model/API calls and does not intentionally write project files.

## What it does

For each prompt it returns one of three recommendations:

- **Proceed** when the request looks clear enough to start.
- **Inspect** when the repository may already contain useful context.
- **Ask** when an important choice is missing, such as a deployment target or data-preservation expectation.

The advisor does not generate or install `AGENTS.md`, `CLAUDE.md`, or other project rules. It may suggest a short instruction file if none is present, but the suggestion is optional. See [the product overview](docs/OVERVIEW.md) for the intended role and current limits.

## Try the CLI

Requires Python 3.10 or newer:

```powershell
python -m pip install -e .
repo-bouncer check --repo . "Make signup better"
repo-bouncer check --repo . --json "Improve the login flow"
```

The CLI is useful on its own and provides a stable JSON result for additional adapters. It does not install dependencies or change project settings. Python may create its normal `__pycache__` files if you run an editable source install from inside the scanned checkout.

## Use with an agent

- **Codex:** add this checkout as a local plugin marketplace with `codex plugin marketplace add .`, then install **Repo Bouncer** from `/plugins`.
- **Claude Code:** from the repository you want Claude to work in, start a session with `claude --plugin-dir "<path-to-this-checkout>"`. This loads the plugin for that session. The bundled hook uses `python3`; on Windows, update its interpreter in `hooks/hooks.json` to the Python 3.10+ launcher available on your PATH (for example, `py` with `-3` in `args`).

Read [integration setup](docs/INTEGRATIONS.md) for details, including the current GitHub Copilot status. Read [security and data handling](docs/SECURITY.md) before enabling prompt hooks in a project.

## Current status

This is an early prototype, not a mature prompt-understanding system or an industry standard. Routing is based on explainable patterns and repository evidence; review its decisions before relying on blocking behavior. The scan is bounded and may miss useful files. The CLI can be used by any agent that can run a local command, but automatic prompt-submit support requires a host-specific adapter.
