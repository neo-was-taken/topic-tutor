# Scenario 02: lesson loop

Fixture workspace (`tests/setup-workspace.sh 02-lesson-loop`): `current: L1.2`, TASK
issued last session (alert expression: counter increased by more than 50 over the last
30 minutes, per instance, using increase()). Mid-lesson, same session; transcript starts
at the learner's first attempt. Learner lines are a fixed script; tutor ran as a separate
session. Recorded 2026-11-17.

## LEARNER

My rule and the test output:

- alert: RequestsSpike
  expr: irate(http_requests_total[30m]) > 50

$ docker run --rm --entrypoint promtool -v "$PWD":/w prom/prometheus:v3.16.0 test rules alerts_test.yml
Unit Testing:  alerts_test.yml
  FAILED:
    alertname: RequestsSpike, time: 30m0s,
        exp: "[{instance=\"web-1\"} 120]"
        got: "[]"

## TUTOR

Good parts: the rule file parses, the harness ran cleanly, and `> 50` is the right comparison shape. The per-instance requirement is also fine in principle: these functions work per series, so the `instance` label survives without extra work.

Now read the diff before editing. `exp: "[{instance=\"web-1\"} 120]"` means at t=30m the test expects RequestsSpike firing for web-1 with value 120. `got: "[]"` means your expression returned no series at that moment. The condition was never true.

Why: the task asks for the **total increase over 30 minutes**, and it named `increase()`. Your expr uses `irate()`, which returns a per-second rate computed from only the last two samples in the window. The `[30m]` does not change that. If the counter grew by 120 over 1800 seconds, irate gives roughly 120/1800 ≈ 0.07 per second. That is nowhere near 50, so the alert never fires and the result is empty. The number 120 the test expects is a total, not a rate; the units must match the threshold.

Fix the expression so it measures the total over the window, re-run the same promtool command, and paste the new output.

## LEARNER

I switched it to increase(http_requests_total[5m]) > 50. Right?

## TUTOR

REVIEW.

Right function this time. `increase()` reports the total growth of the counter over the window, in raw counts, so its result is directly comparable to your threshold of 50. That fixes the units mismatch we read in the diff.

But re-read the task wording: "increased by more than 50 over the last **30 minutes**". Your expression uses `[5m]`. The bracket range is the lookback window that `increase()` sums over, so `[5m]` asks a different question: growth in the last five minutes only. On your test series, most of the growth happened earlier than that, so at time 30m the 5m window sees far less than the 120 the test expects. Same failure shape as before: expected a firing series, got none.

Before you edit, predict: at time 30m, roughly what would the 5m window return versus the 30m window, given how your series grows? Say the two numbers out loud, then make the window match the task, re-run `promtool test rules`, and paste the full output here.

## LEARNER

5m window would be like 20? and the 30m one is 120. Changed it to increase(http_requests_total[30m]) > 50 now. Window fixed.

## TUTOR

The expression now matches the task: `increase()`, a `[30m]` window, threshold 50. And "per instance" comes for free: `increase()` keeps each series' labels, and `> 50` filters each series independently, so web-1 and web-2 are judged separately. No aggregation needed.

Your prediction is right, and the reasoning matters more than the numbers: the counter climbs at the same slope (~4 per minute), so a 5m window collects ~20 and a 30m window ~120. `increase()` scales with the window; that is exactly what `irate()` could not do, since it only ever looks at the last two samples.

But "Window fixed" is a claim, not proof. In this course the only accepted proof is the harness saying so.

VERIFY: from the directory holding your rule and test files, run:

```
docker run --rm --entrypoint promtool -v "$PWD":/w prom/prometheus:v3.16.0 \
  test rules <your-test-file>
```

Expected: `SUCCESS`, with the earlier FAIL diff gone — the test should now see the alert for web-1 at value 120 at the 30m mark.

Run it and paste the full output.

## LEARNER

$ docker run --rm --entrypoint promtool -v "$PWD":/w prom/prometheus:v3.16.0 test rules alerts_test.yml
Unit Testing:  alerts_test.yml
  SUCCESS

## TUTOR

SUCCESS, exactly as expected: the alert for web-1 at 30m, value 120. L1.2 is passed.

Recap, three lines:
- `increase()` is `rate()` times the window in seconds, with extrapolation. It answers "how much in total over this window": 120 over 30m.
- `irate()` uses only the last two samples and returns a per-second rate, about 0.07 here. So `> 50` matched nothing. Your first FAIL diff (`got []`) was a units mismatch, not missing data.
- Match the function to the question: total over a window → `increase()`; sudden per-second spike → `irate()`. And the window must match the task: 30m, not 5m.

Candid note: you first chose irate, then a 5m window, so this took two review rounds. Your prediction and your fix were correct, but the function choice is not automatic yet. That makes this lesson shaky, not solid. We will warm up on it next session.

Status line to copy:

```
L1.2 done shaky: confused irate with increase; two review rounds
```

PROGRESS.md is updated. Next lesson: L1.3, gauges over time.

One check before we close this lesson: in your own words, why did `irate(http_requests_total[30m]) > 50` return no series on the same data where `increase()` returned 120?
