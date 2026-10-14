# Agent integrations

The CLI and advisor are host-independent. Prompt hooks are host-specific, so each integration translates the common `proceed` / `inspect` / `ask` result into that agent's event protocol.

## Codex

The Codex plugin is configured by `plugin.json` and `hooks/codex_hooks.json`. It runs on `UserPromptSubmit`:

- `proceed`: no hook output; the prompt continues.
- `inspect`: returns `additionalContext` with a short reason, likely paths, and guidance to inspect before asking the user to repeat repository information.
- `ask`: returns a blocking decision with the unresolved question.

To load this checkout as a local marketplace:

```text
codex plugin marketplace add .
```

Then open `/plugins`, select the local marketplace, and install **Repo Bouncer**. Codex asks you to review and trust plugin hooks. The hook runs Python 3.10+ locally and imports the package from the plugin directory; a separate global CLI install is not required.

## Claude Code

The Claude Code plugin uses `.claude-plugin/plugin.json`, `hooks/hooks.json`, and `hooks/claude_user_prompt_submit.py`. It uses Claude Code's `UserPromptSubmit` hook to add `additionalContext` for `inspect` or block with a question for `ask`.

For a local checkout, start Claude from the target project and point it at this plugin directory:

```text
claude --plugin-dir "<path-to-repo-bouncer-checkout>"
```

This loads the plugin for that session. The hook config names `python3` as the interpreter. On Windows, edit the `command` and `args` in `hooks/hooks.json` to match the installed Python launcher. For example, use `"command": "py"` and add `"-3"` before the script path in `args`. The selected interpreter must be Python 3.10 or newer.

Claude Code also supports marketplace-installed plugins. This checkout does not yet have a published remote marketplace, so the local `--plugin-dir` flow is the ready-to-use path. Once the project has a public repository, a Claude marketplace entry can point to the plugin for versioned installs and updates.

## Other hosts

| Host | Status | Notes |
| --- | --- | --- |
| Codex | Included | Local plugin marketplace and prompt-submit hook. |
| Claude Code | Included | Claude plugin and prompt-submit hook. |
| GitHub Copilot CLI | Not included | Copilot's documented command hook output for `userPromptSubmitted` is dropped; an SDK callback adapter is needed to inject prompt context. |
| Other editors or agents | CLI available | Any host that can run a local command can use `repo-bouncer check --json`; automatic prompt-submit behavior needs an adapter for its lifecycle and decision format. |

The Copilot note follows its [hooks reference](https://docs.github.com/en/copilot/reference/hooks-reference) and [SDK prompt-submitted hook guide](https://docs.github.com/en/copilot/how-tos/copilot-sdk/hooks/user-prompt-submitted). Claude's behavior follows its [hook reference](https://code.claude.com/docs/en/hooks) and [plugin reference](https://code.claude.com/docs/en/plugins-reference).
