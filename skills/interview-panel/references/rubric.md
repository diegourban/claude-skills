# Rubric

Levels are judgements against written anchors, not measurements. There is no population data behind
them, so the report never shows numbers, percentiles, norm groups or error bars.

Rating each answer and moving steps during the round is the model's job. Everything after that
(assigning levels, edge, depth and breadth from topic areas, bars, feedback picks, strongest and
weakest) is implemented in `scripts/report.py`; this file stays the specification, and the script's
selftest pins the cases.

## The seven axes (the radar, both modes)

The radar has the same seven axes in CV and topics mode, so sessions stay comparable whatever was
discussed. What was discussed (CV projects, topic areas) lives in the evidence tables.

| Key | Axis | What it covers | CV mode source | Topics mode source |
|---|---|---|---|---|
| depth | Depth | How far down they can go on one subject | CV deep-dives (the why behind their own work) | Derived: the highest topic-area level |
| breadth | Breadth | How many subjects they are solid on | Concept questions across their stack | Derived: the two-thirds rule over topic areas |
| design | Design | Components, data flow, boundaries, failure, scale, consistency | Design questions | The walkthrough and any design question |
| problem | Problem solving | Finding causes, reviewing code, working a problem through | The snippet review and the spoken problem | Diagnosis questions (tagged `also: problem`) |
| tradeoffs | Trade-offs | Names options, costs and what was given up; picks and defends | Trade-off questions | Trade-off follow-ups (tagged `also: tradeoffs`) |
| edge | Reasoning at the edge | What they do past the limit of what they know | Any answer that hit "I don't know" | Every area floor |
| communication | Communication | Structure, clarity, conciseness, precision in spoken English | All answers | All answers |

An answer rates its own key and, with `also`, one or more axes as well: a topics-mode diagnosis
question rates its area and problem solving. Every round probes all seven axes; an axis never probed
is `n/o`, skipped in the radar polygon and labelled "not probed".

## Step ladder (question difficulty)

Each axis (and each topic area) has a current step from 1 to 4. A question at step N is one an
engineer at level N should answer solidly.

| Step | Level | A question at this step asks for |
|---|---|---|
| 1 | Junior | What it is, how to use it, what they did |
| 2 | Intermediate | How it works, why it was chosen, one alternative |
| 3 | Senior | Failure modes, trade-offs under constraints, measuring the effect |
| 4 | Staff | Cross-system consequences, organisational trade-offs, what they'd change across teams |

Start every axis and area one step below the target level (Senior target: step 2). Exception: in
topics mode with `short`, areas start at the target step, so two questions can reach a floor.

## Rating an answer

Rate every answer by the level its content demonstrates against the level anchors below, regardless
of the step it was asked at. A step-1 question answered with Senior-quality evidence demonstrates
Senior.

- **Hinted:** the demonstrated level counts one lower (minimum Junior). Use the hinted level for both
  rating and stepping.
- **Skipped:** demonstrates nothing; record it as weak.
- **Wrong** (a clear factual error, not a gap): demonstrates Junior at most.

Then move that axis's (or area's) step for the next question:

- Demonstrated level at or above the current step: step up one (max 4).
- Below the current step, or skipped: step down one (min 1).

Communication and edge are not stepped. Rate communication from all answers at the end. Filler words
go in the coaching section; they lower communication only when they make answers hard to follow.

## Assigning the level

- An axis's or area's level is the highest level demonstrated by any of its answers, after the hinted
  rule.
- Lower it by one if a later answer on the same axis or area demonstrated a lower level on the same
  topic.
- Probed but with only skipped answers is Junior. Never probed is `n/o`.
- Every level needs at least one short verbatim quote as evidence.

Strongest and weakest (report and spoken summary): the highest and lowest axis, excluding n/o. On a
tie, pick the one with more answers at that level, then the earlier one in radar order. Topics mode
also names the strongest and weakest area by the same rule, in setup order.

## Level anchors (what the evidence should show)

| Axis | Junior | Intermediate | Senior | Staff |
|---|---|---|---|---|
| depth | Describes what was built | Explains why this design | Names a rejected alternative and a failure it caused or avoided | Ties the decision to business or team outcomes and would redo it differently with reasons |
| breadth | Defines terms | Explains how they work | Explains limits and failure modes | Connects concepts across layers and picks between them under real constraints |
| design | Lists components | Explains data flow and boundaries | Handles failure, scale and consistency choices explicitly | Designs across teams and systems, evolution and migration paths |
| problem | Tries things, or follows the snippet | Narrows from symptoms, or spots the obvious bug | Forms and tests hypotheses with data; spots concurrency, edge-case or contract bugs and fixes them | Changes systems or processes so the bug class gets caught earlier |
| tradeoffs | Picks one option | Names two options | Weighs costs and names what was given up | Weighs long-term, organisational and cost trade-offs and defends a call |
| edge | Bluffs or states a guess as fact, or stops dead | Says "I don't know" cleanly | Says so, then reasons from adjacent principles to a hypothesis labelled as a hypothesis | Does that, says how they'd verify it and what being wrong would cost |
| communication | Hard to follow | Clear but rambles | Structured, concise, answers the question asked | Adapts depth to the listener, summarises, checks understanding |

