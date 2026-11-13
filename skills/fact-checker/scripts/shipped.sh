#!/usr/bin/env bash
# =============================================================================
# shipped.sh - fact-checker skill: the ground-truth reader
# =============================================================================
# Reads repos at a PINNED REMOTE SHA, never from the working tree.
# The working tree is routinely stale and dirty; every claim this skill makes
# must be sourced from a blob that exists on origin's default branch.
#
# Usage:
#   shipped.sh pin <repo>...                   -> repo<TAB>branch<TAB>sha
#   shipped.sh cat <repo> <sha> <path>         -> file contents at that sha
#   shipped.sh grep <pattern> <repo> <sha> [pathspec...]
#   shipped.sh roles <repo> <sha>              -> role vocabulary, by frequency
#   shipped.sh ops <repo> <sha> <spec> [filter]
#                                              -> path/method/operationId/security per OpenAPI operation
#   shipped.sh self-test                       -> no network required
#
# <repo> is a bare name resolved through the config below, or a path to a
# local clone (anything containing '/', or '.').
#
# Config ($FACT_CHECKER_CONFIG, default ~/.config/fact-checker):
#   sources      one <host>/<owner> per line, e.g. github.com/my-org
#   roles-regex  one POSIX ERE matching the role vocabulary (for `roles`)
#
# Repo lookup order for a bare name:
#   1. $FACT_CHECKER_ROOT/<host>/<owner>/<repo> for each source (default ~/Repositories)
#   2. a bare mirror under $FACT_CHECKER_CACHE (default $TMPDIR/fact-checker),
#      cloned over SSH from each source in order
#
# `pin` EXITS NON-ZERO naming every repo it could not pin. Callers must mark
# those repos' claims UNVERIFIED rather than falling back to the worktree.
# =============================================================================

set -euo pipefail

CONFIG="${FACT_CHECKER_CONFIG:-$HOME/.config/fact-checker}"
ROOT="${FACT_CHECKER_ROOT:-$HOME/Repositories}"
CACHE="${FACT_CHECKER_CACHE:-${TMPDIR:-/tmp}/fact-checker}"

die() { echo "shipped.sh: $*" >&2; exit 1; }
warn() { echo "shipped.sh: $*" >&2; }

sources() {
  [[ -f "$CONFIG/sources" ]] || return 0
  grep -vE '^\s*(#|$)' "$CONFIG/sources"
}

is_git_dir() { [[ -d "$1/.git" || -f "$1/.git" || -f "$1/HEAD" ]]; }

