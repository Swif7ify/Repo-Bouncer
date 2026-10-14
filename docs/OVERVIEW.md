# Product overview

## The problem

People often start coding-agent sessions with a broad request such as “make this better” or “fix the flow.” The repository may already contain requirements, project conventions, tests, or nearby implementation details that make the request clear. In other cases, the request is missing a decision that the codebase cannot safely supply, such as which environment to deploy to or whether existing data must be preserved.

Repo Bouncer checks for those cases before the agent begins work. Its goal is to help the agent use repository evidence first and ask the user only when an unresolved choice matters.

## What happens on a prompt

1. A host adapter receives the submitted prompt and the current working directory.
2. The shared scanner builds a bounded inventory of likely project instructions, manifests, tests, documentation, and request-related files. It looks for prompt terms in selected text files.
3. The advisor makes an explainable `proceed`, `inspect`, or `ask` recommendation.
4. The adapter stays silent, adds concise repository paths and guidance to the agent context, or blocks the prompt with a question and suggested choices.

The CLI exposes the same result as text or JSON. It can be used without an agent integration.

An `ask` result includes a `question` and a `choices` array of suggested answers. Each ask includes an `Other / custom` choice so the user can give a different answer.

## What it is and is not

This is a **prompt preflight layer**: it helps decide what the agent should do before coding. It complements persistent repository instructions such as `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md`, or editor-specific rules. Those files provide stable project facts and conventions; this advisor checks a particular request against the current repository.

It is not a prompt-writing course, prompt template library, code generator, semantic code reviewer, or automatic setup wizard. It does not decide what “better” means on the user's behalf. If it cannot find evidence to resolve a broad request, it asks for a concrete outcome or permission to explore and propose one.

## Recommendation meanings

| Recommendation | Meaning | Agent behavior |
| --- | --- | --- |
| `proceed` | The request appears specific enough for a low-risk first pass. | Start the task and verify the smallest relevant behavior. |
| `inspect` | Repository evidence may establish relevant behavior, conventions, or commands. | Read the cited paths, then proceed if they resolve the uncertainty. |
| `ask` | The current heuristic flags an important choice as missing. It does not prove that project configuration cannot answer it. | Pause and present the question and suggested choices before the affected action. |

The current rules specifically look for broad improvement requests, likely matching files, destructive data language without a preservation/rollback expectation, and deployment requests without an environment in the prompt. They do not currently infer a deployment default or backup policy from project configuration before asking. The rules are intentionally simple and will produce false positives and false negatives.

## Architecture

- `src/repo_bouncer/scanner.py` performs bounded, read-only repository discovery and keyword matching.
- `src/repo_bouncer/advisor.py` converts a prompt and scan result into the common JSON response.
- `src/repo_bouncer/formatting.py` renders ask recommendations as numbered choices for text-based host hooks and the CLI.
- `src/repo_bouncer/cli.py` provides the standalone `repo-bouncer` command.
- `hooks/codex_user_prompt_submit.py` and `hooks/claude_user_prompt_submit.py` translate that response to each host's hook protocol. `integrations/` contains rules and optional prompt-submit ask gates for additional hosts.
- `plugin.json` and `hooks/codex_hooks.json` package the Codex integration; `.claude-plugin/plugin.json` and `hooks/hooks.json` package the Claude Code integration.

The host adapters contain no separate decision logic: every integration uses the same recommendation. Prompt-aware hosts can receive a recommendation directly at submission time. Other hosts use an always-on repository instruction that tells the agent to run the CLI as its first step. When an `ask` result includes choices, Antigravity can use its native multiple-choice question tool; Codex and other prompt-submit gates render them as numbered text because their hook response is a message, not a choice widget. See [integration setup](INTEGRATIONS.md) for which path each host uses and the limits of each API.

## Optional engineering profile

`profiles/personal/AGENTS.md` is a separate, opt-in starter for persistent coding preferences: version-aware official-doc research, security checks, modularity, API/database documentation, backend tests, lint handling, and a suggested commit message in the final response. It is not part of the advisor's decision rules and is not installed automatically. Its approximately 500-line file-size target is explicitly personal, not an industry standard.

## Product boundary

The advisor can identify leads in a repository; it cannot prove that a matching path is authoritative or that a line implements the intended behavior. It does not run tests, inspect Git history, call an LLM, intentionally write project files, execute project scripts, or transmit prompt/repository data. See [security and data handling](SECURITY.md) for scan limits and what is passed back to the agent.

This version is a prototype. Its most important next product question is whether the recommendations are useful and low-noise across real repositories. A representative evaluation set should be built before expanding the rules or treating the hook as a policy gate.

## Repository workflow

The repository includes a [contribution guide](../CONTRIBUTING.md), GitHub issue and pull request templates, a [support page](../SUPPORT.md), and a [security reporting policy](../SECURITY.md). GitHub Actions builds a Python source distribution and wheel on pushes and pull requests; this packaging check is not a substitute for behavioral tests. The project does not yet define a test runner or lint/type-check commands.
