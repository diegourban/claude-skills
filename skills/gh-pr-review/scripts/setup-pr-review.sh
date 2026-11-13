#!/usr/bin/env bash
# setup-pr-review.sh <PR_URL|owner/repo#N>
# Given a GitHub PR reference, fetches PR metadata via the gh CLI, clones the
# base repo into an isolated tmp dir, fetches the PR head via refs/pull/N/head
# (works for fork PRs too), and computes the diff against the base branch.
# Outputs key=value lines Claude reads for repo/PR identity and refs, followed
# by diff stat, file status, and full diff.

set -euo pipefail

PR_REF="${1:?ERROR: PR reference required. Usage: setup-pr-review.sh <github-pr-url>}"

if [[ "$PR_REF" =~ ^https?://github\.com/([^/]+)/([^/]+)/pull/([0-9]+) ]]; then
  GH_OWNER="${BASH_REMATCH[1]}"
  GH_REPO="${BASH_REMATCH[2]}"
  GH_PR_ID="${BASH_REMATCH[3]}"
elif [[ "$PR_REF" =~ ^([^/]+)/([^/#]+)#([0-9]+)$ ]]; then
  GH_OWNER="${BASH_REMATCH[1]}"
  GH_REPO="${BASH_REMATCH[2]}"
  GH_PR_ID="${BASH_REMATCH[3]}"
else
  echo "ERROR: Not a recognized GitHub PR reference: $PR_REF" >&2
  echo "Expected: https://github.com/<owner>/<repo>/pull/<id>  or  <owner>/<repo>#<id>" >&2
  exit 1
fi

command -v gh >/dev/null 2>&1 || { echo "ERROR: gh CLI not found on PATH." >&2; exit 1; }
gh auth status >/dev/null 2>&1 || { echo "ERROR: gh is not authenticated. Run: gh auth login" >&2; exit 1; }

META_FILE="/tmp/ghpr-meta-$$.json"
trap 'rm -f "$META_FILE"' EXIT

if ! gh pr view "$GH_PR_ID" --repo "${GH_OWNER}/${GH_REPO}" \
      --json number,title,state,isDraft,isCrossRepository,headRefName,headRefOid,baseRefName,url,author,additions,deletions,changedFiles \
      > "$META_FILE" 2>/tmp/ghpr-err-$$.txt; then
  echo "ERROR: Failed to fetch PR ${GH_OWNER}/${GH_REPO}#${GH_PR_ID} via gh." >&2
  cat /tmp/ghpr-err-$$.txt >&2 2>/dev/null || true
  rm -f /tmp/ghpr-err-$$.txt
  exit 1
fi
rm -f /tmp/ghpr-err-$$.txt

PR_TITLE=$(jq -r '.title' "$META_FILE")
PR_STATE=$(jq -r '.state' "$META_FILE")
PR_DRAFT=$(jq -r '.isDraft' "$META_FILE")
PR_AUTHOR=$(jq -r '.author.login // "unknown"' "$META_FILE")
PR_FORK=$(jq -r '.isCrossRepository' "$META_FILE")
SOURCE_BRANCH=$(jq -r '.headRefName' "$META_FILE")
HEAD_SHA=$(jq -r '.headRefOid' "$META_FILE")
DESTINATION_BRANCH=$(jq -r '.baseRefName' "$META_FILE")

if [[ "$PR_STATE" != "OPEN" ]]; then
  echo "ERROR: PR is not open (state: $PR_STATE). Refusing to review a merged/closed PR." >&2
  exit 1
fi

SAFE_NAME="ghpr-${GH_REPO}-${GH_PR_ID}"
CLONE_PATH="/tmp/$SAFE_NAME"

rm -rf "$CLONE_PATH"
gh repo clone "${GH_OWNER}/${GH_REPO}" "$CLONE_PATH" -- --quiet \
  || { echo "ERROR: Failed to clone ${GH_OWNER}/${GH_REPO}." >&2; exit 1; }

# gh handles auth for the clone itself, but subsequent git commands need the
# credential helper wired up explicitly (the user's global git config may not
# have `gh auth setup-git` applied).
git -C "$CLONE_PATH" config credential.helper '!gh auth git-credential'

# refs/pull/N/head resolves the PR head even when it lives in a fork.
git -C "$CLONE_PATH" fetch --quiet origin \
  "refs/pull/${GH_PR_ID}/head:refs/ghpr/head" \
  "${DESTINATION_BRANCH}:refs/ghpr/base" \
  || { echo "ERROR: Failed to fetch PR head or base branch '$DESTINATION_BRANCH'." >&2; rm -rf "$CLONE_PATH"; exit 1; }

SOURCE_REF=$(git -C "$CLONE_PATH" rev-parse refs/ghpr/head)
DESTINATION_REF=$(git -C "$CLONE_PATH" rev-parse refs/ghpr/base)

git -C "$CLONE_PATH" checkout --quiet "$SOURCE_REF"

echo "GH_OWNER=$GH_OWNER"
echo "GH_REPO=$GH_REPO"
echo "GH_PR_ID=$GH_PR_ID"
echo "PR_TITLE=$PR_TITLE"
echo "PR_AUTHOR=$PR_AUTHOR"
echo "PR_DRAFT=$PR_DRAFT"
echo "PR_IS_FORK=$PR_FORK"
echo "CLONE_PATH=$CLONE_PATH"
echo "SOURCE_BRANCH=$SOURCE_BRANCH"
echo "SOURCE_REF=$SOURCE_REF"
echo "HEAD_SHA=$HEAD_SHA"
echo "DESTINATION_BRANCH=$DESTINATION_BRANCH"
echo "DESTINATION_REF=$DESTINATION_REF"
echo "CLEANUP_CMD=rm -rf $CLONE_PATH"
echo ""

# Shared with branch-review. Emits the file tags, the
# 600-line measurement, and the diff blocks. Last arg = remove on empty diff.
bash "$(dirname "$0")/../../review-rubric/scripts/emit-diff.sh" \
  "$CLONE_PATH" "$DESTINATION_REF" "$SOURCE_REF" "$CLONE_PATH"
