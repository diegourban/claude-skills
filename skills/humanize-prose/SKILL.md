---
name: humanize-prose
version: "1.0"
description: Rewrites text so it stops reading like LLM output, in five passes (strip the tells, break the rhythm, take a side, say it out loud, hostile reader test), runnable together or one at a time, keeping the meaning and facts identical. Use when the user says "make this sound less like AI", "people can tell I used ChatGPT", "humanize this", "strip the AI tells", "break the rhythm", "make it sound like me", or "run the hostile reader test on this". Do NOT use to check whether a post's claims or numbers are right, use the diegourban:article-review-panel skill instead. Do NOT use to write a commit message, use a direct conversation instead. Do NOT use to write a new document from scratch, have a direct conversation or use the docs skill instead.
argument-hint: "[all|strip|rhythm|side|voice|hostile] <pasted text or path>"
---

# humanize-prose

**Version:** 1.0

Takes a draft (Slack message, email, PR description, post, doc section) and
rewrites it so a reader can't tell an LLM touched it. Five passes, each with
one job. The author's meaning, facts and numbers are the source of truth; the
passes change how it reads, never what it says.

## Critical rules (read first)

1. **Meaning and facts are frozen.** Never add a claim, number, example,
   anecdote or name the draft doesn't contain. Never drop one either, unless a
   pass explicitly cuts it (a summary closer, a redundant caveat).
2. **Each pass does only its own job.** Pass 1 changes nothing but the tells.
   Pass 2 changes nothing but the rhythm. Don't let a pass "improve" other things.
3. **Take the author's side, not yours.** Pass 3 picks the side the draft
   already leans toward. If the draft is genuinely 50/50, ask which side the
   user holds instead of guessing. List every side taken so the user can veto it.
4. **A caveat that's true and matters stays.** Cut reflexive hedging, keep the
   one caveat that would bite the reader if it were missing (a limitation, a
   risk, a compliance condition).
5. **Your own output must pass too.** No em or en dashes, no triads of
   adjectives, no summary closer, no word from `references/tells.md` in the
   rewrite or in your notes.
6. **Match the register of the destination.** Slack is looser than a
   Confluence page. Contractions everywhere is right for Slack, too loose for a
   policy doc. Ask only if the destination isn't obvious from the text.
7. **Restricted data stops the run.** If the draft contains customer records,
   health, financial or HR data, or credentials, ask the user to redact it first.

## Read-first table

| Source | Path | What to extract |
|---|---|---|
| The draft | pasted text, or the file the user names | Every sentence, the destination (Slack, email, post, doc), the author's position |
| The tells catalogue | `references/tells.md` | The words, structures and rhythms each pass hunts for, and what to replace them with |
| Past lessons | `~/.claude/skill-memory/humanize-prose.md` (create it if missing) | The user's voice preferences from earlier runs; apply before rewriting |
| Output checks | `evals.md` | The pass/fail checks the grader runs on the final text |

## Workflow

### Phase 0. Pick the passes

- No pass named, or "humanize this": run all five, in order.
- A pass named ("just strip the tells", "break the rhythm"): run only that one.
  Aliases: `strip`, `rhythm`, `side`, `voice`, `hostile`.

### Pass 1. Strip the tells

Remove the patterns that give away AI writing: em dashes, "it's not X, it's Y"
contrasts, reflexive lists of three, words like "delve" and "crucial", and any
closing line that summarises what was already said. Change nothing else.

- Replace each dash with a full stop, comma, colon or parentheses, whichever
  the sentence needs. Keep dashes only in ranges (2024-2026, pages 4-9).
- Turn "not X, but Y" into a plain statement of Y.
- A list of three that names three real, distinct things stays (tracing,
  metrics and logs). A triad of adjectives or benefits drops to the strongest one.
- Swap each flagged word for the plain one (`references/tells.md` has the map).
- Delete the summary closer outright. Don't replace it.

### Pass 2. Break the rhythm

Every sentence with roughly the same length and shape: rewrite so the rhythm
varies. Some short. Some longer ones that carry a full thought. Keep the
meaning identical.

- Count words per sentence. Three in a row within a few words of each other is
  the signal. Merge two, or split one into a fragment.
- Vary sentence openings. No two consecutive sentences start the same way.
- Vary paragraph length too. A one-line paragraph is allowed.

