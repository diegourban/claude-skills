# session.json

What the model writes at wrap-up for `scripts/report.py`. The model supplies judgement (each answer's
level and flag, quotes, prose, the model solution); the script derives everything rule-based.

```json
{
  "date": "2026-11-24",
  "target": "S",
  "target_label": "Senior backend engineer",
  "language": "Java",
  "problem": {"id": "merge-maintenance-windows", "category": "intervals-heap", "title": "Merge maintenance windows"},
  "setup": "Coding round ready: one problem, about 15 minutes, in Java, target Senior. Keywords: hint, repeat, time out, wrap up.",
  "summary": "Strongest: approach. Weakest: edge cases. Type report when you're out of voice mode.",
  "communication": "S",
  "answers": [
    {"key": "clarifying", "level": "I"},
    {"key": "approach", "level": "S"},
    {"key": "edges", "level": "S", "flag": "hinted"},
    {"key": "correctness", "level": "S", "topic": "trace"}
  ],
  "prose": {
    "approach": {"quote": "verbatim words", "why": "why this level", "next": "what reaches the next level"}
  },
  "feedback_lines": {"landed": "Leslie's voice, verbatim quote", "work_on": "Leslie's voice, quote and next step"},
  "model_solution": {"approach": "...", "complexity": "...", "code": "java sketch", "missed": ["touching windows merge"]},
  "coaching": {"stronger": [{"question": "the question", "answer": "rephrased, candidate's facts only"}]},
  "focus": ["edges: say the touching case before coding", "clarifying: ask about input order", "complexity: name the sort"],
  "transcript": [
    {"speaker": "Leslie", "text": "Leslie here, staff engineer. ...?", "kind": "question"},
    {"speaker": "candidate", "text": "..."}
  ]
}
```

Fields:

- `target`: `J`, `I`, `S` or `St`. `language`: the language the code is written up in.
- `problem.id` must exist in `references/problems.md`.
- `answers`: one entry per rated answer, in order. `key` is one of `clarifying`, `approach`,
  `complexity`, `correctness`, `edges` (never `communication`, which is rated once in `communication`).
  `level` is what the content showed before any flag. `flag`: `hinted` or `wrong`. `topic` (optional)
  groups answers for the "later weaker answer on the same point" rule.
- `prose`: keyed by axis; `quote` must be verbatim from the candidate's turns. One entry per probed
  axis, communication included.
- `feedback_lines`: run `report.py score` first; its `feedback` output names the axis for each point.
- `model_solution`: the bank's model solution, translated to `language`, plus the edge cases this
  candidate missed.
- `transcript`: every turn. Leslie's turns set `kind`: `question` (default), `hint` (a hint the
  candidate asked for), `code` (the on-screen write-up of what they said, one code block, no question
  needed), `trace` (the trace prompt), `answer` (answering the candidate's own question).
- Never put contact details, customer data, credentials or private individuals' names in any field.
