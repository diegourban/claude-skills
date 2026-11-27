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
- Levels follow the assigning rule, edge is the median of its floor ratings, topics-mode depth (highest area) and
  breadth (two-thirds rule) follow the area levels, bars follow core/peripheral, the breadth count k
  of n is right, at most three areas are core, no area key reuses an axis name, each panelist's feedback skills follow
  the picking rule, strongest and weakest (axes, and areas in topics mode) follow the tie-break.
- The radar has the seven generic axes in both modes, unprobed axes are skipped in the polygon and
  labelled n/o, the target ring is the target level, every row and section for the mode is present,
  the other mode's section is absent, filler counts are exact, the session record is `v5` (with its `asked:` line) and the
  seven-axis `levels:` line, the easter-egg footnote is verbatim, no feedback point is missing, and
  the report contains no verdict or hire language ("strong yes", "no hire", "verdict").

Without code execution, check these by hand against the rubric instead.

## Round (transcript, both modes)
- [ ] The round follows the plan: its threads in order, each opened by the planned panelist with the planned move recognisable (a twist changes a constraint, a compare sets two options side by side, a teach-back asks for an explanation to a new joiner, a counter takes the opposite position, a quick-fire asks two or three short questions without follow-ups); deviations only where an answer opened something better.
- [ ] Follow-ups use the panelist's planned angles, and at least one solid answer is followed by a move to a new thread rather than another follow-up.
- [ ] Each planned cross-panel moment happens: the named panelist cuts into the thread (interject or disagree), still with one question.
- [ ] No question, introduction or reaction reuses wording from the skill's own examples or references, in any paraphrase close enough to recognise.
- [ ] No "X, and Y?" compound questions, and no panel turn has more than two sentences before its question.
- [ ] No turn reads code out as prose.
- [ ] No praise, feedback or score before "wrap up" or the end of the round, in any wording the script's word list misses. In topics mode, a reaction is one per turn, at most six words, and takes a position or notes interest.
- [ ] Every CV or CV-anchored question refers only to projects, numbers or technologies in the CV or the candidate's own answers.
- [ ] Each signature line is used at most once, never as the answer to "hint", and the panel names are never explained during the round.
- [ ] After "hint", the answer is flagged hinted in session.json; after "skip", it is flagged skipped and the panel moves on.
- [ ] The turn kinds and follow-up marks in session.json are honest (no question-less turn mislabelled as a hint or answer).

## Round (topics mode only)
- [ ] The recorded setup line states every active option (length, CV or topics with its subject, target level, intros when set) and names 3 to 8 areas as "Core: ...; also: ...", and invites a change before the round; a brief's areas keep the brief's names, a single technology is split into 4 to 6 sub-areas that cover how it is built, run, connected, secured and operated.
- [ ] An area that does not apply (frontend with no frontend in the CV or job description) is dropped from the list and never asked about.
- [ ] Exactly one end-to-end walkthrough question is asked, and its answers are rated under design only; every area still has its own question.
- [ ] Every area is drilled until a floor (a don't-know, wrong, skipped or hinted answer) or Staff, or its exact question budget (full 2 to 4; short 2, a third only in a core area after a solid second) ran out.
- [ ] At most one counter-position per area, asked before that area's floor.
- [ ] Without the `intros` option there are no introductions and no background opener: the first panel turn is the walkthrough, and each panelist's first turn opens with a short role tag ("Dennis here, platform team.").
- [ ] At least one diagnosis question (tagged `also: problem`) and one trade-off follow-up (tagged `also: tradeoffs`) were asked, so every radar axis is probed.

## Ratings (the judgement the script trusts)
- [ ] Each answer's demonstrated level in session.json matches the rubric anchors for what was actually said.
- [ ] Flags are right: a confident wrong answer is `bluff` (topics) or `wrong`, a clear factual error is `wrong`, a gap is not.
- [ ] Keys are right: CV deep-dives `depth`, concept questions `breadth`, the snippet and spoken problem `problem`; `also` only where the answer genuinely showed that axis.
- [ ] Each floor (or CV-mode "I don't know") names the concept the candidate could not answer, and its edge rating matches the edge anchors.
- [ ] Every quote is verbatim from the transcript.

## Report
- [ ] Each panelist's "what landed" and "work on" are in the persona's voice, about the skills the script picked, and each carries a verbatim quote.
- [ ] Every "work on" gives a concrete next step the candidate could act on in the next session, not a judgement ("weak on security" fails; "name how services prove identity, e.g. mTLS or workload identity" passes).
- [ ] No overall call in any wording: no hire or no-hire, pass or fail, thumbs up or down, "ready" or "not ready".
- [ ] The spoken summary contains no panelist feedback, only strongest, weakest, breadth (topics) and the report prompt.
- [ ] Grammar slips have a corrected sentence that changes only the grammar; rephrased answers use only facts the candidate gave.
- [ ] The report repeats no contact details and quotes no customer, health or claims data, credentials or private individuals' names.
