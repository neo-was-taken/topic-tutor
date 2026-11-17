# Scenario 01: cold start

Topic: PromQL. Workspace: `/tmp/opencode/learn/promql`. Learner is scripted, not helpful.

## TUTOR

New course, so first question. PromQL is a query language, and there are many valid goals: writing alerting rules, debugging production incidents, building dashboards for an SLO, exporting metrics for analysis. The curriculum changes a lot depending on which you need.

**What do you want to be able to do with PromQL, and what would prove it?**

Some examples of "proof" so you know what I'm after:
- "Write the alert rules for a service I run" -> proof: the rules load and fire correctly in a test
- "Debug a slow service from Grafana" -> proof: given a symptom, I write the query chain unaided
- "Answer capacity questions" -> proof: a query that returns the right number on real data

Also tell me what metrics you expect to query (Kubernetes/node_exporter, application metrics, synthetic test data) if you know it.

## LEARNER

I want to write my own alerting queries without copying from dashboards. Proof would be that I can write and test an alert rule for a service I run. Metrics are node_exporter and some application metrics; I can use synthetic test data if that is easier.

## TUTOR

Good. That gives me a concrete target: an alert rule you wrote and proved, on node_exporter and application metrics.

**Second question: what do you already know?**

Specifically:
- Have you written PromQL before, even by copying and tweaking? If so, what parts felt unclear?
- Can you read a metric's labels and understand why `rate(node_cpu_seconds_total[5m])` returns many series rather than one?
- Do you already run Prometheus locally (or have access to one), and have you used `promtool` or Grafana's explore view?
- How comfortable are you with regex and with the idea of a time series database generally (SQL background, for instance)?

Rough answers are fine, "no idea" is a fine answer. This decides where the curriculum starts, not whether you can do the course.

## LEARNER

I'm comfortable with SQL and I've used Prometheus a bit, but I've never written PromQL. I can run Prometheus locally in Docker. I don't know promtool.

## TUTOR

Last question, then I'll write the contract and the lesson list.

**Third question: the practice surface.** I need to know exactly where you type and how we decide "that worked," because `promtool test rules` lets us test alert queries against synthetic series with no exporters running at all. That is fast, reproducible, and it is the same mechanism your real rules go through.

Tell me:
- Does Docker work on this machine, and can it pull images (e.g. `docker run --rm prom/prometheus --version` succeeds)?
- Is `promtool` acceptable to install as a standalone binary, or must everything stay inside containers?
- Do you want live node_exporter scraped locally as well, or is synthetic test data plus the Prometheus UI enough for the course?

My assumption, unless you object: synthetic series for every lesson's verification, plus one small live stack (Prometheus + node_exporter, no Grafana) so you see real cardinality at least once.

## LEARNER

Docker works and can pull images. Keep everything in containers; no host installs. Synthetic data plus promtool is fine, and one live Prometheus + node_exporter stack for real cardinality sounds good. No Grafana needed.

## TUTOR

Contract and curriculum are written to `/tmp/opencode/learn/promql`.

Assumptions I filled in for everything the three questions did not cover:
- **Pins:** `prom/prometheus:v3.16.0`. I verified on this machine that `promtool test rules` and `promtool check rules` both work inside the container via `--entrypoint promtool`. node-exporter tag gets pinned during setup.
- **Scope out:** Grafana, Alertmanager, remote storage, scrape config beyond basics, recording rules beyond one optional lesson.
- **Time:** 30 minutes per session, pace 3.
- **Verification:** a `promtool test rules` `SUCCESS` is the only accepted proof of a lesson.

**Phase 0 - Foundations and the test harness**
L0.1 Harness first: rule file + test file, read a PASS and a FAIL diff
L0.2 Instant vectors and series identity
L0.3 Range vectors and time
L0.4 Live scrape, job and instance

**Phase 1 - Rates and aggregation**
L1.1 Counters and `rate()`
L1.2 `increase`, `irate`, extrapolation
L1.3 Gauges over time
L1.4 Aggregation with `by` and `without`

**Phase 2 - Reshaping series for alert expressions**
L2.1 Filtering with comparisons and set operators
L2.2 Label shapes and aggregation as a join key
L2.3 Vector matching and `group_left`
L2.4 Joining info metrics for context labels

**Phase 3 - Writing and testing alert rules**
L3.1 Rule file anatomy
L3.2 Pending, firing and `for`
L3.3 Reading test failures
L3.4 Templates in annotations
L3.5 Alerts on absence
L3.6 Ratios and error budgets

**Phase 4 - The goal**
L4.1 Two alerts, unaided
L4.2 Recording rules for expensive expressions (opt)
L4.3 Latency SLOs with histograms (opt)

What do you want to cut, reorder, or add before I freeze this and start L0.1?

## LEARNER

Cut the recording-rules lesson, keep the rest.

## TUTOR

Frozen: 20 lessons, recording rules gone.

**L0.1 Harness first** - GOAL

You will get the test harness running: a rule file, a test file, and one command that says `SUCCESS` or shows a diff. After this lesson you can check any alert expression you write in about two seconds, with no Prometheus server and no waiting for a real incident to see whether it fires.

That loop is the whole course. Every expression you meet later gets proven the same way.

Before I teach anything: have a look at `/tmp/opencode/learn/promql` and confirm the three files (`TOPIC.md`, `CURRICULUM.md`, `PROGRESS.md`) are there and read correctly. Then tell me your prompt back.
