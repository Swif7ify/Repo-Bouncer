# Repo Bouncer preflight

For each new repository coding request, run `repo-bouncer check --repo . --json "..."` before exploring or editing, using the full current request as the positional prompt argument (for example: `repo-bouncer check --repo . --json "Improve the login flow"`). Preserve it exactly and use safe shell quoting or JSON-over-stdin for multiline text and quotes.

Read and follow the target repository's active instructions and scoped rules. If the optional Repo Bouncer personal profile has been installed, use it as the user's defaults while respecting project-specific conventions and the current request.

Follow the JSON `action`:

- `proceed`: work on the request and verify the smallest relevant behavior.
- `inspect`: read the paths in `evidence` first. If repository evidence resolves the uncertainty, proceed and state any material assumption. Ask only if materially different outcomes remain.
- `ask`: use Antigravity's native `ask_question` tool with the provided `question` and `choices` as a single-select question. The final choice is the custom-answer option. Wait for the answer before the affected action. If that tool is unavailable, show the choices as a numbered text list and let the user reply with a number or custom answer.

Treat evidence paths as leads, not proof. Read files before relying on them. If the command is unavailable or fails, say the preflight could not run and continue using the normal workflow; never invent a result. This heuristic does not override explicit user instructions, repository policy, or Antigravity's safety controls.
