# Contributing

Thanks for helping improve the KYC Central Elixir client. Bug reports, documentation
fixes and new endpoint coverage are all welcome.

## Getting set up

```bash
git clone https://github.com/qualia91/kyccentral-elixir
cd kyccentral-elixir
mix deps.get
```

## Running the checks

```bash
mix test                    # suite — HTTP is stubbed, no network, no API key
mix format --check-formatted
mix credo --strict
mix dialyzer                # first run builds a PLT and takes a few minutes
mix docs                    # ex_doc output in doc/
```

All of these run in CI across the supported Elixir and OTP versions. Please make sure
they pass locally before opening a pull request.

## House rules

**Jason stays the only runtime dependency.** The transport is OTP's own `:httpc`
precisely so that adding this client to a project pulls in no HTTP stack. A pull request
that adds a runtime dependency needs a very good reason. Anyone who wants Req, Finch or
Tesla can pass `:http`.

**Tests never touch the network.** `KYCCentral.Stub` injects an HTTP function and records
requests, so the suite runs offline and contributors don't need an API key. Please don't
add tests that call the live API.

**Never commit credentials.** No API keys in tests, fixtures, examples or commit
messages. Use obviously fake values like `"test-key"`.

**Real payloads, redacted.** When adding a fixture for a new endpoint, base it on a real
response but replace personal data — names, addresses, dates of birth — with invented
values. This library screens people; its test data shouldn't contain any.

**Return tuples, don't raise.** Every public function returns `{:ok, result}` or
`{:error, %KYCCentral.Error{}}`, including for argument errors caught before a request is
made. `KYCCentral.Error` is an exception so callers can `raise` it themselves if they
prefer, but the library should not make that choice for them.

**Match the API, don't reinterpret it.** Endpoints that proxy an upstream registry return
plain maps with string keys on purpose, so new upstream fields reach callers without
waiting on a release here. Only the assessment result is modelled as a struct, because it
is the one shape this API owns.

**Degrade on unknown values.** An unrecognised severity or rule status from a future API
release maps to a safe default rather than crashing the caller — the original string is
still on `:raw`. Keep that property when adding parsing.

## Adding an endpoint

1. Add the function to the right module in `lib/kyccentral/`, taking the client as its
   first argument.
2. Write a `@doc` that says what the endpoint returns and flags any plan requirement, and
   a `@spec`.
3. Validate path segments through `KYCCentral.Transport.segment/2` so a blank value
   returns `{:error, %Error{kind: :invalid_argument}}` instead of silently hitting a
   different URL.
4. Add a row to `@routes` in `test/kyccentral/resources_test.exs`, plus a behaviour test
   if the function validates arguments or builds a body.
5. Add a row to the endpoint table in `README.md`.
6. Add a line to `CHANGELOG.md` under `## Unreleased`.

## Reporting a bug

Open an issue with the client version, your Elixir and OTP versions, the call you made
and the returned error. **Redact your API key and any real company or personal data
first** — and remember that inspecting a `%KYCCentral{}` struct prints your key.

Security issues go to <security@kyccentral.co.uk> instead — see [SECURITY.md](SECURITY.md).

## Releasing

Maintainers only:

1. Bump `@version` in `mix.exs`.
2. Move `## Unreleased` entries under a new version heading in `CHANGELOG.md`.
3. Tag the commit `vX.Y.Z` and push the tag. The publish workflow runs the checks and
   `mix hex.publish`.
