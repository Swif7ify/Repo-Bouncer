# Repo Bouncer preflight

For each new repository coding request, run `repo-bouncer check --repo . --json "..."` before exploring or editing, using the full current request as the positional prompt argument (for example: `repo-bouncer check --repo . --json "Improve the login flow"`). Preserve it exactly and use safe shell quoting or JSON-over-stdin for multiline text and quotes.

Read and follow the target repository's active instructions and scoped rules. If the optional Repo Bouncer personal profile has been installed, use it as the user's defaults while respecting project-specific conventions and the current request.

Follow the JSON `action` and `agent_guidance`:

- `proceed`: work on the request and verify the smallest relevant behavior.
- `inspect`: read the paths in `evidence` first. If an `interaction` brief is present, inspect the relevant implementation and project guidance, then follow its `must_ask` value: ask one focused question before editing when true; when false, ask only if materially different outcomes remain. Adapt the suggested choices to what you found without inventing product requirements. If no interaction brief is present, proceed when evidence resolves the uncertainty; ask only if materially different outcomes remain.
- `ask`: use Antigravity's native `ask_question` tool with the provided `question` and `choices` as a single-select question. Accept a custom response when the UI permits it. Wait for the answer before the affected action.

For an interactive brief, follow `must_ask`, prefer the native question UI, and use the suggested choices as a starting point. Keep **Use your judgment** as the final numbered choice when provided. If selected, make a coherent, repo-informed decision and continue without asking another preference question. If the question tool is unavailable, show numbered choices and accept a number or custom text. A numbered/custom answer applies to the immediately preceding request; continue that request rather than treating the answer as a new task.

If an `inspect` result reveals another necessary question after reading the repo, use the native question UI when available; otherwise ask one concise question with numbered, repo-informed choices.

Treat evidence paths as leads, not proof. Read files before relying on them. If the command is unavailable or fails, say the preflight could not run and continue using the normal workflow; never invent a result. This heuristic does not override explicit user instructions, repository policy, or Antigravity's safety controls.
