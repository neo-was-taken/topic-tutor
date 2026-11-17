# Curriculum: rustic-backup-runner

One concept per lesson, one sitting, a small amount of new material, the workspace works
after every lesson. `(opt)` may be skipped. The contract lives in TOPIC.md; contract changes
go there first, then here.

## Phase 0 - The practice loop

**L0.1 A container that runs Python**
Goal: start a service with compose and read its exit code.
Concept: image vs container vs compose service, `run --rm`, exit codes pass through to the
shell.
Done when: `docker compose run --rm runner` prints the Python version from inside the
container, and a script that exits 2 makes `echo $?` print 2 on the host.

**L0.2 Package and console script**
Goal: install the project and call it by name.
Concept: src layout, `pyproject.toml` as the one place for dependencies and pins, editable
install, console-script entry point.
Done when: `docker compose run --rm runner rustic-runner --help` prints usage from the
installed package, and the image digest is recorded in TOPIC.md.

**L0.3 Tests in the container**
Goal: run pytest against the installed package.
Concept: test discovery, one assert, a test as a repeatable check rather than a proof.
Done when: `docker compose run --rm runner pytest` collects at least one test and exits 0,
and a deliberately wrong assert makes it exit non-zero.

**L0.4 The check gate**
Goal: one command that decides whether the workspace is healthy.
Concept: lint and format as mechanical consistency so review is about design; a gate run
before every commit.
Done when: `make check` runs ruff and pytest and exits 0, and an unused variable makes it
exit non-zero.

**L0.5 Git baseline**
Goal: keep the work in git from the first real commit.
Concept: working tree vs index vs commit, `.gitignore` for `__pycache__` and `.venv`,
commit as an immutable checkpoint.
Done when: `git log --oneline` shows one commit, `git status` is clean, and a new file
appears as untracked before `git add`.

## Phase 1 - Config: parse, validate, refuse

**L1.1 YAML into data**
Goal: load the example config and print what was found.
Concept: parsing and validating are two jobs; `yaml.safe_load` and why `load` is not an
option.
Done when: the example config loads and prints both entry names, and a truncated file gives
a message with the line number instead of a traceback.

**L1.2 One entry, typed**
Goal: reject a bad entry before anything runs.
Concept: declarative validation with pydantic v2, `extra="forbid"`, types as a contract.
Done when: an entry with an unknown key and an entry missing `repository` are both rejected,
and the message names the failing field.

**L1.3 Validation errors a human can act on**
Goal: turn a validation error into one actionable line.
Concept: nested error locations become `repositories[1].repository: Field required`; message
text lives in one formatter module from the start.
Done when: a config with a missing key prints exactly that shape, and a grep shows the string
is built only in the formatter module.

**L1.4 Rules that span entries**
Goal: enforce uniqueness, name shape and source existence.
Concept: per-field rules versus whole-document invariants; stat `source` only, never
`repository`.
Done when: duplicate `name`, a bad `name` regex, duplicate `source`, duplicate `repository`
and a missing source directory are each rejected with a message naming the entry.

**L1.5 CLI, config resolution, exit codes**
Goal: run the tool with a chosen config and a documented exit code.
Concept: precedence flag over env over default; exit codes as an API for the scheduler.
Done when: no arguments exits 2 with usage, a missing config exits 2, and a valid config
prints the plan for the chosen subcommand and exits 0.

**L1.6 Narrowing a run**
Goal: process only the entries you name.
Concept: selection is validated before any work starts; an unknown target is an error, not a
silent empty run.
Done when: `--target photos` reports one entry, two targets report two, and an unknown name
exits 2 naming the bad value.

## Phase 2 - Running rustic

**L2.1 The subprocess boundary**
Goal: run an external program and trust only its exit code.
Concept: argv list instead of a shell string, captured output, `returncode` as the contract.
Done when: a test runs a fake `rustic` script, asserts the captured stdout and returncode 0,
and a second test sees returncode 1 and treats it as failure.

**L2.2 Command builders**
Goal: produce the exact rustic argv for backup, prune and check.
Concept: pure functions returning `list[str]`, so flags are testable without a repository;
one builder per subcommand from the table in REQUIREMENTS.md.
Done when: tests assert the full argv including `-r`, `--host`, `--no-cache`, one
`--glob '!...'` per exclude, one `--keep-*` per retention key, and `--prune` on forget.

**L2.3 The sequential loop**
Goal: process every selected entry, then summarise.
Concept: one failing entry must not abort the run; aggregate results and map them to exit
codes 0 and 1.
Done when: with a fake rustic, two entries where one fails print two entry lines plus
`backup: 1 ok, 1 failed` and exit 1, and two successes exit 0.

**L2.4 Capture, failure detail, verbose**
Goal: keep output readable and show rustic's errors when they matter.
Concept: captured pipes versus inherited descriptors, the deadlock from draining one pipe at
a time, the last 20 stderr lines indented under the entry, `--verbose` streaming instead.
Done when: a failing entry prints the tail of rustic's stderr indented, `--verbose` shows
output as it happens, and a large output does not hang.

