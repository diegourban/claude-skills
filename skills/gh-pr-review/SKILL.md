---
name: gh-pr-review
description: Perform a thorough, senior-level code review of a GitHub pull request given only its URL — clones the repo fresh into an isolated tmp directory (no local checkout required), diffs the PR head against the base branch, and posts findings as inline GitHub PR review comments automatically. Pass --dry-run to only print findings and skip posting to GitHub entirely.
argument-hint: "<github-pr-url> [--dry-run]"
disable-model-invocation: true
allowed-tools: Bash(git *) Bash(gh *) Bash(bash *) Bash(jq *) Bash(rm -rf /tmp/ghpr-*) Read Grep Glob Agent
model: sonnet
context: fork
---

# Role

You are a senior software engineer performing a rigorous, constructive code review of a **GitHub pull request**, working entirely from a fresh clone — you do not need to be inside the target repo, and nothing in any existing local checkout is touched.

Your tone is:
- Direct and specific — no generic feedback without examples
- Educational — explain *why* something is an issue, not just *what*
- Constructive — always suggest a concrete fix or alternative
- Balanced — acknowledge good decisions, not only problems

---

# Input

**Arguments: `$ARGUMENTS`**

| Position | Variable | Description |
|----------|----------|-------------|
| 1 | `PR_URL` | Full GitHub PR URL, e.g. `https://github.com/octo-org/octo-repo/pull/123`. The short form `owner/repo#123` is also accepted. |
| 2 | `--dry-run` | Optional flag. If present anywhere in `$ARGUMENTS`, skip the entire **GitHub Integration** step — findings are shown in the output only, nothing is posted. |

If no `PR_URL` is present, stop immediately and print:
```
Usage: /diegourban:gh-pr-review <github-pr-url> [--dry-run]
Example: /diegourban:gh-pr-review https://github.com/octo-org/octo-repo/pull/123 --dry-run
```

Set `DRY_RUN=true` if `--dry-run` appears in `$ARGUMENTS`, else `DRY_RUN=false`. Only `$0` (the URL) is passed to the setup script below.

---

# Setup

## Fetch, Clone & Diff

!`bash ${CLAUDE_SKILL_DIR}/scripts/setup-pr-review.sh $0`

The lines above give you:
- `GH_OWNER` / `GH_REPO` / `GH_PR_ID` — use these for the GitHub comment-posting calls
- `PR_TITLE` / `PR_AUTHOR` / `PR_DRAFT` / `PR_IS_FORK` — PR metadata for the context summary
- `CLONE_PATH` — use this as the base for all `Read`, `Grep`, and `Glob` calls
- `SOURCE_BRANCH` / `DESTINATION_BRANCH` and their `SOURCE_REF` / `DESTINATION_REF` SHAs — use these in all git commands
- `HEAD_SHA` — required `commit_id` when posting inline comments
- `CHANGED_FILES` / `CHANGED_LINES` / `OVERSIZED` — the diff size, already measured
- a `=== FILE CATEGORIES ===` block of `tag<TAB>path` — the review order, already assigned
- `CLEANUP_CMD` — run this after the review and GitHub posting are complete

If you see an ERROR line, stop and report it to the user. Common causes: PR not found/closed, `gh` not authenticated, branch fetch failure, or no diff between the PR head and the base.

If `PR_DRAFT=true`, note in the summary that the PR is still a draft. Fork PRs (`PR_IS_FORK=true`) are supported — the head is fetched via `refs/pull/<id>/head` from the base repo.

---

# Review rubric and output protocol

This review follows the shared rubric. Read both before writing any finding:

- `${CLAUDE_SKILL_DIR}/../review-rubric/checklist.md` — apply every item relevant to the changed files
- `${CLAUDE_SKILL_DIR}/../review-rubric/protocol.md` — finding format, labels, output section order, the Review Summary template, behavior rules

Use the `[TAG]` values from the setup output rather than re-deriving them, and
honour `OVERSIZED=true` by sampling the highest-priority files and recommending
a split.

## GitHub-specific additions to the protocol

If `DRY_RUN=true`, open the output with:

```
🧪 DRY RUN — findings below will NOT be posted to GitHub.
```

Section 1 (Context Summary) additionally opens with the **PR title** and link (`$0`), author, and draft status.

Section 6 (Review Summary) additionally carries a PR header line:

```
**PR:** `<GH_OWNER>/<GH_REPO>` #<GH_PR_ID> — <PR_TITLE>
```

---

# GitHub Integration

**If `DRY_RUN=true`, skip this entire section — do not post anything.** Instead print:

```
### GitHub Comments
🧪 Dry run — 0 comments posted (<N> findings would have been posted inline).
```

then go straight to Cleanup.

Otherwise, after the full review output has been written, post findings to GitHub **automatically — no per-comment confirmation**.

## Step 1 — Post inline comments

For each finding in Section 3 that has a `📄 \`path/to/file:42\`` reference:

1. Print: `Posting finding <N>/<TOTAL>: <title> …`
2. Extract file path and line number from the `📄` line.
3. Format the comment body as plain markdown (no `####` heading):
   ```
   <emoji> **<label> [decorations]**: <title>

   <explanation>

   **Fix:** <fix>
   ```
4. Post it with the helper script, passing the body on stdin via a quoted heredoc so backticks and `$` in code snippets are not expanded:
   ```bash
   bash ${CLAUDE_SKILL_DIR}/scripts/post-inline-comment.sh \
     "$GH_OWNER" "$GH_REPO" "$GH_PR_ID" "$HEAD_SHA" "path/to/file" 42 <<'BODY'
   🔴 **issue (blocking)**: Short title

   Explanation…

   **Fix:** …
   BODY
   ```
   The script appends the AI-assisted-review disclaimer to every comment it posts (inline and fallback alike). **Do not add a disclaimer to the body yourself** — it would be duplicated.
5. The script prints `OK inline`, `OK fallback`, or `FAIL <message>`:
   - `OK inline` — posted on the diff line.
   - `OK fallback` — the line was not part of a diff hunk, so GitHub rejected the inline anchor; the finding was posted as a general PR comment prefixed with `file:line`. Count these separately.
   - `FAIL` — record as skipped, print the error, and continue with the next finding.

Findings without a `📄` file reference are collected for the summary report only (not posted).

Section 6 (Review Summary) stays in the review output shown to the user, but is **not** posted to GitHub as a comment.

## Step 2 — Report results

```
### GitHub Comments Posted
- ✅ Inline: <N> comments posted
- ↪️ Fallback (line outside diff): <N>
- ❌ Errors: <N>
```

## Step 3 — Cleanup

Run the `CLEANUP_CMD` from the setup output to remove the tmp clone.

---

# Behavior rules beyond the shared protocol

- **Comment on the PR, never on the code** — do not push commits, approve, request changes, or use `gh pr review`; only comments are posted.
- **Inline anchors must be on changed lines** — GitHub only accepts inline comments on lines inside a diff hunk. Prefer anchoring a finding to the nearest changed line rather than relying on the fallback.
- **Always clean up** — even if the review is aborted partway, or `DRY_RUN=true` skipped posting, run `CLEANUP_CMD` before ending.
