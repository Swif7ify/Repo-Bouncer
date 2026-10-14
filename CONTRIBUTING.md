# Contributing

Thanks for considering a contribution. Repo Bouncer is an early prototype, so focused reports and small, clearly explained changes are especially helpful.

## Before starting

- For a larger behavior change, new host integration, or public interface change, open an issue first so the expected behavior and host limitations can be discussed. Small bug fixes and documentation corrections can go straight to a pull request.
- For a small typo or documentation correction, a pull request is fine without an issue.
- Check the existing [product overview](docs/OVERVIEW.md), [integration notes](docs/INTEGRATIONS.md), and [security notes](docs/SECURITY.md) before proposing changes in those areas.
- Do not include private prompts, repository contents, credentials, or other sensitive data in a public issue or pull request. For a vulnerability, follow [SECURITY.md](SECURITY.md).

## Local setup

The package supports Python 3.10 and newer. From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
repo-bouncer --help
```

On macOS or Linux, activate the environment with `source .venv/bin/activate` instead.

## Make a change

- Keep the change focused and follow the existing module and adapter patterns.
- Avoid adding a dependency when the standard library or an existing dependency is sufficient. Explain a necessary dependency in the pull request.
- Update the relevant documentation when behavior, setup, host support, configuration, or security/data handling changes.
- If you change a prompt hook or IDE adapter, describe the host, hook lifecycle, expected input/output, failure behavior, and any trust or permission implications.
- Do not claim that a host supports a capability unless its current official documentation supports it; link relevant documentation when host behavior is material.

## Validation

The repository does not currently define a test runner, lint, formatter, or type-check command. For a code change, include the exact checks or manual CLI steps you performed and note anything you could not validate. Do not report tests or checks as passing unless you ran them. Changes that introduce a test or quality tool should also document how contributors run it.

GitHub Actions builds both a source distribution and a wheel. A local build can be run with:

```powershell
python -m pip install build
python -m build
```

## Pull request checklist

- [ ] The change has a clear problem statement and stays within the agreed scope.
- [ ] Relevant user-facing and integration documentation is updated.
- [ ] Validation steps and their results are described accurately.
- [ ] Security, prompt-data handling, and failure behavior were considered where relevant.
- [ ] No unrelated generated files, credentials, or local environment files are included.
