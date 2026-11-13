---
name: article-review-panel
version: "1.0"
description: Reviews a technical article, blog or LinkedIn post through three independent expert lenses (domain expert, editor, statistician) and writes one markdown file per lens flagging what is good, what is wrong and what needs more explanation, verifying every number against the raw data next to the draft. Use when the user says "review my post", "act like an experienced JVM engineer and review this", "review this article as an editor", "check the statistics in this post", or "is this post ready to publish". Do NOT use to review code or a pull request, use diegourban:gh-pr-review, diegourban:branch-review or /code-review instead. Do NOT use to fact-check a claim about how a codebase works, use the diegourban:fact-checker skill instead. Do NOT use to write the post from scratch, have a direct conversation instead.
argument-hint: "<path-to-draft.md> [--lens domain|editorial|statistics|all] [--domain <field>]"
---

# article-review-panel

**Version:** 1.0

Produces up to three review files next to a draft technical post, each written
by a different expert persona: a **domain expert** (accuracy of the technical
claims), an **editor** (structure, clarity, audience, platform fit) and a
**statistician** (whether the data support the conclusions). Each file uses the
same Good / Wrong / Needs more explanation shape so the author can act on it.
The source of truth is the raw data, scripts and notes in the draft's folder,
never the draft's own summary of them.

## Critical rules (read first)

1. **Read the whole folder before writing a word.** The draft, its notes,
   first-comment drafts, sibling posts, benchmark scripts and raw result files.
   A review that only reads the draft cannot catch a draft that misquotes its data.
2. **Verify every number the draft states.** Recompute it from the raw data or
   mark it unverified. Quote the file and value: `results_gc.json: 173 → 166 MB`.
3. **"Wrong" means wrong, not a style preference.** A claim with no evidence in
   the folder, a number that contradicts the data, a conclusion the analysis does
   not support, or a sentence the platform will render broken. Taste goes under
   "Needs more explanation".
4. **Every "Wrong" item carries a concrete fix**: replacement wording, the
   command that would test the claim, or the cut.
