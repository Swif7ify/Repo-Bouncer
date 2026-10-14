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
        lines.extend(["", "Choose an option by number, or reply with a custom answer:"])
        lines.extend(f"{index}. {choice}" for index, choice in enumerate(choices, start=1))
    return "\n".join(lines)
