"""Command-line entry point."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .advisor import advise
from .formatting import format_ask, format_interaction
from .scanner import scan_repository


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="repo-bouncer",
        description="Locally decide whether an agent should proceed, inspect, or ask.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    check = subparsers.add_parser("check", help="Assess one prompt against a repository")
    check.add_argument("prompt", nargs="*", help="The request that will be sent to the coding agent")
    check.add_argument("--repo", "-r", type=Path, default=Path.cwd(), help="Repository directory (default: current directory)")
    check.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    check.add_argument("--input-json", action="store_true", help="Read {prompt, repo} JSON from stdin")
    return parser


def _request(args: argparse.Namespace) -> tuple[str, Path]:
    if args.input_json:
        try:
            payload: Any = json.load(sys.stdin)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON on stdin: {exc.msg}") from exc
        if not isinstance(payload, dict) or not isinstance(payload.get("prompt"), str):
            raise ValueError('JSON input must be an object with a string "prompt" field.')
        repo = Path(payload.get("repo", args.repo))
        return payload["prompt"], repo
    if not args.prompt:
        raise ValueError("Provide a prompt, or use --input-json.")
    return " ".join(args.prompt), args.repo


def _print_text(result: dict[str, Any]) -> None:
    print(f"Action: {result['action'].upper()}")
    print(f"Reason: {result['reason']}")
    if result.get("question"):
        print(format_ask(result, "Question:"))
    if result.get("interaction"):
        print(format_interaction(result, "Interactive brief:"))
    if result.get("evidence"):
        print("Evidence:")
        for item in result["evidence"]:
            line_text = f" (lines {', '.join(map(str, item['lines']))})" if item.get("lines") else ""
            terms = f"; terms: {', '.join(item['matched_terms'])}" if item.get("matched_terms") else ""
            print(f"  - {item['path']}{line_text} — {item['category']}{terms}")
    if result.get("repo_setup_suggestion"):
        print(f"Optional setup: {result['repo_setup_suggestion']}")
    print(f"Agent guidance: {result['agent_guidance']}")


def main(argv: list[str] | None = None) -> int:
    parser = _parser()
    args = parser.parse_args(argv)
    try:
        prompt, repo = _request(args)
        context = scan_repository(repo, prompt)
        result = advise(prompt, context)
    except (OSError, ValueError) as exc:
        print(f"repo-bouncer: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        _print_text(result)
    return 2 if result["blocking"] else 0
