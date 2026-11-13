#!/usr/bin/env bash
# =============================================================================
# emit-diff.sh - review-rubric: the shared diff block for every review skill
# =============================================================================
# gh-pr-review and branch-review each ended with a
# byte-identical copy of this. Host-specific work (URL parsing, auth, clone
# strategy) stays in each skill's own setup script; everything from "we have a
# working tree and two refs" onwards happens here.
#
# It also does the two things the model used to redo by hand on every review:
# tagging each changed file, and measuring the diff against the 600-line rule.
#
# Usage:
#   emit-diff.sh <workdir> <destination-ref> <source-ref> [cleanup-path]
#   emit-diff.sh self-test
#
# <cleanup-path>, when given, is rm -rf'd if the diff turns out to be empty, so
# the caller does not leak a tmp clone on the no-diff path.
#
# Emits: CHANGED_LINES, CHANGED_FILES, OVERSIZED, then the FILE CATEGORIES,
# DIFF STAT, FILE STATUS and FULL DIFF blocks.
# =============================================================================

set -euo pipefail

OVERSIZE_THRESHOLD="${REVIEW_OVERSIZE_THRESHOLD:-600}"

# Tag precedence is deliberate: a test fixture that happens to be YAML is a
# test, not config; a lock file is generated whatever its extension.
categorize() {
  local f="$1" lower
  lower=$(printf '%s' "$f" | tr '[:upper:]' '[:lower:]')
  case "$lower" in
    */vendor/*|vendor/*|*/node_modules/*|node_modules/*|*/build/*|build/*|\
    */dist/*|dist/*|*/target/*|target/*|*/generated/*|generated/*|\
    *.lock|*-lock.json|*-lock.yaml|*.sum|*.min.js|*.min.css|*.pb.go|\
    *_pb2.py|*.g.dart|*generated*.java|*.freezed.dart)
      echo "GEN" ;;
    */src/test/*|*/src/it/*|*/tests/*|tests/*|*/test/*|test/*|*/__tests__/*|\
    *test.*|*tests.*|*_test.*|*-test.*|*.test.*|*spec.*|*_spec.*|*.spec.*|\
    *testfixtures*|*/testdata/*)
      echo "TST" ;;
    *openapi*.yaml|*openapi*.yml|*openapi*.json|*swagger*.yaml|*swagger*.yml|\
    *.proto|*.graphql|*.graphqls|*/reference/*.yaml|*/reference/*.yml|*asyncapi*)
      echo "API" ;;
    */migration/*|*/migrations/*|*/changelog/*|*/db/*|*.sql|*liquibase*|\
    v[0-9]*__*.sql|*flyway*)
      echo "DB" ;;
    *.md|*.rst|*.adoc|*.txt|docs/*|*/docs/*|license*|notice*)
      echo "DOC" ;;
    *.yaml|*.yml|*.toml|*.ini|*.cfg|*.conf|*.properties|*.env|\
    dockerfile*|*/dockerfile*|*.dockerfile|.github/*|*/.github/*|\
    jenkinsfile*|*.gradle|*.gradle.kts|pom.xml|*.tf|*.tfvars|\
    .pre-commit-config.yaml|makefile|*/makefile|*.mk|*.json)
      echo "CFG" ;;
    *)
      echo "SRC" ;;
  esac
}