# --- locate a repo, cloning a bare mirror if there is no local checkout ------
# Prints the git directory to use. Never mutates a working tree.
repo_dir() {
  local repo="$1" src

  if [[ "$repo" == "." || "$repo" == */* ]]; then
    is_git_dir "$repo" && { (cd "$repo" && pwd); return 0; }
    return 1
  fi

  while read -r src; do
    is_git_dir "$ROOT/$src/$repo" && { echo "$ROOT/$src/$repo"; return 0; }
  done < <(sources)

  local mirror="$CACHE/$repo.git"
  [[ -d "$mirror" ]] && { echo "$mirror"; return 0; }

  # No checkout anywhere; mirror it from the first source that has it.
  mkdir -p "$CACHE"
  local host owner
  while read -r src; do
    host="${src%%/*}"; owner="${src#*/}"
    if git clone --mirror --quiet "git@$host:$owner/$repo.git" "$mirror" 2>/dev/null; then
      echo "$mirror"; return 0
    fi
    rm -rf "$mirror"
  done < <(sources)
  return 1
}

# --- default branch on the REMOTE, not whatever is checked out locally ------
default_branch() {
  local dir="$1"
  local ref
  # Refresh origin/HEAD; it is often unset or stale on a long-lived clone.
  git -C "$dir" remote set-head origin --auto >/dev/null 2>&1 || true
  if ref=$(git -C "$dir" symbolic-ref --quiet refs/remotes/origin/HEAD 2>/dev/null); then
    echo "${ref##refs/remotes/origin/}"; return 0
  fi
  # A mirror clone keeps branches at refs/heads and HEAD points at the default.
  if ref=$(git -C "$dir" symbolic-ref --quiet HEAD 2>/dev/null); then
    echo "${ref##refs/heads/}"; return 0
  fi
  for ref in main master; do
    git -C "$dir" rev-parse --verify --quiet "origin/$ref" >/dev/null 2>&1 && { echo "$ref"; return 0; }
    git -C "$dir" rev-parse --verify --quiet "$ref" >/dev/null 2>&1 && { echo "$ref"; return 0; }
  done
  return 1
}

resolve_sha() {
  local dir="$1" branch="$2" sha
  sha=$(git -C "$dir" rev-parse --verify --quiet "origin/$branch" 2>/dev/null) || true
  [[ -z "$sha" ]] && sha=$(git -C "$dir" rev-parse --verify --quiet "$branch" 2>/dev/null) || true
  [[ -n "$sha" ]] && { echo "$sha"; return 0; }
  return 1
}

cmd_pin() {
  [[ $# -gt 0 ]] || die "pin needs at least one repo name"
  local failed=() repo dir branch sha
  for repo in "$@"; do
    if ! dir=$(repo_dir "$repo"); then
      warn "cannot locate repo '$repo' (no checkout under $ROOT for any source in $CONFIG/sources, and mirror clone failed)"
      failed+=("$repo"); continue
    fi
    # Fetch is what makes this ground truth rather than a cached guess.
    if ! git -C "$dir" fetch --quiet --prune origin 2>/dev/null; then
      warn "fetch failed for '$repo'; refusing to read a possibly stale tree"
      failed+=("$repo"); continue
    fi
    if ! branch=$(default_branch "$dir"); then
      warn "cannot determine default branch for '$repo'"
      failed+=("$repo"); continue
    fi
    if ! sha=$(resolve_sha "$dir" "$branch"); then
      warn "cannot resolve $branch for '$repo'"
      failed+=("$repo"); continue
    fi
    printf '%s\t%s\t%s\n' "$repo" "$branch" "$sha"
  done
  if [[ ${#failed[@]} -gt 0 ]]; then
    warn "UNPINNABLE: ${failed[*]} - mark every claim about these repos UNVERIFIED"
    return 1
  fi
}

cmd_cat() {
  [[ $# -eq 3 ]] || die "cat <repo> <sha> <path>"
  local dir; dir=$(repo_dir "$1") || die "cannot locate repo '$1'"
  git -C "$dir" cat-file -p "$2:$3" 2>/dev/null \
    || die "no blob at $1@${2:0:7}:$3 - path absent on the pinned branch"
}

cmd_grep() {
  [[ $# -ge 3 ]] || die "grep <pattern> <repo> <sha> [pathspec...]"
  local pattern="$1" repo="$2" sha="$3"; shift 3
  local dir; dir=$(repo_dir "$repo") || die "cannot locate repo '$repo'"
  # Exit 1 from git grep means "no matches", which is a real answer, not an error.
  git -C "$dir" grep -n -I -E -e "$pattern" "$sha" ${1+-- "$@"} || true
}

# The role vocabulary, by frequency. A role absent from this list is a typo or
# an invention; both are defects. NOTE: git grep's -E is POSIX ERE and does NOT
# support \b, and its -o is unreliable against a tree-ish, so we match whole
# lines here and extract with a second pass.
cmd_roles() {
  [[ $# -ge 2 ]] || die "roles <repo> <sha> [pathspec...]"
  local repo="$1" sha="$2"; shift 2
  [[ -f "$CONFIG/roles-regex" ]] || die "no $CONFIG/roles-regex: write one ERE matching your role names"
  local re; re=$(grep -vE '^\s*(#|$)' "$CONFIG/roles-regex" | head -1)
  local dir; dir=$(repo_dir "$repo") || die "cannot locate repo '$repo'"
  git -C "$dir" grep -h -I -E "$re" "$sha" -- "${@:-*.yaml}" 2>/dev/null \
    | grep -oE "$re" | sort | uniq -c | sort -rn
}

# Every operation in an OpenAPI spec with its security, one per line:
#   <path>\t<METHOD>\t<operationId>\t<security>
# Security is the x-security.roles extension when present, else the standard
# `security` requirement (scheme(scope scope)), else <no-security>.
# This is the verifier for a permission-allowlist claim: compare the drafted
# list against the siblings sharing the same path prefix.
cmd_ops() {
  [[ $# -ge 3 ]] || die "ops <repo> <sha> <spec-path> [path-filter]"
  local repo="$1" sha="$2" spec="$3" filter="${4:-}"
  local out
  out=$(cmd_cat "$repo" "$sha" "$spec" | yq -r '
    .paths | to_entries | .[] as $p
    | $p.value | to_entries | .[]
    | select(.key == "get" or .key == "post" or .key == "put"
             or .key == "patch" or .key == "delete")
    | [$p.key, (.key | upcase), (.value.operationId // "-"),
       ( (.value."x-security".roles // [] | join(","))
         as $xs
         | if $xs != "" then $xs
           else ((.value.security // [])
                 | map(to_entries | .[] | .key + "(" + (.value | join(" ")) + ")")
                 | join(",")) as $std
             | if $std != "" then $std else "<no-security>" end
           end )]
    | @tsv') || die "could not parse $spec as OpenAPI at ${sha:0:7}"
  [[ -n "$filter" ]] && out=$(printf '%s\n' "$out" | grep -- "$filter" || true)
  printf '%s\n' "$out"
}

cmd_self_test() {
  local fails=0
  check() { if eval "$2" >/dev/null 2>&1; then echo "ok    $1"; else echo "FAIL  $1"; fails=$((fails+1)); fi; }
  notcheck() { if eval "$2" >/dev/null 2>&1; then echo "FAIL  $1"; fails=$((fails+1)); else echo "ok    $1"; fi; }

  check     "usage: bare invocation is an error"   "! $0"
  notcheck  "pin with no args exits non-zero"      "$0 pin"
  notcheck  "cat with wrong arity exits non-zero"  "$0 cat only-one-arg"
  notcheck  "unknown subcommand exits non-zero"    "$0 nonsense"
  notcheck  "unknown bare repo is unpinnable"      "FACT_CHECKER_CONFIG=/nonexistent $0 pin no-such-repo-xyz"

  # End to end against a throwaway repo with an origin: pin, grep, cat, ops.
  local tmp; tmp=$(mktemp -d)
  (
    set -e
    git init -q -b main "$tmp/origin"
    mkdir -p "$tmp/origin/api"
    cat > "$tmp/origin/api/openapi.yaml" <<'YAML'
paths:
  /things:
    get:
      operationId: listThings
      x-security:
        roles: [ADMIN_USER, SUPPORT_USER]
  /things/{id}:
    get:
      operationId: getThing
      security:
        - oauth: [things.read]
    delete:
      operationId: deleteThing
YAML
    git -C "$tmp/origin" add . && git -C "$tmp/origin" -c user.email=t@t -c user.name=t commit -qm init
    git clone -q "$tmp/origin" "$tmp/clone"
  ) >/dev/null 2>&1
  check     "pin a local path"                     "$0 pin $tmp/clone"
  local sha; sha=$("$0" pin "$tmp/clone" 2>/dev/null | cut -f3)
  check     "grep finds a token at the pinned sha" "$0 grep listThings $tmp/clone $sha | grep -q openapi.yaml"
  check     "cat reads a blob"                     "$0 cat $tmp/clone $sha api/openapi.yaml | grep -q getThing"
  if command -v yq >/dev/null 2>&1; then
    check   "ops reads x-security roles"           "$0 ops $tmp/clone $sha api/openapi.yaml | grep -q 'ADMIN_USER,SUPPORT_USER'"
    check   "ops reads standard security"          "$0 ops $tmp/clone $sha api/openapi.yaml | grep -q 'oauth(things.read)'"
    check   "ops flags missing security"           "$0 ops $tmp/clone $sha api/openapi.yaml | grep -q '<no-security>'"
  else
    echo "skip  ops checks (yq not installed)"
  fi
  rm -rf "$tmp"

  echo "---"
  [[ $fails -eq 0 ]] && { echo "self-test: all checks passed"; return 0; }
  echo "self-test: $fails check(s) failed"; return 1
}

case "${1:-}" in
  pin)       shift; cmd_pin "$@" ;;
  cat)       shift; cmd_cat "$@" ;;
  grep)      shift; cmd_grep "$@" ;;
  roles)     shift; cmd_roles "$@" ;;
  ops)       shift; cmd_ops "$@" ;;
  self-test) shift; cmd_self_test ;;
  -h|--help) sed -n '2,32p' "$0" ;;
  *)         sed -n '2,32p' "$0" >&2; exit 2 ;;
esac
