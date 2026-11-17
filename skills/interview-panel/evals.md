# Evals: interview-panel

Grade the transcript and the report against each check. Pass or fail, no scores.
Any failure: return the failed checks with the offending turn or report section quoted.

## Round (transcript)
- [ ] Every panel turn starts with "<Name> here." and asks exactly one question, with no "X, and Y?" compound (Phase 1 introductions may ask none).
- [ ] No panel turn has more than two sentences before its question.
- [ ] No spoken turn contains markdown (lists, tables, headings); code appears only as a code block of at most 15 lines.
- [ ] No turn reads code out as prose.
- [ ] No praise, feedback or score appears before "wrap up" or the end of the round.
- [ ] Every CV question refers only to projects, numbers or technologies in the CV or the candidate's own answers.
- [ ] No panelist asks more than two questions in a row, except a direct follow-up.
- [ ] Each signature line is used at most once, never as the answer to "hint", and the panel names are never explained during the round.
- [ ] After "hint", the answer is marked hinted; after "skip", the question is marked weak and the panel moves on.

## Scoring
- [ ] The report contains no numeric score, percentile, norm group or error bar.
- [ ] All seven skills appear, each with a level (Junior, Intermediate, Senior, Staff or n/o).
- [ ] Every level other than n/o has at least one verbatim quote from the transcript.
- [ ] Each level follows the rubric's assigning rule: the highest level demonstrated (hinted counts one lower), lowered by one for a later weaker answer on the same topic; probed but only skipped is Junior.
- [ ] All seven skills were probed at least once, or the report marks the unprobed ones n/o.
- [ ] The radar points match the coordinate table for the stated levels (n/o at 170,170).

## Report
- [ ] Each panelist present has a verdict (strong no, no, yes, strong yes) with two lines citing evidence.
- [ ] The English coaching section lists fillers with counts, grammar slips with a corrected sentence, and rephrased answers that use only facts the candidate gave.
- [ ] The report repeats no contact details and quotes no customer, health or claims data, credentials or private individuals' names.
- [ ] The report ends with a session record in the `interview-panel record v1` format and the easter-egg footnote.
