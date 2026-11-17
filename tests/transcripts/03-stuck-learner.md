# Scenario 03: stuck learner

Fixture workspace (`tests/setup-workspace.sh 03-stuck-learner`): `current: L1.4`, GOAL
and TEACH already delivered in the same session. Transcript starts at the TASK message;
its closing guiding question is hint ladder rung 1, so each "I'm stuck" below moves
exactly one rung (2 then 3), and "show me" reaches rung 4. Learner lines are a fixed
script; tutor ran as a separate session. Recorded 2026-11-17.

## TUTOR

**L1.4 TASK — total rate per instance**

Build a fresh rule file and test file in the workspace, same pattern as L1.1.

Input: synthetic counter `http_requests_total`, sampled every 15s over 10m, all with `job="api"`:

- `instance="a:9100"`, `handler="/login"`, rising 2 per second
- `instance="a:9100"`, `handler="/orders"`, rising 3 per second
- `instance="b:9100"`, `handler="/login"`, rising 4 per second

Goal: one series per instance holding that instance's total per-second request rate.

Constraints:

- Use `rate()` over a 5m window, then aggregate with `sum`.
- The output must carry exactly `instance` and `job`. No `handler`, no metric name.
- Expected values: 5 for `a:9100`, 4 for `b:9100`.
- Choose `by` or `without` yourself. Both can work here; pick one and be ready to say why.
- Prove it with `promtool test rules` in the pinned v3.16.0 container. Make the test strict: it must fail if `handler` survives or a total is wrong.

Paste your files or the promtool output when you run it.

Before you type the expression: look at the input label sets — which labels must survive into the result, and which must disappear?

## LEARNER

I'm stuck

## TUTOR

No problem — this lesson rests on one mental model. Here it is.

Think of `sum` as sorting series into buckets. Every series with the same values for the grouping labels lands in one bucket; the values in each bucket get added, and the result carries only the grouping labels. Everything else disappears.

`by (instance, job)` means: one bucket per distinct instance+job pair, keep those two labels. `without (handler)` says it from the other side: drop handler, group by everything that remains. In your data both spellings produce the same buckets, so the choice is about which list you would rather write and maintain.

Your SQL background maps directly: `sum by (instance, job)` is `GROUP BY instance, job`; `without` is "group by every column except these".

Two facts to hold in mind: `rate()` already strips the metric name, so each input series carries only job, instance and handler; and the aggregation happens after rate(), on its output.

Now picture the three rate() series as rows in a table. Grouped by (instance, job): how many buckets do you get, and which series land in each?

## LEARNER

I'm stuck

## TUTOR

Let's make it concrete. Here is the skeleton of your expression. The inner part is old material from L1.1: `rate()` over a 5m window gives one per-second rate per input series. The outer part is this lesson's new material, and I have left the decisive piece blank:

```promql
sum ______ (
  rate(http_requests_total{job="api"}[5m])
)
```

The blank is the grouping clause. Two shapes fit there:

- `by (label, ...)` keeps only the labels you list; all others disappear.
- `without (label, ...)` drops the labels you list; all others survive.

Your output must carry exactly `instance` and `job`. Your input series also carry `path`, and `rate()` has already removed the metric name. So exactly one label must go, and the clause you pick decides how.

Think of the blank as the `GROUP BY` line of your SQL query: it names what the buckets are built from.

Task: fill the blank with one of the two shapes, paste the completed expression, and tell me which labels your clause keeps and which it drops.

## LEARNER

show me

## TUTOR

Here is the full solution:

`sum by (instance, job) (rate(http_requests_total{job="api"}[5m]))`

Read it inside out. `rate(...[5m])` runs first, per series: it turns each counter into its per-second slope (2, 3, 4) and drops the metric name. Then `sum` merges series into groups. `by (instance, job)` means: keep these two labels, drop all others. `handler` disappears, the two a:9100 series merge into one, and 2 + 3 = 5. b:9100 stays 4.

The equivalent `without` form is `sum without (handler) (...)`: same result here, because handler is the only extra label. Prefer `by` when you can name exactly what should survive; it stays correct if new labels appear later.

I saved the proof as `l1.4-test.yml` in the workspace:

```yaml
rule_files: []
evaluation_interval: 1m
tests:
  - interval: 1m
    input_series:
      - series: 'http_requests_total{job="api",instance="a:9100",handler="/login"}'
        values: '0+120x10'
      - series: 'http_requests_total{job="api",instance="a:9100",handler="/orders"}'
        values: '0+180x10'
      - series: 'http_requests_total{job="api",instance="b:9100",handler="/login"}'
        values: '0+240x10'
    promql_expr_test:
      - expr: sum by (instance, job) (rate(http_requests_total{job="api"}[5m]))
        eval_time: 10m
        exp_samples:
          - labels: '{job="api",instance="a:9100"}'
            value: 5
          - labels: '{job="api",instance="b:9100"}'
            value: 4
```

`0+120x10` means start at 0, add 120 each minute: 2/s. Expected labels carry no metric name, because rate() removed it and `by` kept only instance and job.

Task: from the workspace, run `docker run --rm --entrypoint promtool -v "$PWD":/w prom/prometheus:v3.16.0 test rules /w/l1.4-test.yml` and paste the output.