emit() {
  local workdir="$1" dest="$2" src="$3" cleanup="${4:-}"
  local range="${dest}...${src}"

  local diff_stat
  diff_stat=$(git -C "$workdir" diff --stat "$range")
  if [ -z "$diff_stat" ]; then
    [ -n "$cleanup" ] && rm -rf "$cleanup"
    echo "ERROR: No differences found between the two refs." >&2
    exit 1
  fi

  # numstat gives added<TAB>deleted<TAB>path, with '-' on both counts for binary.
  local numstat
  numstat=$(git -C "$workdir" diff --numstat "$range")

  local changed_lines changed_files
  changed_lines=$(printf '%s\n' "$numstat" | awk -F'\t' '$1 != "-" { n += $1 + $2 } END { print n+0 }')
  changed_files=$(printf '%s\n' "$numstat" | grep -c . || true)

  echo "CHANGED_FILES=$changed_files"
  echo "CHANGED_LINES=$changed_lines"
  if [ "$changed_lines" -gt "$OVERSIZE_THRESHOLD" ]; then
    echo "OVERSIZED=true"
  else
    echo "OVERSIZED=false"
  fi
  echo "OVERSIZE_THRESHOLD=$OVERSIZE_THRESHOLD"
  echo ""

  echo "=== FILE CATEGORIES ==="
  echo "# tag<TAB>path  (review order: SRC, API, DB, CFG, TST, DOC; GEN/BIN skipped)"
  local added deleted path tag
  while IFS=$'\t' read -r added deleted path; do
    [ -z "${path:-}" ] && continue
    if [ "$added" = "-" ] && [ "$deleted" = "-" ]; then
      tag="BIN"
    else
      tag=$(categorize "$path")
    fi
    printf '%s\t%s\n' "$tag" "$path"
  done <<< "$numstat"
  echo ""

  echo "=== DIFF STAT ==="
  echo "$diff_stat"
  echo ""
  echo "=== FILE STATUS ==="
  git -C "$workdir" diff --name-status "$range"
  echo ""
  echo "=== FULL DIFF ==="
  git -C "$workdir" diff "$range"
}

self_test() {
  local fails=0 tmp
  check() { if eval "$2" >/dev/null 2>&1; then echo "ok    $1"; else echo "FAIL  $1"; fails=$((fails+1)); fi; }

  # Categorization is pure string work; assert it directly.
  local cases="src/main/java/App.java:SRC
src/test/java/AppTest.java:TST
orders/reference/orders-openapi.yaml:API
schema/user.graphqls:API
db/changelog/001-init.sql:DB
.github/workflows/ci.yml:CFG
build.gradle:CFG
README.md:DOC
package-lock.json:GEN
vendor/foo/bar.go:GEN
build/classes/App.class:GEN
src/main/resources/application.yaml:CFG"
  local line f want got
  while IFS= read -r line; do
    f="${line%:*}"; want="${line##*:}"
    got=$(categorize "$f")
    if [ "$got" = "$want" ]; then echo "ok    tag $f -> $got"
    else echo "FAIL  tag $f -> $got (want $want)"; fails=$((fails+1)); fi
  done <<< "$cases"

  # End-to-end against a throwaway repo: no network, no user repo touched.
  tmp=$(mktemp -d)
  (
    cd "$tmp"
    git init --quiet -b main .
    git config user.email t@t; git config user.name t
    mkdir -p src/main/java
    echo "class A {}" > src/main/java/A.java
    git add -A; git commit --quiet -m base
    echo "class B {}" > src/main/java/B.java
    echo "# doc" > README.md
    git add -A; git commit --quiet -m change
  )
  local base head out
  base=$(git -C "$tmp" rev-parse HEAD~1)
  head=$(git -C "$tmp" rev-parse HEAD)
  out=$("$0" "$tmp" "$base" "$head")

  check "emits CHANGED_LINES"       "printf '%s' \"\$(echo '$out')\" | grep -q '^CHANGED_LINES='"
  echo "$out" | grep -q '^OVERSIZED=false$' && echo "ok    small diff is not oversized" || { echo "FAIL  small diff is not oversized"; fails=$((fails+1)); }
  echo "$out" | grep -q '^SRC	src/main/java/B.java$' && echo "ok    tags new source file" || { echo "FAIL  tags new source file"; fails=$((fails+1)); }
  echo "$out" | grep -q '^DOC	README.md$' && echo "ok    tags new doc file" || { echo "FAIL  tags new doc file"; fails=$((fails+1)); }
  echo "$out" | grep -q '=== FULL DIFF ===' && echo "ok    emits full diff" || { echo "FAIL  emits full diff"; fails=$((fails+1)); }

  # Empty diff must be an error, and must clean up when asked.
  if "$0" "$tmp" "$head" "$head" >/dev/null 2>&1; then
    echo "FAIL  empty diff exits non-zero"; fails=$((fails+1))
  else
    echo "ok    empty diff exits non-zero"
  fi

  rm -rf "$tmp"
  echo "---"
  [ "$fails" -eq 0 ] && { echo "self-test: all checks passed"; return 0; }
  echo "self-test: $fails check(s) failed"; return 1
}

case "${1:-}" in
  self-test) self_test ;;
  "")        sed -n '2,20p' "$0" >&2; exit 1 ;;
  *)         emit "$@" ;;
esac
