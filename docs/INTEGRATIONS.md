# Agent integrations

Repo Bouncer has one host-independent CLI and advisor, with host-specific ways to make an agent use it. The difference matters: some hosts can add the recommendation to the model's context before a request, while others can only stop the request or load a persistent instruction.

## Install the CLI

Repo Bouncer is not published to PyPI yet. Clone this repository and install it into the same Python environment your agent hooks will use:

```powershell
python -m pip install -e "<path-to-repo-bouncer-checkout>"
repo-bouncer --help
```

On Windows, make sure the configured hook interpreter points at that same Python environment. The CLI uses Python 3.10 or newer.

For an agent that uses repository instructions but has no prompt hook, install the CLI and add the matching instructions below. The instruction tells the agent to run `repo-bouncer check` against each new coding request and follow its JSON recommendation. This is model-guided; it is not a deterministic enforcement boundary.

## Host status

| Host | Included path | What it can do | Limitation |
| --- | --- | --- | --- |
| Codex CLI | Local plugin and `UserPromptSubmit` hook | Passes `inspect` context to the agent or blocks an `ask`. | Hooks must be reviewed and trusted. |
| Codex in ChatGPT desktop | Same local Codex plugin | Runs the plugin in a local Codex/Work execution context. | A regular ChatGPT conversation does not automatically have access to a local checkout. |
| Claude Code | Claude plugin and `UserPromptSubmit` hook | Passes `inspect` context to the agent or blocks an `ask`. | Install the plugin in the Claude Code session; configure the Python interpreter. |
| Cursor | Always-on `.mdc` rule and optional `beforeSubmitPrompt` gate | Rule runs the CLI for full `proceed` / `inspect` / `ask` handling; hook can block an `ask`. | Cursor's prompt-submit hook cannot inject the `inspect` result into model context. |
| VS Code Local harness | Workspace instruction and optional `UserPromptSubmit` hook | Instruction runs the CLI for all three actions; Local hook can stop an `ask` and pass the question to the model. | VS Code's hook experience is Preview and the hook configuration applies to the **Local** target only. Copilot, Claude, and Codex Agent Host sessions use their provider's hook runtime. |
| Antigravity | Workspace plugin with an always-loaded rule | Rule runs the CLI for all three actions. | The documented `PreInvocation` hook payload has no submitted prompt field; the rule asks the agent to run the CLI itself. |
| GitHub Copilot CLI | No dedicated adapter | The CLI can still be run manually. | A Copilot SDK callback adapter is not included. |

## Codex

The Codex plugin is configured by `plugin.json` and `hooks/codex_hooks.json`. Its `UserPromptSubmit` hook:

- lets `proceed` pass silently;
- provides `inspect` evidence and guidance as additional context;
- blocks `ask` with the unresolved question.

From this repository root, add the local marketplace:

```text
codex plugin marketplace add .
```

Then open `/plugins`, select the local marketplace, and install **Repo Bouncer**. Codex asks you to review and trust plugin hooks. The hook runs Python 3.10+ locally and imports the package from the plugin directory, so a separate global CLI installation is not needed for this adapter.

### Codex in the ChatGPT desktop app

The same local plugin marketplace can be installed from the Plugins Directory in Codex in the ChatGPT desktop app. Add this repository as the local marketplace, restart the desktop app if needed, then install Repo Bouncer from the marketplace. Review and trust the local hook when prompted. The hook needs to run in a local execution context where this plugin's Python files are available.

This does not make the ordinary ChatGPT chat composer inspect a local repository. Use a local Codex/Work surface with the repository open for the checkout-aware hook. See OpenAI's [plugin packaging guide](https://developers.openai.com/plugins/build/plugins) for current local-marketplace and desktop behavior.

## Claude Code

The Claude Code plugin uses `.claude-plugin/plugin.json`, `hooks/hooks.json`, and `hooks/claude_user_prompt_submit.py`. Its `UserPromptSubmit` hook adds context for `inspect` and blocks `ask`.

From the repository where Claude should work, start a session with this plugin directory:

```text
claude --plugin-dir "<path-to-repo-bouncer-checkout>"
```

The hook config names `python3` as the interpreter. On Windows, edit `hooks/hooks.json` and use the installed Python launcher, for example `"command": "py"` with `"-3"` before the script path in `args`. The selected interpreter must be Python 3.10 or newer.