5. **Each lens stays in its lane.** Cross-reference the other files ("technical
   accuracy is in `REVIEW-…-JVM.md`") instead of repeating their findings.
6. **Statistics lens: analyse, don't eyeball.** Run `scripts/paired_stats.py` on
   the raw data. Never conclude "noise" or "no effect" without a CI and a
   minimum-detectable-effect figure.
7. **Respect the length budget.** Count the draft's characters against the
   platform limit (LinkedIn: 3,000) and say what each addition must cost.
8. **Flag confidentiality.** Internal names, ticket IDs, hosts, customer or
   production figures: say they need Comms/Legal sign-off. Never put restricted
   data (member, claims, health, credentials) into a review or a search.

## Read-first table

| Source | Path | What to extract |
|---|---|---|
| The draft | the file the user names | Every factual claim, every number, every command, the hook (first ~210 chars), the CTA, character count |
| Author notes | `*.md` siblings (data notes, first comment, sibling posts) | The author's own caveats and corrections the draft dropped; repeated text between sibling posts |
| Benchmark scripts | `*.py`, `*.sh`, Dockerfiles in the folder | Run order (randomised? blocked?), what each metric really measures and when it is sampled |
| Raw results | `*.json`, `*.csv`, `*.log` | The numbers to recompute; block size for pairing |
| Domain lens guide | `references/domain-lens.md` | The domain checklist; the JVM section is the worked domain |
| Editorial lens guide | `references/editorial-lens.md` | Platform rules (LinkedIn markdown, fold, limit) and the structure checklist |
| Statistics lens guide | `references/statistics-lens.md` | The analysis recipe and the standard methodological flags |
| Past lessons | `~/.claude/skill-memory/article-review-panel.md` (create it if missing) | Feedback from earlier runs; apply it before drafting |

## Workflow

### Phase 1. Inventory

List the folder. Read the draft and every note, script and result file. Count
the draft's characters. Build a claim list: each number and each factual
assertion, with its line.

### Phase 2. Pick lenses

Default to all three. Run only the lens the user names ("act like a
statistician"). For the domain lens, take the field from the user ("JVM",
"Kubernetes", "Postgres") or infer it from the draft and say which you chose.

### Phase 3. Verify

Recompute each claim from the raw data. For benchmarks, run:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/paired_stats.py --file <results.json> --list
python3 ${CLAUDE_SKILL_DIR}/scripts/paired_stats.py --file <results.json> \
  --block-size <variants per round> --pair <A>:<B> [--pair ...] --metrics <m1,m2>
```

Grep the folder for evidence of every qualitative claim ("won't start",
"silently ignored"). No evidence means "Wrong: untested", with the test command.

### Phase 4. Write one file per lens

Write to the draft's folder, named `REVIEW-<DRAFT-STEM>-<LENS>.md` with LENS in
`JVM`/`<DOMAIN>`, `EDITORIAL`, `STATISTICS`. Follow the output format below and
the lens guide in `references/`.

### Phase 5. Grade and report

Run `evals.md` via a grader subagent with a clean context (give it only
`evals.md`, the draft and the review files). Fix every failure and re-grade.
Then report to the user: one line per lens with the top "Wrong" item, and the
paths. Add any new lesson the user gives to `~/.claude/skill-memory/article-review-panel.md` (newest first; create it if missing).

## Output format

```markdown
# Review of <draft file>: <lens name>

Reviewer view: <persona>. <What was checked against what.>

## Verdict

<2–4 sentences: publishable or not, the strongest thing, the must-fix count.>

## Good

- **<Bold claim>.** <Evidence, with file and number.>

## Wrong: <must fix before publishing | the conclusions don't follow from the data>

### 1. <One-line statement of the defect>

<What the draft says, what the data say, why it matters.>

Suggested fix: <wording, command, or cut>.

## Needs more explanation

### N. <Topic>

<What is missing and a suggested line.>

## Smaller points

- **<Label>:** <one or two sentences>.
```

The statistics file adds a **How the analysis was done** section after the
header, and a **Recommended re-runs** list at the end.

## Worked example

Input:
> act like an experienced JVM engineer and review POST-1-DEFAULT-CDS-EN.md in
> ~/aot-exploration/linkedin-cds, then an editor, then a statistician

Steps Claude takes:

1. Reads the post, `DADOS-POST.md`, the first-comment draft, post 2,
   `bench*.py` and `results*.json`. Counts 2,623 of 3,000 characters.
2. Domain lens: confirms ZGC maps `classes_nocoops.jsa`; finds no file mentions
   `AOTCache`, so the "JVM won't even start" claim is flagged Wrong with a test command.
3. Editorial lens: the 87-character hook fits above the fold; four backticked
   commands will render literally on LinkedIn (Wrong).
4. Statistics lens: sees `random.shuffle(order)` inside the round loop, so runs
   `paired_stats.py --block-size 12`. The pooled shift is −2.1% [−3.2%, −1.5%],
   so "that's noise" is Wrong. The "+2%" came from comparing unpaired medians.
5. Writes three `REVIEW-POST-1-*.md` files, grades them with `evals.md`, reports.

Output (statistics file, excerpt):

```markdown
### 1. "Startup time: −4% to +2%. That's noise." is not what the data say

| Setup | Paired shift | 95% CI | Faster with CDS | Exact p |
|---|---|---|---|---|
| Serial | −69 ms | [−104, −49] | **10/10** | **0.002** |
| **Pooled, 50 pairs** | **−2.1%** | **[−3.2%, −1.5%]** | **39/50** | n/a |

The correct conclusion is "a real but small effect: about 2%, or 20–70 ms",
not "noise".
```

The complete three-file output of this run is summarised in `references/examples.md`.

## Reference files

- `references/domain-lens.md`: domain-expert checklist; JVM/CDS/AOT worked domain.
- `references/editorial-lens.md`: editor checklist and LinkedIn platform rules.
- `references/statistics-lens.md`: analysis recipe and standard methodological flags.
- `references/examples.md`: the CDS-post run, finding by finding.
- `evals.md`: pass/fail checks. Run via a clean-context grader before delivering.
- `~/.claude/skill-memory/article-review-panel.md`: lessons log, newest first, private to this machine (see `memory.md`). Read before drafting.

## Scripts

- `scripts/paired_stats.py`: stdlib-only paired A/B analysis (exact Wilcoxon,
  sign-flip, Hodges-Lehmann, bootstrap CI, MDE, pooled shift, drift and order
  checks). `--list` shows variants and metrics; `--self-test` runs 8 checks.

## When NOT to use this skill

- Reviewing code, a branch or a PR. Use diegourban:gh-pr-review, diegourban:branch-review or /code-review.
- Checking how a codebase really behaves. Use diegourban:fact-checker.
- Writing or rewriting the post itself. Have a direct conversation; this skill only reviews.
- A deck or slides. Review the content with this skill only if the user asks; build with create-slide-deck.
