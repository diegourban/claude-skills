# session.json

What the model writes at wrap-up for `scripts/report.py`. The model supplies judgement (each answer's
demonstrated level, flags, floors, quotes, prose); the script derives every rule-based value.

```json
{
  "mode": "topics",
  "length": "short",
  "date": "2026-11-18",
  "target": "S",
  "target_label": "Senior backend engineer",
  "panel": ["Leslie", "Dennis", "Freda"],
  "core": ["backend", "databases", "performance"],
  "na": ["frontend"],
  "area_mapping": "testing -> methodology; cloud -> infrastructure",
  "communication": "S",
  "answers": [
    {"key": "databases", "level": "S", "by": "Leslie", "topic": "isolation"},
    {"key": "databases", "level": "I", "by": "Leslie", "floor": "MVCC read views", "edge": "S"},
    {"key": "security", "level": "J", "flag": "bluff", "by": "Dennis", "floor": "service identity", "edge": "J"}
  ],
  "prose": {
    "databases": {"quote": "verbatim words", "why": "why this level", "next": "what reaches the next level"}
  },
  "verdict_lines": {"Leslie": "two lines in persona voice"},
  "coaching": {
    "grammar": [{"said": "We have ran both flows", "better": "We ran both flows"}],
    "overused": [{"word": "obviously", "try": "clearly"}],
    "stronger": [{"question": "the question", "answer": "rephrased answer, candidate's facts only"}]
  },
  "focus": ["security: service identity in-cluster", "edge: stated a guess as fact", "databases: MVCC"],
  "transcript": [
    {"speaker": "Leslie", "text": "Leslie here. ...?", "kind": "question"},
    {"speaker": "candidate", "text": "..."}
  ]
}
```

Fields:

- `mode`: `cv` or `topics`. `length`: `full` or `short`. `target`: `J`, `I`, `S` or `St`.
- `answers`: one entry per rated answer, in order. `key` is a CV skill (`depth`, `design`, `coding`,
  `debugging`, `concepts`, `tradeoffs`) or, in topics mode, an area or `design`/`tradeoffs`. `level` is
  what the content demonstrated before any flag. `flag`: `hinted`, `skipped`, `wrong` or `bluff`
  (a confident wrong answer). `topic` (optional) groups answers for the "later weaker answer on the
  same topic" rule. Topics mode: `by` is the asking panelist; a floor answer adds `floor` (the concept)
  and `edge` (the level of reasoning at the edge). Do not list `edge` or `communication` as keys.
- `communication`: the level rated from all answers (not stepped).
- `prose`: keyed by skill or area; `quote` must be verbatim from the transcript.
- `transcript`: every turn. Panel turns may set `kind` to `intro`, `hint` or `answer` (may end without
  a question) and `followup: true` (a direct follow-up, exempt from the two-in-a-row limit).
- Never put contact details, customer, health or claims data, credentials or private individuals'
  names in any field.
