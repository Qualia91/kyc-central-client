# Security policy

## Reporting a vulnerability

Please report security issues privately to **security@kyccentral.co.uk**, or through
[GitHub private vulnerability reporting](https://github.com/qualia91/kyccentral-elixir/security/advisories/new).

Do not open a public issue for a security problem.

Include what you can: affected version, a description of the issue, and steps to
reproduce. We aim to acknowledge within 3 working days and to ship a fix or a mitigation
plan within 30 days. We'll credit you in the advisory unless you'd rather we didn't.

## Supported versions

Security fixes land on the latest minor release. Older minors are not backported.

## TLS verification

The default `:httpc` transport is configured with `verify: :verify_peer` against the OS
trust store, hostname checking via `:public_key.pkix_verify_hostname_match_fun(:https)`,
and TLS 1.2/1.3 only.

This matters more than it might look: **`:httpc` does not verify certificates unless it
is told to**, and a great many Elixir projects using it are silently accepting any
certificate. A client that carries an API key must never talk to an unverified peer, so
this library sets those options explicitly rather than relying on defaults.

If you supply your own `:http` function, TLS configuration becomes yours to get right.

## Handling API keys

This library reads your API key from the `KYCCENTRAL_API_KEY` environment variable, or
from the `:api_key` option. A few things worth knowing:

- **The key is only ever sent to your configured `:base_url`**, as an `X-API-Key` header,
  over HTTPS. It is never logged by this library.
- **The client struct contains your key.** `inspect/1` on a `%KYCCentral{}` will print
  it, so don't log the struct, and be careful with crash reports and `Logger` metadata
  that capture function arguments.
- **Error messages include the request method and URL, not headers.** A stack trace in a
  bug report will not leak your key — but query strings can contain company numbers and
  names, so redact before sharing.
- **A custom `:http` function sees everything**, including the `X-API-Key` header. If you
  pass one for logging or tracing, make sure it does not record that header.
- **Rotate a leaked key immediately** from [Account settings](https://kyccentral.co.uk/account).
  A revoked key stops working within about five minutes, the lifetime of the API's key
  cache.

## Supply chain

The only runtime dependency is [Jason](https://hex.pm/packages/jason); the HTTP transport
is OTP's own `:httpc`. That is deliberate — it keeps the transitive attack surface of
adding this client to your project as small as it can reasonably be.

## Handling personal data

This client retrieves data about identifiable people — directors, beneficial owners,
sanctions and insolvency subjects. Responses are returned to your process and are not
cached, persisted or transmitted anywhere else by this library. What happens to them next
is yours to control: applicable data-protection obligations, including UK GDPR, sit with
you as the controller of whatever you store or log.
