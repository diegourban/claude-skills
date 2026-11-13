---
name: review-rubric
description: The shared code-review rubric and output protocol used by gh-pr-review and branch-review — the review checklist, the Conventional Comments finding format and label set, the output section order, the Review Summary template, and the file-categorization and diff-size script. Background knowledge loaded by a review skill; it does not review anything on its own.
user-invocable: false
allowed-tools: Read Bash(bash *)
---

# Review rubric

Shared material for the review skills. There is nothing to run here — a review
skill loads these files and applies them.

| File | What it holds |
|---|---|
| `checklist.md` | The review checklist: general, SOLID, clean code, error handling, security, performance, database, config/CI, API design (REST/GraphQL/gRPC), semver impact, testing |
| `protocol.md` | File categorization, finding format, the 6 labels, output section order, the Review Summary template, behavior rules |
| `scripts/emit-diff.sh` | The shared setup tail: diff stat, file status, full diff, plus a `[TAG]` per changed file and the `CHANGED_LINES`/`OVERSIZED` measurement |

## Why this exists

The three review skills carried byte-identical copies of `checklist.md` and
about 110 further duplicated lines of finding-format and output scaffolding.
Three copies meant three places to fix a rubric bug, and they stayed identical
only by luck — the fourth copy, in a separate team review command, had
already drifted to a different label set and a different fix-effort scale.

## For a review skill

```markdown
Apply the checklist in `${CLAUDE_SKILL_DIR}/../review-rubric/checklist.md`
and the protocol in `${CLAUDE_SKILL_DIR}/../review-rubric/protocol.md`.
```

and in its setup script, after the working tree and the two refs are ready:

```bash
bash "$(dirname "$0")/../../review-rubric/scripts/emit-diff.sh" \
  "$CLONE_PATH" "$DESTINATION_REF" "$SOURCE_REF" "$CLONE_PATH"
```

The fourth argument is the path to remove if the diff turns out to be empty.

Host-specific behaviour — URL parsing, authentication, clone strategy, how
comments are posted — stays in the calling skill. Those differ for real reasons:
`gh-pr-review` resolves fork PRs through `refs/pull/N/head`, while `branch-review`
works on local branches in a worktree. Do not merge them.

`scripts/emit-diff.sh self-test` checks the tag rules and runs end to end
against a throwaway repo. No network, and it never touches a real checkout.
