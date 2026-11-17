# Test results

Artifacts: `src/SKILL.md` 147 lines, `src/curriculum-design.md` 61 lines,
`dist/learn-topic-prompt.md` 282 lines.

## Static

`tests/check-artifact.py` passes: frontmatter, trigger phrases, required sections in both
outputs, no leftover markers, no project-specific vocabulary, skill resources present,
line budgets, deterministic rebuild.

## Behavioural

| scenario | result | notes |
|---|---|---|
| 01 cold start | pass | 3 topic questions, assumptions stated, files written, list shown, revision applied, stopped at GOAL |
| 04 resume | pass | two-line recap, setup check, continued at `current`, no restart, warm-up correctly skipped |
| Golden replay | pass after fix | see below |
| 02 lesson loop | pending | needs a mid-lesson session |
| 03 stuck learner | pending | needs a TASK in progress |
| 05 non-code topic | pending | |
| 06 pressure | pending | |

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

## Not yet proven

Same-model sessions share blind spots. The golden replay and a real three-lesson session
carry more weight than the scripted scenarios.
