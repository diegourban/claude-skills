# Rubric

Levels are judgements against written anchors, not measurements: Junior, Intermediate, Senior,
Staff. There is no population data behind them, so the report never shows a number, a percentile or
a hire verdict. Rating each answer is the model's job; assigning levels, feedback picks, the radar
and the record are implemented in `scripts/report.py`, and its selftest pins the cases.

## The six axes (radar order)

| Key | Axis | Rated from |
|---|---|---|
| clarifying | Clarifying | Questions before the approach: inputs, edge cases, constraints |
| approach | Approach | Choice of data structure and algorithm, compared with the brute force |
| complexity | Complexity | Time and space, stated and justified |
| correctness | Correctness | The code on screen, and the trace through the hidden test |
| edges | Edge cases | Edge cases found unprompted versus only when pointed at |
| communication | Communication | Thinking aloud: structure, signposting, precision in spoken English |

## Level anchors

| Axis | Junior | Intermediate | Senior | Staff |
|---|---|---|---|---|
| clarifying | Starts solving with no questions | Asks about the input format | Asks about edge cases and constraints (empty, duplicates, size) before choosing an approach | Also asks about usage or scale that would change the design |
| approach | Brute force only, no reasoning about structures | Names a workable approach with a fitting structure | Reaches the expected approach, compares it with the brute force, justifies the structure | Weighs alternatives under other constraints (streaming, memory, concurrency) unprompted; an answer to the prompted follow-up caps at Senior |
| complexity | Cannot state it, or states it wrong | States time correctly | States time and space and ties both to the structures used | Covers amortised or worst-case nuances and what dominates in practice |
| correctness | The code does not solve the problem | The main path works, edge cases break | Correct including edge cases, or catches its own bugs during the trace | Invariants are explicit and the code reads as obviously correct |
| edges | Misses them even when pointed at | Handles them once pointed at | Names them unprompted | Designs them away (sentinels, half-open ranges) and says how to test them |
| communication | Silent or hard to follow | Narrates but rambles | Structured: says what they will do, does it, summarises | Checks understanding, adapts, invites correction |

## Rating an answer

Rate every answer by the level its content demonstrates against the anchors, whatever the phase.

- **Hinted:** an answer given after a hint counts one level lower (minimum Junior), on the axis the
  hint served, and that axis caps at its best hinted answer: a later unhinted answer cannot lift it.
- **Wrong** (a clear factual error, such as a wrong complexity): Junior at most.
- **Self-corrected:** a bug the candidate finds in their own trace is not wrong; rate the correction.

An axis's level is the highest level its answers demonstrated, lowered by one if a later answer on
the same point demonstrated a lower level. Never probed is `n/o`. Communication is rated once, from
the whole round. Every level needs a short verbatim quote.

## Feedback

Leslie gives one "what landed" (the highest axis) and one "work on" (the axis furthest below target;
when none is below, the lowest axis, aiming at the next level). Ties go by radar order. The spoken
summary's strongest and weakest are these same two axes, so summary and report agree. Both carry a
verbatim quote; work on carries a concrete next step ("say the empty-input case before you code").
No verdict, no hire call, no overall pass or fail.

## English coaching (affects only communication)

Filler words used three or more times, with counts (the script counts them), and one or two answers
whose content was right but poorly delivered, rephrased using only facts the candidate gave. Coach
wording, never accent; ignore obvious transcription errors.
