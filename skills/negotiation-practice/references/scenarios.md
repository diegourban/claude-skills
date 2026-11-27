# Scenario bank

Ten original scenarios, five per family, with fictional companies and people. `scripts/report.py`
reads each `## <id>:` heading and the JSON block under it, so keep that shape.

Per scenario:

- **Your brief** is read to the candidate at setup: what they would really know going in.
- **Counterpart** is who Claude plays: name, role, style, what they want.
- **Hidden brief** is never shown before the debrief.
- The JSON block holds what the script checks:
  - `scale`: what the outcome is measured in; `direction` is `up` when larger is better for the
    candidate.
  - `opening`, `target`, `limit`: the counterpart's first position, what they hope to close at, and
    the furthest they can go.
  - `steps`: the positions the counterpart may move through, in order, one at a time and only when
    trust allows. The last step is the limit.
  - `facts`: hidden information with the kind of move that unlocks each (`trigger`). `pick` activates
    two per session.
  - `tactics`: pressure moves the counterpart uses; `pick` orders them per session.
  - `first`: who speaks first.

Difficulty changes the counterpart, not the numbers: `easy` gains trust quickly and uses one tactic;
`medium` is as written; `hard` needs two good moves per step and uses every tactic.

## nj-expectations-first: The recruiter asks first
Family: new-job

**Your brief:** You are in the final stage for a senior backend role at Northwind Freight, a logistics
scale-up. The recruiter has called to "align on expectations" before the offer. You earn €74,000
now. Your research says the role pays €78,000 to €88,000 in this market. You have no other offer.

**Counterpart:** Maya Okafor, talent partner. Accommodating, friendly, under pressure to close. She
wants you to name a number first.

**Hidden brief:** The approved band tops out at €86,000, well above her opening. The hiring manager wants a signed offer
this week because a senior engineer just handed in their notice. An equity grant can be added if the
salary is at the top of the band.

```json
{"id": "nj-expectations-first", "family": "new-job", "title": "The recruiter asks first",
 "scale": {"kind": "money", "unit": "EUR per year", "direction": "up"},
 "opening": 76000, "target": 80000, "limit": 86000, "steps": [76000, 79000, 81500, 83500, 85000, 86000],
 "facts": [
   {"id": "band", "fact": "the approved band tops out well above the figure she opened with", "trigger": "a calibrated question about how the range was set"},
   {"id": "urgency", "fact": "a senior engineer just resigned, so the manager wants to sign this week", "trigger": "a label on her time pressure"},
   {"id": "equity", "fact": "an equity grant is possible at the top of the band", "trigger": "a question about what else is in the package"}],
 "tactics": ["asks for your number first", "says the budget is tight this year", "mentions other candidates"],
 "first": "counterpart"}
```

## nj-lowball-offer: A low first offer
Family: new-job

**Your brief:** Aurora Health Tech has offered you a staff engineer role at €72,000. You earn
€76,000 now, and comparable offers you have heard of are €82,000 to €86,000. The hiring manager has
called to talk it through. You like the team and want the job.

**Counterpart:** Tom Lindqvist, engineering director. Analytical, calm, data-driven. He will defend
the number with "internal parity".

**Hidden brief:** The last candidate declined over pay. Finance pre-approved up to €84,000 if Tom
writes a justification. A €5,000 signing bonus pool is unused this quarter.

```json
{"id": "nj-lowball-offer", "family": "new-job", "title": "A low first offer",
 "scale": {"kind": "money", "unit": "EUR per year", "direction": "up"},
 "opening": 72000, "target": 76000, "limit": 84000, "steps": [72000, 75000, 78000, 80500, 82500, 84000],
 "facts": [
   {"id": "declined", "fact": "the previous candidate declined over pay", "trigger": "a label on his worry about losing another candidate"},
   {"id": "finance", "fact": "finance pre-approved a higher figure if he writes a justification", "trigger": "a calibrated question about how the number could move"},
   {"id": "bonus", "fact": "an unused 5,000 signing bonus pool", "trigger": "a question about one-off or non-salary items"}],
 "tactics": ["cites internal parity", "says it is already above the midpoint", "suggests revisiting at the six-month review"],
 "first": "counterpart"}
```

## nj-competing-offer: Two offers on the table
Family: new-job

**Your brief:** Cobalt Payments offered you €82,000 for a senior engineer role. You also hold an
offer of €88,000 from another company with a worse commute. You prefer Cobalt. The recruiter has
asked for your decision.

**Counterpart:** Sara Novak, senior recruiter. Assertive, quick, sees competing offers as a bluff
until proven.

**Hidden brief:** Cobalt has lost two candidates to the same competitor this year. The team can add
a €2,000 learning budget and a four-day-week trial. Sara's quarterly hiring target is short by one.

