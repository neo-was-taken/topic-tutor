#!/usr/bin/env python3
"""Static checks for the topic-tutor artifacts. Run after build.sh."""

import hashlib
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
SKILL = DIST / "topic-tutor" / "SKILL.md"
PROMPT = DIST / "topic-tutor-prompt.md"

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
BANNED = ["rustic", "docker compose", "uv sync", "VAULT_", "GitLab", "learn-topic"]
MAX_LINES = {"skill": 165, "reference": 100, "prompt": 320}

failures: list[str] = []


def fail(message: str) -> None:
    failures.append(message)


def read(path: Path) -> str:
    if not path.is_file():
        fail(f"missing file: {path.relative_to(ROOT)}")
        return ""
    return path.read_text()


def parse_frontmatter(block: str) -> dict[str, str]:
    """Parse `key: value` pairs, keeping colons in values and folding wrapped lines."""
    fields: dict[str, str] = {}
    key = None
    for line in block.splitlines():
        start = re.match(r"^([A-Za-z][\w-]*):(.*)$", line)
        if start and not line.startswith((" ", "\t", "-")):
            key = start.group(1)
            fields[key] = start.group(2).strip()
            continue
        if key is None:
            continue
        if not line.strip():
            key = None
            continue
        fields[key] = f"{fields[key]} {line.strip()}".strip()
    return fields


def check_frontmatter(text: str) -> None:
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        fail("SKILL.md has no frontmatter block")
        return
    fields = parse_frontmatter(match.group(1))
    for required in ["name", "description"]:
        if required not in fields:
            fail(f"frontmatter lacks a {required} field")
    name = fields.get("name", "").strip()
    description = fields.get("description", "").strip()
    version = fields.get("version", "").strip()
    if name != "topic-tutor":
        fail(f"frontmatter name is {name!r}, expected 'topic-tutor'")
    if not re.fullmatch(r"\d+\.\d+\.\d+", version):
        fail(f"frontmatter version is {version!r}, expected semver")
    if "tags" in fields:
        fail("frontmatter tags belong to the Agensi release package, not the public skill")
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


def check_variants(skill_text: str, prompt_text: str) -> None:
    """Each output must carry its own rendered variant and not the other one's."""
    variants = [
        ("skill", r"propose\s+one\s+inside\s+the\s+current\s+project"),
        ("skill", r"fetch\s+each\s+named\s+file\s+with\s+your\s+skill\s+tool"),
        ("skill", r"use\s+the\s+course\s+directory\s+confirmed\s+at\s+session\s+start"),
        ("prompt", r"ask\s+the\s+learner\s+to\s+paste"),
        ("prompt", r"cannot\s+write\s+files,\s+say\s+so\s+once"),
        ("prompt", r"at\s+the\s+end\s+of\s+this\s+prompt"),
    ]
    texts = {"skill": skill_text, "prompt": prompt_text}
    for owner, pattern in variants:
        other = "prompt" if owner == "skill" else "skill"
        if not re.search(pattern, texts[owner], re.IGNORECASE):
            fail(f"{owner} lacks its own variant text: /{pattern}/")
        if re.search(pattern, texts[other], re.IGNORECASE):
            fail(f"{other} carries {owner}-only text: /{pattern}/")


SUPPORTING_FILES = [
    "references/curriculum-design.md",
    "templates/TOPIC.md",
    "templates/CURRICULUM.md",
    "templates/PROGRESS.md",
]


def check_requires(text: str, label: str) -> None:
    for phrase in ["Requires:", "writable course directory", "VERIFY"]:
        if phrase not in text:
            fail(f"{label} lacks required phrase: {phrase}")


def check_skill_files(skill_text: str) -> None:
    skill_dir = DIST / "topic-tutor"
    for relative in SUPPORTING_FILES:
        if relative not in skill_text:
            fail(f"SKILL.md does not name supporting file: {relative}")
        if not (skill_dir / relative).is_file():
            fail(f"skill is missing {relative}")


def check_lengths() -> None:
    limits = {
        "skill": (SKILL, MAX_LINES["skill"]),
        "reference": (DIST / "topic-tutor" / "references" / "curriculum-design.md", MAX_LINES["reference"]),
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
    check_requires(skill_text, "SKILL.md")
    check_requires(prompt_text, "prompt")
    check_clean(skill_text, "SKILL.md")
    check_clean(prompt_text, "prompt")
    check_variants(skill_text, prompt_text)
    check_skill_files(skill_text)
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
