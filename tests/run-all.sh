#!/usr/bin/env bash
# Every mechanical check in one command: static artifact checks plus the budget checks
# for each recorded transcript. Behavioural scoring still needs a reader.
set -uo pipefail

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
status=0

printf '== static\n'
python3 "$root/tests/check-artifact.py" || status=1

for transcript in "$root"/tests/transcripts/*.md; do
    printf '\n== %s\n' "$(basename "$transcript")"
    python3 "$root/tests/check-transcript.py" "$transcript" || status=1
done

printf '\n'
if [[ $status -eq 0 ]]; then
    printf 'ok all mechanical checks\n'
else
    printf 'FAIL see output above\n'
fi
exit $status
