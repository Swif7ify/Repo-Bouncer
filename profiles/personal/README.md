# Personal engineering profile

This optional `AGENTS.md` captures one developer's preferred defaults for AI coding agents. It is a starter profile, not an official Repo Bouncer policy or a claim that every rule is a universal industry standard.

To use it, copy it into the target repository as `AGENTS.md`, or merge its sections into the instructions that repository already uses. Codex and Cursor support `AGENTS.md`; VS Code Local and Copilot support it too, with Local support controlled by a setting and documented as experimental. Other hosts may use their own instruction format; for example, adapt the rules into Claude Code's `CLAUDE.md` or an Antigravity plugin rule. Review the final file with the team before committing it to a shared repository.

Some preferences in the profile are intentionally personal: the approximate 500-line review threshold, OpenAPI for HTTP backends, `DATABASE.md` for database work, backend unit tests, and a commit-message draft in the final response. It also asks agents to make accessibility, migration safety, and sensitive-data handling part of relevant changes. The profile qualifies these rules so agents update the right docs, avoid artificial refactors, and do not hide uncertain lint warnings.

The added baseline practices follow primary references:

- TypeScript's strict compiler options and typescript-eslint's [`no-explicit-any`](https://typescript-eslint.io/rules/no-explicit-any/) guidance support stronger type checking and `unknown` for untrusted values.
- The [OpenAPI Specification](https://spec.openapis.org/oas/latest.html) defines a language-independent description format for HTTP APIs.
- OWASP's [Secure Coding Practices Quick Reference](https://owasp.org/projects/secure-coding-practices-quick-reference-guide) covers defensive practices such as input validation, access control, secrets, and least privilege.
- W3C's [WCAG 2.2 Quick Reference](https://www.w3.org/WAI/WCAG22/quickref/) is a reference for accessibility criteria and techniques; the profile's accessibility defaults are a reminder to consider these needs, not a claim of WCAG conformance.
- ESLint documents [automatic fixes](https://eslint.org/docs/latest/use/command-line-interface#--fix); the profile requires reviewing those edits and keeping suppressions narrow.
- [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) is a useful fallback commit-message format, not a required standard for repositories with another convention.

The profile also tells agents to check the versions installed in the repository and consult the framework/dependency's official documentation when version-specific behavior matters. Those APIs and recommendations change, so the profile does not freeze a framework checklist into the tool.
