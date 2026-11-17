# Topic: PromQL

## Goal

Write my own alerting queries without copying from dashboards.

Proof: I can write and test an alert rule for a service I run, unaided, and it passes
`promtool test rules`.

## Learner

- Starting point: comfortable with SQL, used Prometheus a bit, never written PromQL,
  does not know promtool.
- Learns best by: typing, predicting output before running, debugging from errors.

## Practice surface

- Where the learner works: everything in containers, no host installs. Rule and test
  files live in this workspace; `promtool` runs via
  `docker run --rm --entrypoint promtool -v "$PWD":/w prom/prometheus:v3.16.0`.
- How success is checked: `promtool test rules` printing SUCCESS against synthetic
  series is the only accepted proof of a lesson. One live Prometheus + node_exporter
  stack (L0.4) shows real cardinality; queries there are checked in the Prometheus UI.

## Environment

- Pins: `prom/prometheus:v3.16.0` (verified: `promtool test rules` and
  `promtool check rules` work in the container). node-exporter tag pinned during L0.4
  setup and recorded in PROGRESS.md notes.
- Setup: Docker works and can pull images. Nothing installed on the host.

## Constraints

- Time per session: 30 minutes.
- Out of scope: Grafana, Alertmanager, remote storage, scrape config beyond basics,
  recording rules (cut at approval).

## Agreements

- Synthetic series for every lesson's verification, plus one small live stack so real
  cardinality is seen at least once.
- No Grafana.
- The curriculum was approved with the recording-rules lesson cut; 20 lessons remain.
