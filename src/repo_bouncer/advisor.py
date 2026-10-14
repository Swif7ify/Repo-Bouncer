"""Explainable repo-aware routing and interactive briefs for coding requests."""

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
DESIGN_DOMAIN_RE = re.compile(
    r"\b(ui|ux|design|frontend|front[- ]end|interface|layout|visual|styling|style|look|feel|"
    r"screen|page|dashboard|website|site|web app|component|button|form|font|theme|color|colour|css|stylesheet)\b",
    re.I,
)
DESIGN_OPINION_RE = re.compile(
    r"\b(improve|better|modern|modernize|weird|strange|off|bad|dated|messy|clean|cleaner|prettier|nicer|ugly|unpolished|polish|polished|refine|"
    r"redesign|refresh|rework)\b"
    r"|\b(?:looks?|feels?)\b.{0,24}\b(weird|off|dated|messy|wrong|bad)\b",
    re.I,
)
DESIGN_DIRECTION_RE = re.compile(
    r"\b(accessib(?:le|ility)|wcag|responsive|mobile|conversion|brand|visual identity|"
    r"typography|font|spacing|contrast|color palette|colour palette|dark mode|light mode|"
    r"minimal|minimalist|bold|editorial|playful|reference|inspired by|keep the current)\b",
    re.I,
)
JUDGMENT_REQUEST_RE = re.compile(
    r"\b(up to you|your call|use your judgment|use your judgement|"
    r"use your own judgment|use your own judgement|use my judgment|use my judgement|"
    r"choose for me|make the call|at your discretion|whatever you think is best|"
    r"you decide|take the lead|surprise me)\b",
    re.I,
)
ISSUE_REPORT_RE = re.compile(
    r"\b(error|exception|traceback|stack trace|not working|doesn't work|does not work|"
    r"broken|fail(?:s|ed|ure)?|bug|issue|problem)\b",
    re.I,
)
FEATURE_REQUEST_RE = re.compile(r"\b(add|build|create|implement|introduce|enable|support)\b", re.I)


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
    design_request = bool(DESIGN_DOMAIN_RE.search(clean_prompt) and DESIGN_OPINION_RE.search(clean_prompt))
    design_direction_given = bool(DESIGN_DIRECTION_RE.search(clean_prompt))
    judgment_requested = bool(JUDGMENT_REQUEST_RE.search(clean_prompt))
    issue_report = bool(ISSUE_REPORT_RE.search(clean_prompt))
    feature_request = bool(FEATURE_REQUEST_RE.search(clean_prompt))

    action = "proceed"
    reason = "The request appears specific enough for a low-risk first pass."
    question = None
    choices: list[str] = []
    interaction = None
    agent_guidance = "Proceed with the requested change and verify the smallest relevant behavior."

    if not clean_prompt:
        action = "ask"
        reason = "No task was provided."
        question = "What would you like changed, and what outcome should count as success?"
        choices = [
            "I will describe the change and how to tell it worked.",
            "Inspect the repository and suggest a few concrete tasks; do not edit yet.",
            "Use your judgment: inspect the repository and recommend a sensible first step; do not edit yet.",
        ]
        agent_guidance = (
            "Wait for the user to provide a task unless they choose an inspect/recommend option. If they delegate "
            "the first step, inspect the repository and suggest a concrete task without editing."
        )
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
    elif issue_report and not feature_request:
        action = "inspect"
        reason = "The request reports a failure. Trace the supplied error through the relevant code and checks before proposing a fix."
        if judgment_requested:
            agent_guidance = (
                "Start with the pasted error or reproduction, then inspect the likely implementation and relevant tests. "
                "The user delegated the fix: choose the safest evidence-supported correction, verify it, and explain "
                "assumptions. Ask only if a required fact is unavailable or a safety boundary blocks the fix."
            )
        else:
            agent_guidance = (
                "Start with the pasted error or reproduction, then inspect the likely implementation and relevant tests. "
                "Do not ask a generic clarification before this first investigation. Ask one focused question only if "
                "the evidence leaves materially different fixes or expected behaviors; make the options concise and "
                "evidence-based, keep Use your judgment last, and accept a custom answer."
            )
    elif feature_request and not design_request:
        action = "inspect"
        reason = "The request adds product behavior. Inspect the existing flow and conventions before choosing an implementation."
        if judgment_requested:
            agent_guidance = (
                "Inspect the current behavior, related routes/components, data and API boundaries, instructions, and "
                "relevant tests or docs. The user delegated product choices: implement the smallest coherent feature "
                "that fits the request and project, then explain assumptions. Ask only if blocked by a required fact "
                "or safety boundary."
            )
        else:
            agent_guidance = (
                "Inspect the current behavior, related routes/components, data and API boundaries, instructions, and "
                "relevant tests or docs. If the requested outcome is clear, state a short plan and proceed. If materially "
                "different behaviors remain possible, ask one focused question with concise repo-informed choices and a "
                "final Use your judgment option; accept custom input and wait before implementing."
            )
    elif design_request and not design_direction_given and not judgment_requested:
        action = "inspect"
        reason = "The request asks for a subjective design improvement without choosing a direction. Inspect the current experience, then ask the user to steer it before editing."
        interaction = {
            "mode": "after_inspection",
            "kind": "design_direction",
            "must_ask": True,
            "question": "After reviewing the current UI, which direction should guide the improvement?",
            "choices": [
                "Polish the existing look: keep the structure and visual identity, but improve spacing, typography, and consistency.",
                "Make it cleaner and more modern: strengthen hierarchy and simplify the visual treatment while preserving behavior.",
                "Make it more distinctive: create a bolder visual direction that still fits the product and audience.",
                "Use your judgment: choose the strongest direction for this product, implement it, and explain your choices.",
            ],
            "allow_custom_answer": True,
        }
        agent_guidance = (
            "Inspect the relevant screens, components, styles, and any project design guidance before asking. "
            "Then ask one focused design-direction question using the interactive brief; tailor its wording to the "
            "actual product and keep Use your judgment as the final numbered choice. Wait for the answer before editing. "
            "If the user chooses Use your judgment, proceed without another design interview."
        )
    elif design_request and (design_direction_given or judgment_requested):
        action = "inspect"
        reason = "The request already gives a design direction or delegates that choice. Inspect the current UI before implementing it."
        agent_guidance = (
            "Inspect the relevant screens, components, styles, and project design guidance, then implement the requested "
            "direction. Preserve existing user flows and basic accessibility. If the user delegated judgment, make a "
            "cohesive choice and explain it instead of asking another design question."
        )
    elif vague and judgment_requested:
        action = "inspect"
        reason = "The request is broad but delegates judgment. Inspect the relevant repository context and make a sensible choice."
        agent_guidance = (
            "Inspect the relevant files and project guidance, then make the highest-value, low-risk choice that fits "
            "the request. Do not ask a preference question after the user has delegated judgment. Explain assumptions "
            "and proceed unless a required fact or safety boundary blocks the work."
        )
    elif vague:
        action = "inspect"
        reason = "The request is open-ended. Inspect the relevant project context, then ask one focused question if materially different directions remain."
        interaction = {
            "mode": "after_inspection",
            "kind": "work_direction",
            "must_ask": False,
            "question": "After reviewing the relevant project context, what should this improvement prioritize?",
            "choices": [
                "Improve the user-facing experience and make the main task clearer.",
                "Improve reliability and handle important edge cases.",
                "Simplify the implementation and make it easier to maintain.",
                "Use your judgment: choose the highest-value, low-risk direction for this project and explain why.",
            ],
            "allow_custom_answer": True,
        }
        agent_guidance = (
            "Inspect the relevant files and project guidance before deciding whether to ask. If the prompt already "
            "states a concrete outcome and constraints, skip the interview and proceed. Otherwise ask one focused "
            "question before editing; tailor the suggested choices to the project and keep Use your judgment last. "
            "If selected, proceed without another preference question."
        )
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
        "interaction": interaction,
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
