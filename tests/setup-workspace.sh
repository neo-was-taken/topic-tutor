#!/usr/bin/env bash
# Assemble a scratch course workspace from the fixtures, so a recorded run never
# mutates the committed fixtures. Usage: setup-workspace.sh <scenario>
set -euo pipefail

if [[ $# -ne 1 ]]; then
    printf 'usage: %s <scenario>\n' "$0" >&2
    printf 'scenarios: 02-lesson-loop 03-stuck-learner 04-resume 06-pressure\n' >&2
    exit 2
fi

scenario=$1
root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
fixtures="$root/tests/fixtures"
progress="$fixtures/progress/$scenario.md"
dest="/tmp/opencode/learn/$scenario"

if [[ ! -f "$progress" ]]; then
    printf 'no progress fixture for %s\n' "$scenario" >&2
    exit 1
fi
if [[ -e "$dest" ]]; then
    printf '%s already exists; remove it first for a fresh run\n' "$dest" >&2
    exit 1
fi

mkdir -p "$dest"
cp "$fixtures/promql/TOPIC.md" "$fixtures/promql/CURRICULUM.md" "$dest/"
cp "$progress" "$dest/PROGRESS.md"
printf '%s\n' "$dest"
