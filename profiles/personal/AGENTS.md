# Personal engineering defaults

These are the user's preferred defaults for coding-agent work. They are intentionally opinionated. Follow the target repository's documented conventions and the user's current request where they differ, and never weaken host or security controls.

## Understand the request before implementation

- Read the repository instructions and inspect the relevant code, manifests, dependency versions, tests, and documentation before proposing a change. Treat existing project evidence as stronger than generic preferences in this file.
- For a broad request such as “improve this,” identify the likely user problem, inspect relevant evidence, and state a small set of concrete options or a low-risk first step. Do not silently invent product requirements.
- Separate confirmed facts from assumptions. Proceed with reversible, low-impact assumptions when useful and state them; ask first when an unresolved choice could change public behavior, expose or destroy data, cause an external side effect, or substantially change scope.
- If a foundation directly relevant to the task is missing (for example, backend tests, an API contract, database documentation, or security guidance), point out the gap and suggest the smallest useful setup. Don't stop unrelated work or silently add a new toolchain; ask before substantial scaffolding or extra dependencies.
- Keep the change focused. Do not add unrelated cleanup, dependencies, or architecture solely because a pattern is fashionable.

## Before changing code

- Read the repository's agent instructions, relevant source, tests, manifests, and lockfiles. Identify the framework, runtime, and installed dependency versions before choosing APIs or commands.
- For framework/dependency APIs used in the change, dependency additions/upgrades, or behavior that may have changed by version, consult the official documentation and version-specific migration/release notes. Prefer official sources over memory or outdated examples. If browsing is unavailable, inspect the installed package's local docs/types and state what could not be confirmed. Link material research in the final response or project docs.
- Prefer existing project scripts, tools, dependency versions, and patterns. Do not add or upgrade a dependency until its official documentation, compatibility, maintenance/security status, and a simpler existing option have been checked. Explain a new dependency when it is material.

## Design and code quality

- Keep modules cohesive and focused on one responsibility. Prefer clear boundaries and small functions over a large file that mixes unrelated work.
- Personal file-size target: keep source files at or below about 500 lines when practical. Treat approaching or exceeding that size as a signal to review the module boundary, not as a reason to split code artificially. Do not refactor unrelated legacy files just to meet the target.
- In TypeScript, do not introduce explicit `any` or `as any`. Prefer a real type; use `unknown` at untrusted or genuinely unknown boundaries and narrow it before use. Preserve the repository's strict compiler settings; enable stricter settings for new TypeScript projects where compatible. If a genuine edge case requires `any`, keep it narrowly scoped, explain why in code, and ask before adding a lint suppression.
- Validate untrusted input at system boundaries. For backend work, check authorization as well as authentication, use parameterized database operations, avoid exposing internal errors or secrets, and apply least privilege. Follow the repository's security framework and threat model where present.
- Do not log credentials, tokens, sensitive request bodies, or personal data. Keep error messages useful to users without exposing internal details.
- For user-facing interfaces, preserve keyboard access, semantic structure, readable contrast, and clear loading, empty, and error states. Follow the project's existing accessibility tooling and conventions.
- For API or database changes, consider compatibility with existing clients/data and provide a safe migration or rollout path when the change requires one. Do not claim that a migration is reversible unless that has been checked.

## Documentation

- Every new feature or behavior change needs documentation: update the relevant existing docs or add one concise page if there is no suitable home. Keep setup, configuration, deployment, and public-interface instructions aligned with verified behavior; avoid duplicate docs. For an internal refactor that changes no behavior, do not create documentation churn.
- Prefer one authoritative place for each instruction. Link related docs rather than copying long, easily outdated sections into multiple files.
- For a backend that exposes HTTP endpoints, create or update an OpenAPI description (use the version and tooling already adopted by the project). Document request/response schemas, authentication, relevant errors, and examples. Do not create an API spec for a backend that has no HTTP API.
- When implementing or materially changing database storage/schema, create or update `DATABASE.md`. Document the verified schema and relationships, migrations/seeding, local setup, and data retention/backup/restore expectations when known. Never put credentials or secrets in it. Mark unknown operational details as unknown instead of guessing.
- For a project that handles sensitive data, authentication, or public deployment, create or update `SECURITY.md` (or the repository's existing threat-model document) with verified trust boundaries, sensitive data flows, and security controls. Do not claim a compliance certification or security guarantee without evidence.
- Update an existing `CHANGELOG.md` when the project uses one and the change belongs there. Do not create a release changelog entry for every private implementation task.

## Tests, lint, and validation

- For backend changes, add or update meaningful unit tests for business logic. Add integration tests for important API/database boundaries when those are part of the change. Bug fixes should include a regression check when feasible; do not write hollow tests that only mirror implementation details.
- Use the repository's documented test, lint, type-check, and format commands. Run the relevant checks after implementation. Do not invent a toolchain when the project has none; report any check that could not run.
- Run the configured linter and formatter. Use the project's safe auto-fix command on the relevant files when appropriate, review the resulting diff, and fix lint errors and warnings in the changed scope. Avoid unrelated repository-wide cleanup unless requested.
- Do not silently hide a warning with a broad config change or ignore comment. If a warning appears to be a tool false positive and suppressing it is the proposed fix, show the warning and ask whether to add a narrow, explained suppression. Do not “fix” it by weakening checks across unrelated files.
- Report pre-existing warnings separately from issues caused by the change. Do not claim that lint, tests, or type checking passed unless they were actually run.
- When a suitable test or check cannot run because the repository lacks a runner, dependency, credentials, or environment, say exactly what is missing and report any lower-cost check that was actually performed.

## Wrap-up and commit reference

- Keep a concise summary of the actual changes and validation results as you work.
- In the final response, include a suggested commit subject (use the repository's convention; otherwise a concise Conventional Commit is fine) and a short body when useful. Base it on the final diff, not the original plan.
- Keep that commit draft in the final response unless the repository has a specific change log or task-note convention. Do not stage, commit, push, or publish unless the user asks.
