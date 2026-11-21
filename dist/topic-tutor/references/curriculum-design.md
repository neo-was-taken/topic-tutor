# Curriculum design

Read `TOPIC.md` first. Design from its goal, starting point, practice surface and pins.
The curriculum is a dependency order, not a table of contents.

## Every lesson has three fields

- **Goal**: what the learner can do afterwards.
- **Concept**: the one idea it teaches.
- **Done when**: an observable check the learner can run or see. A command prints
  something, a test passes, a query returns the expected shape, an artifact exists, a
  prediction is confirmed.

No lesson without all three. A lesson without a "done when" is a reading recommendation
and does not belong here.

## Atomicity test

One concept, one sitting of 15 to 30 minutes, a small amount of new material, the practice
workspace still works afterwards. If you cannot name the lesson in one short phrase, it is
two lessons. Split rather than compress: `L1.5` becomes `L1.5a` and `L1.5b`.

## Ordering

- First lesson produces something observable, so there is a reason to continue.
- Order by dependency: nothing is used before it is taught.
- Anything taught in one lesson is used within the next two, or it is cut.
- Group into phases of four to eight lessons, each phase ending with something usable.
- One lesson near the end tests the goal itself, not a subtopic.
- Mark genuinely optional lessons `(opt)`.
- Ten to thirty lessons for a scoped topic. More means the topic is too broad: scope it
  down or split it into two courses.

## Coverage

Before showing the list, map what the goal and the specification require onto lessons:

- Every operation, mode, command, flag family or deliverable named in the spec gets a
  lesson, even when several share one implementation step.
- Every tool the practice surface depends on that the learner has not used yet gets a
  lesson before the first lesson that needs it. This includes version control, shells,
  registries and cluster access.
- Every failure mode the spec calls out, such as cleanup, exit codes, secret handling or
  retries, gets a lesson where it is introduced, not a passing mention.
- Anything still unmapped is either a new lesson or an explicit out-of-scope line in
  `TOPIC.md`.

## Failure signs

- A lesson that is only reading.
- A lesson with no observable "done when".
- Two concepts in one lesson.
- A required operation that appears only inside another lesson's example.
- A phase that does not end with something that works.
- Lessons that exist because a book has them, not because the goal needs them.

## Approval

Show one line per lesson, grouped by phase. Ask what to cut or reorder. Freeze the list
after approval. Later changes go through `TOPIC.md` first, then the curriculum, then the
lesson.
