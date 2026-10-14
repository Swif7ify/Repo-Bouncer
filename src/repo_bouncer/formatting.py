"""Human-readable formatting shared by the CLI and host adapters."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any


def format_ask(result: Mapping[str, Any], heading: str) -> str:
    """Render an ask recommendation with numbered choices when available."""
    question = str(result.get("question") or "What outcome should count as success?")
    lines = [heading, question]
    choices = result.get("choices")
    if isinstance(choices, list) and choices:
        lines.extend(["", "Choose a number or reply with a different answer:"])
        lines.extend(f"{index}. {choice}" for index, choice in enumerate(choices, start=1))
    return "\n".join(lines)


def format_interaction(result: Mapping[str, Any], heading: str) -> str:
    """Render a question the agent should ask after inspecting repository context."""
    interaction = result.get("interaction")
    if not isinstance(interaction, Mapping):
        return ""

    question = str(interaction.get("question") or "What direction should guide this work?")
    if interaction.get("must_ask"):
        timing = "Inspect the relevant project context first, then ask before editing."
    else:
        timing = (
            "Inspect the relevant project context first. Ask before editing only if materially different "
            "directions remain; skip the question if the prompt already makes the outcome clear."
        )
    lines = [heading, timing, question]
    choices = interaction.get("choices")
    if isinstance(choices, list) and choices:
        lines.extend(["", "Offer these as choices; accept a custom answer too:"])
        lines.extend(f"{index}. {choice}" for index, choice in enumerate(choices, start=1))
    return "\n".join(lines)
