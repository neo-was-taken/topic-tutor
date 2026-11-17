# Curriculum: PromQL

One concept per lesson, one sitting, a small amount of new material, the workspace works
after every lesson. `(opt)` may be skipped. The contract lives in TOPIC.md; contract
changes go there first, then here.

Approved with the recording-rules lesson cut. 20 lessons.

## Phase 0 - Foundations and the test harness

**L0.1 Harness first: rule file + test file, read a PASS and a FAIL diff**
Goal: run the test harness and read both outcomes.
Concept: a rule file plus a test file, checked by promtool, is the feedback loop.
Done when: `promtool test rules` prints SUCCESS for a passing test and a diff for a
deliberately broken one.

**L0.2 Instant vectors and series identity**
Goal: select one series and explain what makes it unique.
Concept: metric name plus label set identifies a series; an instant vector is one
sample per series.
Done when: a test with two series differing only in one label returns both, and the
learner predicts which selector narrows to one.

**L0.3 Range vectors and time**
Goal: select a window of samples and say what it contains.
Concept: a range vector is samples over time per series, not a single value.
Done when: a test confirms the sample count in a 5m window at a 15s scrape interval.

**L0.4 Live scrape, job and instance**
Goal: see real scraped series and their job/instance labels.
Concept: scraping adds job and instance labels; real cardinality is larger than
synthetic tests.
Done when: the live stack is up and a query in the Prometheus UI returns node_exporter
series with job and instance labels.

## Phase 1 - Rates and aggregation

**L1.1 Counters and rate()**
Goal: compute per-second increase of a counter.
Concept: counters only go up; rate() is the per-second slope over a window.
Done when: a test proves rate() over a counter with a known slope, including a reset.

**L1.2 increase, irate, extrapolation**
Goal: choose increase() or irate() for a total-over-window question.
Concept: increase() is rate() times window with extrapolation; irate() uses the last
two samples only.
Done when: a test proves increase() over 30m for a counter, and the learner explains
why irate() gives a different number on the same data.

**L1.3 Gauges over time**
Goal: alert on a gauge's current value and on its trend.
Concept: gauges go up and down; no rate() needed for level alerts, deriv() or
comparisons for trend.
Done when: a test proves a gauge level alert fires and clears at the right samples.

**L1.4 Aggregation with by and without**
Goal: collapse series along chosen labels.
Concept: sum/avg/min/max aggregate across series; by keeps labels, without drops them.
Done when: a test proves sum by (instance, job) keeps exactly those labels.

## Phase 2 - Reshaping series for alert expressions

**L2.1 Filtering with comparisons and set operators**
Goal: keep only the series that matter.
Concept: comparison operators filter by value; and/or/unless combine series sets.
Done when: a test proves a filter keeps matching series and unless removes them.

**L2.2 Label shapes and aggregation as a join key**
Goal: make two metrics' label sets compatible.
Concept: aggregation can strip labels down to a shared join key.
Done when: a test proves two metrics reduced to the same label set.

**L2.3 Vector matching and group_left**
Goal: combine two vectors with different label sets.
Concept: on/ignoring control matching; group_left/group_right allow many-to-one.
Done when: a test proves a many-to-one join with group_left keeps the left labels.

**L2.4 Joining info metrics for context labels**
Goal: enrich an alert expression with metadata labels.
Concept: info metrics carry labels as values of 1; join them for context.
Done when: a test proves an expression gains a team label from an info metric.

## Phase 3 - Writing and testing alert rules

**L3.1 Rule file anatomy**
Goal: write a valid rule file from scratch.
Concept: groups, rules, alert/expr/for/labels/annotations; promtool check rules.
Done when: `promtool check rules` passes on a hand-written file.

**L3.2 Pending, firing and for**
Goal: control when an alert fires.
Concept: for delays firing until the condition holds; pending vs firing states.
Done when: a test proves an alert is pending before for elapses and firing after.

**L3.3 Reading test failures**
Goal: diagnose a failing test from its diff alone.
Concept: the diff shows expected vs got per timestamp; read it before touching expr.
Done when: the learner fixes a deliberately broken expression using only the diff.

**L3.4 Templates in annotations**
Goal: put useful values into alert annotations.
Concept: Go templates with $labels and $value in annotations.
Done when: a test proves an annotation renders the instance label and value.

**L3.5 Alerts on absence**
Goal: alert when a series disappears.
Concept: absent() and absent_over_time() detect missing series; up == 0 is not the
same thing.
Done when: a test proves absent() fires when the series is gone and not otherwise.

**L3.6 Ratios and error budgets**
Goal: write a ratio alert with a safe denominator.
Concept: error ratios need matching numerator/denominator label sets and protection
against zero denominators.
Done when: a test proves an error-ratio alert fires above threshold and stays silent
when the denominator is zero.

## Phase 4 - The goal

**L4.1 Two alerts, unaided**
Goal: write and prove two alert rules for a service, without help.
Concept: the whole loop, applied to the goal itself.
Done when: two original alert rules pass `promtool test rules` with no tutor hints.

**L4.3 Latency SLOs with histograms (opt)**
Goal: alert on a latency budget using histogram_quantile.
Concept: histogram buckets, quantile estimation, multi-window burn rates.
Done when: a test proves a p99 latency alert fires on a synthetic bucket series.
