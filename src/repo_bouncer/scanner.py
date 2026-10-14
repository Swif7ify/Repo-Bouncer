"""Bounded, read-only repository inventory and keyword evidence search."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any


MAX_FILES = 5000
MAX_CANDIDATES = 36
MAX_FILE_BYTES = 96_000
MAX_TOTAL_BYTES = 900_000
MAX_LINES_PER_FILE = 1200

IGNORED_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "node_modules",
    "vendor",
    "dist",
    "build",
    "target",
    ".next",
    ".nuxt",
    ".turbo",
    "coverage",
    "__pycache__",
}

SENSITIVE_PARTS = {
    ".aws",
    ".azure",
    ".ssh",
    ".gnupg",
    "secrets",
    "credentials",
    "private_keys",
}

SENSITIVE_NAMES = {
    ".env",
    ".env.local",
    ".env.production",
    "id_rsa",
    "id_ed25519",
    "credentials",
    "secrets.json",
}

TEXT_SUFFIXES = {
    ".md",
    ".mdx",
    ".rst",
    ".txt",
    ".toml",
    ".yaml",
    ".yml",
    ".json",
    ".py",
    ".pyi",
    ".js",
    ".jsx",
    ".mjs",
    ".cjs",
    ".ts",
    ".tsx",
    ".go",
    ".rs",
    ".java",
    ".kt",
    ".cs",
    ".php",
    ".rb",
    ".swift",
    ".vue",
    ".svelte",
    ".sql",
    ".sh",
    ".ps1",
    ".html",
    ".css",
}

INSTRUCTION_NAMES = {
    "agents.md",
    "claude.md",
    "gemini.md",
    "copilot-instructions.md",
}

MANIFEST_NAMES = {
    "package.json",
    "pyproject.toml",
    "requirements.txt",
    "go.mod",
    "cargo.toml",
    "pom.xml",
    "build.gradle",
    "build.gradle.kts",
    "composer.json",
    "gemfile",
}

CODE_SUFFIXES = {
    ".py", ".pyi", ".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx", ".go",
    ".rs", ".java", ".kt", ".cs", ".php", ".rb", ".swift", ".vue",
    ".svelte", ".sql",
}

STOP_WORDS = {
    "about", "after", "again", "also", "and", "are", "because", "before",
    "better", "build", "can", "change", "code", "could", "create", "does",
    "file", "for", "from", "have", "help", "into", "make", "more", "need",
    "please", "project", "repo", "repository", "should", "some", "that",
    "the", "their", "then", "there", "this", "those", "through", "with",
    "work", "would", "you", "your",
}

TOKEN_RE = re.compile(r"[a-zA-Z][a-zA-Z0-9_-]{2,}")


def prompt_terms(prompt: str) -> list[str]:
    terms: list[str] = []
    for raw in TOKEN_RE.findall(prompt.lower()):
        token = raw.strip("-_")
        if token and token not in STOP_WORDS and token not in terms:
            terms.append(token)
    return terms[:12]


def _is_sensitive(path: Path) -> bool:
    parts = {part.lower() for part in path.parts}
    name = path.name.lower()
    if parts & SENSITIVE_PARTS or name in SENSITIVE_NAMES:
        return True
    if name.startswith(".env") or name.endswith((".pem", ".p12", ".pfx", ".key")):
        return True
    return any(word in name for word in ("secret", "credential", "private-key"))


def _path_category(rel: str, path: Path) -> str | None:
    name = path.name.lower()
    lower = rel.lower()
    if (
        name in INSTRUCTION_NAMES
        or name.endswith(".instructions.md")
        or ".cursor/rules/" in lower
        or ".agents/skills/" in lower
        or ".claude/rules/" in lower
        or ".claude/skills/" in lower
        or ".github/agents/" in lower
    ):
        return "agent instructions"
    if name in {"readme.md", "readme.mdx", "readme.rst"}:
        return "project overview"
    if name in MANIFEST_NAMES or path.suffix.lower() == ".sln" or name in {"pnpm-workspace.yaml", "package-lock.json"}:
        return "project manifest"
    if "test" in lower or "spec" in lower:
        return "tests"
    if name in {"architecture.md", "database.md", "security.md", "contributing.md"}:
        return "project guidance"
    if ".github/workflows/" in lower or ".gitlab-ci" in lower or "jenkinsfile" in lower:
        return "CI configuration"
    return None


def scan_repository(root: Path, prompt: str) -> dict[str, Any]:
    """Inspect repository names and bounded text matches without executing anything."""
    repo = root.expanduser().resolve(strict=True)
    if not repo.is_dir():
        raise ValueError(f"Repository path is not a directory: {repo}")

    terms = prompt_terms(prompt)
    inventory: list[Path] = []
    truncated = False

    for current, dirs, filenames in os.walk(repo, topdown=True, followlinks=False):
        current_path = Path(current)
        dirs[:] = [
            name
            for name in dirs
            if name.lower() not in IGNORED_DIRS
            and name.lower() not in SENSITIVE_PARTS
            and not (current_path / name).is_symlink()
        ]
        for filename in filenames:
            candidate = current_path / filename
            if candidate.is_symlink() or _is_sensitive(candidate):
                continue
            inventory.append(candidate)
            if len(inventory) >= MAX_FILES:
                truncated = True
                break
        if truncated:
            break

    tagged: list[tuple[int, Path, str]] = []
    for path in inventory:
        rel = path.relative_to(repo).as_posix()
        category = _path_category(rel, path)
        path_text = re.sub(r"[^a-z0-9]+", " ", rel.lower())
        path_hits = [term for term in terms if term in path_text]
        priority = (5 if category == "agent instructions" else 0)
        priority += (3 if category in {"project overview", "project manifest", "project guidance"} else 0)
        priority += (2 if category in {"tests", "CI configuration"} else 0)
        score = priority + 4 * len(path_hits)
        if score:
            tagged.append((score, path, category or "request-related path"))

    tagged.sort(key=lambda item: (-item[0], len(item[1].parts), item[1].as_posix().lower()))
    candidates = tagged[:MAX_CANDIDATES]
    matches: list[dict[str, Any]] = []
    total_bytes = 0

    for _, path, category in candidates:
        try:
            size = path.stat().st_size
        except OSError:
            continue
        if size > MAX_FILE_BYTES or total_bytes + size > MAX_TOTAL_BYTES:
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name.lower() not in {"makefile", "dockerfile"}:
            continue
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        total_bytes += size
        found_lines: dict[str, list[int]] = {}
        for line_no, line in enumerate(content.splitlines()[:MAX_LINES_PER_FILE], start=1):
            lowered = line.lower()
            for term in terms:
                if re.search(rf"\b{re.escape(term)}\b", lowered):
                    found_lines.setdefault(term, []).append(line_no)
        if found_lines:
            matches.append(
                {
                    "path": path.relative_to(repo).as_posix(),
                    "category": category,
                    "matched_terms": list(found_lines),
                    "lines": sorted({n for nums in found_lines.values() for n in nums})[:8],
                }
            )

    categories: dict[str, list[str]] = {}
    for _, path, category in tagged:
        categories.setdefault(category, []).append(path.relative_to(repo).as_posix())

    source_count = sum(1 for path in inventory if path.suffix.lower() in CODE_SUFFIXES)
    return {
        "repo": str(repo),
        "prompt_terms": terms,
        "instructions": categories.get("agent instructions", [])[:12],
        "manifests": categories.get("project manifest", [])[:12],
        "tests": categories.get("tests", [])[:12],
        "related_paths": [
            {"path": path.relative_to(repo).as_posix(), "category": category}
            for score, path, category in candidates
            if (
                set(terms)
                & set(re.sub(r"[^a-z0-9]+", " ", path.relative_to(repo).as_posix().lower()).split())
            )
        ][:12],
        "matches": matches[:12],
        "source_file_count": source_count,
        "inventory_truncated": truncated,
    }
