# Claim types and their verifiers

Every claim in a draft answer gets exactly one type from this table, and that type's
command decides its verdict. `$S` is `${CLAUDE_SKILL_DIR}/scripts/shipped.sh`, `$SHA` a
pinned SHA from `$S pin`. If no row fits (here or in `~/.config/fact-checker/claim-types.md`),
the claim is `UNVERIFIED`; do not improvise a verifier.

## 1. Identifier exists

*"`InvoiceSummary` is a new schema" / "there is a `getInvoices` operation".*

```bash
bash $S grep 'InvoiceSummary' api-specs "$SHA" '*.yaml'
```

CONFIRMED when the exact token is found; record `file:line`. **A hit REFUTES a
"this is new" claim**: the thing already ships, so extend it rather than defining a
near-duplicate. Absence only confirms a negative when the pathspec covered every place
the identifier could live; otherwise UNVERIFIED.

## 2. Permission allowlist

*"this endpoint should allow ADMIN and BILLING_ADMIN".*

```bash
bash $S ops api-specs "$SHA" orders/openapi.yaml /customers/
bash $S roles api-specs "$SHA" | head -40      # needs ~/.config/fact-checker/roles-regex
```

Two checks, both required:

- **Vocabulary**: every drafted role appears in `roles` output. A role that does not is a
  typo or an invention. REFUTED.
- **Sibling diff**: compare against operations sharing the path prefix. A role present on
  every sibling but absent from the draft is REFUTED and called out explicitly: *a missing
  role is a production 403, a spare role is harmless.* State which operation the list was
  copied from, so the reader can check the derivation rather than trusting it.

`<no-security>` in the `ops` output is itself a finding: an operation with no declared
security.

## 3. `$ref` target and style

*"`Money` is referenced as `'../common/schemas/Money.yaml'`".*

```bash
bash $S grep 'Money' api-specs "$SHA" 'orders/*'
```

Two separate questions. **Does the target resolve?** An unresolvable `$ref` is REFUTED and
a real defect. **Does the style match the file?** Count internal (`#/components/schemas/…`)
against external (`'../…yaml'`) refs and follow the majority. A minority style is REFUTED
even when it resolves, because code generators often key off the reference style.

**Scope the count to the module, never the repo.** An illustrative case:

| Scope | internal | external | verdict |
|---|---|---|---|
| repo-wide (`*.yaml`) | 19 | 346 | external, **and wrong for `orders`** |
| `billing/*` | 0 | 66 | external, unambiguous |
| `orders/*` | 1 | 1 | **UNVERIFIED**: a genuine tie, no convention to cite |

A repo-wide count answers "external" with apparent authority and misleads anyone working
in `orders`. When the module count ties, say so and ask; do not break the tie with the
repo-wide number, and do not break it with your own preference.

## 4. Shared response / error shape

*"404 returns an inline error object".*

```bash
bash $S grep 'CustomerNotFound' api-specs "$SHA" 'orders/*' | wc -l
```

A hand-rolled error block where a shared `#/components/responses/<X>` already exists is
REFUTED. Name the count of precedents in the evidence column.

## 5. Convention

*"gateway queries always return a union with Error".*

```bash
bash $S grep '^union ' gateway "$SHA" '*.graphqls' | wc -l          # precedents
bash $S grep '^type [A-Za-z]+Response ' gateway "$SHA" '*.graphqls' # counterexamples
```

**Both numbers are mandatory.** Fewer than 3 precedents → UNVERIFIED, never asserted. With
counterexamples, report them: 268 unions against 24 bare `Response` types is a strong
majority convention and *not* an absolute rule. Never round a majority up to "always".

Counting from the working tree instead of a pinned SHA inflates these, because `grep -r`
walks gitignored build output. That error alone is what this skill exists to prevent.

## 6. Behaviour

*"`findAllowed` returns results in request order when the filter is disabled".*

```bash
bash $S cat <repo> "$SHA" src/main/java/.../AccessService.java | sed -n '120,190p'
```

Read the cited method at the pinned SHA and quote the lines that decide it. CONFIRMED or
REFUTED only when the code settles it outright; if the answer depends on runtime config or
data, it is UNVERIFIED and the missing input is named. This is the weakest verifier in the
set: it is regex and reading, not structural matching. Installing `ast-grep` upgrades it.

## 7. Published artifact contents

*"the 1.4.0 release contains `getInvoices`".*

Resolve from the registry with local caches bypassed (`~/.m2/repository`,
`~/.gradle/caches/modules-2`, `node_modules`, the Go module cache). A stale cached artifact
produces false verdicts. Without registry credentials this claim is UNVERIFIED; say so
rather than reading the cache and calling it evidence.

## 8. Repo state

*"the working tree is 24 commits behind".*

`$S pin` is the whole verifier. Report `repo@sha` and the default branch name. Default
branches differ between repos (`main`, `master`, others), and guessing wrong silently
reads the wrong tree.

## 9. Spec or config validity

*"this spec change is valid and lints clean".*

Run the repo's own linter or validation task at the pinned SHA. Exit 0 is CONFIRMED.
Anything it catches is already enforced by CI; report it as a build failure, not as a
novel finding.
