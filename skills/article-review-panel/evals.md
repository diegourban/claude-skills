# Evals: article-review-panel

Grade each review file against each check. Pass or fail, no scores.
Any failure: return the file name with the failed checks listed.

## Shape
- [ ] The file has the sections Verdict, Good, Wrong, Needs more explanation, in that order.
- [ ] Every "Wrong" item has a "Suggested fix" (wording, command or cut).
- [ ] The file is named `REVIEW-<DRAFT-STEM>-<LENS>.md` and sits next to the draft.

## Evidence
- [ ] Every number the review quotes from the data names the file it came from, or appears in a table whose source is stated.
- [ ] No claim is called false or untested without saying what was searched or computed.
- [ ] No "Wrong" item is a pure style preference.

## Lens discipline
- [ ] The review does not repeat another lens's findings at length; it cross-references the other file instead.
- [ ] Statistics file: it states the design (paired or unpaired) and reports at least one CI and one MDE.
- [ ] Editorial file: it states the character count against the platform limit.
- [ ] Domain file: it names the versions the claims were checked against.
- [ ] Domain file: it says whether every claim the author didn't measure is cited (inline link plus a References entry), and lists each unsourced claim as Wrong.
- [ ] Domain file: it reports the overlap check's result (`scripts/check_posts.py`) when the blog has it, including sources it couldn't fetch.

## Safety
- [ ] No restricted data (member, claims, health, credentials) appears in the review.
- [ ] Production or internal figures are flagged for Comms/Legal sign-off, not repeated as publishable.
