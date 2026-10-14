---
applyTo: "**"
---

Use Repo Bouncer before acting on each new repository coding request when the `repo-bouncer` command is available.

Read and follow the target repository's active instructions (for example, `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md`, and scoped rules). If the optional Repo Bouncer personal profile has been installed, use it as the user's defaults while respecting project-specific conventions and the current request.

1. Run `repo-bouncer check --repo . --json "..."`, using the full current request as the positional prompt argument (for example: `repo-bouncer check --repo . --json "Improve the login flow"`). Preserve it exactly and use safe shell quoting or JSON-over-stdin for multiline text and quotes.
2. Follow the JSON `action`:
   - `proceed`: work on the request and verify the smallest relevant behavior.
   - `inspect`: read the paths in `evidence` first. If repository evidence resolves the uncertainty, proceed and state any material assumption. Ask only if materially different outcomes remain.
   - `ask`: present the provided `question` and numbered `choices` before the affected action. The Local prompt hook can only return a text message, so include the choices there and let the user reply with a number or custom answer. Wait for the answer before proceeding.
3. Treat evidence paths as leads, not proof. Read files before relying on them.
4. If Repo Bouncer is missing or fails, say the preflight could not run and continue using the normal repository workflow. Do not invent a result.

This is an advisory heuristic and does not override explicit user instructions, repository policy, or VS Code's safety controls.
