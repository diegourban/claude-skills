# Rubric

Levels are judgements against written anchors, not measurements. There is no population data behind
them, so the report never shows numbers, percentiles, norm groups or error bars.

## The seven skills

| Key | Skill | What it covers |
|---|---|---|
| depth | Depth on own work | Explains the why behind their own CV projects, three follow-ups deep |
| design | System design and architecture | Components, data flow, boundaries, scaling, consistency choices |
| coding | Coding | Reading and writing code, the snippet review, correctness of spoken solutions |
| debugging | Debugging and problem solving | Finding causes from symptoms, narrowing down, verifying a fix |
| concepts | CS and general concepts | Fundamentals of their stack: concurrency, databases, networking, JVM, testing |
| tradeoffs | Trade-off reasoning | Names options, costs and what was given up; picks and defends |
| communication | Communication | Structure, clarity, conciseness and precision in spoken English |

## Step ladder (question difficulty)

Each skill has a current step from 1 to 4. A question at step N is one an engineer at level N should
answer solidly.

| Step | Level | A question at this step asks for |
|---|---|---|
| 1 | Junior | What it is, how to use it, what they did |
| 2 | Intermediate | How it works, why it was chosen, one alternative |
| 3 | Senior | Failure modes, trade-offs under constraints, measuring the effect |
| 4 | Staff | Cross-system consequences, organisational trade-offs, what they'd change across teams |

Start every skill one step below the target level (Senior target: start at step 2).

## Rating an answer

Rate every answer by the level its content demonstrates against the level anchors below, regardless
of the step it was asked at. A step-1 question answered with Senior-quality evidence demonstrates
Senior.

- **Hinted:** the demonstrated level counts one lower (minimum Junior).
- **Skipped:** demonstrates nothing; record it as weak.
- **Wrong** (a clear factual error, not a gap): demonstrates Junior at most.

Then move that skill's step for the next question:

- Demonstrated level at or above the current step: step up one (max 4).
- Below the current step, or skipped: step down one (min 1).

Communication is not stepped; rate it from all answers at the end.

## Assigning the level

- A skill's level is the highest level demonstrated by any of its answers, after the hinted rule.
- Lower it by one if a later answer in the same skill demonstrated a lower level on the same topic.
- A skill probed but with only skipped answers is Junior. A skill never probed is `n/o`.
- Every level needs at least one short verbatim quote as evidence.

Strongest and weakest skill (for the report and spoken summary): highest and lowest level, excluding
n/o. On a tie, pick the skill with more answers at that level, then the earlier one in radar order.

## Level anchors (what the evidence should show)

| Skill | Junior | Intermediate | Senior | Staff |
|---|---|---|---|---|
| depth | Describes what was built | Explains why this design | Names a rejected alternative and a failure it caused or avoided | Ties the decision to business or team outcomes and would redo it differently with reasons |
| design | Lists components | Explains data flow and boundaries | Handles failure, scale and consistency choices explicitly | Designs across teams and systems, evolution and migration paths |
| coding | Follows the snippet | Spots the obvious bug | Spots concurrency, edge-case or contract bugs and fixes them cleanly | Reasons about the design behind the code and how to prevent the class of bug |
| debugging | Tries things | Narrows from symptoms | Forms and tests hypotheses with data (logs, metrics, traces) | Changes systems or processes so the bug class gets caught earlier |
| concepts | Defines terms | Explains how they work | Explains limits and failure modes | Connects concepts across layers and picks between them under real constraints |
| tradeoffs | Picks one option | Names two options | Weighs costs and names what was given up | Weighs long-term, organisational and cost trade-offs and defends a call |
| communication | Hard to follow | Clear but rambles | Structured, concise, answers the question asked | Adapts depth to the listener, summarises, checks understanding |

## English coaching (report section, affects only communication)

From the transcript, list:

- Filler words used three or more times, with counts ("basically" x6).
- Grammar slips a listener would notice, recurring ones first, each with the candidate's sentence and
  a corrected one that changes only the grammar, never the meaning or word choice.
- Words or phrases leaned on too often, with one alternative each.
- Two or three answers whose content was right but poorly delivered, rephrased as a strong spoken
  answer using only facts the candidate gave. For an answer whose content was wrong, add one line on
  what a strong answer would cover instead; never put words in the candidate's mouth.

Speech-to-text mangles words and drops pronunciation. Coach wording, never accent, and ignore
obvious transcription errors.

## Verdicts

Each panelist gives one of strong no, no, yes, strong yes against the target level, weighted by their
angle (see `personas.md`). Ignore key skills that are n/o; if all of a panelist's key skills are n/o,
they judge on the skills they did probe.

- **strong yes:** every key skill at or above target, and at least one above it.
- **yes:** every key skill at or above target.
- **no:** exactly one key skill below target.
- **strong no:** two or more key skills below target.

Verdicts use the assigned levels only; hints and skips already lowered those levels.

Key skills: Leslie (design, coding, concepts), Dennis (debugging, design, depth), Freda (tradeoffs,
depth, communication). Each verdict gets two lines in the persona's voice citing evidence.
