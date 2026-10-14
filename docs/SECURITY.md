# Security and data handling

Repo Bouncer is designed to run locally with a narrow, read-only role. Direct prompt-submit hooks receive the prompt and the current working directory, then the scanner reads a limited set of repository paths. Rule-based integrations ask the agent to run the same local CLI. Repo Bouncer itself does not make network requests, invoke a model, execute project commands, intentionally write project files, or save a prompt history of its own. Python may create normal bytecode cache files when the package is installed in editable mode inside the scanned checkout.

## What the scanner reads

The scanner walks the repository without following symlinks. It ignores common generated/vendor directories such as `.git`, `node_modules`, `.venv`, `vendor`, `dist`, and `build`; sensitive directory names such as `.ssh`, `.aws`, `secrets`, and `credentials`; and secret-like filenames such as `.env`, private keys, and credential files.

The scan is bounded: it inventories at most 5,000 paths, considers at most 36 candidate text files for content matching, caps a file at 96 KB, caps total content read at 900 KB, and examines at most 1,200 lines per file. These limits reduce work and exposure but do not guarantee that every sensitive or relevant file is excluded. A file containing secrets under an ordinary name may be read if it is selected as a candidate.

## What can reach the agent context

Hooks that support context injection may return a recommendation, a short explanation, a question with suggested choices, guidance, and repository-relative paths with line numbers and categories. They do not return source excerpts. The CLI JSON can include matched prompt terms. In rule-based integrations, the agent receives the CLI result through its normal terminal tool workflow.

This tool cannot replace the host's own permissions, sandbox, or data-handling controls. If a repository contains files that should never be read by local tooling, keep them outside the scanned working tree or add appropriate exclusions before enabling the hook.

## Hook failure behavior

All four prompt-submit adapters fail open on advisor errors: the user's prompt proceeds without preflight context if Python is missing, the repository cannot be scanned, or the adapter raises an error. Recommendations are heuristics and should not be treated as a security boundary or proof of correctness. Cursor and VS Code's optional gates can block only when Repo Bouncer successfully returns `ask`.
