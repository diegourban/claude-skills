# Evals: interview-panel

Two layers. `scripts/report.py` enforces the mechanical checks; the clean-context grader judges the
rest. Pass or fail, no scores. Any failure: return the failed checks with the offending turn or
report section quoted.

## Enforced by the script (the grader does not re-check these)

`report.py selftest` passes, `report.py check session.json` reports no failures, and the report was
produced by `report.py build`. That guarantees:

- Every panel turn starts with "<Name> here." and has exactly one question mark, except turns of kind
  intro, hint or answer; no markdown in spoken turns; code blocks of at most 15 lines; no code in
  topics mode; no listed praise words; no third question in a row without a follow-up mark.
- Levels follow the assigning rule, edge follows the floor rule, bars follow core/peripheral, breadth
  k of n is counted correctly, at most three areas are core, verdicts follow the counting rules and
  key skills for the mode, strongest and weakest follow the tie-break (areas only in topics mode).
- Radar points and axis labels match the mode, every row and section for the mode is present, the
  other mode's section is absent, filler counts are exact, the session record is `v2` in the right
  shape, and the easter-egg footnote is verbatim.

Without code execution, check these by hand against the rubric instead.

## Round (transcript, both modes)
- [ ] No "X, and Y?" compound questions, and no panel turn has more than two sentences before its question.
- [ ] No turn reads code out as prose.
- [ ] No praise, feedback or score before "wrap up" or the end of the round, in any wording the script's word list misses. In topics mode, a reaction is one per turn, at most six words, and takes a position or notes interest.
- [ ] Every CV or CV-anchored question refers only to projects, numbers or technologies in the CV or the candidate's own answers.
- [ ] Each signature line is used at most once, never as the answer to "hint", and the panel names are never explained during the round.
- [ ] After "hint", the answer is flagged hinted in session.json; after "skip", it is flagged skipped and the panel moves on.
- [ ] The turn kinds and follow-up marks in session.json are honest (no question-less turn mislabelled as a hint or answer).

## Round (topics mode only)
- [ ] The setup line states the area mapping, the core areas, and frontend n/a when it applies.
- [ ] Frontend is n/a only when neither the CV nor the job description shows frontend work; an n/a area is never asked about.
- [ ] Exactly one end-to-end walkthrough question is asked, and its answers are rated under design only; every area still has its own question.
- [ ] Every applicable area is drilled until a floor (a don't-know, wrong, skipped or hinted answer) or Staff, or its budget ran out.
- [ ] At most one counter-position per area, asked before that area's floor.

## Ratings (the judgement the script trusts)
- [ ] Each answer's demonstrated level in session.json matches the rubric anchors for what was actually said.
- [ ] Flags are right: a confident wrong answer is `bluff` (topics) or `wrong`, a clear factual error is `wrong`, a gap is not.
- [ ] Each floor names the concept the candidate could not answer, and its edge rating matches the edge anchors.
- [ ] Every quote is verbatim from the transcript.

## Report
- [ ] Each verdict's two lines are in the persona's voice and cite evidence consistent with the computed verdict.
- [ ] Grammar slips have a corrected sentence that changes only the grammar; rephrased answers use only facts the candidate gave.
- [ ] The report repeats no contact details and quotes no customer, health or claims data, credentials or private individuals' names.
