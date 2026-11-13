---
name: fact-checker
version: "2.0"
description: Answers a question about how a codebase or a set of repos currently works (or checks a draft spec, contract change or reviewer comment), and verifies every factual claim against freshly fetched origin blobs before showing it, returning a claim ledger marking each claim CONFIRMED, REFUTED or UNVERIFIED with a repo@sha and file:line. Use when the user says "what roles does this endpoint allow", "is this how we actually do it", "check origin/main, the worktree is stale", "fact-check this reviewer comment", "are you sure that schema exists", or "verify it before you tell me". Never cites the local working tree as evidence. Do NOT use to review a whole pull request or branch, use diegourban:gh-pr-review or diegourban:branch-review instead. Do NOT use to debug production behaviour from traces and metrics, use an observability tool instead.
argument-hint: "<question-or-claim> [--repos a,b] [--check-only] [--deep]"
allowed-tools: Bash(git *) Bash(gh *) Bash(jq *) Bash(yq *) Bash(rg *) Bash(curl *) Bash(bash *) Read Grep Glob
model: sonnet
---

# fact-checker

**Version:** 2.0

Answers a question about what a codebase currently does, then proves the answer before
showing it. Ground truth is the remote default branch at a pinned SHA, never the local
working tree, which is routinely stale, dirty, and polluted with build output.
Owns one question, answered and evidenced.

## Critical rules (read first)

1. **Pin before reading. Never cite the working tree.** Every read goes through
   `scripts/shipped.sh cat|grep|ops`. A claim sourced from an unpinned local file is
   a defect, not a shortcut: a plain `grep -r` also walks gitignored build output and
   can inflate precedent counts several times over.
2. **An unverified claim is never stated as fact.** Label it `UNVERIFIED` and name the
   reason. Softening the wording is not labelling it.
3. **Never present the answer before the ledger is complete.** Every claim carries
   CONFIRMED, REFUTED or UNVERIFIED. Rewrite the draft to remove REFUTED claims, then show.
4. **A convention claim needs ≥3 precedents AND its counterexamples, counted at the
   narrowest scope that contains the change.** Report the counterexamples even when they
   weaken the answer, because they are usually the finding. "We always do X" is almost never
   true; "X in 268 places, 24 exceptions, here they are" is. A repo-wide count where a
   module-scoped one was called for is confidently wrong, not approximately right.
5. **A permission missing from an allowlist is a production 403; a spare one is harmless.**
   Always diff a drafted role or scope list against the sibling operations on the same
   path prefix (`ops`), and flag omissions loudly.
6. **Resolve published artifacts from the registry, never from local caches** (`~/.m2`,
   `~/.gradle`, `node_modules`, ...). A stale cached artifact produces false verdicts.
7. **If a repo cannot be pinned, say so and mark its claims UNVERIFIED.** Never silently
   fall back to the worktree. Missing credentials for a host are the usual cause.
8. **Never put personal or regulated data in a claim, a quote or a search pattern**
   (customer records, health or financial data, credentials). Redact to the shape of the value.

## Configuration: the corpus

The skill is generic; what it knows about *your* repos comes from a corpus, read in this order:

1. `~/.config/fact-checker/` if it exists (override with `$FACT_CHECKER_CONFIG`):
   - `sources`: one `<host>/<owner>` per line, e.g. `github.com/my-org`. `shipped.sh` looks
     for clones at `$FACT_CHECKER_ROOT/<host>/<owner>/<repo>` (default root `~/Repositories`)
     in that order, then mirrors over SSH.
   - `corpus.md`: repo → host → default branch → what ground truth it holds.
   - `claim-types.md`: extra claim types and verifiers specific to these repos.
   - `roles-regex`: an ERE matching the role/permission vocabulary, used by `roles`.
2. Otherwise the project's `CLAUDE.md`, for which repos matter and where they live.
3. Otherwise only the current repository (pass `.` as the repo name).

`references/corpus.md` describes the format with a worked template. These files stay local:
they describe private infrastructure and never belong in this plugin.

## When this fires

| The ask | Claim type | How it is proven |
|---|---|---|
| "check `origin/main`, the working tree is ~24 commits behind and dirty" | repo state | `pin` every repo in scope, print `repo@sha`, read only pinned blobs |
| "what roles does this endpoint allow?" | permission allowlist | `ops` on the path prefix + `roles` vocabulary |
| "is `Money` an internal component or an external file ref?" | `$ref` target | resolve the ref in the pinned blob; report the majority style in that file |
| "fact-check this reviewer comment about row order" | behaviour | read the cited method at the pinned SHA; CONFIRM or REFUTE with `file:line` |
| "does that schema already exist, or am I adding it?" | identifier | `grep` the pinned corpus; if it exists, extend it, never duplicate |
| "does the 1.4.0 release actually contain `getOrders`?" | artifact contents | resolve from the registry with local caches bypassed |
| "is this how we do GraphQL responses?" | convention | count precedents *and* counterexamples at the narrowest scope |

Do not fire on a request to implement a change, to review a whole PR, or to read
production telemetry.

## Read-first table

| Source | Path | What to extract |
|---|---|---|
| Local corpus | `~/.config/fact-checker/corpus.md` (else project `CLAUDE.md`) | repo → host → default branch → ground truth held |
| Verifier table | `references/claim-types.md` + `~/.config/fact-checker/claim-types.md` | the exact command that proves each claim type |
| Pinned SHAs | `bash ${CLAUDE_SKILL_DIR}/scripts/shipped.sh pin <repos>` | `repo<TAB>branch<TAB>sha` for every repo in scope |
| Sibling operations | `bash ${CLAUDE_SKILL_DIR}/scripts/shipped.sh ops <repo> <sha> <spec> [filter]` | `path / METHOD / operationId / security` per OpenAPI operation |
| Already enforced by CI | the repo's lint config at the pinned SHA | rules CI already enforces; do not re-report them as findings |

