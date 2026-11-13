# claude-skills

Personal [Claude Code](https://claude.com/claude-code) skills by [@diegourban](https://github.com/diegourban),
packaged as a single plugin (`diegourban`) in a plugin marketplace of the same name.

## Install

In Claude Code:

```
/plugin marketplace add diegourban/claude-skills
/plugin install diegourban@diegourban
```

Skills are then invoked with the `diegourban:` prefix, e.g. `/diegourban:branch-review feat/x main`.

## Skills

| Skill | What it does |
|---|---|
| `gh-pr-review` | Senior-level review of a GitHub PR in a throwaway clone; posts inline comments only on request |
| `branch-review` | The same review for a local branch against another, in a git worktree so your checkout is untouched |
| `review-rubric` | The shared checklist, Conventional Comments format and diff script both review skills load |
| `fact-checker` | Answers a question about a codebase and verifies every claim against freshly fetched origin at a pinned SHA, with a CONFIRMED/REFUTED/UNVERIFIED ledger |
| `article-review-panel` | Reviews a technical post through three lenses (domain expert, editor, statistician), checking every number against the raw data |
| `humanize-prose` | Rewrites text so it stops reading like LLM output, in five passes, keeping meaning and facts identical |

## Local, private state

Some skills keep machine-local state **outside the plugin**, because the installed plugin is a
cached copy replaced on every update:

- `~/.claude/skill-memory/<skill>.md`: the lessons log for `humanize-prose` and `article-review-panel`.
- `~/.config/fact-checker/`: which repos `fact-checker` knows about (see
  [`skills/fact-checker/references/corpus.md`](skills/fact-checker/references/corpus.md)).

## Development

Edit in a clone, bump `version` in **both** `.claude-plugin/plugin.json` and
`.claude-plugin/marketplace.json`, push, then run `/plugin marketplace update diegourban` in
each Claude Code profile.

Script self-tests (no network):

```sh
bash skills/review-rubric/scripts/emit-diff.sh self-test
bash skills/fact-checker/scripts/shipped.sh self-test
```

## License

[MIT](LICENSE)
