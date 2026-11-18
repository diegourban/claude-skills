# Rubric

Levels are judgements against written anchors, not measurements. There is no population data behind
them, so the report never shows numbers, percentiles, norm groups or error bars.

Rating each answer and moving steps during the round is the model's job. Everything after that
(assigning levels, edge, bars, breadth, verdicts, strongest and weakest) is implemented in
`scripts/report.py`; this file stays the specification, and the script's selftest pins the cases.

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

- **Hinted:** the demonstrated level counts one lower (minimum Junior). Use the hinted level for both
  rating and stepping.
- **Skipped:** demonstrates nothing; record it as weak.
- **Wrong** (a clear factual error, not a gap): demonstrates Junior at most.

Then move that skill's step for the next question:

- Demonstrated level at or above the current step: step up one (max 4).
- Below the current step, or skipped: step down one (min 1).

Communication is not stepped; rate it from all answers at the end. Filler words go in the coaching
section; they lower communication only when they make answers hard to follow.

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

## Topics mode

Everything above applies to CV mode. In `topics` mode the same step ladder, rating rules, hinted,
skipped and wrong rules apply, but the things being rated change.

### Topic areas (the radar)

Seven fixed axes, in radar order: frontend, backend, databases, security, performance, infrastructure,
methodology. Phase 0 maps every area the brief names onto the nearest axis ("cloud" → infrastructure,
"testing" or "agile" → methodology, "APIs" → backend) and states the mapping in its setup line. An area
the brief leaves out is still probed only if the budget allows; otherwise it is `n/o` and is left out
of the breadth count's n.

- **Frontend applicability:** if the CV shows no frontend work and the job description doesn't ask for
  it, frontend is `n/a`. It is never probed and never counts against the candidate.
- **Core or peripheral:** Phase 0 marks at most three applicable areas core: the areas of the CV's
  primary language and primary datastore, and anything the job description stresses; the rest are
  peripheral. For a backend engineer, backend, databases and performance are usually core.
- **Bar:** a core area meets the bar at the target level; a peripheral area meets it one level below.

Topic anchors (one table for every area; judge against the area's own fundamentals):

| Junior | Intermediate | Senior | Staff |
|---|---|---|---|
| Defines terms, says what they used | Explains how it works and why it was chosen over one alternative | Explains limits, failure modes and how to measure them | Connects the area to other layers and picks between approaches under real constraints |

### Drilling to the floor

Drill each area one step deeper per question until a floor or Staff. A **floor** is an answer that
was a don't-know, wrong, skipped or hinted; name it as a concept ("MVCC visibility rules", "TLS
session resumption"). The floor column says "none" when the area reached Staff and "not reached" when
the question budget ran out first. An area's level is the highest level demonstrated before the floor,
after the hinted rule; if the first answer is the floor, rate the area by that answer (Wrong caps it at
Junior, Skipped makes it Junior).

### Thinking skills (the table under the radar)

Four rows: design (from the end-to-end walkthrough and any design question), tradeoffs, edge
(reasoning at the edge) and communication. They use the CV-mode anchors, except edge:

| Skill | Junior | Intermediate | Senior | Staff |
|---|---|---|---|---|
| edge | Bluffs or states a guess as fact, or stops dead | Says "I don't know" cleanly | Says so, then reasons from adjacent principles to a hypothesis labelled as a hypothesis | Does that, says how they'd verify it and what being wrong would cost |

Edge is rated at every floor and is not stepped. A confident wrong answer rates that floor Junior, on
top of the Wrong rule for the topic. Edge's level is the level most floors showed (on a tie, the lower
one), with no further adjustment. With no floor reached, edge is `n/o`.
Quote the floor answer as evidence.

### Breadth

Breadth is a count, not a score: "Breadth: <k> of <n> applicable areas at Intermediate or above",
where n excludes `n/a` areas. It is allowed because it counts the candidate's own areas and compares
them with no population.

### Verdicts in topics mode

Same four verdicts and the same counting rules. "At or above target" means at or above each area's
bar (core or peripheral); thinking skills use the target level as their bar. "Above it" in strong yes
always means above the target level, never above a lowered peripheral bar. Key skills: Leslie
(backend, databases, edge), Dennis (infrastructure, security, design), Freda (methodology, tradeoffs,
communication). Performance and frontend count for every panelist who asked a question in them; `n/a`
and `n/o` areas are ignored like n/o skills.

Strongest and weakest in topics mode are areas only (not thinking skills), with the CV-mode tie-break.
In `two-panel` mode infrastructure and security join Leslie's key skills.
