# Tests

`./tests/run-all.sh` runs every mechanical check: the static checks plus the budget check
for each recorded transcript. Run it after every edit to `src/`.

## What is checked mechanically

`tests/check-artifact.py` builds, checks frontmatter and trigger phrases, required
sections in both outputs, leftover markers, project-specific vocabulary, the per-output
variant blocks, file presence, line budgets, and build determinism.

`tests/check-transcript.py` enforces per-message budgets: prose words, number of code
blocks, code block length, one step label per message. Its limits are the contract's
stated budget plus 10 percent, so "about 200 words" does not fail on 204. It reports
whether each tutor message ends by asking or tasking, which needs a reader to confirm.

## How to run a behavioural scenario

The tutor and learner must be separate sessions, otherwise one model plays both sides and
the tutor can see the script.

1. Start a tutor session with the contents of `dist/learn-topic-prompt.md` and the
   instruction: "You are being evaluated on following this contract. Produce only your next
   message to the learner." Give it the workspace path for a fixture scenario, or the topic
   alone for a cold start. Never give it the scenario section: the pass criteria and the
   learner script are for the relay and the reader, not for the tutor.
2. Start a learner session with only the learner script: "You are a learner, not a tutor.
   Reply only as the learner would. Never help, never break character."
3. Relay messages by hand, or with a small script: tutor output into the learner session,
   learner output back into the tutor session.
4. Record the exchange as `## TUTOR` / `## LEARNER` sections in `tests/transcripts/`.
5. Run `python3 tests/check-transcript.py tests/transcripts/<name>.md` and score the
   scenario's pass criteria by reading it.

The learner session is the part people skip. Without it, the transcript measures nothing:
a tutor session prompted for both sides will always agree with itself.

## What this cannot prove

Both sessions run on the same model, so they share blind spots. Mechanical checks catch
budget and discipline failures. Judgement of quality needs a human reader, and the golden
replay against an independently written curriculum for the same specification is the
strongest available check because the reference was written independently.

Useful failure signal: a scenario where the tutor writes files or teaches during the cold
start. That is a real defect in the contract, not in the learner script.
