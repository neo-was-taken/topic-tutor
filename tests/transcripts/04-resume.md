# Scenario 04: resume

Fresh session against the fixture workspace (`tests/setup-workspace.sh 04-resume`):
`current: L1.4`, `L1.2 done shaky`, last session two days ago. Learner says "back".
Tutor and learner ran as separate sessions; learner outputs are scripted. Recorded
2026-11-17.

## LEARNER

back

## TUTOR

Welcome back. Where we left off, from `PROGRESS.md`:

- 7 of 20 lessons done: L0.1 through L1.1 and L1.3 are `done solid`; L1.2 is `done shaky` — you mixed up irate and increase, and extrapolation is still unclear.
- `current: L1.4` (aggregation with by and without), pace 3, last session 2026-11-15.

Before we teach anything, `TOPIC.md` declares setup: everything runs in containers, nothing on the host, with `prom/prometheus:v3.16.0` pinned. We need to confirm that still works. Run this in the workspace and paste the output:

```bash
docker run --rm --entrypoint promtool -v "$PWD":/w prom/prometheus:v3.16.0 --version
```

If Docker or the image fails, paste the exact error instead — we fix the harness before anything else. Once it works, we'll do a quick two-question warm-up on L1.2's shaky spots, then start L1.4.

Does that command run cleanly?

## LEARNER

$ docker run --rm --entrypoint promtool -v "$PWD":/w prom/prometheus:v3.16.0 --version
promtool, version 3.16.0

## TUTOR

Harness confirmed: `promtool, version 3.16.0` from the pinned image, exactly what `TOPIC.md` requires. That same `docker run` invocation is our practice surface for everything ahead.

Now the warm-up on L1.2, which `PROGRESS.md` marks `done shaky: mixed up irate and increase; extrapolation still unclear`. Two questions, one at a time, before we touch L1.4.

**Warm-up 1.** You are writing an alert with this wording: "fire if the service handled more than 500 failed requests in the last 30 minutes." The counter is `http_requests_failed_total`. Two candidate expressions:

- `increase(http_requests_failed_total[30m]) > 500`
- `irate(http_requests_failed_total[30m]) > 500`

Pick the expression that matches the alert's wording, and say in one sentence what the other one actually measures. Reason from what each function computes over the window, not from which name looks familiar. If it helps, think of the SQL distinction between "total change across a period" and "current speed" — but commit to an answer either way.

## LEARNER

I'd take increase(), it should be the total added over the 30m window... the name says increase so that's my guess. irate is the instant one, like current speed at the end, so it'd miss most of the window I think. Not fully sure though.

## TUTOR

Right pick, and your irate instinct is correct too. Now replace the name-guess with the mechanism, because you already proved it in L1.1: `increase()` is `rate()` over the window multiplied by the window's seconds. Per-second slope times 1800 seconds gives the total added over 30m. That is why it answers "how many failed requests in total".

One sharpening on irate: it is not just "the current speed". It is a per-second rate computed from the **last two samples only**. So `irate(http_requests_failed_total[30m]) > 500` has two problems: it compares requests-per-second against a total count, wrong units, and the `[30m]` only tells it where to look for those last two samples. Everything earlier in the window is ignored, exactly as you said.

Warm-up question 2, on the part PROGRESS.md still flags as unclear: extrapolation.

Scrapes land every 15s. Inside a 30m window the counter's samples show a rise of exactly 300, but the first and last samples sit a few seconds inside the window edges, not on them.

Predict: does `increase(...[30m])` return exactly 300, more than 300, or less than 300? Why?

## LEARNER

Exactly 300? That's what the samples show... but you said the edges matter, so maybe a bit more? I don't really get why it would change.

## TUTOR

Close: a bit more than 300. Your second guess was right. Here is why it changes: increase() is rate() times the window in seconds, and rate() does not take the first and last samples at face value. It extrapolates the measured slope out to the window edges, because scrapes almost never land exactly on those edges. With 15s scrapes, your samples cover slightly less than the full 30m, so the function extends the slope a little on each side and the result comes out above the raw 300. That extrapolation step is the one part of L1.2 still fuzzy, so I have noted it; we will meet it again when a test demands an exact expected value.

Warm-up done. On to the current lesson.

**L1.4 Aggregation with by and without — goal**

An alert like "total failed requests across the whole service" needs many per-instance series collapsed into one number. In this lesson you will use sum, avg, min and max to aggregate across series, and control the labels that survive: `by` keeps the labels you list, `without` drops them. Afterwards you can turn per-instance series into a per-job total and predict exactly which labels remain on the result.

Ready to start?