## Reasoning at the edge

Rated at every floor (topics mode) and at every "I don't know" (CV mode). A confident wrong answer
rates that point Junior, on top of the Wrong rule. A hinted floor is rated on how they reasoned after
the nudge, at most Intermediate. A skipped floor is Junior. Edge's level is the median of those points (a
bluff counts as its Junior rating; on an even count, the lower middle), with no further adjustment, so
one bluff costs something without wiping out good moments elsewhere. With none, edge is `n/o`. Quote the
answer as evidence.

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

## Panel feedback

No panelist gives a verdict, a hire call or any overall pass/fail. Each gives exactly two points in
the written report, in their persona's voice (see `personas.md`):

- **What landed:** one specific strength, with a verbatim quote of the answer that showed it.
- **Work on:** one specific gap, with a verbatim quote and a concrete next step ("next time, name the
  isolation level and what it costs"). When nothing in the lens is below target, it says what would
  reach the next level.

Each panelist comments only on their lens, in both modes: Leslie (depth, design, edge), Dennis
(problem solving, breadth, design), Freda (trade-offs, communication, breadth). In `two-panel` mode
Dennis's lens joins Leslie's. Ignore n/o axes; if the whole lens is n/o, the panelist comments on any
probed axis. The text may name a topic area or CV project ("your networking floor").

Which axis each point is about is a fixed rule, picked by `scripts/report.py`:

- What landed: the highest-level axis in the lens.
- Work on: the axis furthest below target; when none is below, the lowest-level one. Topics mode:
  when the picked axis is not below target, work on moves to the panelist's weakest owned area that
  sits below its bar (largest gap, then lower level, then setup order), if there is one.
- Ties go by radar order. An axis an earlier panelist already took for the same point is skipped when
  the lens has an alternative, and work on never repeats the panelist's own what landed when it can
  avoid it.

Feedback stays out of the spoken summary; it appears only in the report.

## Topics mode

The same ladder, rating and assigning rules apply to each topic area.

### Topic areas (the evidence table)

The areas come from the session, 3 to 8 of them, in setup order with core areas first:

- **From a brief:** the areas the brief names, as named.
- **A single technology** ("Docker", "Kafka"): split it into 4 to 6 sub-areas that cover how it is
  built, run, connected, secured and operated (4 in `short`). The canonical Docker list: Images and
  builds, Runtime and isolation, Networking, Storage and volumes, Security, Orchestration and
  operations (short: drop Storage and volumes and Security into a single Security and storage area,
  or keep the four closest to the CV). Sub-area questions follow the runtime the CV actually uses
  (Kubernetes networking rather than Swarm overlay for an EKS shop), or contrast the two.
- **Nothing named** (the user just said `topics`): frontend, backend, databases, security,
  performance, infrastructure, methodology.

The setup line names them; the user may change them before the round. An area that does not apply
(frontend for a backend CV with no frontend in the job description) is dropped, not listed. An area
never probed is `n/o`, shown as "not probed", and left out of depth, breadth and the count.

- **Core or peripheral:** at most three areas are core: the ones closest to the CV's main stack and
  anything the job description stresses; the rest are peripheral.
- **Bar:** a core area's bar is the target level; a peripheral area's is one level below. The bar is
  shown in the topics table; the radar's target ring is always the target level.
- **Owner:** each area goes to the panelist whose angle fits (`personas.md`). It decides who asks,
  not whose feedback lens it joins. Order areas within the core and peripheral groups so no panelist
  opens three areas in a row.

Topic anchors (one table for every area; judge against the area's own fundamentals):

| Junior | Intermediate | Senior | Staff |
|---|---|---|---|
| Defines terms, says what they used | Explains how it works and why it was chosen over one alternative | Explains limits, failure modes and how to measure them | Connects the area to other layers and picks between approaches under real constraints |

### Drilling to the floor

Drill each area one step deeper per question until a floor or Staff. A **floor** is an answer that
was a don't-know, wrong, skipped or hinted; record it with `floor` and `edge` (the script rejects a
flagged area answer without a floor). Answers after an area's floor do not change its level. Name the
floor as a concept ("MVCC visibility rules", "overlay
network internals"). The floor column says "none" when the area reached Staff and "not reached" when
the question budget ran out first. An area's level is the highest level demonstrated before the floor,
after the hinted rule; if the first answer is the floor, rate the area by that answer (Wrong caps it at
Junior, Skipped makes it Junior).

### Depth and breadth from the areas

- **Depth:** the highest level among the rated areas.
- **Breadth:** the highest level that at least two-thirds of the rated areas reach. Areas at S, S, I
  and J give Intermediate: three of four are at Intermediate or above.
- **Breadth count:** "<k> of <n> probed areas at Intermediate or above, <m> at the target level",
  shown under the radar, so the count and the breadth level read on the same scale. A count of the
  candidate's own areas, compared with no population.

Strongest-axis ties credit derived depth and breadth with the answers of the areas behind them.

## Older session records

Records v1 to v3 use other keys. Map them onto the axes: depth → depth, concepts → breadth, the higher
of coding and debugging → problem, design, tradeoffs, edge and communication keep their names. v2 and
v3 topics records named fixed areas; read them as topic areas. Ignore any `verdicts:` line.
