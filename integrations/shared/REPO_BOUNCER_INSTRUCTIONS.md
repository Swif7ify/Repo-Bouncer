# Repo Bouncer preflight instructions

Use Repo Bouncer before acting on each new repository coding request when the `repo-bouncer` command is available.

Read and follow the target repository's active instructions (for example, `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md`, and scoped rules). If the user's optional Repo Bouncer personal engineering profile (`AGENTS.md` or the `engineering-defaults` skill) is installed and available, apply it as their defaults while respecting project-specific conventions and the current request.

1. Run `repo-bouncer check --repo . --json "..."`, using the full current request as the positional prompt argument (for example: `repo-bouncer check --repo . --json "Improve the login flow"`). Preserve it exactly and use safe shell quoting or JSON-over-stdin for multiline text and quotes.
2. Read the JSON result and follow its `action` and `agent_guidance`:
   - `proceed`: work on the request and verify the smallest relevant behavior.
   - `inspect`: read the paths in `evidence` first. If an `interaction` brief is present, inspect the relevant implementation and project guidance, then follow `interaction.must_ask`: ask before editing when true; otherwise ask only if materially different outcomes remain. Tailor the suggested choices to what you found. Without a brief, proceed when evidence resolves the uncertainty; ask only if materially different outcomes remain.
   - `ask`: present the provided `question` and `choices`. Use the host's native single-choice question UI when available; otherwise show numbered text. Accept a custom response. Wait for the user's answer before the affected action.
3. Treat evidence paths as leads, not proof. Read files before relying on them.
4. If the command is missing or fails, say the preflight could not run and continue using the host's normal repository workflow. Never invent a Repo Bouncer result.

This is an advisory heuristic. It does not override explicit user instructions, project policy, or the host's safety controls.

For an `interaction` brief, follow `must_ask`; when asking, ask at most one focused question and wait. Tailor the suggested choices to the repo and keep **Use your judgment** as the final numbered choice. If selected, make a coherent choice from the repo and user goal, explain it, and continue without another preference question. A number or custom answer applies to the immediately preceding request; continue that request. For reported errors, investigate the supplied error and relevant code/tests before asking generic clarification. For feature requests, inspect the current behavior first and ask only about missing decisions that would change the implementation materially.

If inspection uncovers a necessary clarification, use the host's native question UI when available; otherwise show one concise question with numbered, repo-informed choices and accept a custom answer.
