# Test results

Run everything mechanical with `./tests/run-all.sh`. Current sizes are printed by the
static checker; they are not repeated here, because a quoted count goes stale silently.

## Static

`tests/check-artifact.py` passes: frontmatter, trigger phrases, required sections in both
outputs, no leftover markers, no project-specific vocabulary, per-output variants present
in their own output and absent from the other, skill resources present, line budgets,
deterministic rebuild.

## Behavioural

| scenario | result | notes |
|---|---|---|
| 01 cold start | pass (re-recorded) | workspace path withheld until asked: the tutor asked and wrote nothing before the answer; 3 topic questions plus the prompt's resume check; 26 lessons shown, all three fields present in `CURRICULUM.md` on disk, `current: L0.1`; cut applied to 25; stopped at GOAL |
| 02 lesson loop | pass | REVIEW twice on wrong attempts, error diff used as evidence, query never rewritten, VERIFY before pass, `done shaky` recorded on disk |
| 03 stuck learner | pass | each "I'm stuck" moved one rung (2 then 3), rung 3 a skeleton with the grouping clause blank, `show me` gave the full solution with explanation |
| 04 resume | pass (re-recorded) | two-line recap quoting 7 of 20 from the files, setup check, two-question warm-up on shaky L1.2, continued at `current` L1.4, warm-up outcome written to PROGRESS.md |
| Golden replay | pass after fix | see below |
| 05 non-code topic | pass | 24 lessons, every done when a command or a cluster observation, five fault-injection lessons, mesh exclusion written in `TOPIC.md`, versions left unpinned until read off the cluster, no scaffolding invented; ran to TEACH with one 7-line manifest and a prediction question |
| 06 pressure | pass | dump refused with `show me` offered, jump to last lesson declined with reasons, `skip` honoured: `L2.1 skipped` and `current: L2.2` verified on disk, no other status touched |

Recorded 2026-11-17 against the workspace fixtures (`tests/fixtures/`, assembled by
`tests/setup-workspace.sh` into scratch copies under `/tmp/topic-tutor/`). Scenarios 01
and 05 are cold starts and created their own workspace during the run, from a session that
was given the topic and nothing else. Tutor and learner ran as separate sessions; learner
lines are scripted. Tutor state changes were verified on disk after each run, not taken
from the tutor's claims. The 04 transcript was replaced (defect 6) and 01 was re-recorded
(defect 7).

## Golden replay

Input: a specification document plus a learner profile, no hand-written curriculum.
Reference: an independently written 39-lesson curriculum for the same specification.

Run 1 produced 26 lessons. Lesson quality was good: atomic, observable done-when, phases
ending in something usable. Coverage was not. Missing against the specification:

- version control and the commit hygiene the spec's secret rule depends on
- the GitLab project, branch and merge-request step before CI
- runner registration, which the delivery phase cannot start without
- an end-to-end run against a real repository
- the prune and check semantics that live outside the argv builders: retention groups,
  two-phase deletion, `check` exit codes

It also inferred a version pin from a passing mention of a patch release instead of
recording the pin as unknown.

Fixes in `src/`:

- a Coverage section in `curriculum-design.md`: every operation, every unfamiliar tool in
  the practice surface, and every failure mode in the spec maps to a lesson, or becomes an
  explicit out-of-scope line
- a new failure sign: an operation that exists only inside another lesson's example
- an Accuracy rule: a version mentioned in passing is not a pin

Run 2 produced 29 lessons and added `L0.5 Git baseline`, `L4.2 GitLab project and push`,
`L4.3 A runner and the gate in CI`, and `L3.6 End to end against a real repository`. It
left the tool version unpinned until the lesson that checks it, and it reported the
unreachable GitLab and Vault hosts rather than assuming them.

Residual differences from the hand-written curriculum, judged acceptable: no dedicated
dependency-injection or Protocol lesson, no separate prune/check dispatch lesson (both are
covered inside the builder and end-to-end lessons), no cluster concurrency lesson, and no
optional runner-in-cluster lesson. These are depth choices for one project, not coverage
of its specification.

## Defects found and fixed

1. Cold start did not create `PROGRESS.md`; the next session would have found no state.
2. The curriculum approval message exceeded the 200-word budget by nature. It is now
   exempt, and the checker allows it when the message contains lesson IDs.
3. Resume summarised the curriculum as "13 lessons" against a 20-lesson file. Session start
   now requires quoting counts and statuses from the files.
4. Curriculum design omitted requirements-level coverage. Fixed with the Coverage section.
5. A version mentioned in passing was treated as a pin. Fixed with an explicit rule.
6. The recorded 04 evidence was inconsistent: it recapped "13 lessons" for the course
   the cold-start transcript froze at 20 (defect 3's failure shape), and it used
   `current: L0.1` with no shaky lesson while the scenario spec requires `L1.4` with
   `L1.2 done shaky`. Re-recorded against the written spec with fixture files, so the
   counts are quoted from disk and the shaky warm-up path is exercised.
7. The 01 evidence pre-supplied the workspace path, so the workspace question, which the
   design calls a real failure mode, was never exercised, and the recorded path had drifted
   away from `setup-workspace.sh`. Re-recorded with the path withheld.
8. Scenario 01 demanded goal, concept and done when on every line of the approval message,
   which the one-line-per-lesson rule and the word budget make impossible. The three fields
   belong in `CURRICULUM.md`; the criterion now reads the file.
9. The session-start and workspace instructions assumed a working directory and file
   tools, which a pasted chat prompt has neither of. Both are now per-output variants, and
   the static checker fails if an output carries the other's text.
10. Documented budgets and checker constants disagreed (200 and 20 against 220 and 25).
    The checker now derives its limits from the stated budget plus an explicit 10 percent
    tolerance.

## Observations (not criterion failures)

- 03 rung 3: the tutor said the input carries a `path` label where the TASK defined
  `handler`. A slip in the hint text; the ladder behaviour itself was correct.
- 02 VERIFY: the command used a `<your-test-file>` placeholder although the learner's
  paste named `alerts_test.yml`. "Exact command" could be tighter.
- 01 re-recorded: `L0.2 The data model` has a done when of "you label the parts of one
  result in your own words", which is observable only to a reader. It is the weakest done
  when in the generated list.
- 05: `PROGRESS.md` was written with `L0.1 doing` before the lesson ran. Harmless and
  arguably correct, but the contract never asks for it.
- 05: several done-when lines read "the learner names the evidence". For a diagnosis
  course the evidence is the observation, so this is accepted, not a reading lesson.

## Not yet proven

Same-model sessions share blind spots. The golden replay and a real three-lesson session
carry more weight than the scripted scenarios.
