# Behavioural scenarios

Each scenario is a fixed learner script plus pass criteria. Run it against a fresh tutor
session loaded with `dist/learn-topic-prompt.md` (or the `learn-topic` skill). Record both
sides as `## TUTOR` / `## LEARNER` sections, then run `tests/check-transcript.py`.

Keep the learner dumb and stubborn. A helpful learner hides tutor failures.

Workspace fixtures: scenarios 02, 03, 04 and 06 run against the PromQL course in
`tests/fixtures/promql/` (the 20-lesson curriculum frozen in transcript 01) with a
per-scenario state from `tests/fixtures/progress/`. Run
`tests/setup-workspace.sh <scenario>` to assemble a scratch copy under
`/tmp/opencode/learn/<scenario>`; point the tutor session at that copy, never at the
fixtures. After the run, check the scratch `PROGRESS.md` to verify claimed state
changes. Scenario 01 creates its own workspace during the run.

## 01 cold start

Topic: PromQL. Learner answers, one at a time, as asked:

- Workspace: `/tmp/opencode/learn/promql`
- Goal: "write my own alerting queries without copying from dashboards"
- Starting point: "comfortable with SQL, basic Prometheus, no PromQL"
- Practice surface: "local Prometheus in Docker, I run queries in its UI and paste results"

After the curriculum list appears: "cut the recording-rules lesson, keep the rest".

Pass criteria:

- Three topic questions at most, plus the workspace question.
- No teaching, no example queries, before curriculum approval.
- `TOPIC.md` and `CURRICULUM.md` written on disk before the list is shown.
- Every lesson line has goal, concept and done when.
- The revision request is applied, then the message stops.

## 02 lesson loop

Workspace exists, `current: L1.2`, curriculum has lessons for the topic. Learner runs the
task and pastes a wrong query plus the error text.

Pass criteria over eight messages:

- One step per message; no GOAL and TASK in the same message.
- Learner's query is reviewed, not rewritten.
- The error text is used as evidence.
- No lesson marked done before VERIFY output is pasted.

## 03 stuck learner

Learner replies "I'm stuck" twice in a row during a TASK, then "show me".

Pass criteria:

- Each "I'm stuck" moves exactly one rung of the ladder.
- Rung three is a partial snippet, not the answer.
- `show me` produces the full solution with explanation.

## 04 resume

Fresh session against an existing workspace: `current: L1.4`, `L1.2 done shaky`,
last session two days ago, learner says "back".

Pass criteria:

- Two-line recap, no restart from lesson 1.
- Warm-up question targets the `shaky` lesson.
- Continues at `current` afterwards.
- `PROGRESS.md` is read before any teaching.

## 05 non-code topic

Topic: "debug Kubernetes networking with kubectl". Practice surface is a kind cluster and
`kubectl` commands. Learner is a developer who knows Docker.

Pass criteria:

- No invented project scaffolding; the practice surface is the cluster.
- Every lesson's done when is a command and an expected observation.
- VERIFY gives the exact `kubectl` command.
- Any uncertain flag is flagged for the learner to check with `--help`.

## 06 pressure

Learner says "just give me all the code", then "skip to the last lesson".

Pass criteria:

- Refuses to dump, offers `show me` or a smaller task instead.
- `skip` is honoured as a lesson skip, with `PROGRESS.md` updated and `skipped` recorded.
- No status is invented for a lesson that was never verified.
