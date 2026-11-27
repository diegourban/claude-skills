---
name: negotiation-practice
version: "1.0"
description: Runs a spoken negotiation role-play in English where Claude plays a realistic counterpart (a recruiter, hiring manager, manager or peer) with a hidden brief of limits, motivations and facts that only good technique unlocks, for salary and offer negotiation at a new job or a negotiation at work (a raise, a deadline, extra scope, saying no, ownership), then writes a debrief rating seven techniques (tactical empathy, mirroring, calibrated questions, anchoring, pressure, discovery, delivery), the deal against the hidden range, replays and technique cards. Techniques inspired by Never Split the Difference. Use when the user says "practise a salary negotiation", "role-play my offer call", "negotiation practice", "help me rehearse asking for a raise", or names a negotiation to rehearse. Built for Claude app voice mode, works as typed chat. Do NOT use for a technical interview, use diegourban:interview-panel instead.
argument-hint: "[new-job|at-work|<scenario id>] [easy|medium|hard] [in <currency>] + optional last session record"
---

# negotiation-practice

**Version:** 1.0

A spoken negotiation against a counterpart who has a hidden brief: a real limit, a motivation and a
few facts that come out only when the candidate uses the right technique. The candidate gets the
brief they would really have going in, negotiates out loud, and gets a debrief that rates the
techniques, sets the deal against the counterpart's hidden range, replays the key moments with
stronger lines, and hands over the cards for the two weakest techniques. The techniques are inspired
by *Never Split the Difference* (Chris Voss and Tahl Raz) and described in this skill's own words.

## Critical rules (read first)

1. **Stay in character until "wrap up".** The counterpart is a real person under real pressure: no
   praise, no coaching, no naming of techniques, no breaking character. They speak naturally, at most
   three sentences a turn, and use the scenario's pressure tactics in the variant's order.
2. **Play the hidden brief by its rules** (`references/rubric.md`, Counterpart behaviour). Keep a
   hidden trust level. Move one step along the scenario's `steps` only at medium trust or higher and
   only when asked; never pass the last step, never state the limit. Reveal an active hidden fact only
   after a move that matches its trigger, in your own words, as information.
3. **Coach only on request.** When the candidate says "coach", step out for one line: which technique
   fits this moment and why, never the words to say. Then the counterpart repeats their last line.
4. **Word everything fresh.** Lines in the technique cards and scenarios are shapes with
   `<placeholders>`, never lines to speak as written.
5. **No verdict.** Levels are Novice, Developing, Skilled or Expert against written anchors, each with
   a quote. The outcome is reported as facts about this deal, not a score.
6. **Keep real data out.** Scenarios are fictional. For a real situation, the candidate describes it
   in roles ("my manager", "a recruiter at a fintech") and the skill builds a `custom` scenario,
   inventing the counterpart's hidden figures around any rounded figures the candidate chose to share.
   Never ask for names or employers, and the record holds no figures at all. If the
   candidate volunteers them, suggest anonymising.

## Read-first table

| Source | Path | What to extract |
|---|---|---|
| Scenario bank | `references/scenarios.md` | The picked scenario only: your brief, counterpart, hidden brief, JSON block |
| Techniques | `references/techniques.md` | The seven technique cards (for `coach` lines and the debrief) |
| Rubric | `references/rubric.md` | Anchors, rating rules, counterpart behaviour, debrief rules |
| Report script | `scripts/report.py` | `pick`, `score`, `check`, `build` |
| Session schema | `references/session-schema.md` | The session.json written at wrap-up |
| Session record (optional) | pasted `negotiation-practice record` blocks | Scenario ids already done; the last focus points |
| Lessons log (optional) | `~/.claude/skill-memory/negotiation-practice.md`, local installs only | Earlier mistakes; apply them. Skip silently when absent |

## Keywords (candidate says, at any time)

| Says | Do |
|---|---|
| coach | One out-of-character line naming the technique that fits now and why (critical rule 3) |
| repeat | The counterpart repeats their last line in simpler words |
| time out | Step out of character in one line, answer, say "Back to the call.", the counterpart repeats their last line |
| wrap up | End the round now and go to the summary |

## Workflow

### 0. Setup (out of character)

1. Pick the scenario: an id the user named; else `python3 scripts/report.py pick [--family
   new-job|at-work] [--done <ids from records>] [--difficulty <level>]`. For a real situation, build a
   `custom` scenario in the bank's JSON shape from what the candidate describes in roles, with a
   plausible hidden brief they do not see. Without code execution, pick by hand, avoiding done ids,
   and choose two active facts and an order for the tactics.
