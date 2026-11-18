# Evals: interview-panel

Grade the transcript and the report against each check. Pass or fail, no scores.
Any failure: return the failed checks with the offending turn or report section quoted.

## Round (transcript, both modes)
- [ ] Every panel turn starts with "<Name> here." and asks exactly one question, with no "X, and Y?" compound (Phase 1 introductions, hint nudges and answers to the candidate's questions may ask none).
- [ ] No panel turn has more than two sentences before its question.
- [ ] No spoken turn contains markdown (lists, tables, headings); code appears only as a code block of at most 15 lines.
- [ ] No turn reads code out as prose.
- [ ] No praise, feedback or score appears before "wrap up" or the end of the round. In topics mode, any reaction is one per turn, at most six words, and takes a position or notes interest, never judges the answer (no "great", "exactly", "good point").
- [ ] Every CV or CV-anchored question refers only to projects, numbers or technologies in the CV or the candidate's own answers.
- [ ] No panelist asks more than two questions in a row, except a direct follow-up (in topics mode, any question within the same area's drill).
- [ ] Each signature line is used at most once, never as the answer to "hint", and the panel names are never explained during the round.
- [ ] After "hint", the answer is marked hinted; after "skip", the question is marked weak and the panel moves on.

## Round (topics mode only)
- [ ] The setup line states the area mapping, the core areas, and frontend n/a when it applies.
- [ ] Frontend is n/a only when neither the CV nor the job description shows frontend work; an n/a area is never asked about.
- [ ] No code snippet is pasted, and exactly one end-to-end walkthrough question is asked.
- [ ] Every applicable area is probed and drilled until a floor (a don't-know, wrong, skipped or hinted answer) or Staff, unless its question budget ran out, which the report's floor column says ("not reached").
- [ ] The walkthrough's answers are rated under design only; every area still has its own question.
- [ ] At most one counter-position per area, asked before that area's floor, and each still ends in exactly one question.

## Scoring (both modes)
- [ ] The report contains no numeric score, percentile, norm group or error bar; the topics-mode breadth count is the only count.
- [ ] The radar points match the coordinate table for the stated levels (n/o and n/a at 170,170), and the axis labels match the mode.

## Scoring (CV mode only)
- [ ] All seven skills appear, each with a level (Junior, Intermediate, Senior, Staff or n/o).
- [ ] Every level other than n/o has at least one verbatim quote from the transcript.
- [ ] Each level follows the rubric's assigning rule: the highest level demonstrated (hinted counts one lower), lowered by one for a later weaker answer on the same topic; probed but only skipped is Junior.
- [ ] All seven skills were probed at least once, or the report marks the unprobed ones n/o.

## Scoring (topics mode only)
- [ ] All seven areas appear, each with a level (or n/o, n/a) backed by a verbatim quote, core or peripheral, its bar, and a named floor or "none" (Staff reached).
- [ ] Bars follow the rule: core = target, peripheral = one below; the target polygon uses each area's bar.
- [ ] The four thinking skills (design, trade-offs, reasoning at the edge, communication) appear with levels and quotes.
- [ ] Edge follows the rubric: the level most floors showed (tie: lower), no further adjustment; a confident wrong answer rated that floor Junior.
- [ ] The breadth count k of n matches the area levels (n excludes n/a and unprobed n/o; k counts Intermediate or above).
- [ ] At most three areas are core.
- [ ] Verdicts use the topics-mode key skills and each area's bar; thinking skills use the target; strong yes needs a key skill above the target level itself.
- [ ] Strongest and weakest are areas, not thinking skills.

## Report
- [ ] Each panelist present has a verdict (strong no, no, yes, strong yes) with two lines citing evidence.
- [ ] The English coaching section lists fillers with counts, grammar slips with a corrected sentence, and rephrased answers that use only facts the candidate gave.
- [ ] The report repeats no contact details and quotes no customer, health or claims data, credentials or private individuals' names.
- [ ] The report ends with a session record in the `interview-panel record v2` format for its mode (`format: cv` or `format: topics`) and the easter-egg footnote.
