# Scenario 04: resume

Fresh session, existing workspace, `current: L0.1`, no lessons started. Learner says "back".

## LEARNER

back

## TUTOR

Where we left off: the contract and curriculum are approved (13 lessons; the recording-rules lesson was cut). No lesson has been taught yet: L0.1 "Harness first" is at step 1 of 6.

Before I teach anything, confirm the setup still works. `TOPIC.md` says everything runs in containers, nothing installed on the host. Run these two:

```bash
docker version --format '{{.Server.Version}}'
docker run --rm --entrypoint promtool prom/prometheus:v3.16.0 --version
```

Expected: a Docker server version, then `promtool, version 3.16.0`. The second command may take a minute the first time while the image pulls.

Paste both outputs, or the error if either fails.
