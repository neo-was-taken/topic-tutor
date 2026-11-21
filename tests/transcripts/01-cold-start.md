# Scenario 01: cold start

Topic: PromQL. Re-recorded 2026-11-17 against `dist/topic-tutor-prompt.md`. The tutor
session was given the topic only: no workspace path, no scenario script, no pass criteria.
Learner lines are the fixed script from `tests/scenarios/README.md`, relayed verbatim.

Verified on disk after the run, not taken from the tutor's claims:

- `/tmp/topic-tutor/01-cold-start/` did not exist while the workspace question was asked,
  and held `TOPIC.md`, `CURRICULUM.md` and `PROGRESS.md` before the lesson list was shown.
- All 25 frozen lessons in `CURRICULUM.md` carry goal, concept and done when.
- `PROGRESS.md` has `pace: 3`, `current: L0.1`, no lessons started.
- The cut lesson (`L2.6 topk`) is absent from `CURRICULUM.md`; the count fell 26 to 25.

## LEARNER

teach me PromQL

## TUTOR

Before we start: do you already have a course for this, with `TOPIC.md`, `CURRICULUM.md` and `PROGRESS.md` somewhere I can read? If yes, give me the path. If not, say "new" and we begin from scratch.

## LEARNER

new

## TUTOR

New course it is.

First question: what do you want to be able to do with PromQL, and what would prove you can do it? For example, "write the queries behind an alert that fires on real error rates" or "build a dashboard panel for latency percentiles" or "debug someone else's broken query". Give me the concrete thing you picture yourself doing unaided.

## LEARNER

write my own alerting queries without copying from dashboards

## TUTOR

Good, that is a sharp goal.

Second question: what do you already know? Have you written any PromQL before, even copied and modified? Do terms like label matcher, `rate()`, instant vector, range vector mean anything to you, or is this the first contact?

## LEARNER

comfortable with SQL, basic Prometheus, no PromQL

## TUTOR

Noted: SQL-fluent, Prometheus basics, PromQL from zero.

Third question: where will you type queries, and how do we check the result? Options I can picture:

- A real Prometheus you already have, via its web UI (`/graph`) or `curl` against `/api/v1/query`
- A Grafana Explore tab pointed at a Prometheus datasource
- A throwaway local Prometheus (Docker) scraping itself, which gives you real `up`, `scrape_duration_seconds` and HTTP metrics to play with

Which one do you have access to right now, and what version of Prometheus is behind it if you know?

## LEARNER

local Prometheus in Docker, I run queries in its UI and paste results

## TUTOR

Good: local Prometheus in Docker, queries in its web UI, results pasted to me.

Last thing before I write anything: where should the three course files go? Give me a directory path, for example `~/promql-course/` or a path inside your current project. I will create `TOPIC.md`, `CURRICULUM.md` and `PROGRESS.md` there.

## LEARNER

/tmp/topic-tutor/01-cold-start

## TUTOR

Written to `/tmp/topic-tutor/01-cold-start/`: `TOPIC.md`, `CURRICULUM.md`, `PROGRESS.md`.

Assumptions I filled in, say the word if any are wrong: 15-30 minutes per session, pace 3 (standard), goal is alerting so every lesson serves that, Prometheus version treated as unknown until we read it off your server, and out of scope are Alertmanager routing and notifications, Grafana, exporter authoring, long-term storage.

Proposed lessons, 26 in five phases:

**Phase 0 - Environment and data model**
- L0.1 Pin the environment: read your server's own version
- L0.2 The data model: metric name, labels, sample
- L0.3 Selectors and label matchers: `=`, `!=`, `=~`, `!~`
- L0.4 Instant vector and range vector: what `[5m]` does

**Phase 1 - Counters and rates**
- L1.1 Counter or gauge: classify before you query
- L1.2 `rate()`: a counter becomes a per-second rate
- L1.3 `increase()`, `irate()` and `rate()`: which one for an alert
- L1.4 Counter resets and window size: rates that lie
- L1.5 Staleness and lookback: debugging "no data"

**Phase 2 - Aggregation and math**
- L2.1 Aggregation operators: `sum`, `avg`, `min`, `max`, `count`
- L2.2 `by` and `without`: which labels survive
- L2.3 Vector and scalar arithmetic: units and percentages
- L2.4 Vector matching with `on` and `ignoring`
- L2.5 `group_left` and `group_right`: many-to-one joins
- L2.6 `topk`, `bottomk`, `count_values` (opt)

**Phase 3 - Query shapes alerts need**
- L3.1 Comparison operators and `bool`: empty means healthy
- L3.2 The error ratio: aggregate, then divide
- L3.3 Histograms and `histogram_quantile`: latency percentiles
- L3.4 `absent()` and `absent_over_time()`: alert on silence
- L3.5 `offset` and subqueries: now versus earlier

**Phase 4 - From query to alert**
- L4.1 Rule files and reloading into the container
- L4.2 `for`, pending, and the `ALERTS` metric
- L4.3 Labels, annotations and templating
- L4.4 Testing rules with `promtool`
- L4.5 Alert hygiene: cardinality, flapping, no-data
- L4.6 Capstone: an alert from a symptom, unaided

What do you want cut or reordered, or shall I freeze this list and start L0.1?

## LEARNER

cut the topk lesson, keep the rest

## TUTOR

L2.6 is cut. The list is frozen at 25 lessons.

**L0.1 Pin the environment — GOAL**

You will learn how to ask Prometheus which version of itself it is running, using a query instead of a shell command. Afterwards you can pin that version in `TOPIC.md`, so that every flag, function and rule syntax we use for the rest of the course is checked against your server rather than my memory.

Ready to start the teaching step?
