# The corpus: where ground truth lives

The skill is generic. Knowledge about *your* repositories lives in a local, untracked
config directory, `~/.config/fact-checker/` (override with `$FACT_CHECKER_CONFIG`).
Never commit it to this plugin: it describes private infrastructure.

## Files

| File | Used by | Format |
|---|---|---|
| `sources` | `shipped.sh` | one `<host>/<owner>` per line, searched in order |
| `roles-regex` | `shipped.sh roles` | one POSIX ERE matching your role/permission names |
| `corpus.md` | the skill | the template below, filled in |
| `claim-types.md` | the skill | extra verifiers that only make sense for your repos |

## How `shipped.sh` finds a repo

For a bare repo name, in order:

1. `$FACT_CHECKER_ROOT/<host>/<owner>/<repo>` for each line in `sources`
   (default root `~/Repositories`, i.e. a `~/Repositories/github.com/my-org/api` layout)
2. a bare mirror under `$FACT_CHECKER_CACHE` (default `$TMPDIR/fact-checker`), cloned over
   SSH from each source in order

A repo argument containing `/` or equal to `.` is used as a path to a local clone instead.

Never read these paths directly. The checkout is only a transport for `git cat-file`; the
SHA from `pin` is what makes a read evidence.

## Template for `~/.config/fact-checker/corpus.md`

```markdown
# Corpus

## Default branches (never assume)

| `main` | `master` |
|---|---|
| api-specs, gateway | legacy-service |

## Names that exist on more than one host

<list them; say which host a claim concerns, and pass a path rather than the bare name>

## What each repo is ground truth for

| Repo | Host | Ground truth for |
|---|---|---|
| `api-specs` | GitHub | The OpenAPI contract: security, schema names, shared responses. |
| `gateway` | GitHub | The GraphQL schema and its conventions. |
| `deploy-config` | GitLab | What is enabled in each environment. |

## Credentials

<which hosts need which env vars or SSH keys; without them, claims are UNVERIFIED>
```

## Cost

`pin` fetches. Pinning two repos takes a few seconds against warm clones; a cold mirror of
a large repo takes minutes. Pin only the repos the question actually touches, and pin them
all in one call so the fetches are batched.
