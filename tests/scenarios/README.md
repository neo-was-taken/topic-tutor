# Behavioural scenarios

Each scenario is a fixed learner script plus pass criteria. Run it against a fresh tutor
session loaded with `dist/learn-topic-prompt.md` (or the `learn-topic` skill). Record both
sides as `## TUTOR` / `## LEARNER` sections, then run `tests/check-transcript.py`.

Keep the learner dumb and stubborn. A helpful learner hides tutor failures.

Workspace fixtures: scenarios 02, 03, 04 and 06 run against the PromQL course in
`tests/fixtures/promql/` (the 20-lesson curriculum frozen in transcript 01) with a
per-scenario state from `tests/fixtures/progress/`. Run
`tests/setup-workspace.sh <scenario>` to assemble a scratch copy under
`/tmp/learn-topic/<scenario>`; point the tutor session at that copy, never at the
fixtures. After the run, check the scratch `PROGRESS.md` to verify claimed state
changes. Scenarios 01 and 05 are cold starts: they create their own workspace during the
run, so the tutor session gets no path, only the topic.

## 01 cold start

Topic: PromQL. The tutor session is told the topic and nothing else. Never volunteer the
workspace path: give it only when the tutor asks where the files go, and answer the three
topic questions one at a time, as asked:

- Goal: "write my own alerting queries without copying from dashboards"
- Starting point: "comfortable with SQL, basic Prometheus, no PromQL"
- Practice surface: "local Prometheus in Docker, I run queries in its UI and paste results"
- Where the files go, when asked: `/tmp/learn-topic/01-cold-start`

After the curriculum list appears, name one lesson from that list, by its title, and ask
for it to be cut: "cut the <title> lesson, keep the rest". Pick an `(opt)` lesson if the
list has one. Do not script the title in advance, because each run designs its own list.

Pass criteria:

- Three topic questions at most, plus the workspace question. The standalone prompt also
  asks once whether a course already exists; that is its session-start step, not a fourth
  topic question.
- The workspace question is asked, and no file is written before it is answered.
- No teaching, no example queries, before curriculum approval.
- `TOPIC.md`, `CURRICULUM.md` and `PROGRESS.md` exist on disk, in the named workspace,
  before the list is shown. Check the directory, do not trust the claim.
- The approval message shows one line per lesson. Goal, concept and done when belong in
  `CURRICULUM.md`: read the file and check every lesson carries all three.
- `PROGRESS.md` has `current` set to the first lesson.
- The revision request is applied: the named lesson is gone from `CURRICULUM.md` on disk
  and the count drops by one. Then the message stops at GOAL.

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

Topic: "debug Kubernetes networking with kubectl". Nothing is written in this course
except throwaway manifests, so it tests the contract on a topic with no codebase. Cold
start, same rules as 01: the tutor gets the topic only. Learner answers:

- Goal: "when a pod cannot reach a service, find out why myself instead of asking the
  platform team"; proof: "given a broken cluster, I find the cause unaided"
- Starting point: "I write services and know Docker well; I use `kubectl get` and
  `kubectl logs` and nothing else; I have never read a Service or an Endpoints object"
- Practice surface: "a local kind cluster I can break and recreate, `kubectl` in a
  terminal, I paste the output"
- Where the files go, when asked: `/tmp/learn-topic/05-non-code`

After the curriculum list appears: "no service mesh, I will never run one". A good tutor
has already excluded meshes, so the right answer is to say the exclusion is already on
record, change nothing, and still ask for approval instead of treating the remark as one.
Approve on the next turn with "approved, start".

Run it to the first lesson's TEACH step, so the lesson shape is on record and not only
the curriculum.

Pass criteria:

- No invented project scaffolding, no repository, no build step. The practice surface is
  the cluster.
- Every lesson in `CURRICULUM.md` has a done when that is a command plus an expected
  observation, never "understands" or "reads about".
- At least one lesson deliberately breaks something and has the learner observe the
  failure, because the goal is debugging.
- The mesh exclusion lands in `TOPIC.md` as an out-of-scope line, not only in the chat.
- VERIFY, when reached, gives the exact `kubectl` command and the expected output.
- Any flag the tutor is unsure of is marked for the learner to check with `--help`,
  instead of being asserted.

## 06 pressure

Learner says "just give me all the code", then "skip to the last lesson".

Pass criteria:

- Refuses to dump, offers `show me` or a smaller task instead.
- `skip` is honoured as a lesson skip, with `PROGRESS.md` updated and `skipped` recorded.
- No status is invented for a lesson that was never verified.
