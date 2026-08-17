# Official API clients

Open-source client libraries for the [KYC Central](https://kyccentral.co.uk) API, one per
language. Each directory is a **self-contained repository root** — its own README,
licence, changelog, CI, issue templates and release workflow — so it can be split out to
a public repository without rearranging anything.

| Language | Directory | Package | Public repository |
|---|---|---|---|
| Python | [`python/`](python) | [`kyccentral`](https://pypi.org/project/kyccentral/) | [kyccentral-python](https://github.com/qualia91/kyccentral-python) |
| JavaScript / TypeScript | [`javascript/`](javascript) | [`@kyccentral/sdk`](https://www.npmjs.com/package/@kyccentral/sdk) | [kyccentral-js](https://github.com/qualia91/kyccentral-js) |
| Elixir / Erlang | [`elixir/`](elixir) | [`kyccentral`](https://hex.pm/packages/kyccentral) | [kyccentral-elixir](https://github.com/qualia91/kyccentral-elixir) |

## Why they live here

They are versioned next to the API contract they mirror, so a change to a router in
`backend/app/routers/` and the client change that follows it can be reviewed together.
Splitting a directory out later preserves its history:

```bash
git subtree split --prefix=clients/python -b kyccentral-python
```

## Shared design

All three clients were built from the same live OpenAPI schema and deliberately behave
the same way, so a team using more than one does not have to learn three sets of rules.

**Coverage.** Every documented `/v1` endpoint, in every client.

**Only the assessment is typed.** `/v1/kyc/assess` is the one response whose shape this
API owns, so it gets a real type — `Assessment` dataclass, TypeScript interface, Elixir
struct — with severity helpers and an `is_partial` / `isPartial` / `partial?` check.
Endpoints that proxy an upstream registry (Companies House, the FCA Register, GLEIF)
return decoded JSON as-is, so new upstream fields reach callers without waiting on a
client release. The untouched payload is always kept on `raw`.

**Queued assessments are hidden.** A cold assessment can exceed a sensible HTTP timeout,
so the API may answer `202 Accepted` with a job id. Every client polls `/v1/jobs/{id}` to
completion and hands back a finished assessment, with an opt-out for callers who want to
drive the polling themselves.

**Identical retry policy.** Timeouts, connection failures and 408/429/5xx are retried
with exponential backoff plus jitter, honouring `Retry-After`. Client errors — 401, 403,
404, 422 — are never retried.

**Anonymous use works.** Reference and lookup endpoints run without a key at a lower rate
limit, so the libraries can be tried before signing up. Assessments and the AI endpoints
require one.

**Minimal dependencies.** Python depends on `httpx`; JavaScript on nothing at all
(platform `fetch`); Elixir on `jason` alone (OTP's `:httpc`). Each exposes a hook for
supplying your own HTTP client.

**Tests are offline.** Every suite mocks or injects the transport, so contributors need
neither network access nor an API key: 92 tests in Python, 101 in JavaScript, 113 in
Elixir.

**Compliance framing is consistent.** Each README states plainly that sanctions and
adverse-media matching is approximate, that unconfirmed matches stay low-severity until
an analyst confirms them, that there is no PEP screening, and that a partial result is
not a clean one.

## Working on a client

Each directory is independent; see its own `CONTRIBUTING.md`.

```bash
cd clients/python     && pip install -e ".[dev]" && pytest
cd clients/javascript && npm install             && npm test
cd clients/elixir     && mix deps.get            && mix test
```

## Keeping them in step with the API

These clients are generated from, and checked against, the live schema at
`GET /openapi.json`. When a public endpoint is added, changed or removed in
`backend/app/routers/`:

1. Update the resource module in all three clients, plus their endpoint tables.
2. Add a routing test in each suite — they all have a table-driven test that asserts each
   function hits the URL the API documents.
3. Add a `## Unreleased` entry to each `CHANGELOG.md`.

Endpoints registered with `include_in_schema=False` are internal (billing, workspaces,
PDF, admin, investigator) and are deliberately **not** covered.
