# session.json

What the model writes at wrap-up for `scripts/report.py`. The model supplies judgement (each move's
level, the outcome, quotes, replays); the script derives the levels, the outcome statement, the radar,
the picks and the record.

```json
{
  "date": "2026-11-27",
  "scenario": "nj-lowball-offer",
  "difficulty": "medium",
  "variant": {"active_facts": ["finance", "bonus"], "tactics": ["cites internal parity", "..."]},
  "setup": "Negotiation ready: A low first offer, medium. ... Keywords: coach, repeat, time out, wrap up.",
  "summary": "You closed at 80,500 with a signing bonus. Strongest: questions. Weakest: numbers. Type report ...",
  "delivery": "S",
  "moves": [
    {"key": "questions", "level": "S"},
    {"key": "numbers", "level": "D", "topic": "first counter"},
    {"key": "empathy", "level": "S", "flag": "coached"}
  ],
  "outcome": {"ended": "deal", "value": 80500, "terms": ["signing bonus 5,000"], "relationship": "up"},
  "prose": {"questions": {"quote": "verbatim words", "why": "why this level", "next": "what reaches the next level"}},
  "feedback_lines": {"landed": "...", "work_on": "..."},
  "replays": [{"moment": "after the parity line", "said": "verbatim", "stronger": "rewritten using the round's facts", "technique": "questions"}],
  "focus": ["numbers: ...", "pressure: ...", "discovery: ..."],
  "transcript": [
    {"speaker": "counterpart", "text": "...", "offer": 72000},
    {"speaker": "candidate", "text": "...", "unlocks": "finance"},
    {"speaker": "counterpart", "text": "...", "reveals": "finance"},
    {"speaker": "candidate", "text": "coach"},
    {"speaker": "coach", "text": "..."}
  ]
}
```

Fields:

- `scenario`: a bank id, or `custom` with a `custom_scenario` object shaped like a bank JSON block
  (an anonymised real situation: roles, not names). For `custom`, the record leaves out every figure.
- `difficulty`: `easy`, `medium` or `hard`. `variant`: the `pick` output's variant, unchanged.
- `moves`: one entry per rated candidate move. `key` is one of `empathy`, `mirroring`, `questions`,
  `numbers`, `pressure`, `discovery` (never `delivery`, rated once in `delivery`). `level`: `N`, `D`,
  `S` or `E`. `flag`: `coached` or `damaging`. `topic` (optional) groups moves for the "later weaker
  move on the same point" rule.
- `outcome.ended`: `deal`, `walk-away`, `budget` or `wrap-up`. `value`: the agreed position on the
  scenario's scale (null without a deal). `relationship`: `up`, `neutral` or `strained`.
- `transcript`: every turn. Counterpart turns carry `offer` when they state a position on the scale,
  and `reveals` with a fact id when they reveal one. Candidate turns carry `unlocks` with a fact id
  when the model judged the move to meet that fact's trigger at sufficient trust. Coach lines use
  speaker `coach`.
- `prose`: keyed by axis; `quote` verbatim from the candidate's turns, one per rated axis.
- Never put contact details, real employer names, colleagues' names or real compensation figures in
  any field.
