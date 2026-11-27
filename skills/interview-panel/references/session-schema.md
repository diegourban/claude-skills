# session.json

What the model writes at wrap-up for `scripts/report.py`. The model supplies judgement (each answer's
demonstrated level, flags, floors, quotes, prose); the script derives every rule-based value.

```json
{
  "mode": "topics",
  "length": "short",
  "date": "2026-11-19",
  "target": "S",
  "target_label": "Senior backend engineer",
  "panel": ["Leslie", "Dennis", "Freda"],
  "setup": "Panel ready: ... Core: images and builds, networking; also: storage and volumes. Say change X to Y before we start.",
  "summary": "Strongest: depth. Weakest: reasoning at the edge. ... Type report when you're out of voice mode.",
  "areas": [
    {"key": "images-builds", "label": "Images and builds", "core": true, "owner": "Leslie"},
    {"key": "networking", "label": "Networking", "core": true, "owner": "Dennis"},
    {"key": "storage", "label": "Storage and volumes", "core": false, "owner": "Dennis"}
  ],
  "communication": "S",
  "answers": [
    {"key": "design", "level": "S", "by": "Leslie"},
    {"key": "networking", "level": "S", "by": "Dennis", "also": "problem", "topic": "dns"},
    {"key": "networking", "level": "I", "by": "Dennis", "floor": "overlay network internals", "edge": "S"},
    {"key": "storage", "level": "J", "flag": "bluff", "by": "Dennis", "floor": "volume drivers", "edge": "J"}
  ],
  "prose": {
    "networking": {"quote": "verbatim words", "why": "why this level", "next": "what reaches the next level"},
    "depth": {"quote": "verbatim words", "why": "why this level", "next": "what reaches the next level"}
  },
  "feedback_lines": {"Leslie": {"landed": "persona-voice strength with a verbatim quote", "work_on": "persona-voice gap with a quote and a next step"}},
  "coaching": {
    "grammar": [{"said": "We have ran both flows", "better": "We ran both flows"}],
    "overused": [{"word": "obviously", "try": "clearly"}],
    "stronger": [{"question": "the question", "answer": "rephrased answer, candidate's facts only"}]
  },
  "focus": ["storage: volume drivers", "edge: stated a guess as fact", "networking: overlay internals"],
  "transcript": [
    {"speaker": "Leslie", "text": "Leslie here. ...?", "kind": "question"},
    {"speaker": "candidate", "text": "..."}
  ]
}
```

Fields:

- `mode`: `cv` or `topics`. `length`: `full` or `short`. `target`: `J`, `I`, `S` or `St`.
  `intros` (optional, topics mode): `true` when the user asked to keep Phase 1; without it `check`
  rejects intro turns and requires a role tag on each panelist's first turn.
- `plan`: the `report.py plan` output, unchanged. `check` compares each thread's first turn with
  the planned opener and counts the cross-panel turns.
- `asked`: the topic tags that actually came up, starting from `plan.planned_tags` (drop what was
  skipped, add what came up unplanned). It becomes the record's `asked:` line, which the next plan
  steers away from.
- `setup` and `summary`: the exact setup line and spoken summary, so the grader can check them.
  `check` verifies the setup line names every area label and the summary carries no panel feedback.
- `areas` (topics mode only): the session's topic areas in setup order, core first. `key` is lowercase
  and hyphenated, and may not be one of the seven axis names. At most three `core`. An area that does
  not apply is left out, not listed.
- `answers`: one entry per rated answer, in order.
  - `key`: an axis (`depth`, `breadth`, `design`, `problem`, `tradeoffs`; Freda's behavioural question
    is `tradeoffs`) or, in topics mode, an area
    key. A question asked inside an area (including another panelist's trade-off follow-up or a
    diagnosis question) is keyed to that area, with `also` for the axis. In CV mode, deep-dives are
    `depth`, concept questions `breadth`, the snippet review and the spoken problem `problem`. In topics mode, depth and breadth are derived from the areas; do not use
    them as keys. Never use `edge` or `communication` as keys.
  - `also` (optional): an axis, or a list of axes, the same answer also rates (`"also": "problem"` on a
    diagnosis question, `"also": "tradeoffs"` on a trade-off follow-up).
  - `level`: what the content demonstrated before any flag. `flag`: `hinted`, `skipped`, `wrong` or
    `bluff` (a confident wrong answer). `topic` (optional) groups answers for the "later weaker answer
    on the same topic" rule. `by`: the asking panelist.
  - A floor (topics mode) or an "I don't know" (CV mode) adds `floor` (the concept) and `edge` (the
    level of reasoning at the edge). In topics mode every flagged area answer (`hinted`, `skipped`,
    `wrong`, `bluff`) is a floor and must carry both. A don't-know floor's `level` is `J`; it only rates
    the area when it is the area's first answer. Answers after an area's floor don't change its level.
  - `key` must be one of the session's area keys or an allowed axis; the script rejects anything else.
- `communication`: the level rated from all answers (not stepped).
- `prose`: keyed by axis or area key; `quote` must be verbatim from the transcript. Give every probed
  axis and area an entry, including derived depth and breadth (quote the answer that set them).
- `feedback_lines`: per panelist, the `landed` and `work_on` text. Run `report.py score` first: its
  `feedback` output names the axis each point must be about. No verdict or hire language.
- `transcript`: every turn. Panel turns may set `kind` to `intro`, `hint` or `answer` (may end without
  a question) and `followup: true` (a direct follow-up, exempt from the two-in-a-row limit). In topics
  mode, every drill question after an area's first sets `followup: true`; `check` still rejects a fifth
  turn in a row from one panelist. Every panel turn sets `thread` (the plan's thread number; 0 for
  intros, the opener, the walkthrough, the snippet, the diagnosis question, the behavioural question
  and the close), and a cross-panel turn sets `kind: interject`.
- Never put contact details, customer, health or claims data, credentials or private individuals'
  names in any field.
