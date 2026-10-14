"""Claude Code UserPromptSubmit adapter for Repo Bouncer."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path


def _emit(payload: dict[str, object]) -> None:
    sys.stdout.write(json.dumps(payload, ensure_ascii=False) + "\n")


def main() -> int:
    try:
        event = json.load(sys.stdin)
        prompt = event.get("prompt")
        if not isinstance(prompt, str) or not prompt.strip():
            return 0

        plugin_root = Path(os.environ["CLAUDE_PLUGIN_ROOT"]).resolve()
        sys.path.insert(0, str(plugin_root / "src"))
        from repo_bouncer.advisor import advise
        from repo_bouncer.scanner import scan_repository

        repo_value = event.get("cwd") or os.getcwd()
        context = scan_repository(Path(repo_value), prompt)
        result = advise(prompt, context)

        if result["action"] == "proceed":
            return 0

        if result["action"] == "ask":
            _emit(
                {
                    "decision": "block",
                    "reason": f"Repo Bouncer needs one decision before coding: {result['question']}",
                }
            )
            return 0

        evidence_lines = []
        for item in result.get("evidence", []):
            location = item["path"]
            if item.get("lines"):
                location += ":" + ",".join(str(line) for line in item["lines"])
            evidence_lines.append(f"- {location} ({item['category']})")

        context_note = [
            "Repo Bouncer recommends inspecting repository evidence before asking the user for more context.",
            f"Reason: {result['reason']}",
        ]
        if evidence_lines:
            context_note.append("Likely evidence:\n" + "\n".join(evidence_lines))
        context_note.append(result["agent_guidance"])
        if result.get("repo_setup_suggestion"):
            context_note.append("Optional repo setup note: " + result["repo_setup_suggestion"])

        _emit(
            {
                "hookSpecificOutput": {
                    "hookEventName": "UserPromptSubmit",
                    "additionalContext": "\n".join(context_note),
                }
            }
        )
        return 0
    except Exception:
        # Fail open: advisor errors must not prevent the user's prompt from running.
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
