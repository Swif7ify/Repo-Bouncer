# Product overview

## The problem

People often start coding-agent sessions with a broad request such as “make this better,” “the UI feels weird,” or “authentication is failing.” The repository may already contain requirements, project conventions, tests, or nearby implementation details that should shape the work. Sometimes a subjective choice still belongs to the user; sometimes the agent should investigate first and then make a sensible choice itself.

Repo Bouncer gives the agent a small, repo-aware briefing workflow: inspect relevant context, ask one focused question when an open-ended decision materially affects the result, and let the user delegate judgment when they do not want to choose. Error reports should lead to investigation before generic clarification.

## What happens on a prompt

1. A host adapter receives the submitted prompt and the current working directory.
2. The shared scanner builds a bounded inventory of likely project instructions, manifests, tests, documentation, and request-related files. It looks for prompt terms in selected text files.
3. The advisor makes an explainable `proceed`, `inspect`, or `ask` recommendation. An `inspect` result may include an `interaction` brief that tells the agent to inspect first and ask a focused question before editing.
4. The adapter stays silent, adds repository paths and workflow guidance to the agent context, or blocks the prompt with a question and suggested choices.

The CLI exposes the same result as text or JSON. It can be used without an agent integration.

An immediate `ask` result includes a `question` and suggested `choices`. An `interaction` brief is different: the agent reads relevant files first and follows its `must_ask` flag. Design briefs require one focused question; broader briefs ask only when materially different directions remain. The agent adapts choices to the project, keeps “Use your judgment” last, and accepts a custom response.

An open-ended design request such as “Make this UI better” returns `action: "inspect"` with a brief like:

```json
{
  "mode": "after_inspection",
  "kind": "design_direction",
  "must_ask": true,
  "question": "After reviewing the current UI, which direction should guide the improvement?",
  "choices": ["Polish the existing look", "Make it cleaner and more modern", "Make it more distinctive", "Use your judgment"],
  "allow_custom_answer": true
}
```

That `interaction` object guides the host agent; it is not a blocking hook decision. The agent reads the relevant project context first, adapts the choices, asks once when required, and then continues the original request after the user's answer. Hosts that cannot provide a native question widget show numbered text choices instead.

## What it is and is not

This is a **prompt-shaping layer**: it helps the agent use the repository and gather the one missing preference before coding. It complements persistent repository instructions such as `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md`, or editor-specific rules. Those files provide stable project facts and conventions; this advisor routes a particular request and tells the agent how to handle it.

It is not a prompt-writing course, code generator, semantic code reviewer, or automatic setup wizard. It does not make the underlying model more capable. Its value comes from a better sequence: inspect first, ask about real preferences, or proceed under delegated judgment. If an integration cannot provide native choice UI, the agent presents numbered text choices instead.

## Recommendation meanings

| Recommendation | Meaning | Agent behavior |
| --- | --- | --- |
| `proceed` | The request appears specific enough for a low-risk first pass. | Start the task and verify the smallest relevant behavior. |
| `inspect` | Repository evidence may establish relevant behavior, conventions, or commands. It may also carry an interactive brief. | Read the cited paths. Follow `interaction.must_ask` if a brief is present; otherwise proceed or ask if a material choice remains. |
| `ask` | The current heuristic flags an important choice as missing. It does not prove that project configuration cannot answer it. | Pause and present the question and suggested choices before the affected action. |

The current rules look for open-ended requests (including subjective design requests), reported errors, feature requests, likely matching files, destructive data language without a preservation/rollback expectation, and deployment requests without an environment in the prompt. They do not infer a deployment default or backup policy from project configuration before asking. The rules are intentionally simple and will produce false positives and false negatives.

## Architecture

- `src/repo_bouncer/scanner.py` performs bounded, read-only repository discovery and keyword matching.
- `src/repo_bouncer/advisor.py` converts a prompt and scan result into the common JSON response.
- `src/repo_bouncer/formatting.py` renders immediate asks and after-inspection briefs for text-based host hooks and the CLI.
- `src/repo_bouncer/cli.py` provides the standalone `repo-bouncer` command.
- `hooks/codex_user_prompt_submit.py` and `hooks/claude_user_prompt_submit.py` translate that response to each host's hook protocol. `integrations/` contains rules and optional prompt-submit ask gates for additional hosts.
- `plugin.json` and `hooks/codex_hooks.json` package the Codex integration; `.claude-plugin/plugin.json` and `hooks/hooks.json` package the Claude Code integration.

The host adapters contain no separate decision logic: every integration uses the same recommendation. Prompt-aware hosts receive evidence and `agent_guidance` at submission time. Other hosts use an always-on repository instruction that tells the agent to run the CLI as its first step. Antigravity can use its native question UI for the follow-up; Codex, Claude Code, Cursor, and VS Code present choices as text or let the agent ask in its normal conversation. See [integration setup](INTEGRATIONS.md) for host-specific limits.

## Optional engineering profile

`profiles/personal/` provides the same opt-in defaults as persistent `AGENTS.md` instructions and a portable `engineering-defaults` Agent Skill. The defaults cover version-aware framework/dependency research, security, TypeScript, modularity, feature docs, OpenAPI for HTTP backends, `DATABASE.md` for database changes, backend unit tests, lint handling, and a suggested commit message in the final response. When a relevant project foundation is missing, they ask the agent to identify the gap and suggest a small setup without silently expanding the task. They are not part of the advisor's decision rules and are not installed automatically. The approximately 500-line file-size target is explicitly personal, not an industry standard. See the [profile setup guide](../profiles/personal/README.md) for host-specific skill paths.

## Product boundary

The advisor can identify leads in a repository; it cannot prove that a matching path is authoritative or that a line implements the intended behavior. It does not run tests, inspect Git history, call an LLM, intentionally write project files, execute project scripts, or transmit prompt/repository data. The host agent—not Repo Bouncer—reads the evidence and conducts the interactive brief, so this behavior depends on the agent following its host instructions. See [security and data handling](SECURITY.md) for scan limits and what is passed back to the agent.

This version is a prototype. Its most important next product question is whether the recommendations are useful and low-noise across real repositories. A representative evaluation set should be built before expanding the rules or treating the hook as a policy gate.

## Repository workflow

The repository includes a [contribution guide](../CONTRIBUTING.md), GitHub issue and pull request templates, a [support page](../SUPPORT.md), and a [security reporting policy](../SECURITY.md). GitHub Actions builds a Python source distribution and wheel on pushes and pull requests; this packaging check is not a substitute for behavioral tests. The project does not yet define a test runner or lint/type-check commands.
