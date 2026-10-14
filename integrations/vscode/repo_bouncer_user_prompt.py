"""Optional VS Code Local UserPromptSubmit ask gate for Repo Bouncer."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path


def emit(payload: dict[str, object]) -> None:
    sys.stdout.write(json.dumps(payload, ensure_ascii=False) + "\n")


def main() -> int:
    try:
        event = json.load(sys.stdin)
        prompt = event.get("prompt")
        if not isinstance(prompt, str) or not prompt.strip():
            emit({"continue": True})
            return 0

        from repo_bouncer.advisor import advise
        from repo_bouncer.scanner import scan_repository

        repo = Path(event.get("cwd") or os.getcwd()).resolve()
        result = advise(prompt, scan_repository(repo, prompt))
        if result["action"] == "ask":
            # Local hooks use exit code 2 to stop the operation and send stderr to the model.
            sys.stderr.write(
                "Repo Bouncer needs one decision before proceeding: "
                f"{result['question']}\n"
            )
            return 2
        emit({"continue": True})
    except Exception:
        # Fail open: a local advisor or installation error must not strand the prompt.
        emit({"continue": True})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
