# Personal engineering defaults

This opt-in profile captures one developer's preferred defaults for AI coding agents. It is not Repo Bouncer's universal policy, and it does not claim that every preference is an industry standard. It is available in two forms:

- [`AGENTS.md`](AGENTS.md) is a persistent instruction starter. Copy it to a project's `AGENTS.md` or merge it with the project's existing instructions.
- [`skills/engineering-defaults/SKILL.md`](skills/engineering-defaults/SKILL.md) is a portable Agent Skill. Install the skill folder in an agent's skill directory or invoke it when you want the workflow applied.

For an always-loaded project baseline, copy `AGENTS.md` into the target repository (or merge it into the host's persistent instruction file). For a reusable/on-demand skill, copy the whole `engineering-defaults` folder to one of these locations:

| Host | Project skill path | Personal skill path |
| --- | --- | --- |
| Codex CLI/IDE/desktop, Cursor, Antigravity, VS Code/Copilot | `.agents/skills/engineering-defaults/` | `~/.agents/skills/engineering-defaults/` (Antigravity's documented global path is `~/.gemini/config/skills/engineering-defaults/`) |
| Claude Code | `.claude/skills/engineering-defaults/` | `~/.claude/skills/engineering-defaults/` |

The skill file is plain Agent Skills format and is portable; supported discovery paths and whether a host chooses it automatically vary. Invoke it explicitly as `$engineering-defaults` in Codex, `@engineering-defaults` in ChatGPT, or `/engineering-defaults` in hosts with slash-command skill invocation. A skill alone is not guaranteed to load on every request. For predictable always-on project guidance, use `AGENTS.md` (or the target host's persistent instruction format) as well. Review the profile before committing it to a shared repository.

Some preferences in the profile are intentionally personal: the approximate 500-line review threshold, OpenAPI for HTTP backends, `DATABASE.md` for database work, backend unit tests, and a commit-message draft in the final response. It also asks agents to make accessibility, migration safety, and sensitive-data handling part of relevant changes. When a relevant project foundation is missing, it asks the agent to point that out and suggest a small setup, without silently expanding unrelated work. The profile qualifies these rules so agents update the right docs, avoid artificial refactors, and ask before hiding a suspected false-positive lint warning.

The added baseline practices follow primary references:

- TypeScript's strict compiler options and typescript-eslint's [`no-explicit-any`](https://typescript-eslint.io/rules/no-explicit-any/) guidance support stronger type checking and `unknown` for untrusted values.
- The [OpenAPI Specification](https://spec.openapis.org/oas/latest.html) defines a language-independent description format for HTTP APIs.
- OWASP's [Secure Coding Practices Quick Reference](https://owasp.org/projects/secure-coding-practices-quick-reference-guide) covers defensive practices such as input validation, access control, secrets, and least privilege.
- W3C's [WCAG 2.2 Quick Reference](https://www.w3.org/WAI/WCAG22/quickref/) is a reference for accessibility criteria and techniques; the profile's accessibility defaults are a reminder to consider these needs, not a claim of WCAG conformance.
- ESLint documents [automatic fixes](https://eslint.org/docs/latest/use/command-line-interface#--fix); the profile requires reviewing those edits and keeping suppressions narrow.
- [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) is a useful fallback commit-message format, not a required standard for repositories with another convention.

The profile also tells agents to check the versions installed in the repository and consult official framework/dependency documentation when version-specific behavior matters. Those APIs and recommendations change, so the profile does not freeze a framework checklist into the tool.

The Agent Skill uses the portable `SKILL.md` directory format. See the [Agent Skills specification](https://agentskills.io/specification), [Codex skills guide](https://developers.openai.com/codex/skills), [Claude Code skills guide](https://code.claude.com/docs/en/skills), [Cursor skills guide](https://cursor.com/docs/skills), [Antigravity skills guide](https://antigravity.google/docs/skills), and [VS Code skills guide](https://code.visualstudio.com/docs/agent-customization/agent-skills) for current host paths and behavior.
