# Rubric

Levels are judgements against written anchors, not measurements: Novice, Developing, Skilled,
Expert. There is no population data behind them, so the report never shows a score, a percentile or
a verdict. The outcome is reported as facts about this deal against the hidden brief. Rating each
move is the model's job; levels, picks, the radar, the outcome and the record are computed by
`scripts/report.py`, whose selftest pins the cases.

## The seven axes (radar order)

Keys and techniques are defined in `references/techniques.md`: `empathy`, `mirroring`, `questions`,
`numbers`, `pressure`, `discovery`, `delivery`.

## Level anchors

| Axis | Novice | Developing | Skilled | Expert |
|---|---|---|---|---|
| empathy | Argues their own case, never names the other side's position | Names the other side's position once, often followed by "but" | Labels pressure and concerns as they appear and lets the label land | Defuses objections before they are voiced and turns the mood of the conversation |
| mirroring | Never mirrors | Mirrors mechanically or in a challenging tone | Mirrors key words at the right moments and gets more information | Mirrors and stays silent so the other side fills the gap with something useful |
| questions | Yes/no or "why" questions | Some open questions, mostly to gather facts | "How" and "what" questions that make the other side work on the gap | Steers the other side into proposing the solution themselves |
| numbers | Names a round number first or accepts the first offer | Counters, but in equal or growing steps or by splitting the difference | Lets them anchor or anchors high and precise, concedes in shrinking steps | Also trades non-monetary terms to close above target without straining the relationship |
| pressure | Concedes to a deadline or "final" line | Holds once, then gives way or argues | Holds calmly, uses silence and no-oriented questions | Turns the pressure into information about what is driving it |
| discovery | Finds none of the hidden facts | Finds one, by accident or late | Finds every active hidden fact before conceding | Finds them early and uses each one to change the deal |
| delivery | Rushed, defensive or combative | Calm in places, wobbles under pressure | Calm, curious, paced; summarises their position | Summarises so well that the other side confirms it outright, and keeps that tone throughout |

## Rating a move

Rate each of the candidate's moves that shows an axis, by the level its content demonstrates.

- **Coached:** a move made right after a `coach` line counts one level lower (minimum Novice) on the
  axis the coaching served, and that axis caps at its best coached move.
- **Self-damaging** (an ultimatum, an insult, accepting below their own floor): Novice on that axis.

An axis's level is the highest level its moves demonstrated, lowered by one if a later move on the
same point was weaker. Never shown is `n/o`. Delivery is rated once from the whole round.

**Discovery is capped by what was found:** with none of the active hidden facts revealed, discovery
is Novice; with some but not all, at most Developing; with all, as rated.

## Counterpart behaviour

The counterpart keeps a hidden trust level: low, medium or high. It starts at medium (`easy`: high,
`hard`: low).

- Trust rises after a move rated Skilled or Expert on empathy, mirroring, questions or delivery.
- Trust falls after an ultimatum, an argument, a "why" that accuses, or a demand with no reason.
- **Concessions:** the counterpart moves one step along the scenario's `steps` only at medium trust or
  higher, and only after the candidate has asked for movement. At `hard`, two good moves are needed
  per step. The counterpart never goes past the last step and never states the limit.
- **Hidden facts:** an active fact is revealed only after a candidate move that matches its trigger,
  at medium trust or higher. It comes out in the counterpart's own words, as information, never as
  advice.

## Feedback and debrief

One "what landed" (the highest axis) and one "work on" (the lowest), picked by the script, ties by
radar order. Two or three replays: a moment from the transcript, what was said, and a stronger
version using a named technique and only facts from the round. Technique cards for the two weakest
axes come from `references/techniques.md`. No verdict, no pass or fail.

## English coaching

Filler words used three or more times, with counts (the script counts them). Coach wording, never
accent; ignore obvious transcription errors.
