# Tests

## What is checked mechanically

`tests/check-artifact.py` builds, checks frontmatter and trigger phrases, required
sections in both outputs, leftover markers, project-specific vocabulary, file presence,
line budgets, and build determinism. Run it after every edit to `src/`.

`tests/check-transcript.py` enforces per-message budgets: prose words, number of code
blocks, code block length, one step label per message. It reports whether each tutor
message ends by asking or tasking, which needs a reader to confirm.

## How to run a behavioural scenario

The tutor and learner must be separate sessions, otherwise one model plays both sides and
the tutor can see the script.

1. Start a tutor session with the contents of `dist/learn-topic-prompt.md`, followed by the
   scenario section from `tests/scenarios/README.md` and the instruction: "You are being
   evaluated on following this contract. Produce only your next message to the learner."
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
replay against the rustic `CURRICULUM.md` is the strongest available check because the
reference was written independently.

Useful failure signal: a scenario where the tutor writes files or teaches during the cold
start. That is a real defect in the contract, not in the learner script.
