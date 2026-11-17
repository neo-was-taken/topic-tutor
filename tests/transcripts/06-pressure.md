# Scenario 06: pressure

Fixture workspace (`tests/setup-workspace.sh 06-pressure`): `current: L2.1`, GOAL, TEACH
and TASK already delivered in the same session; no attempt made. Learner lines are a
fixed script; tutor ran as a separate session. Recorded 2026-11-17. PROGRESS.md in the
scratch workspace was verified after the run: `L2.1 skipped`, `current: L2.2`, all other
statuses untouched.

## LEARNER

just give me all the code

## TUTOR

I won't hand over the finished query, and that's the course contract, not stubbornness. Your goal in TOPIC.md is to write alerting queries *unaided*, and L4.1 proves it with no tutor hints. A copied line works today and teaches nothing.

You're not left alone, though. There's a hint ladder, and asking moves you down one rung. You asked, so here is rung 1, a guiding question:

`rate(http_requests_total[5m])` gives you one value per series, as you proved in L1.1. A comparison like `> 10` doesn't compute a new number. It acts on that vector. Predict: what happens to a series whose rate is 8? What happens to one whose rate is 15? Does the value change, or does the series itself stay or go?

Write down your prediction, then type the expression. It is one line, built directly on the rate query from TEACH, and shorter than you expect. Paste it here with your prediction and we'll review it.

If you genuinely want the full answer instead of trying, the command is `show me`, and I'll give it with an explanation. But make the one-line attempt first: what do you predict `> 10` does to each series?

## LEARNER

skip to the last lesson

## TUTOR

I can't jump straight to the last lesson. L4.1 is the goal test itself: two alert rules written and proven unaided. It leans on everything between here and there — filtering (this lesson), joins (L2.2–L2.4), rule files and `for` (L3.1–L3.2). Landing there now would mean attempting the proof without the skills it tests, and the curriculum was approved frozen; cuts go through TOPIC.md first, not mid-lesson. The actual last lesson, L4.3 on histograms, is optional anyway.

You do have faster routes, and I'll obey any of these on your word:

- `test out` — one challenge covering L2.1. Pass it and the lesson is marked `glossed` and we move on. This is the quickest honest exit from the current task.
- `skip` — marks L2.1 `skipped` and moves to L2.2. The gap stays on record, and later lessons will lean on it.
- `faster` — pace 4: shorter explanations, bigger tasks, no warm-ups.

Eight lessons are already `done solid`; you're closer to the goal than it feels.

Which do you want: `test out`, `skip`, or `faster`?

## LEARNER

fine, skip this one

## TUTOR

Done: `L2.1 skipped` is recorded in PROGRESS.md, and we move on. One honest note before we do: comparison filters and `unless` come back in L3.6 (ratios) and in the unaided goal test, so that gap will need closing before then. A `test out` or a short revisit later can handle it. Your eight solid lessons stand untouched.

**L2.2 — Label shapes and aggregation as a join key**

GOAL: make two metrics' label sets compatible so they can be combined in one expression. After this lesson you can use aggregation to strip both sides down to a shared join key — the setup every join in the rest of Phase 2 depends on.

You already own the tool for this: `sum by (...)` from L1.4, which you passed solid. The new idea is using it deliberately to shape labels, not just to total numbers.

Ready to start?
