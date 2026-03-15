#!/usr/bin/env python3
"""Validate Markdown docs links and detect stale documentation wording.

This script checks internal Markdown links in project documentation and fails
if stale wording from legacy documentation tooling is found.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC_FILES = [
    ROOT / "README.md",
    ROOT / "CONTRIBUTING.md",
    *sorted((ROOT / "docs").glob("*.md")),
]

# Markdown link pattern: [text](target)
LINK_PATTERN = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")

# Keep this list strict to active docs (CHANGELOG is historical and excluded).
LEGACY_TERMS = [
    "read the docs",
    "readthedocs",
    "auto-generated using sphinx",
]


def _normalize_target(raw_target: str) -> str:
    """Normalize a Markdown link target by removing wrappers and title suffixes.

    Parameters
    ----------
    raw_target : str
        Raw target text from a Markdown link.

    Returns
    -------
    str
        Normalized target path/URL.

    """
    target = raw_target.strip().strip("<>")

    # Handle link titles: [x](path "title") or [x](path 'title')
    for sep in (' "', " '", " ("):
        if sep in target and not target.startswith(("http://", "https://")):
            target = target.split(sep, 1)[0]
            break

    return target


def _is_external_link(target: str) -> bool:
    """Return whether a target points to an external URL scheme.

    Parameters
    ----------
    target : str
        Normalized Markdown link target.

    Returns
    -------
    bool
        True when the target uses an external scheme.

    """
    lowered = target.lower()
    return lowered.startswith(("http://", "https://", "mailto:", "tel:"))


def _check_links(file_path: Path) -> list[str]:
    """Check a Markdown file for broken internal links.

    Parameters
    ----------
    file_path : Path
        Markdown file path to check.

    Returns
    -------
    list[str]
        Validation error messages for broken links.

    """
    errors: list[str] = []
    text = file_path.read_text(encoding="utf-8")

    for line_no, line in enumerate(text.splitlines(), start=1):
        for match in LINK_PATTERN.finditer(line):
            target = _normalize_target(match.group(1))

            if not target or _is_external_link(target) or target.startswith("#"):
                continue

            path_part = target.split("#", 1)[0]
            resolved = (file_path.parent / path_part).resolve()

            if not resolved.exists():
                rel_file = file_path.relative_to(ROOT)
                rel_target = Path(path_part)
                errors.append(f"{rel_file}:{line_no}: broken link target '{rel_target}'")

    return errors


def _check_legacy_wording(file_path: Path) -> list[str]:
    """Check a Markdown file for outdated docs wording.

    Parameters
    ----------
    file_path : Path
        Markdown file path to scan.

    Returns
    -------
    list[str]
        Validation error messages for legacy terms.

    """
    errors: list[str] = []
    text = file_path.read_text(encoding="utf-8")
    lowered = text.lower()

    for term in LEGACY_TERMS:
        if term in lowered:
            rel_file = file_path.relative_to(ROOT)
            errors.append(f"{rel_file}: contains legacy term '{term}'")

    return errors


def main() -> int:
    """Run documentation validation checks.

    Returns
    -------
    int
        Process exit code: 0 on success, 1 on failure.

    """
    errors: list[str] = []

    for file_path in DOC_FILES:
        if not file_path.exists():
            errors.append(f"missing documentation file: {file_path.relative_to(ROOT)}")
            continue

        errors.extend(_check_links(file_path))
        errors.extend(_check_legacy_wording(file_path))

    if errors:
        print("Documentation checks failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Documentation checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