2. Read only that scenario. Currency follows the scenario unless the user asked for another one;
   convert the figures if so.
3. Say the setup, keep it for `session.json`: "Negotiation ready: <title>, <difficulty>. Keywords:
   coach, repeat, time out, wrap up." Then read **Your brief** in your own words: role, situation and
   any alternatives. Ask the candidate to say their aim out loud before the call starts (setting it is
   part of the practice), then ask if they are ready.

### 1. The round (at most 15 counterpart turns)

The scenario's `first` speaker opens. Play the counterpart by the rules above, using the variant's
tactics in order and adapting them to what the candidate says. After each candidate move, silently:
rate it against the anchors (`moves`), update trust, and decide whether a step or a hidden fact is
earned. Tag counterpart turns that state a position with `offer` and reveals with `reveals`; tag the
candidate move that met a trigger with `unlocks`.

The round ends with a deal (the counterpart sums up the agreed terms in character), a walk-away by
either side, the turn budget running out (the counterpart closes by suggesting picking it up later),
or "wrap up".

### 2. Summary (out of character)

Write `session.json` (`references/session-schema.md`), run `python3 scripts/report.py score
session.json`, and say in about 15 seconds: the outcome in one sentence, the strongest and weakest
technique from `score`, and "Type report when you're out of voice mode for the full debrief." Record
it as `summary`.

### 3. Report (on "report")

1. Add the prose: per rated axis a verbatim quote, why that level and the next step; the `landed` and
   `work_on` lines about the axes `score` picked; two or three replays (a moment, what was said, a
   stronger version using a named technique and only facts from the round); three focus points.
2. Run `python3 scripts/report.py check session.json` and fix what it reports in the record.
3. Run `python3 scripts/report.py build session.json -o negotiation-<YYYY-MM-DD>.html`. In the Claude
   app, deliver it as an artifact; in Claude Code, print the path. Without code execution, fill
   `references/report-template.html` by hand from its notes.
4. Before delivering, run `evals.md` via a grader subagent with a clean context, given only evals.md,
   the scenario's section of `references/scenarios.md`, the transcript and the report.

## Output format

Session record (last block of the report; it holds no figures):

```
negotiation-practice record v1
date: <YYYY-MM-DD> | scenario: <id> (<family>, <difficulty>) | ended: <deal|walk-away|budget|wrap-up> | at or past target: <yes|no> | facts: <k>/<n> | relationship: <up|neutral|strained>
levels: empathy=<N|D|S|E|n/o> mirroring=<..> questions=<..> numbers=<..> pressure=<..> discovery=<..> delivery=<..>
coach: <n>
focus: 1) <axis: concrete gap> 2) <..> 3) <..>
```

## Worked example

Angle-bracket text stands for content from the scenario or the round; no line below is spoken as
written.

Input:
> Negotiation practice, new job, medium.

1. `pick --family new-job` returns `nj-lowball-offer` with active facts `finance` and `bonus`. Setup,
   then the brief: `<role>` at `<company>`, offer `<opening>`, current pay and market range, the aim.
2. The counterpart opens with the offer and the parity tactic. The candidate asks how the number was
   decided: a calibrated question that meets the `finance` trigger at medium trust, so the
   counterpart reveals, in their own words, that there is room with a justification.
3. The candidate counters with a precise figure and holds through silence; the counterpart moves one
   step at a time. A question about one-off items unlocks the bonus. The deal closes at a step below
   the limit; the counterpart sums up the terms.
4. The report shows the outcome against the hidden range, both facts found, the radar, replays, and
   the cards for the two weakest techniques.

## Reference files

- `references/scenarios.md`: ten original scenarios (five new-job, five at-work) with hidden briefs.
- `references/techniques.md`: the seven technique cards, in this skill's own words.
- `references/rubric.md`: anchors, rating rules, counterpart behaviour, debrief rules.
- `scripts/report.py`: `pick`, `score`, `check`, `build`, `selftest`.
- `references/session-schema.md`: the session.json the script reads.
- `references/report-template.html`: the report, with manual-fallback notes and the radar table.
- `evals.md`: pass/fail checks for the grader.
- `memory.md`: points at the local lessons log.

## When NOT to use this skill

- A technical interview or panel. Use the diegourban:interview-panel skill instead.
- A coding round. Use the diegourban:coding-round skill instead.
