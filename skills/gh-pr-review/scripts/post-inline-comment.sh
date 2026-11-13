#!/usr/bin/env bash
# post-inline-comment.sh <owner> <repo> <pr_id> <head_sha> <path> <line>
# Reads the comment body from stdin and posts it as an inline review comment on
# the RIGHT side of the diff. GitHub rejects (422) inline comments on lines that
# are not part of the diff hunks; in that case this falls back to a top-level PR
# comment prefixed with the file:line reference so the finding is never lost.
# Every posted comment gets the AI-assisted-review disclaimer appended.
#
# Prints: OK inline | OK fallback | FAIL <message>

set -uo pipefail

OWNER="${1:?owner required}"
REPO="${2:?repo required}"
PR_ID="${3:?pr id required}"
HEAD_SHA="${4:?head sha required}"
FILE_PATH="${5:?file path required}"
LINE="${6:?line required}"

BODY=$(cat)
if [ -z "$BODY" ]; then
  echo "FAIL empty comment body"
  exit 1
fi

# Mirrors the disclaimer other forge integrations append, so reviews read the
# same whichever forge they land on. Applied here rather than in SKILL.md so it
# cannot be forgotten on an individual finding; the fallback path below embeds
# $BODY and therefore inherits it too.
BODY="${BODY}

---
*AI-assisted review.
Findings are a starting point, not final judgment.*"

TMP_OUT=$(mktemp /tmp/ghpr-comment-XXXXXX)
trap 'rm -f "$TMP_OUT"' EXIT

if gh api "repos/${OWNER}/${REPO}/pulls/${PR_ID}/comments" \
     --method POST \
     -f "commit_id=${HEAD_SHA}" \
     -f "path=${FILE_PATH}" \
     -F "line=${LINE}" \
     -f "side=RIGHT" \
     -f "body=${BODY}" \
     > "$TMP_OUT" 2>&1; then
  echo "OK inline"
  exit 0
fi

ERR=$(tr '\n' ' ' < "$TMP_OUT" | sed 's/  */ /g')

FALLBACK_BODY="📄 \`${FILE_PATH}:${LINE}\` _(line not in diff — posted as a general comment)_

${BODY}"

if gh api "repos/${OWNER}/${REPO}/issues/${PR_ID}/comments" \
     --method POST \
     -f "body=${FALLBACK_BODY}" \
     > "$TMP_OUT" 2>&1; then
  echo "OK fallback"
  exit 0
fi

echo "FAIL ${ERR}"
exit 1