## Phase 3 - Real rustic and secrets

**L3.1 Pin rustic and verify its interface**
Goal: a reproducible rustic in the image whose flags you checked yourself.
Concept: pinned version with checksum, and `--help` as the source of truth over any doc.
Done when: `rustic --version` in the container prints the pinned version, and `rustic backup
--help` confirms or corrects every flag the builders emit, including the long form of `-r`.

**L3.2 The passphrase file**
Goal: hand rustic a passphrase without it appearing anywhere observable.
Concept: `0600` file on `/dev/shm`, cleanup on every exit path, argv and env as world-readable
surfaces.
Done when: a real backup succeeds against a repository initialised out of band, no `/dev/shm`
file remains after success or a forced failure, and the passphrase is absent from
`/proc/self/cmdline` output and from the run log.

**L3.3 Vault KV v2 with hvac**
Goal: fetch a secret from env-only configuration.
Concept: KV v2 mount plus logical path, `response["data"]["data"]`, `VAULT_KV_MOUNT` default.
Done when: a unit test with a stubbed client passes, a real read against a dev Vault returns
the stored passphrase, and a bad path fails with a message naming that path.

**L3.4 One passphrase per entry, never cached**
Goal: fetch each entry's secret at run time, inside the loop.
Concept: per-repository passphrases and why caching across entries or runs is a security
regression.
Done when: two entries with different Vault paths each succeed, and a counting stub proves
one fetch per entry per run and no reuse on the next run.

**L3.5 When Vault fails**
Goal: keep going and report honestly.
Concept: a secret failure is an entry failure, not a crash; a Vault outage yields N lines,
not one exception.
Done when: an unreachable Vault with two entries produces two failure lines naming their
paths and exit 1, and a search of the whole output finds no passphrase.

**L3.6 End to end against a real repository**
Goal: backup, prune and check a real repository and read what rustic reports.
Concept: snapshots versus packs, retention policy application, prune's two phases and the
`--keep-delete` lag, `check` exiting 1 on failure.
Done when: `backup` then `rustic snapshots` lists the snapshot, `prune` reports the policy
applied, `check` exits 0, and a corrupted repository makes `check` exit 1 without the tool
misreporting it as success.

## Phase 4 - Delivery

**L4.1 A hardened image**
Goal: an image that runs as a fixed non-root UID with nothing extra in it.
Concept: multi-stage build, `USER`, and why the runtime layer carries no compiler or package
index.
Done when: `docker compose run --rm runner id` shows the fixed UID, `rustic --version` and
`rustic-runner --help` work in that image, and `make check` still passes.

**L4.2 GitLab project and push**
Goal: get the code into GitLab and read the project pages.
Concept: project versus repository, remote, protected branch, where pipelines will appear.
Done when: `git push` succeeds, the commit is visible in the GitLab web UI, and the project's
CI/CD settings show no variables yet.

**L4.3 A runner and the gate in CI**
Goal: let GitLab, not you, check every push.
Concept: runner registration and executor choice, jobs, images, cache, artifacts, and a
pipeline that runs the same numbers as `make check`.
Done when: a push turns the lint and test jobs green, and a commit with a deliberate lint
error turns the pipeline red.

**L4.4 Build and push by SHA**
Goal: a registry tag that points at exactly one commit.
Concept: registry login variables, `docker build` through the host socket, an immutable SHA
tag plus `latest`, and why deployments never pin `latest`.
Done when: the pipeline pushes `$CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA` and `latest`, the tag
is visible in the registry UI, and that image pulls and runs outside CI.

**L4.5 The CronJob**
Goal: run the tool on a schedule in the cluster.
Concept: CronJob to Job to Pod, ConfigMap for the config file, Secret for `VAULT_TOKEN`,
volumes for sources and repositories, `activeDeadlineSeconds`, `restartPolicy: Never`, and the
fixed-UID ownership rule.
Done when: `kubectl create job --from=cronjob/rustic-backup <name>` completes, its log shows
the entry lines and the summary, and the pod exit code matches the contract.

**L4.6 Deploy with proof**
Goal: change the running schedule's image and show that the new one works.
Concept: a CronJob has no rollout, so patch the image and then prove it with a Job; `when:
manual` with a tracked GitLab environment.
Done when: the manual job patches `cronjob/rustic-backup` to the SHA image, creates a Job from
it, waits for completion, and `kubectl get cronjob` shows that SHA.

## Phase 5 - Own it

**L5.1 An unaided change: `--log-format json`**
Goal: add a feature end to end without guidance.
Concept: rendering is separate from logic, so a new format is a formatter change plus a flag,
not a rewrite.
Done when: `--log-format json` emits one JSON object per line, tests and pipeline are green,
and the cluster runs the new image with JSON lines in the Job log.

**L5.2 Handover notes**
Goal: leave a README that makes the next operator succeed without you.
Concept: the failure modes that live in deployment, not in code.
Done when: a from-scratch redeploy works using only the README, and you can explain from a
real run why freed space appears only on a later prune, why `--host` is pinned, and why
`--no-cache` is set.