## Workflow

### Phase 1. Scope and pin

Name every repo the question touches. Run `scripts/shipped.sh pin` on all of them in one
call and print the `repo@sha` line. Any repo that fails to pin is named now, not later.

### Phase 2. Draft the answer

Answer from the pinned blobs. Write it as if final, since the verification pass is what
makes it final. Do not hedge here, and do not pad with caveats that Phase 4 replaces
with evidence.

### Phase 3. Extract claims

Decompose the draft into atomic claims. A claim is anything a reader could act on: a role
list, a schema or type name, a file path, a version string, a convention, a behaviour.
Assign each a type from the verifier table. If a sentence resists being typed, it
asserts nothing, so rewrite it or cut it.

### Phase 4. Verify, the gate

Run each claim's verifier. Assign exactly one verdict:

- **CONFIRMED**: the command found it. Record `repo@sha path:line`.
- **REFUTED**: the command found the opposite. Record the contradicting evidence and
  **rewrite the draft** so the claim is gone. A REFUTED claim never survives into the answer.
- **UNVERIFIED**: no verifier could reach it, because the repo is unpinnable, credentials
  are absent, there are fewer than 3 precedents, or the behaviour needs a runtime to
  settle. Record *which*.

`--deep` adds an adversarial second pass over every CONFIRMED convention claim, hunting
only for counterexamples. Use it when the answer will be relayed to someone else as fact.

`--check-only` skips Phase 2: the user supplied the draft (a spec, a reviewer comment), so
extract and verify its claims as given.

Iterate Phases 2 to 4 until no claim is REFUTED. Then, and only then, present.

## Output format

```
**Answer.** <the verified answer, 1 to 5 sentences, no hedging. Proven, or not here at all>

**Ground truth**
api-specs@9be631e (main) · gateway@d0d1e73 (main)

| # | Claim | Verdict | Evidence |
|---|---|---|---|
| 1 | <atomic claim> | CONFIRMED | api-specs@9be631e orders/openapi.yaml:6218 |
| 2 | <atomic claim> | REFUTED | <the contradicting evidence> |

**Could not verify**
- <claim>: <why: repo unpinnable / no credentials / 2 precedents only / needs a runtime>
```

Omit the "Could not verify" block only when it is empty. Never omit the ledger.

## Worked example

Input:

> Add `GET /customers/{customerId}/invoices/{invoiceId}` returning the invoice summary.
> What roles, and what response shape?

Steps:

1. `pin api-specs gateway` → `api-specs@9be631e (main)`, `gateway@d0d1e73 (main)`.
2. Draft: roles `ADMIN, BILLING_ADMIN`; define a new `InvoiceSummary`; inline error object
   for 404; gateway query returns `InvoiceSummary`.
3. Claims: (a) the role list, (b) `InvoiceSummary` is new, (c) 404 is inline, (d) the
   gateway returns a bare type.
4. Verify:
   - (a) `ops api-specs 9be631e orders/openapi.yaml /customers/` → every sibling also allows
     `SUPPORT_AGENT`. **REFUTED**: the draft would 403 support staff.
   - (b) `grep 'InvoiceSummary' api-specs 9be631e '*.yaml'` → hit at `orders/openapi.yaml:6218`.
     **REFUTED**: it ships; extend it.
   - (c) `grep 'CustomerNotFound' api-specs 9be631e 'orders/*'` → 20 precedents. **REFUTED**:
     `$ref` the shared response.
   - (d) `grep '^union '` vs `grep '^type [A-Za-z]+Response '` in `gateway` → 268 vs 24.
     **REFUTED** as drafted: majority convention is a union with `Error`.
5. Rewrite, re-verify, present:

```
**Answer.** Allow ADMIN, BILLING_ADMIN and SUPPORT_AGENT (copied from
GET /customers/{customerId}/invoices). Extend the shipped InvoiceSummary rather than
defining a new schema, $ref the shared CustomerNotFound response for 404, and return a union
from the gateway.

**Ground truth**
api-specs@9be631e (main) · gateway@d0d1e73 (main)

| # | Claim | Verdict | Evidence |
|---|---|---|---|
| 1 | Roles match the list-invoices operation exactly | CONFIRMED | api-specs@9be631e orders/openapi.yaml → GET /customers/{customerId}/invoices |
| 2 | InvoiceSummary is already shipped | CONFIRMED | same file:6218 |
| 3 | 404 uses the shared CustomerNotFound response | CONFIRMED | same file, 20 precedents in module |
| 4 | Gateway queries return a union with Error | CONFIRMED | gateway@d0d1e73 268 unions vs 24 bare Response types |
```

## Reference files

- `references/claim-types.md`: the generic verifier command per claim type
- `references/corpus.md`: the format of the local corpus in `~/.config/fact-checker/`
- `scripts/shipped.sh`: the pinned-blob reader (`self-test` runs without network)

## When NOT to use this skill

- Reviewing a whole pull request or branch → `diegourban:gh-pr-review` or `diegourban:branch-review`
- Production behaviour from traces and metrics → an observability tool
- A question whose answer contains no factual claim (naming, preference, opinion)
