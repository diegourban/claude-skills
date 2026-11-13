# Review protocol

The parts of a code review that are the same whatever the host: how a finding is
written, how findings are labelled, what sections the output has, and the rules
that hold for every review.

Previously this text lived, verbatim, in `gh-pr-review` and
`branch-review`. Change it here and both change together.

---

## File discovery and categorization

`review-rubric/scripts/emit-diff.sh` — which the calling skill's setup script
runs — emits a `=== FILE CATEGORIES ===` block of `tag<TAB>path`. Use those tags;
do not re-derive them by eye.

| Tag | What it is | Priority |
|-----|-----------|---------|
| `[SRC]` | Production source files | 1 — review first |
| `[API]` | API contracts: OpenAPI, proto, GraphQL schema, public DTOs | 2 |
| `[DB]` | Database migrations and schema files | 3 |
| `[CFG]` | Configuration files, Dockerfiles, CI scripts | 4 |
| `[TST]` | Test files | 5 |
| `[DOC]` | Documentation only | 6 — note but skip detailed review |
| `[GEN]` | Generated files, lock files, vendor directories, compiled outputs | 7 — skip review entirely |
| `[BIN]` | Binary files | 8 — note presence only |

The setup output also carries `CHANGED_LINES` and `OVERSIZED`. When
`OVERSIZED=true`, say so explicitly, focus on the highest-priority files and
representative samples, and recommend the author split the PR.

---

## Finding format

Findings follow the [Conventional Comments](https://conventionalcomments.org/) spec:

```
<emoji> <label> [decorations]: <subject>
```

For every finding:

```
#### <emoji> <label> [decorations]: Short title
📄 `path/to/file:42`

Clear explanation of the problem or observation and why it matters.

**Fix:** Concrete fix or alternative. Include a code snippet when it adds clarity.
```

The closing field is label-dependent:
- `issue`, `suggestion`, `nitpick` → **Fix:**
- `question` → **Question:**
- `thought` → **Suggestion:**

### Labels

| Label | Decorations | Meaning |
|-------|-------------|---------|
| 🔴 `issue` | `(blocking)` | Must fix before merge. Correctness, security, or data integrity risk. |
| 🟠 `issue` | `(non-blocking)` | Should fix. Significant design, performance, or maintainability concern. |
| 🟡 `suggestion` | `(non-blocking)` | Nice to fix. Code smell, readability, or non-critical improvement. |
| 🔵 `nitpick` | `(non-blocking)` | Optional. Style, naming, or trivial polish. |
| ❓ `question` | `(blocking)` or `(non-blocking)` | Intent is unclear; ask the author. |
| 💭 `thought` | `(non-blocking)` | Architectural observation worth discussing; not a problem in itself. |

---

## Output structure

Produce these sections in order. A host-specific skill may add fields to
section 1 (PR number, author, draft status) and may prepend a dry-run banner.

### 1. Context Summary
1. **Branch purpose** — 2–3 sentences inferred from branch name, commits, and diff shape.
2. **Affected domains**
3. **File breakdown** — each file with its `[TAG]` and a one-line description of what changed.

### 2. High-Level Assessment
One paragraph: overall verdict, dominant concerns, and confidence level.

### 3. Detailed Findings
Grouped by label: `issue (blocking)` → `issue (non-blocking)` → `question (blocking)` → `question (non-blocking)` → `suggestion` → `thought` → `nitpick`.

### 4. API & Contract Notes *(if applicable)*
Call out changes to public APIs, database schemas, or message formats. Note backward compatibility risks.

### 5. Testing & Verification Plan
Recommend concrete tests the author should add or run.

### 6. Review Summary

```
## 📋 Review Summary

**Branch:** `<source>` → `<destination>`

### Verdict
🔴 CHANGES REQUIRED — blocking items must be resolved before merge.
🟠 REVISIONS SUGGESTED — no blockers, but non-blocking issues should be resolved.
🟡 APPROVED WITH COMMENTS — suggestions and nitpicks only. Author's discretion.
✅ APPROVED — Ready to merge.
❓ ON HOLD — Blocking questions must be answered before a verdict.

### Finding Counts

| Label | Count |
|-------|-------|
| 🔴 `issue (blocking)` | |
| 🟠 `issue (non-blocking)` | |
| 🟡 `suggestion` | |
| 🔵 `nitpick` | |
| ❓ `question (blocking)` | |
| ❓ `question (non-blocking)` | |
| 💭 `thought` | |

### Version Bump
💥 MAJOR | ✨ MINOR | 🔧 PATCH | ⬜ N/A

### Estimated Fix Effort
< 30 min | ~2 hours | ~1 day | ~3 days | > 1 week

### Top Issues to Address
1. <Title> — `file:line`

### What Went Well
- ...

### Suggested Next Steps
- ...
```

---

## Behavior rules

- **One finding per issue** — group repeated concerns and reference all locations.
- **Code snippets over prose** — show the fix; don't just describe it.
- **Never assume intent** — flag unclear blocks as questions.
- **Do not rewrite the PR** — targeted guidance only.
- **Respect existing patterns** — flag deviations only when they introduce real risk.
- **Language idioms** — apply the language's established conventions.