```json
{"id": "nj-competing-offer", "family": "new-job", "title": "Two offers on the table",
 "scale": {"kind": "money", "unit": "EUR per year", "direction": "up"},
 "opening": 82000, "target": 85000, "limit": 90000, "steps": [82000, 84000, 86000, 87500, 89000, 90000],
 "facts": [
   {"id": "lost-two", "fact": "two candidates were lost to the same competitor this year", "trigger": "a label on how she sees the competitor"},
   {"id": "extras", "fact": "a 2,000 learning budget and a four-day-week trial are available", "trigger": "a question about what else matters to the team"},
   {"id": "quota", "fact": "her quarterly hiring target is short by one", "trigger": "a calibrated question about what closing this means for her"}],
 "tactics": ["asks to see the other offer in writing", "sets a decision deadline of tomorrow", "says the other company has a worse culture"],
 "first": "counterpart"}
```

## nj-fixed-budget: The salary is fixed
Family: new-job

**Your brief:** Helios Energy offered €80,000 for a lead engineer role and says the salary band is
fixed by a collective agreement. Your target was €85,000 total first-year value. You want the job.

**Counterpart:** Daniel Ferreira, hiring manager. Accommodating but firm on salary, open on almost
everything else if asked well.

**Hidden brief:** The salary truly cannot move. A €6,000 signing bonus is available, as is a senior
title with a €1,500 allowance. The steps are 80,000 (salary only), 81,500 (the title allowance),
86,000 (the signing bonus) and 87,500 (both); a step needs its item unlocked or proposed by the
candidate. Daniel cares most about a start date within six weeks.

```json
{"id": "nj-fixed-budget", "family": "new-job", "title": "The salary is fixed",
 "scale": {"kind": "money", "unit": "EUR first-year value", "direction": "up"},
 "opening": 80000, "target": 81500, "limit": 87500, "steps": [80000, 81500, 86000, 87500],
 "facts": [
   {"id": "signing", "fact": "a 6,000 signing bonus is available", "trigger": "a no-oriented question about one-off payments"},
   {"id": "title", "fact": "a senior title with a 1,500 allowance is possible", "trigger": "a question about how the role is levelled"},
   {"id": "start", "fact": "he needs a start date within six weeks", "trigger": "a label on his timing concerns"}],
 "tactics": ["repeats that the band is fixed", "says everyone joins on the same terms", "asks for a quick yes"],
 "first": "counterpart"}
```

## nj-exploding-offer: The offer expires Friday
Family: new-job

**Your brief:** Lumen Retail offered you €78,000, which you are happy with, but it expires on Friday,
two working days from now. You are a week away from a final round elsewhere. You want more time, not
more money. The outcome is measured in working days of extension.

**Counterpart:** Ines Brandt, recruiter. Assertive, process-driven, says the deadline is policy.

**Hidden brief:** The deadline comes from Ines's own pipeline report, not from the manager. The
manager would rather wait than restart the search. The other finalist is weaker.

```json
{"id": "nj-exploding-offer", "family": "new-job", "title": "The offer expires Friday",
 "scale": {"kind": "days", "unit": "working days of extension", "direction": "up"},
 "opening": 0, "target": 4, "limit": 10, "steps": [0, 2, 4, 7, 10],
 "facts": [
   {"id": "own-report", "fact": "the deadline comes from her own pipeline report", "trigger": "a calibrated question about what drives the Friday date"},
   {"id": "manager-waits", "fact": "the manager would rather wait than restart the search", "trigger": "a question about how the manager sees the timing"},
   {"id": "weaker", "fact": "the other finalist is weaker", "trigger": "a label on her worry about losing the slot"}],
 "tactics": ["says the deadline is company policy", "mentions another finalist", "asks whether you are serious about the role"],
 "first": "counterpart"}
```

## aw-raise: The annual review
Family: at-work

**Your brief:** At your annual review at a mid-size SaaS company, your manager offers a 3% raise. You
have led two major launches this year and believe a promotion-level raise is due. A recruiter
contacted you last month, and your manager heard about it. The outcome is
measured in percent raise.

**Counterpart:** Ravi Menon, your engineering manager. Analytical, supportive, tied to HR's process.

**Hidden brief:** There is one promotion slot this cycle. Ravi knows a recruiter approached you and
worries about losing you. HR needs a written case by the end of the month.

```json
{"id": "aw-raise", "family": "at-work", "title": "The annual review",
 "scale": {"kind": "percent", "unit": "percent raise", "direction": "up"},
 "opening": 3, "target": 5, "limit": 9, "steps": [3, 4, 5, 6.5, 8, 9],
 "facts": [
   {"id": "slot", "fact": "there is one promotion slot this cycle", "trigger": "a calibrated question about what a promotion would take"},
   {"id": "retention", "fact": "he worries about losing you to a recruiter", "trigger": "a label on his concern about the team"},
   {"id": "hr-case", "fact": "HR needs a written case by the end of the month", "trigger": "a question about how he can make the case"}],
 "tactics": ["says raises are fixed by a company formula", "points to budget pressure", "suggests waiting until next year"],
 "first": "counterpart"}
```

## aw-deadline: The two-week deadline
Family: at-work

