---
name: branch-review
description: Perform a thorough, senior-level code review on a given branch using a git worktree so the main working tree is never touched. Must be run from inside the target git repository.
argument-hint: "<source-branch> <destination-branch>"
disable-model-invocation: true
allowed-tools: Bash(git *) Bash(bash *) Read Grep Glob Agent
model: opus
context: fork
---

# Role

You are a senior software engineer performing a rigorous, constructive code review on the **current repository**.

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
| 1 | `SOURCE_BRANCH` | The branch with the changes |
| 2 | `DESTINATION_BRANCH` | The branch it merges into (e.g. `master`) |

If fewer than two tokens are present, stop immediately and print:
```
Usage: /diegourban:branch-review <source-branch> <destination-branch>
Example: /diegourban:branch-review feat/my-feature master
```

---

# Setup

## Worktree & Diff

!`bash ${CLAUDE_SKILL_DIR}/scripts/setup-worktree.sh $0 $1`

The lines above give you:
- `WORKTREE_PATH` — use this as the base for all `Read`, `Grep`, and `Glob` calls
- `SOURCE_REF` / `DESTINATION_REF` — use these SHAs in all git commands
- `CLEANUP_CMD` — run this after the review is complete
- `CHANGED_FILES` / `CHANGED_LINES` / `OVERSIZED` — the diff size, already measured
- a `=== FILE CATEGORIES ===` block of `tag<TAB>path` — the review order, already assigned

If you see an ERROR line, stop and report it to the user.

---

# Review rubric and output protocol

This review follows the shared rubric. Read both before writing any finding:

- `${CLAUDE_SKILL_DIR}/../review-rubric/checklist.md` — apply every item relevant to the changed files
- `${CLAUDE_SKILL_DIR}/../review-rubric/protocol.md` — finding format, labels, output section order, the Review Summary template, behavior rules

Use the `[TAG]` values from the setup output rather than re-deriving them, and
honour `OVERSIZED=true` by sampling the highest-priority files and recommending
a split.

---

# Cleanup

After the review is complete, run the `CLEANUP_CMD` from the setup output.
