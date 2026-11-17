#!/usr/bin/env python3
"""Static checks for the learn-topic artifacts. Run after build.sh."""

import hashlib
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
SKILL = DIST / "learn-topic" / "SKILL.md"
PROMPT = DIST / "learn-topic-prompt.md"

REQUIRED_SECTIONS = [
    "# Role",
    "# Workspace",
    "# Session start",
    "# Cold start",
    "# The lesson loop",
    "# Teaching rules",
    "# Accuracy",
    "# Pace",
    "# State",
    "# Hard rules",
]
REQUIRED_PROMPT_SECTIONS = REQUIRED_SECTIONS + ["## Curriculum design", "## File templates"]
BANNED = ["rustic", "docker compose", "uv sync", "VAULT_", "GitLab"]
MAX_LINES = {"skill": 150, "reference": 100, "prompt": 320}

failures: list[str] = []


def fail(message: str) -> None:
    failures.append(message)


def read(path: Path) -> str:
    if not path.is_file():
        fail(f"missing file: {path.relative_to(ROOT)}")
        return ""
    return path.read_text()


def check_frontmatter(text: str) -> None:
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        fail("SKILL.md has no frontmatter block")
        return
    fields = dict(
        line.split(":", 1) for line in match.group(1).splitlines() if ":" in line
    )
    name = fields.get("name", "").strip()
    description = fields.get("description", "").strip()
    if name != "learn-topic":
        fail(f"frontmatter name is {name!r}, expected 'learn-topic'")
    if len(description) < 80:
        fail("frontmatter description is too short to trigger reliably")
    for phrase in ["teach me", "learning plan", "TOPIC.md"]:
        if phrase.lower() not in description.lower():
            fail(f"frontmatter description lacks trigger phrase: {phrase}")


def check_sections(text: str, sections: list[str], label: str) -> None:
    for section in sections:
        if section not in text:
            fail(f"{label} lacks section: {section}")


def check_clean(text: str, label: str) -> None:
    for token in ["@@", "<!-- skill only -->", "<!-- prompt only -->", "<!-- end -->"]:
        if token in text:
            fail(f"{label} contains leftover build marker: {token}")
    for word in BANNED:
        if word.lower() in text.lower():
            fail(f"{label} leaks project-specific vocabulary: {word}")


def check_skill_files() -> None:
    skill_dir = DIST / "learn-topic"
    for relative in [
        "references/curriculum-design.md",
        "templates/TOPIC.md",
        "templates/CURRICULUM.md",
        "templates/PROGRESS.md",
    ]:
        if not (skill_dir / relative).is_file():
            fail(f"skill is missing {relative}")


def check_lengths() -> None:
    limits = {
        "skill": (SKILL, MAX_LINES["skill"]),
        "reference": (DIST / "learn-topic" / "references" / "curriculum-design.md", MAX_LINES["reference"]),
        "prompt": (PROMPT, MAX_LINES["prompt"]),
    }
    for label, (path, limit) in limits.items():
        if not path.is_file():
            continue
        lines = len(path.read_text().splitlines())
        if lines > limit:
            fail(f"{label} is {lines} lines, limit is {limit}")


def snapshot() -> dict[str, str]:
    return {
        str(path.relative_to(DIST)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(DIST.rglob("*"))
        if path.is_file()
    }


def check_drift() -> None:
    before = snapshot()
    result = subprocess.run(
        ["bash", str(ROOT / "build.sh")],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    if result.returncode != 0:
        fail(f"build.sh failed during drift check: {result.stderr.strip()}")
        return
    if snapshot() != before:
        fail("dist/ changed after rebuild; build is not deterministic")


def main() -> int:
    skill_text = read(SKILL)
    prompt_text = read(PROMPT)

    check_frontmatter(skill_text)
    check_sections(skill_text, REQUIRED_SECTIONS, "SKILL.md")
    check_sections(prompt_text, REQUIRED_PROMPT_SECTIONS, "prompt")
    check_clean(skill_text, "SKILL.md")
    check_clean(prompt_text, "prompt")
    check_skill_files()
    check_lengths()

    if "--no-drift" not in sys.argv:
        check_drift()

    if failures:
        print("FAIL")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    for label, path in [("skill", SKILL), ("prompt", PROMPT)]:
        print(f"ok {label}: {len(path.read_text().splitlines())} lines")
    print("ok all static checks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
