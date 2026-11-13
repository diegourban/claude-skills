# Review Checklist

Apply all items relevant to the changed files.

## General

- [ ] Implementation matches the likely intent of the branch name and commits
- [ ] Edge cases handled: null inputs, empty collections, boundary values, zero/negative
- [ ] No hardcoded values that should be configurable
- [ ] Naming is clear, consistent, and follows existing conventions
- [ ] Complex logic has explanatory comments (the *why*, not the *what*)
- [ ] No unnecessary duplication — DRY where meaningful

## Design & Architecture — SOLID

- [ ] **SRP** Single Responsibility — each class and method has one reason to change
- [ ] **OCP** Open/Closed — behavior extended via new code, not by modifying stable code
- [ ] **LSP** Liskov Substitution — subtypes are fully substitutable for their base types without altering correctness
- [ ] **ISP** Interface Segregation — interfaces are small and focused; no client forced to depend on methods it doesn't use
- [ ] **DIP** Dependency Inversion — high-level modules depend on abstractions, not concretions; dependencies injected, not instantiated
- [ ] No inappropriate coupling between layers (e.g., domain referencing HTTP types)
- [ ] New code follows patterns already established in the codebase
- [ ] No god classes, long methods, or excessive branching

## Clean Code

- [ ] Functions are small and do one thing; no functions longer than ~20–30 lines without clear justification
- [ ] No magic numbers or magic strings — use named constants
- [ ] No flag arguments (`doSomething(true)`) — split into two clearly named methods instead
- [ ] Early returns / guard clauses used to reduce nesting depth
- [ ] Maximum nesting depth of 2–3 levels; deeply nested blocks are extracted into methods
- [ ] Command-Query Separation — methods either change state or return a value, not both
- [ ] No output arguments — methods communicate results via return values, not by mutating parameters
- [ ] Dead code removed — no commented-out blocks, unreachable paths, or unused variables
- [ ] Comments explain *why*, never *what* — if a comment is needed to explain *what*, the code should be rewritten

## Error Handling & Observability

- [ ] Errors caught at the right level; not silently swallowed without logging or re-raising
- [ ] Checked vs. unchecked exceptions (or equivalent) chosen appropriately for the language
- [ ] Error messages include all three components: **context** (what was being attempted), **the error** (what failed), and **mitigation** (how to resolve it)
- [ ] Either raise/throw an exception OR log the error — never both for the same failure (avoids duplicate log noise)
- [ ] Errors that can be detected early (startup, config validation) fail fast rather than surfacing at runtime
- [ ] Log levels appropriate: `DEBUG` for tracing, `INFO` for lifecycle, `WARN` for recoverable, `ERROR` for failures
- [ ] No sensitive data (PII, tokens, passwords) in logs or error responses
- [ ] Metrics or traces instrumented on critical paths consistent with existing patterns

## Security

- [ ] All external input validated and sanitized (HTTP, DB, queues, files)
- [ ] No hardcoded secrets, tokens, or credentials
- [ ] Authorization enforced — not just authentication
- [ ] SQL queries use parameterized statements — no string concatenation
- [ ] Sensitive data never logged or leaked in responses
- [ ] No newly introduced dependencies with known vulnerabilities — check with the appropriate tool for the ecosystem.

## Performance & Scalability

- [ ] No N+1 query problems — use eager loading strategies, batch fetching, or projections instead of issuing one query per item
- [ ] Large result sets use pagination or streaming
- [ ] No expensive operations inside tight loops
- [ ] No unbounded in-memory collections or caches
- [ ] Appropriate timeouts and backoff on external calls
- [ ] Thread safety of shared state

## Database & Migrations

- [ ] Schema changes are backward compatible, or have a migration strategy
- [ ] New queries have appropriate indexes considered
- [ ] Migrations are idempotent where possible
- [ ] Transactions scoped appropriately — not held open during I/O

## Configuration & CI

- [ ] No secrets, tokens, or credentials hardcoded in config files or CI env blocks
- [ ] Base images pinned to a specific digest or version tag — not `latest`
- [ ] CI steps use pinned action versions (e.g. `actions/checkout@v4`, not `@main`)
- [ ] No overly broad IAM roles, permissions, or access scopes
- [ ] Sensitive values sourced from a secrets manager or CI secret store, not plaintext
- [ ] No world-readable file mounts or exposed internal ports in container config
- [ ] Environment-specific config is clearly separated and not mixed

## API Design

Apply the subsection(s) matching the changed `[API]` files; skip inapplicable ones.

### REST

- [ ] HTTP methods used semantically (`GET` safe/idempotent, `POST` creates, `PUT`/`PATCH` updates)
- [ ] HTTP status codes correct (`201` created, `400` bad input, `404` not found, `422` validation failure)
- [ ] Breaking changes are versioned
- [ ] Response payloads consistent with existing API conventions

### GraphQL

- [ ] No fields removed or renamed without a deprecation cycle (`@deprecated(reason: "...")`)
- [ ] New required input fields or removed optional fields are breaking changes — flag them
- [ ] Errors returned in the `errors` envelope, not as HTTP 4xx/5xx
- [ ] N+1 risk on new resolvers — verify DataLoader or equivalent is used
- [ ] Schema additions follow existing naming conventions (casing, pluralisation)

### gRPC / Protobuf

- [ ] No fields removed or renumbered — only additions are wire-compatible
- [ ] Field numbers not reused for different types
- [ ] Enums only extended, not reordered or renamed
- [ ] Streaming RPCs (server/client/bidi) have documented cancellation and timeout behaviour
- [ ] Breaking changes bumped to a new package version (e.g. `v1` → `v2`)

## Semantic Versioning Impact

Determine the minimum semver bump warranted by the changes:

- [ ] **MAJOR** — breaking change: removed or renamed public symbol, changed method/function signature, dropped or renamed response field, altered behavior that callers depend on, incompatible DB schema change
- [ ] **MINOR** — backward-compatible addition: new endpoint, new optional parameter, new public type or field, new opt-in behavior
- [ ] **PATCH** — internal only: bug fix, refactor, performance improvement, no public contract change
- [ ] **N/A** — no versioned public interface is affected (e.g. pure infrastructure, docs, or test-only changes)

If multiple categories apply, the highest wins (MAJOR > MINOR > PATCH).

## Testing

- [ ] Tests exist for new features and public APIs
- [ ] Edge cases and error paths tested
- [ ] Tests are deterministic — no reliance on external state or ordering
- [ ] No excessive mocking hiding real behavior
- [ ] Test names describe what is being tested and the expected outcome
- [ ] Bug fixes include a regression test
