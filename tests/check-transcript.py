#!/usr/bin/env python3
"""Mechanical budget checks for a recorded tutor/learner transcript.

Transcript format:

    ## TUTOR
    message text

    ## LEARNER
    reply text

Hard failures: word budget, code block count, oversized code block, more than one
step label. "Ends by waiting" is reported for review because it needs a reader.

The contract says "about 200 words" and "about 20 lines", so the limits below are the
stated budget plus 10 percent. "About" does not fail; a real overrun still does.
"""

import math
import re
import sys
from pathlib import Path

WORD_BUDGET = 200
BLOCK_LINE_BUDGET = 20
TOLERANCE = 1.1

MAX_WORDS = math.floor(WORD_BUDGET * TOLERANCE)
MAX_BLOCK_LINES = math.floor(BLOCK_LINE_BUDGET * TOLERANCE)
MAX_WORDS_CURRICULUM = 400
MAX_BLOCKS = 1
STEP_LABELS = re.compile(r"^\s*(?:#{1,3}\s*)?(GOAL|TEACH|TASK|REVIEW|VERIFY|WRAP)\b", re.MULTILINE)
LESSON_ID = re.compile(r"\bL\d+\.\d+[a-z]?\b")


def split_messages(text: str) -> list[tuple[str, str]]:
    messages: list[tuple[str, str]] = []
    speaker = None
    buffer: list[str] = []
    for line in text.splitlines():
        header = re.match(r"^##\s+(TUTOR|LEARNER)\s*$", line)
        if header:
            if speaker and "".join(buffer).strip():
                messages.append((speaker, "\n".join(buffer).strip()))
            speaker = header.group(1)
            buffer = []
            continue
        buffer.append(line)
    if speaker and "".join(buffer).strip():
        messages.append((speaker, "\n".join(buffer).strip()))
    return messages


def blocks(message: str) -> list[list[str]]:
    found, current = [], None
    for line in message.splitlines():
        if line.strip().startswith("```"):
            if current is None:
                current = []
            else:
                found.append(current)
                current = None
            continue
        if current is not None:
            current.append(line)
    if current is not None:
        found.append(current)
    return found


def prose(message: str) -> str:
    kept, inside = [], False
    for line in message.splitlines():
        if line.strip().startswith("```"):
            inside = not inside
            continue
        if not inside:
            kept.append(line)
    return " ".join(kept)


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: check-transcript.py <transcript.md>")
        return 2

    path = Path(sys.argv[1])
    messages = split_messages(path.read_text())
    if not messages:
        print("FAIL no messages found; check the ## TUTOR / ## LEARNER headers")
        return 1

    failures: list[str] = []
    notes: list[str] = []
    turn = 0

    for speaker, message in messages:
        if speaker != "TUTOR":
            continue
        turn += 1
        words = len(prose(message).split())
        found_blocks = blocks(message)
        labels = STEP_LABELS.findall(message)
        last_line = next(
            (line.strip() for line in reversed(message.splitlines()) if line.strip()), ""
        )

        prefix = f"tutor message {turn}"
        limit = MAX_WORDS_CURRICULUM if len(LESSON_ID.findall(message)) >= 3 else MAX_WORDS
        if words > limit:
            failures.append(f"{prefix}: {words} words of prose, limit {limit}")
        if len(found_blocks) > MAX_BLOCKS:
            failures.append(f"{prefix}: {len(found_blocks)} code blocks, limit {MAX_BLOCKS}")
        for block in found_blocks:
            if len(block) > MAX_BLOCK_LINES:
                failures.append(
                    f"{prefix}: code block of {len(block)} lines, limit {MAX_BLOCK_LINES}"
                )
        if len(labels) > 1:
            failures.append(f"{prefix}: more than one step label: {labels}")
        if not last_line.endswith("?"):
            notes.append(f"{prefix}: ends with {last_line[:60]!r}; confirm it asks or tasks")

    print(f"{len(messages)} messages, {turn} tutor messages")
    for failure in failures:
        print(f"FAIL {failure}")
    for note in notes:
        print(f"REVIEW {note}")
    if failures:
        return 1
    print("ok budgets")
    return 0


if __name__ == "__main__":
    sys.exit(main())
