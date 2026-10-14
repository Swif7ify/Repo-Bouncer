---
name: engineering-defaults
description: Apply this developer's personal engineering preferences when planning or implementing code changes, reviewing architecture, or preparing a change for handoff. Use for software work; defer to the current request and the target repository's established conventions when they conflict.
---

# Personal engineering defaults

These are one developer's defaults, not universal industry rules. Follow the user's current request, repository instructions, and existing conventions when they conflict. Keep changes scoped to the task and don't add fashionable patterns or dependencies without a concrete reason.

## Before implementation

- Read the applicable agent instructions, relevant source, manifests/lockfiles, tests, and docs. Identify the framework, runtime, and installed versions before choosing APIs.
- Consult official, version-specific framework and dependency documentation when an API used in the change, a dependency addition/upgrade, or version-sensitive behavior needs confirmation. Prefer the installed version's official docs and migration notes. If the network is unavailable, inspect local package docs/types and say what remains unverified. Don't spend time researching unrelated dependencies.
- If a foundation directly relevant to the task is missing (such as backend tests, an API contract, database documentation, or security guidance), point it out and suggest the smallest useful setup. Don't stop unrelated work or silently add a new toolchain; ask before substantial scaffolding or extra dependencies.
- For broad requests such as “improve this,” inspect first, then ask one focused question with concrete options if different choices would materially change the result. Keep “Use your judgment” as the last option. If the user delegates judgment, choose from project evidence and continue the original task.

## Code and security

- Keep files cohesive and modules focused. Aim for about 500 lines or fewer per source file when practical; treat that as a personal review threshold, not an industry standard or a reason to split code artificially. Avoid unrelated refactors.
- In TypeScript, don't introduce `any` or `as any`. Prefer precise types; use `unknown` at untrusted boundaries and narrow it. If an exceptional case appears to require `any`, explain the reason and ask before using it.
- Validate untrusted input at boundaries. For backend changes, consider authorization, parameterized database operations, least privilege, safe error messages, and protection of secrets and personal data. Follow the project's threat model and framework guidance.
- For user-facing interfaces, preserve semantic HTML, keyboard access, readable contrast, and useful loading, empty, and error states.
- For API or schema changes, consider compatibility and safe rollout/migration needs. Never claim a migration is reversible unless verified.

## Documentation and tests

- Every new feature or behavior change needs an update to the appropriate existing documentation, or one concise new page if there is no suitable home. Keep documented commands and behavior verified; avoid duplicate docs. Internal refactors with no behavior change don't need documentation churn.
- For a backend that exposes HTTP endpoints, create or update an OpenAPI description using the project's existing version/tooling. Include request/response schemas, auth, relevant errors, and examples. Don't add an HTTP API spec for a backend with no HTTP API.
- When implementing or materially changing database storage or schema, create or update `DATABASE.md` with verified schema/relationships, migrations/seeding, local setup, and operational data expectations when known. Mark unknowns instead of guessing; never include secrets.
- For backend changes, add or update meaningful unit tests for business logic and regression coverage for bug fixes where feasible. Add integration coverage for important API/database boundaries when changed.
- Update `SECURITY.md` or the existing threat-model docs when the task materially changes sensitive data flows, authentication, or public exposure. Update `CHANGELOG.md` when the repository uses it and the change belongs there.

## Lint and validation

- Use the repository's documented test, lint, type-check, and format commands. Run relevant checks after implementation, and report precisely what ran and what could not run.
- Run the configured linter/formatter and use its safe auto-fix on the changed scope when appropriate. Review auto-fix diffs, resolve errors and warnings caused by the change, and avoid unrelated repository-wide cleanup.
- Don't silence a warning with a broad config change or ignore comment. If a warning looks like a false positive and a narrow suppression is the proposed fix (for example, a lint warning on `axios.create`), show the warning and ask before adding an explained suppression.

## Handoff

- Keep a concise record of actual changes and validation results while working.
- In the final response, include a suggested commit subject and a short body when useful, based on the final diff and the repository's convention (Conventional Commits is a fallback only). Don't stage, commit, push, or publish unless asked.
