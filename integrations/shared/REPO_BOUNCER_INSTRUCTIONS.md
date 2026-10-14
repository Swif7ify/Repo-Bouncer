# Repo Bouncer preflight instructions

Use Repo Bouncer before acting on each new repository coding request when the `repo-bouncer` command is available.

Read and follow the target repository's active instructions (for example, `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md`, and scoped rules). If the optional `profiles/personal/AGENTS.md` profile has been installed, use it as the user's defaults while respecting project-specific conventions and the current request.

1. Run `repo-bouncer check --repo . --json "..."`, using the full current request as the positional prompt argument (for example: `repo-bouncer check --repo . --json "Improve the login flow"`). Preserve it exactly and use safe shell quoting or JSON-over-stdin for multiline text and quotes.
2. Read the JSON result and follow its `action`:
   - `proceed`: work on the request and verify the smallest relevant behavior.
   - `inspect`: read the paths in `evidence` first. If repository evidence resolves the uncertainty, proceed and state any material assumption. Ask only if materially different outcomes remain.
   - `ask`: present the provided `question` and numbered `choices`. Use the host's native single-choice question UI when available; otherwise show the choices as text. The final choice is the custom-answer option. Wait for the user's answer before the affected action.
3. Treat evidence paths as leads, not proof. Read files before relying on them.
4. If the command is missing or fails, say the preflight could not run and continue using the host's normal repository workflow. Never invent a Repo Bouncer result.

This is an advisory heuristic. It does not override explicit user instructions, project policy, or the host's safety controls.