**Your brief:** A product lead wants a new billing feature shipped in two weeks. Your honest estimate
is five weeks for the whole feature. The outcome is measured in days until the deadline.

**Counterpart:** Julia Kowalski, product lead. Assertive and stressed; she has promised the date.

**Hidden brief:** The real driver is a customer demo that only needs one slice of the feature. Sales
promised the date without asking product. A phased release is acceptable to the customer.

```json
{"id": "aw-deadline", "family": "at-work", "title": "The two-week deadline",
 "scale": {"kind": "days", "unit": "days until the deadline", "direction": "up"},
 "opening": 14, "target": 21, "limit": 35, "steps": [14, 18, 21, 28, 35],
 "facts": [
   {"id": "demo", "fact": "the real driver is a customer demo that needs one slice", "trigger": "a calibrated question about what has to be true on the date"},
   {"id": "sales", "fact": "sales promised the date without asking product", "trigger": "a label on the position she has been put in"},
   {"id": "phased", "fact": "a phased release is acceptable to the customer", "trigger": "a no-oriented question about shipping in parts"}],
 "tactics": ["says the date is already committed", "asks the team to work weekends", "escalates to your manager"],
 "first": "counterpart"}
```

## aw-extra-scope: One more project
Family: at-work

**Your brief:** Your manager asks you to take on a database migration on top of your current three
projects. You are already at capacity. The outcome is measured in projects taken off your plate
(dropped, paused or handed to someone else).

**Counterpart:** Omar Haddad, your manager. Accommodating, overloaded, avoids conflict.

**Hidden brief:** One of your current projects matters less than he has said. He is also overloaded
by the migration request from above. There is contractor budget he has not mentioned.

```json
{"id": "aw-extra-scope", "family": "at-work", "title": "One more project",
 "scale": {"kind": "count", "unit": "projects taken off your plate", "direction": "up"},
 "opening": 0, "target": 1, "limit": 2, "steps": [0, 1, 2],
 "facts": [
   {"id": "low-priority", "fact": "one current project matters less than he said", "trigger": "a calibrated question about how the projects rank"},
   {"id": "overloaded", "fact": "he is overloaded by the request from above too", "trigger": "a label on the pressure he is under"},
   {"id": "contractor", "fact": "there is unspent contractor budget", "trigger": "a question about what resources exist"}],
 "tactics": ["says everyone is stretched", "appeals to your growth", "asks you to just try for a month"],
 "first": "counterpart"}
```

## aw-skip-review: Ship without the review
Family: at-work

**Your brief:** A vice president wants to skip the five-day security review to ship a payment change
this quarter. You own the service. The outcome is measured in days of review kept.

**Counterpart:** Lena Vogel, vice president of product. Assertive, senior, outcome-focused.

**Hidden brief:** Lena's bonus depends on the launch quarter. A review of only the payment flow (three
days) is acceptable to compliance. Compliance escalated a skipped review to the board last year.

```json
{"id": "aw-skip-review", "family": "at-work", "title": "Ship without the review",
 "scale": {"kind": "days", "unit": "days of review kept", "direction": "up"},
 "opening": 0, "target": 2, "limit": 5, "steps": [0, 1, 2, 3, 5],
 "facts": [
   {"id": "quarter", "fact": "her bonus depends on the launch quarter", "trigger": "a label on what this quarter means for her"},
   {"id": "partial", "fact": "a three-day review of only the payment flow is acceptable", "trigger": "a calibrated question about what a smaller review would look like"},
   {"id": "board", "fact": "compliance escalated a skipped review to the board last year", "trigger": "a no-oriented question about the risk of skipping"}],
 "tactics": ["pulls rank", "says the risk is small", "asks who will take the blame for missing the quarter"],
 "first": "counterpart"}
```

## aw-ownership: Who owns the service
Family: at-work

**Your brief:** A peer team lead wants to take over a service your team built and runs. You want to
keep it until your team finishes its current roadmap, about four months away, and your team has a
painful migration coming up. The outcome is measured in months before any
handover.

**Counterpart:** Marco Bianchi, platform team lead. Analytical, polite, persistent.

**Hidden brief:** Marco's team is measured on platform consolidation this year. He fears inheriting
the service's on-call load. His team has spare capacity this quarter that could run your migration.

```json
{"id": "aw-ownership", "family": "at-work", "title": "Who owns the service",
 "scale": {"kind": "months", "unit": "months before handover", "direction": "up"},
 "opening": 0, "target": 3, "limit": 6, "steps": [0, 2, 3, 4, 6],
 "facts": [
   {"id": "goal", "fact": "his team is measured on platform consolidation", "trigger": "a calibrated question about what success looks like for his team"},
   {"id": "on-call", "fact": "he fears inheriting the on-call load", "trigger": "a label on his hesitation about the handover details"},
   {"id": "trade", "fact": "his team has spare capacity this quarter to run your migration", "trigger": "a question about what each team needs from the other"}],
 "tactics": ["cites a director's mandate", "says consolidation is inevitable", "proposes an immediate handover"],
 "first": "counterpart"}
```
