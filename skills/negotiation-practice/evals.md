# Evals: negotiation-practice

Two layers. `scripts/report.py` enforces the mechanical checks; the clean-context grader judges the
rest. Pass or fail, no scores. Any failure: return the failed checks with the offending turn or
report section quoted.

## Enforced by the script (the grader does not re-check these)

`report.py selftest` passes, `report.py check session.json` reports no failures, and the report was
produced by `report.py build`. That guarantees: counterpart turns of at most three sentences that
never name a technique; no statement of a money limit before reaching it; offers only on the
scenario's steps, one step at a time, never backwards, never past the limit; hidden facts revealed
only when active and after an unlocking move; coach lines only after "coach"; the setup names the
scenario; the summary carries no verdict; quotes are verbatim; feedback, two or three replays and
three focus points exist; levels, discovery's cap, picks, the outcome statement, the radar and the
figure-free record follow the rubric.

## Round
- [ ] The counterpart stays in character: no praise, no coaching, no hint of the hidden brief beyond what was revealed.
- [ ] The counterpart uses the variant's pressure tactics, adapted to the conversation, not recited.
- [ ] Trust moves as the rubric says: steps and reveals follow Skilled or better moves, and stall or reverse after ultimatums or arguing.
- [ ] Every `unlocks` tag sits on a move that genuinely matches that fact's trigger.
- [ ] Each coach line names a technique and why, and never supplies the words to say.
- [ ] No counterpart line reuses wording from the technique cards' patterns or the scenario text verbatim.

## Ratings
- [ ] Each move's level matches the anchors for what was actually said.
- [ ] Moves made right after coaching are flagged `coached`; ultimatums or accepting below one's own floor are flagged `damaging`.

## Report
- [ ] Each replay quotes what the candidate said and offers a stronger version that uses a named technique and only facts from the round.
- [ ] The landed and work-on lines are about the axes the script picked, each with a verbatim quote; work on has a concrete next step.
- [ ] No overall call in any wording: no win or loss, pass or fail, grade or score.
- [ ] Nothing quotes *Never Split the Difference*; techniques are described in the skill's own words.
- [ ] The report repeats no contact details, real employer or colleague names, or real compensation figures.
