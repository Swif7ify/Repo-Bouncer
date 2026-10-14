"""Explainable first-pass routing for vague and higher-impact requests."""

from __future__ import annotations

import re
from typing import Any


VAGUE_PATTERNS = (
    r"\bmake\b.{0,30}\b(better|good|modern|cleaner)\b",
    r"\b(improve|optimize|clean up|refactor)\b",
    r"\bfix\b.{0,20}\b(bug|issue|problem|it|this|that)\b",
    r"\b(update|change|redo)\b.{0,20}\b(it|this|that|everything)\b",
    r"\bmake it work\b",
    r"\bdo what is needed\b",
)

DESTRUCTIVE_RE = re.compile(r"\b(delete|drop|truncate|wipe|erase|reset|remove)\b", re.I)
DATA_RE = re.compile(r"\b(data|database|db|table|record|user|account|customer|production)\b", re.I)
DEPLOY_RE = re.compile(r"\b(deploy|release|publish|production|prod)\b", re.I)
ENV_RE = re.compile(r"\b(staging|stage|production|prod|development|dev|test|preview|beta|canary)\b", re.I)
SAFETY_DETAIL_RE = re.compile(r"\b(backup|rollback|preserve|retain|archive|retention|dry.run|reversible)\b", re.I)


def _matches_any(patterns: tuple[str, ...], prompt: str) -> bool:
    return any(re.search(pattern, prompt, flags=re.I | re.S) for pattern in patterns)


def advise(prompt: str, context: dict[str, Any]) -> dict[str, Any]:
    clean_prompt = prompt.strip()
    matches = context.get("matches", [])
    related = context.get("related_paths", [])
    instructions = context.get("instructions", [])
    vague = _matches_any(VAGUE_PATTERNS, clean_prompt)
    destructive_data = bool(DESTRUCTIVE_RE.search(clean_prompt) and DATA_RE.search(clean_prompt))
    underspecified_deploy = bool(DEPLOY_RE.search(clean_prompt) and not ENV_RE.search(clean_prompt))
    missing_safety_detail = not SAFETY_DETAIL_RE.search(clean_prompt)

    action = "proceed"
    reason = "The request appears specific enough for a low-risk first pass."
    question = None
    choices: list[str] = []
    agent_guidance = "Proceed with the requested change and verify the smallest relevant behavior."

    if not clean_prompt:
        action = "ask"
        reason = "No task was provided."
        question = "What would you like changed, and what outcome should count as success?"
        choices = [
            "I will describe the change and how to tell it worked.",
            "Inspect the repository and suggest a few concrete tasks; do not edit yet.",
            "Other / custom: I will describe what I want.",
        ]
        agent_guidance = "Wait for the user to provide a task."
    elif destructive_data and missing_safety_detail:
        action = "ask"
        reason = "The request may delete or rewrite data, but it does not state the preservation or rollback expectation."
        question = "Should existing data be preserved, and what backup or rollback expectation applies?"
        choices = [
            "Preserve existing data and use a non-destructive approach.",
            "Back up first and show me the rollback plan before acting.",
            "Change only the specific data I identify; confirm the exact scope first.",
            "Other / custom: I will describe the preservation and rollback requirements.",
        ]
        agent_guidance = "Do not make a destructive data change until the user answers."
    elif underspecified_deploy:
        action = "ask"
        reason = "The request mentions deployment but does not identify an environment."
        question = "Which environment should this target, and should the change stop short of deploying?"
        choices = [
            "Use the configured preview or staging target; stop before deploying.",
            "Prepare a production deployment, but ask me to confirm before the final deploy action.",
            "Inspect or prepare deployment configuration only; do not publish.",
            "Other / custom: specify the host, environment, and how far to proceed.",
        ]
        agent_guidance = "Do not deploy until the user identifies the target environment."
    elif vague and matches:
        action = "inspect"
        reason = "The outcome is broad, but repository files match the request. Inspect those before asking the user to repeat information the repo may contain."
        agent_guidance = "Read the cited files first. If they establish the desired behavior, proceed and state your assumption. Ask only if multiple materially different outcomes remain."
    elif vague:
        action = "ask"
        reason = "The requested outcome is broad and the repository scan found no matching files to clarify it."
        question = "What specific outcome should change, and how will we know it worked?"
        choices = [
            "Inspect the repository and propose a few concrete outcomes; do not edit yet.",
            "I will provide the intended change and success criteria.",
            "Other / custom: I will describe the outcome I want.",
        ]
        agent_guidance = "Wait for a concrete outcome or permission to explore and propose one before editing."
    elif matches or related:
        action = "inspect"
        reason = "The repository contains likely relevant files. Use them to confirm local patterns and the smallest useful validation command."
        agent_guidance = "Inspect the cited files before editing. Avoid asking about facts already available in the repository."

    setup_suggestion = None
    if not instructions and context.get("source_file_count", 0) and action in {"inspect", "ask"}:
        setup_suggestion = (
            "No supported agent instruction file was found. This is not a blocker. "
            "If agents repeatedly need the same project-specific rules, consider adding a short AGENTS.md with verified commands and boundaries."
        )

    evidence = matches[:8]
    if not evidence:
        evidence = related[:8]

    return {
        "schema_version": 1,
        "action": action,
        "blocking": action == "ask",
        "reason": reason,
        "question": question,
        "choices": choices,
        "repo": context.get("repo"),
        "evidence": evidence,
        "instructions_found": instructions,
        "repo_setup_suggestion": setup_suggestion,
        "agent_guidance": agent_guidance,
        "limitations": [
            "This is a heuristic recommendation, not a semantic model judgment.",
            "A matching path or keyword is a lead to inspect, not proof of behavior.",
        ],
    }
