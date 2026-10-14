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
| Codex CLI and desktop | Local plugin and `UserPromptSubmit` hook | Adds `inspect` guidance and after-inspection briefs to agent context; blocks immediate `ask` choices as text. | No clickable choice buttons from the prompt hook; the agent conducts the follow-up. |
| Claude Code | Claude plugin and `UserPromptSubmit` hook | Adds `inspect` guidance and after-inspection briefs to agent context; blocks immediate `ask` choices as text. | Install the plugin in the Claude Code session; configure the Python interpreter. |
| Cursor | Always-on `.mdc` rule and optional `beforeSubmitPrompt` gate | Rule handles interactive briefs; hook can block immediate `ask` choices. | Cursor's prompt-submit hook cannot inject the `inspect` result into model context. |
| VS Code Local harness | Workspace instruction and optional `UserPromptSubmit` hook | Instruction handles interactive briefs; Local hook can stop immediate `ask` choices. | VS Code's hook experience is Preview and the hook configuration applies to the **Local** target only. Copilot, Claude, and Codex Agent Host sessions use their provider's hook runtime. |
| Antigravity | Workspace plugin with an always-loaded rule | Rule can inspect first, then use Antigravity's native question UI for an interactive brief. | The documented `PreInvocation` hook payload has no submitted prompt field; the rule asks the agent to run the CLI itself. |
| GitHub Copilot CLI | No dedicated adapter | The CLI can still be run manually. | A Copilot SDK callback adapter is not included. |

## Codex

The Codex plugin is configured by `plugin.json` and `hooks/codex_hooks.json`. Its `UserPromptSubmit` hook:

- lets `proceed` pass silently;
- provides `inspect` evidence, investigation guidance, and interactive briefs as additional context;
- blocks immediate `ask` with the unresolved question and numbered choices in the hook's text reason.

The prompt hook returns text rather than a native choice widget. For open-ended design requests, the agent reads the relevant files and then asks one focused question in its normal conversation. For immediate asks, users can reply with a choice number or custom text. If they choose **Use your judgment**, Codex should continue the original request and explain its decision. See OpenAI's [UserPromptSubmit hook reference](https://developers.openai.com/codex/hooks/).

From this repository root, add the local marketplace:

```text
codex plugin marketplace add .
```

Adding the marketplace only makes the plugin available; it does **not** install it. Separately install **Repo Bouncer** from the `repo-bouncer-local` marketplace:

```text
codex plugin add repo-bouncer@repo-bouncer-local
```

Then open Codex and review/trust the plugin hook. In Codex CLI, use `/hooks` to inspect and trust non-managed hooks. The hook runs Python 3.10+ locally and imports the package from the plugin directory, so a separate global CLI installation is not needed for this adapter.

### Codex in the ChatGPT desktop app

Use the desktop app instead of the CLI if you prefer a UI:

1. Open the **Plugins Directory** and select the **Repo Bouncer (local)** marketplace. If it is missing, add this repository as a local marketplace and restart Codex.
2. Open **Repo Bouncer** and select **Install**. Seeing the marketplace or plugin listing alone does not mean the plugin is installed.
3. Review and trust the plugin's `UserPromptSubmit` hook when Codex asks. Installing/enabling the plugin does not automatically trust its hook; an untrusted hook is skipped.
4. Start a **new local coding session** with the target repository open. A regular ChatGPT conversation does not automatically have access to a local checkout.

To smoke-test the interactive brief without permitting edits, submit: `Make this UI better. Do not edit yet; run Repo Bouncer and follow any interactive brief.` The expected path is: inspect the relevant UI context, then ask for a design direction with text choices and a final **Use your judgment** option. A clear bug report should receive investigate-first guidance instead of a generic prompt interview. `proceed` is silent, while `inspect` guidance is added to agent context.

See OpenAI's [plugin packaging guide](https://developers.openai.com/plugins/build/plugins) and [hook guide](https://developers.openai.com/codex/hooks/) for current local-marketplace, installation, and hook-trust behavior.

## Claude Code

The Claude Code plugin uses `.claude-plugin/plugin.json`, `hooks/hooks.json`, and `hooks/claude_user_prompt_submit.py`. Its `UserPromptSubmit` hook adds evidence and interactive-brief instructions for `inspect`, and blocks immediate `ask` choices as text.

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

The rule makes the agent run the CLI, inspect first when asked, and conduct an interactive brief before editing when the result includes one. The optional hook is an additional early gate for immediate `ask`; it lets `inspect` prompts continue because Cursor's documented `beforeSubmitPrompt` output supports continuing or blocking with a message to the user, but not prompt-specific context injection. Project hooks run in trusted workspaces. This adapter is intended for local Cursor sessions; it fails open if Python, the package, or the scan is unavailable. Cloud agents may not have the CLI installed.

See Cursor's [Hooks](https://cursor.com/docs/hooks) and [Rules](https://cursor.com/docs/rules) references for their current formats and behavior.

## VS Code

The files under `integrations/vscode/` support VS Code's **Local** agent harness.