### Pass 3. Take a side

Where it reads like a neutral observer trying not to offend anyone, rewrite it
with a clear opinion. Cut every "it depends", "on the other hand" and balanced
caveat that isn't genuinely needed (rule 4 decides what's needed).

- State the recommendation as a recommendation: "Use X." not "X may be worth considering."
- Record each side taken for the notes (rule 3).

### Pass 4. Say it out loud

Rewrite it the way the user would say it to a colleague across the desk. Drop
formal transitions like moreover, additionally and furthermore. Use
contractions. Start with the point, not the setup.

- Move the conclusion or the ask to the first sentence.
- Delete throat-clearing openers ("I wanted to reach out", "In today's...").
- Read it as speech. Any phrase nobody would say aloud gets rewritten.

### Pass 5. The hostile reader test

Spawn a subagent with a clean context. Give it only the rewritten text,
`references/tells.md` and `evals.md`, never the original draft. Prompt it:

> Act as a reader who assumes this was written by AI. Quote every sentence that
> made you suspicious and say why in one line. Then grade the text against
> evals.md, pass or fail per check.

Rewrite only the quoted sentences, plus whatever a failed check points at.
Re-run the subagent until it quotes nothing and every check passes (stop after
three rounds and report what's left). When the user asked for this pass alone,
show them the quote list and the rewrites; skip the subagent if the text is
under 100 words and do it inline.

### Phase 6. Deliver

Show the result in the format below. Edit a file in place only when the user
asked for the file to be changed. Add any voice feedback the user gives to `~/.claude/skill-memory/humanize-prose.md` (newest first; create it if missing).

## Output format

All passes:

```
<the rewritten text>

---
Sides taken: <each opinion pass 3 committed to, or "none">. Veto any you don't hold.
Kept on purpose: <a caveat or list of three you left in, and why, or omit the line>
Hostile reader: <"nothing flagged after N rounds" | the sentences still flagged>
```

Single pass: the rewritten text, then one line saying what the pass changed.
Hostile reader alone: the quote list (`> sentence` then `why: ...`), then each rewrite.

## Worked example

Input:
> humanize this before I post it in #engineering:
> In today's fast-paced engineering landscape, observability is not just a
> nice-to-have — it's a crucial foundation. Let's delve into why. Teams that
> invest in tracing, metrics, and logging see faster incident resolution,
> happier engineers, and more reliable systems. That said, the right approach
> depends on your team's context and maturity. In summary, observability is
> key to modern software delivery.

Steps Claude takes:

1. Pass 1: drops "In today's fast-paced engineering landscape", the em dash,
   the "not just X, it's Y" frame, "crucial", "delve", and the "In summary" closer.
   Keeps "tracing, metrics and logs" (three real things), cuts the benefit
   triad to "fix incidents faster".
2. Pass 2: the survivors are all 10 to 14 words. Opens with a three-word sentence.
3. Pass 3: the draft argues for observability, so "depends on your team's
   maturity" becomes "don't wait until you feel ready". Noted as a side taken.
4. Pass 4: Slack destination, so contractions and the point first.
5. Pass 5: a clean subagent flags nothing; all evals pass.

Output:

```
You need observability. Teams that invest in tracing, metrics and logs fix
incidents faster. Don't wait until your team feels mature enough for it.

---
Sides taken: "don't wait for maturity" replaces "it depends on your team's maturity". Veto it if you meant the caveat.
Kept on purpose: tracing, metrics and logs, because they're three distinct things, not a rhetorical triad.
Hostile reader: nothing flagged after 1 round.
```

## Reference files

- `references/tells.md`: the catalogue of vocabulary, structural and rhythm
  tells, with the plain replacement for each.
- `evals.md`: pass/fail checks. The pass 5 subagent grades the final text with
  them; iterate until all pass.
- `~/.claude/skill-memory/humanize-prose.md`: lessons log, newest first, private to this machine (see `memory.md`). Read before rewriting.

## When NOT to use this skill

- Checking whether a post's facts, numbers or conclusions hold up. Use diegourban:article-review-panel.
- Writing a commit message. Use a commit-message skill or a direct conversation.
- Drafting something new from nothing. Have a direct conversation, then run this on the draft.
- Code comments and API docs, where precise and formal is the right register.
