#!/usr/bin/env bash
# setup-worktree.sh <source-branch> <destination-branch>
# Creates a git worktree for the source branch and outputs the diff + metadata.
# Outputs key=value lines Claude reads for worktree path and SHA refs,
# followed by diff stat, file status, and full diff.

set -euo pipefail

SOURCE_BRANCH="${1:?ERROR: source-branch required. Usage: setup-worktree.sh <source-branch> <destination-branch>}"
DESTINATION_BRANCH="${2:?ERROR: destination-branch required. Usage: setup-worktree.sh <source-branch> <destination-branch>}"

SAFE_NAME="nmcr-$(echo "$SOURCE_BRANCH" | sed 's/[^a-zA-Z0-9]/-/g')"
WORKTREE_PATH="/tmp/$SAFE_NAME"

git fetch --all --prune 2>/dev/null

SOURCE_REF=$(git rev-parse --verify "refs/heads/$SOURCE_BRANCH" 2>/dev/null \
  || git rev-parse --verify "refs/remotes/origin/$SOURCE_BRANCH" 2>/dev/null \
  || { echo "ERROR: Branch '$SOURCE_BRANCH' not found locally or on remote." >&2; exit 1; })

DESTINATION_REF=$(git rev-parse --verify "refs/heads/$DESTINATION_BRANCH" 2>/dev/null \
  || git rev-parse --verify "refs/remotes/origin/$DESTINATION_BRANCH" 2>/dev/null \
  || { echo "ERROR: Branch '$DESTINATION_BRANCH' not found locally or on remote." >&2; exit 1; })

git worktree remove "$WORKTREE_PATH" --force 2>/dev/null || rm -rf "$WORKTREE_PATH" 2>/dev/null || true
git worktree add "$WORKTREE_PATH" "$SOURCE_REF" 2>/dev/null

echo "WORKTREE_PATH=$WORKTREE_PATH"
echo "SOURCE_BRANCH=$SOURCE_BRANCH"
echo "SOURCE_REF=$SOURCE_REF"
echo "DESTINATION_BRANCH=$DESTINATION_BRANCH"
echo "DESTINATION_REF=$DESTINATION_REF"
echo "CLEANUP_CMD=git worktree remove $WORKTREE_PATH --force"
echo ""

# Shared with gh-pr-review. No cleanup arg: a worktree is
# removed with `git worktree remove`, not rm -rf, so we handle it here.
if ! bash "$(dirname "$0")/../../review-rubric/scripts/emit-diff.sh" \
       "$WORKTREE_PATH" "$DESTINATION_REF" "$SOURCE_REF"; then
  git worktree remove "$WORKTREE_PATH" --force 2>/dev/null || true
  exit 1
fi