1. Install the CLI as described above.
2. Copy `integrations/vscode/repo-bouncer.instructions.md` to `.github/instructions/repo-bouncer.instructions.md` in the target repository.
3. To add a native ask gate, copy `integrations/vscode/repo_bouncer_user_prompt.py` to `.github/hooks/repo_bouncer_user_prompt.py`.
4. Copy `integrations/vscode/hooks.json` to `.github/hooks/repo-bouncer.json`.
5. Use VS Code's Local session target and enable trusted-workspace hooks. The JSON includes a Windows `py -3` command; change it if the CLI was installed in another Python environment.

The instruction makes the agent run the CLI and handle `proceed`, `inspect` (including after-inspection briefs), and `ask`. The optional Local hook stops only immediate `ask`. VS Code documents exit code 2 as a way for a Local hook to block and provide its error text to the model. Its hook experience is currently Preview. If the selected session target is Copilot, Claude, or Codex on Agent Host, use the hook protocol for that provider; this Local configuration does not apply.

See VS Code's [hooks overview](https://code.visualstudio.com/docs/agent-customization/hooks), [Local hooks reference](https://code.visualstudio.com/docs/agents/reference/hooks-reference), and [agent customization guide](https://code.visualstudio.com/docs/agents/guides/customize-copilot-guide).

## Antigravity

The plugin under `integrations/antigravity/` contains an always-loaded Repo Bouncer rule.

1. Install the CLI in the environment Antigravity uses for shell commands.
2. Copy the contents of `integrations/antigravity/` into the target workspace at `.agents/plugins/repo-bouncer/`.
3. Enable the plugin in Antigravity's Plugins Manager if prompted.

The rule tells the agent to run the CLI and follow `agent_guidance`. For a design `interaction` brief, it inspects the relevant screens, components, styles, and project guidance before asking one focused question through Antigravity's native `ask_question` UI. It tailors the suggestions to those findings and keeps **Use your judgment** last. For immediate `ask`, it uses the same native UI when available. Antigravity's documented `PreInvocation` hook can inject instructions, but its payload does not include the current prompt; this integration avoids reading an undocumented transcript format. See Google's [plugin](https://antigravity.google/docs/plugins) and [hook](https://antigravity.google/docs/hooks/) references.

## Generic agent instruction

For an agent that recognizes `AGENTS.md`, copy or merge `integrations/shared/REPO_BOUNCER_INSTRUCTIONS.md` into the target repository's `AGENTS.md`. It asks the agent to inspect first, then run a short interactive brief only when the result calls for one. This is a lightweight alternative to a host-specific rule, but it does not install the CLI or create a deterministic hook. Do not overwrite project-specific instructions already in that file.

## Optional personal engineering defaults

Repo Bouncer includes the developer's opinionated defaults in two opt-in forms: persistent [`AGENTS.md` instructions](../profiles/personal/AGENTS.md) and a portable [Agent Skill](../profiles/personal/skills/engineering-defaults/SKILL.md). This profile is separate from Repo Bouncer's prompt-routing behavior and is not installed by the Repo Bouncer plugin. It covers framework/dependency documentation research, no TypeScript `any`, modularity and an approximate 500-line review target, feature documentation, OpenAPI for HTTP backends, `DATABASE.md` for database changes, backend unit tests, lint handling, and a commit-message draft in the final response.

For defaults that should apply throughout a project, copy or merge `AGENTS.md` into the target repo's persistent instruction file. For a callable/automatically discoverable skill, copy the complete `engineering-defaults` folder to the host's skill directory:

| Host | Project path | Personal path |
| --- | --- | --- |
| Codex CLI/IDE/desktop, Cursor, Antigravity, VS Code/Copilot | `.agents/skills/engineering-defaults/` | `~/.agents/skills/engineering-defaults/` (Antigravity: `~/.gemini/config/skills/engineering-defaults/`) |
| Claude Code | `.claude/skills/engineering-defaults/` | `~/.claude/skills/engineering-defaults/` |

Invoke it as `$engineering-defaults` in Codex, `@engineering-defaults` in ChatGPT, or `/engineering-defaults` where slash-invoked skills are supported. Skill discovery paths and automatic invocation differ by host. An installed skill is not guaranteed to be loaded for every prompt, so use persistent instructions when these are meant to be defaults on every coding task. Review the profile before committing it to a shared repository.

The skill uses the Agent Skills `SKILL.md` format. See the official [specification](https://agentskills.io/specification), [Codex](https://developers.openai.com/codex/skills), [Claude Code](https://code.claude.com/docs/en/skills), [Cursor](https://cursor.com/docs/skills), [Antigravity](https://antigravity.google/docs/skills), and [VS Code](https://code.visualstudio.com/docs/agent-customization/agent-skills) documentation for current behavior and paths.

## Security and reliability

Every hook runs local code with the permissions of its host process. Read `docs/SECURITY.md` and review the adapter before enabling it. The Cursor and VS Code add-on hooks fail open: a hook error does not block work. The advisor's `ask` decisions are heuristic and can be wrong, so treat them as a helpful prompt for clarification rather than a security policy.

All host formats can change. Check the linked official documentation when upgrading an IDE or changing its selected agent harness.