## Cursor

Cursor has a project-rule pack and an optional prompt-submit gate under `integrations/cursor/`.

1. Install the CLI as described above.
2. Copy `integrations/cursor/rules/repo-bouncer.mdc` to the target repository's `.cursor/rules/repo-bouncer.mdc`.
3. To add a native ask gate, copy `integrations/cursor/repo_bouncer_before_submit.py` to `.cursor/hooks/repo_bouncer_before_submit.py`.
4. Merge the `beforeSubmitPrompt` entry from `integrations/cursor/hooks.json` into the target repository's `.cursor/hooks.json`. If it does not exist, copy that file as `.cursor/hooks.json`.

The rule makes the agent run the CLI and follow all three recommendations. The hook is an additional early gate for `ask`; it lets other prompts continue because Cursor's documented `beforeSubmitPrompt` output supports continuing or blocking with a message to the user, but not prompt-specific context injection. Project hooks run in trusted workspaces. This adapter is intended for local Cursor sessions; it fails open if Python, the package, or the scan is unavailable. Cloud agents may not have the CLI installed.

See Cursor's [Hooks](https://cursor.com/docs/hooks) and [Rules](https://cursor.com/docs/rules) references for their current formats and behavior.

## VS Code

The files under `integrations/vscode/` support VS Code's **Local** agent harness.

1. Install the CLI as described above.
2. Copy `integrations/vscode/repo-bouncer.instructions.md` to `.github/instructions/repo-bouncer.instructions.md` in the target repository.
3. To add a native ask gate, copy `integrations/vscode/repo_bouncer_user_prompt.py` to `.github/hooks/repo_bouncer_user_prompt.py`.
4. Copy `integrations/vscode/hooks.json` to `.github/hooks/repo-bouncer.json`.
5. Use VS Code's Local session target and enable trusted-workspace hooks. The JSON includes a Windows `py -3` command; change it if the CLI was installed in another Python environment.

The instruction makes the agent run the CLI and handle `proceed`, `inspect`, and `ask`. The optional Local hook stops only `ask`. VS Code documents exit code 2 as a way for a Local hook to block and provide its error text to the model. Its hook experience is currently Preview. If the selected session target is Copilot, Claude, or Codex on Agent Host, use the hook protocol for that provider; this Local configuration does not apply.

See VS Code's [hooks overview](https://code.visualstudio.com/docs/agent-customization/hooks), [Local hooks reference](https://code.visualstudio.com/docs/agents/reference/hooks-reference), and [agent customization guide](https://code.visualstudio.com/docs/agents/guides/customize-copilot-guide).

## Antigravity

The plugin under `integrations/antigravity/` contains an always-loaded Repo Bouncer rule.

1. Install the CLI in the environment Antigravity uses for shell commands.
2. Copy the contents of `integrations/antigravity/` into the target workspace at `.agents/plugins/repo-bouncer/`.
3. Enable the plugin in Antigravity's Plugins Manager if prompted.

The rule tells the agent to run the CLI and follow all three recommendations. Antigravity's documented `PreInvocation` hook can inject instructions, but its payload does not include the current prompt; this integration avoids reading an undocumented transcript format. See Google's [plugin](https://antigravity.google/docs/plugins) and [hook](https://antigravity.google/docs/hooks/) references.

## Generic agent instruction

For an agent that recognizes `AGENTS.md`, copy or merge `integrations/shared/REPO_BOUNCER_INSTRUCTIONS.md` into the target repository's `AGENTS.md`. This is a lightweight alternative to a host-specific rule, but it does not install the CLI or create a deterministic hook. Do not overwrite project-specific instructions already in that file.

Repo Bouncer also includes an optional [personal engineering profile](../profiles/personal/). It is separate from prompt routing: copy or merge its `AGENTS.md` into a project only if those defaults are wanted. Keep it distinct from Repo Bouncer's installation instructions and review it before committing it to a team repository.

## Security and reliability

Every hook runs local code with the permissions of its host process. Read `docs/SECURITY.md` and review the adapter before enabling it. The Cursor and VS Code add-on hooks fail open: a hook error does not block work. The advisor's `ask` decisions are heuristic and can be wrong, so treat them as a helpful prompt for clarification rather than a security policy.

All host formats can change. Check the linked official documentation when upgrading an IDE or changing its selected agent harness.
