# learn-topic

A reusable teaching contract for OpenCode. It takes one scoped technical topic, designs an
atomic curriculum, and teaches it through a fixed six-step lesson loop with state on disk.

Two artifacts come out of one source:

- `dist/learn-topic/`: an installable OpenCode skill
- `dist/learn-topic-prompt.md`: a self-contained prompt for any chat tool

## Start here

| You want to | Read |
|---|---|
| Use it now | [Quick start](#quick-start) |
| Know how it behaves | [How it works](#how-it-works) |
| Change it | [Source layout](#source-layout), [Customising](#customising) |
| Know why it is built this way | [Design decisions](#design-decisions) |
| Know what was tested | [Testing](#testing) |

## Quick start

Requirements: OpenCode, `bash`, `python3`. Nothing is installed on the host.

```bash
cd /path/to/topic-tutor
./build.sh
python3 tests/check-artifact.py
ln -sfn "$PWD/dist/learn-topic" ~/.config/opencode/skills/learn-topic
```

Restart OpenCode so it discovers the skill. Then say:

> teach me PromQL

or any topic phrased as "I want to learn X". The skill asks three questions, asks where the
course files go, writes `TOPIC.md`, `CURRICULUM.md` and `PROGRESS.md`, and shows the lesson
list. It teaches nothing until you approve that list.

For a chat tool without skills, paste `dist/learn-topic-prompt.md` as the first message. If
that chat cannot write files, say so: the tutor keeps the state in the conversation and
prints `PROGRESS.md` for you to store at the end of each session.

Remove the skill with `rm ~/.config/opencode/skills/learn-topic`.

## What it is

- A tutor contract: role, lesson loop, message discipline, hint ladder, accuracy rules,
  pace control and state format.
- A curriculum designer: scope the topic, decompose it into atomic lessons, check coverage
  against the goal, get approval.
- A state machine: three files that let a fresh session continue exactly where the last one
  stopped.

## What it is not

- Not a content library. It designs the course from the model's knowledge of the topic.
- Not a spaced-repetition system. It tracks mastery per lesson but does not schedule
  reviews beyond a warm-up on `shaky` lessons.
- Not multi-learner and not multi-topic at once. One workspace is one course.
- Not a grader. Verification is a command or observation the learner runs, plus review of
  their attempt.

## How it works

### The three files

| File | Role | Written when |
|---|---|---|
| `TOPIC.md` | The contract: goal, proof, learner profile, practice surface, pins, out of scope. Wins over anything said later. | Cold start, and whenever the goal changes |
| `CURRICULUM.md` | Ordered atomic lessons, each with goal, concept and an observable "done when" | Cold start, approved before lesson 1 |
| `PROGRESS.md` | Pace, current lesson, lesson statuses, notes, exact next step | After every passed lesson and at session end |

If a lesson exposes a gap in the contract, the tutor stops, amends `TOPIC.md`, then the
curriculum, then continues. It never redefines the goal mid-lesson.

### Cold start

1. Three questions at most: goal and proof, starting point, practice surface.
2. Ask where the three files go.
3. State the assumptions for everything else: session length, pins, scope.
4. Write the three files.
5. Show the lesson list, one line per lesson.
6. Stop for approval. Teach nothing in this message.

After approval, lesson 1 starts. Later changes follow the same order: contract, curriculum,
lesson.

### The lesson loop

One step per message. Every step ends by waiting for the learner.

| Step | What happens | Stops after |
|---|---|---|
| GOAL | One or two sentences: what we learn, what the learner can do afterwards | Statement plus question or prompt to start |
| TEACH | One concept, one small example, one check question | The check question |
| TASK | Scoped exercise: goal, constraints, signature or skeleton if useful | The task, never the solution |
| REVIEW | What is good, what to improve and why, using the learner's own output or error | The learner has a fix to make |
| VERIFY | Exact command or action, and the expected result | The learner runs it |
| WRAP | Three-line recap, status line, next lesson | Session or lesson handoff |

A lesson is atomic: one concept, 15 to 30 minutes, about 20 lines of new code where code is
involved, and the practice workspace still works at the end. Oversized lessons are split
(`L1.5` becomes `L1.5a` and `L1.5b`) and the curriculum is updated first.

At the end of a phase, the tutor offers one mixed task covering that phase. It is not a
gate and it changes no status unless the learner fails it badly.

### Hard rules

These override everything else in the skill:

- One step per message. No previewing the next step.
- About 200 words and at most one code block of about 20 lines. The curriculum approval
  message is exempt.
- End every message with one question or one task, then stop.
- Never write the learner's solution, except on `show me`.
- Never mark a lesson passed without a VERIFY result.
- Verify uncertain facts. Never invent flags, APIs or version behaviour.
- Before sending: one step only, and did I end by waiting?

### Commands

| Command | Effect |
|---|---|
| `pace N` | Set the global pace (2, 3 or 4) |
| `slower` / `faster` | Step the pace by one |
| `pace N now` | Override the pace for this lesson only |
| `hint` | Move down one rung of the hint ladder |
| `show me` | Show the full solution with explanation |
| `repeat` | Re-teach the same concept with a different example |
| `test out` | One challenge covering the lesson; pass marks it `glossed` |
| `recap` | Summarise the lesson so far |
| `skip` | Move to the next lesson, recorded as `skipped` |
| `pause here` | End the session cleanly and update state |

### Pace

| Level | Behaviour |
|---|---|
| 2 careful | Two examples, a check question per sub-concept, smaller tasks, hints early, full recap |
| 3 standard | One example, one check question, normal task (default) |
| 4 brisk | Short explanation, check question only for tricky concepts, bigger tasks, no warm-up |

The tutor may suggest a change. It never changes pace without agreement.

### Statuses

`doing`, `done solid`, `done shaky`, `glossed`, `skipped`. Lessons not listed have not been
started. `shaky` is used honestly: it is the input to the warm-up at the next session.

## Source layout

```
README.md                              this guide
src/SKILL.md               147 lines   the tutor contract (canonical)
src/curriculum-design.md    61 lines   scoping, atomicity, ordering, coverage, approval
src/templates/                         TOPIC, CURRICULUM, PROGRESS skeletons
build.sh                               generates dist/ in one direction
dist/learn-topic/                      installable skill (SKILL.md + references/ + templates/)
dist/learn-topic-prompt.md 282 lines   self-contained paste-anywhere prompt
tests/check-artifact.py                static checks and drift check
tests/check-transcript.py              per-message budget checks
tests/scenarios/README.md              scripted learner scenarios and pass criteria
tests/transcripts/                     recorded runs used as evidence
tests/RESULTS.md                       current test matrix and defect log
```

`dist/` is generated. Never edit it. `src/` is the only place to make changes.

The skill points at `references/curriculum-design.md` and `templates/PROGRESS.md`. The
prompt inlines both, because a pasted file has no sibling directories. `build.sh` performs
that substitution and the static checker fails if a placeholder or a build marker leaks
into an output.

## Building

```bash
./build.sh                      # rebuild dist/ from src/
python3 tests/check-artifact.py # static checks plus deterministic-rebuild check
```

The static checker verifies:

- frontmatter name and trigger phrases
- required sections present in the skill and the prompt
- no leftover `@@...@@` placeholders or `<!-- ... -->` markers
- no project-specific vocabulary (`rustic`, `docker compose`, `uv sync`, `VAULT_`, `GitLab`)
- the skill ships its references and templates
- line budgets
- rebuild produces byte-identical output

After editing `src/`, rerun both. Editing `dist/` will be overwritten and the checker will
not catch it before the rebuild.

## Testing

### What is proven

| Check | Command | Proves |
|---|---|---|
| Static | `python3 tests/check-artifact.py` | Frontmatter, sections, cleanliness, determinism |
| Transcript budgets | `python3 tests/check-transcript.py tests/transcripts/<file>.md` | Word count, code-block count and size, one step per message |
| Cold start | `tests/transcripts/01-cold-start.md` | 3 questions, files written, list shown, revision applied, stop before teaching |
| Resume | `tests/transcripts/04-resume.md` | Two-line recap, setup check, continue at `current`, no restart |
| Golden replay | see [Golden replay](#golden-replay) | Curriculum quality against a hand-written reference |

Current matrix: cold start, resume and golden replay pass. Loop discipline (02), hint
ladder (03), non-code topic (05) and pressure (06) are pending because they need a
mid-lesson session. Details in `tests/RESULTS.md`.

### Running a behavioural scenario

The tutor and learner must be separate sessions. A single model asked to play both sides
will always agree with itself.

1. Tutor session: give it `dist/learn-topic-prompt.md`, the scenario from
   `tests/scenarios/README.md`, and "produce only your next message to the learner".
2. Learner session: give it only the learner script and "never help, never break
   character".
3. Relay messages between them, or script it.
4. Record the exchange as `## TUTOR` and `## LEARNER` sections.
5. Run `check-transcript.py` and score the scenario's pass criteria by reading it.

### Transcript format

```markdown
## TUTOR
message text

## LEARNER
reply text
```

The checker treats messages with three or more lesson IDs as the curriculum approval
message and allows it 400 words. It reports, but does not fail, when a message ends with
something other than a question, because distinguishing a task from a statement needs a
reader.

### Golden replay

Give the skill only a specification and a learner profile, then compare the generated
curriculum with a hand-written one for the same specification, written independently.

Run 1 produced 26 lessons with good atomicity but incomplete coverage: no git, no GitLab
push or merge request, no runner registration, no real end-to-end run. Run 2, after the
Coverage rule, produced 29 and added all four.

### Limits

Both sessions usually run on the same model, so they share blind spots. Mechanical checks
catch budgets and discipline. Curriculum quality needs a human reader and a real session.
Treat the scripted scenarios as regression tests, not as proof that learning happens.

## Design decisions

| Decision | Reason | Rejected alternative |
|---|---|---|
| Skill plus generated prompt | The skill triggers on its own and ships templates; the prompt travels to any chat and holds the role harder | Skill only (not portable), prompt only (manual, no templates) |
| One canonical `src/` | Two hand-written artifacts drift apart | Editing `dist/` directly |
| Three pace levels | The two extra levels duplicated the message budget and were never used | The original five levels |
| `glance` and `dig in` removed | They are one-lesson pace overrides; two commands with no new capability | Keeping eleven commands |
| Coverage check in curriculum design | The golden replay showed well-formed lessons with missing requirements | Relying on lesson quality alone |
| Always ask where files go | Writing course files into an unrelated repository is a real failure mode | Guessing `~/learning/` or the current directory |
| Light scoping path | A reusable skill needs a low-friction entry; full interviews are optional | Interviewing before every course |
| Phase checkpoints | Mixed retrieval once per phase is cheap and catches decay | Per-lesson assessment only |
| `TOPIC` / `CURRICULUM` / `PROGRESS` | `TOPIC` is clearer than `REQUIREMENTS` for a non-project subject | `REQUIREMENTS.md` (original), `BRIEF.md` |
| Version facts recorded as unknown | A passing mention of a version is not a pin; guessing produced a wrong pin in run 1 | Inferring from any version string in the spec |
| No file access fallback | The standalone prompt must work in plain chats | Requiring file tools |

## Customising

- **Tone and role**: edit `# Role` in `src/SKILL.md`.
- **Budgets**: the 200-word and 20-line limits appear in `# Hard rules` and in
  `tests/check-transcript.py` (`MAX_WORDS`, `MAX_BLOCK_LINES`). Change both.
- **Pace levels**: edit `# Pace` and the table in `# Hard rules` if the wording changes.
- **Commands**: add or remove lines in `# Pace`. Keep the semantics in sync with
  `PROGRESS.md` statuses.
- **File names**: change them in `src/SKILL.md`, `src/templates/`, and the scenario
  expectations. The build does not enforce names.
- **Templates**: `src/templates/*.md` flow into both outputs. Keep them free of fenced code
  blocks, because the prompt wraps each one in a Markdown fence.
- **Curriculum rules**: edit `src/curriculum-design.md`. This is where topic width, lesson
  count and coverage live.
- **Description and triggers**: the frontmatter of `src/SKILL.md`. Test a phrase change by
  restarting OpenCode and asking with that phrase.

After any change: `./build.sh && python3 tests/check-artifact.py`.

## Troubleshooting

**The skill is not listed.** Restart OpenCode. Confirm the symlink points at a directory
that contains `SKILL.md` with valid frontmatter.

**It does not trigger.** Use an explicit phrase from the description, or invoke the skill
by name. Vague requests such as "help me with PromQL" may not match.

**It writes course files in the wrong repository.** The contract says to ask first. If that
still happens, tighten `# Workspace` and add a scenario that checks the question.

**It dumps code or runs ahead.** The hard rules sit at the end on purpose, because middle
instructions decay. Check that the installed skill is the current build, then run the
transcript checker on a real session to find which rule fails.

**The curriculum is too broad.** More than 30 lessons means the topic is too wide. Narrow
the goal in `TOPIC.md`, not the lesson count.

**The curriculum is too shallow.** The coverage rule maps operations and failure modes to
lessons. Add missing items to the goal or the practice surface so the design has to cover
them.

**The checker reports REVIEW on a message that ends with a task.** That is expected. The
heuristic only recognises a trailing question mark. Read the line; do not edit the
transcript to silence it.

**The build fails after a template edit.** A fenced code block in a template breaks the
prompt wrapper. Remove the fence or move the example into `src/SKILL.md`.

## Known limitations

- Curriculum quality is bounded by the model's knowledge of the topic. For fast-moving
  tools, the accuracy rules force verification but cannot supply it.
- The scenario suite is not independent of the model under test.
- No cross-topic review scheduling, no recall prompts after a course ends.
- The standalone prompt needs a chat that can either write files or keep a printed state
  block.
- English only.

## Status

Experimental. No license declared. Version controlled; add a license before any public
release.
