# Evals: coding-round

Two layers. `scripts/report.py` enforces the mechanical checks; the clean-context grader judges the
rest. Pass or fail, no scores. Any failure: return the failed checks with the offending turn or
report section quoted.

## Enforced by the script (the grader does not re-check these)

`report.py selftest` passes, `report.py check session.json` reports no failures, and the report was
produced by `report.py build`. That guarantees: one interviewer; the role tag on Leslie's first turn;
"Leslie here." on every turn; one question per turn except hint, code and answer turns; no markdown in
spoken turns; code blocks of at most 15 lines; no listed praise words; hints only after the candidate
asked; a trace turn exists; the setup line states the language and target; the summary carries no
verdict or feedback; quotes are verbatim; three focus points; levels follow the assigning and hinted
rules; feedback picks, radar points, filler counts and the record follow the rubric.

## Round
- [ ] No "X, and Y?" compound questions, and no turn except the opening one (which may carry the problem statement) has more than two sentences before its question.
- [ ] Turn budgets held: clarifying at most 3 Leslie turns, approach at most 4, code at most 4 write-ups, the trace started by Leslie's 10th turn, the follow-up only before turn 11.
- [ ] No praise, feedback or score before "wrap up", in any wording the script's word list misses.
- [ ] Every code write-up matches what the candidate said step for step: syntax and misheard names may be cleaned up, but no logic, operator, bound or initial value differs from what was spoken unless the candidate corrected it.
- [ ] Reveal-on-ask facts were given only in answer to a question that reached them.
- [ ] The approach and its complexity were asked before any code was written up.
- [ ] The trace used one of the problem's hidden tests, preferring an edge case.
- [ ] Every hint matches the problem's hint ladder, in order, and the answer it served is flagged hinted.

## Ratings (the judgement the script trusts)
- [ ] Each answer's level matches the rubric anchors for what was actually said.
- [ ] A bug the candidate found in their own trace is rated as a self-correction, not as wrong.
- [ ] A missing half of a two-part answer (space without time) was not prompted and is rated as missing.
- [ ] Edges distinguishes found unprompted from found only when the trace pointed at it.

## Report
- [ ] Leslie's what landed and work on are about the axes the script picked, each with a verbatim quote; work on has a concrete next step.
- [ ] The model solution solves the problem, is in the round's language, and lists the edge cases this candidate missed.
- [ ] Rephrased answers use only facts the candidate gave.
- [ ] No overall call in any wording: no hire or no-hire, pass or fail, "ready" or "not ready".
- [ ] The report repeats no contact details and quotes no customer data, credentials or private individuals' names.
