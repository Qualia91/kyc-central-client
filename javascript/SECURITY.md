# Security policy

## Reporting a vulnerability

Please report security issues privately to **security@kyccentral.co.uk**, or through
[GitHub private vulnerability reporting](https://github.com/qualia91/kyccentral-js/security/advisories/new).

Do not open a public issue for a security problem.

Include what you can: affected version, a description of the issue, and steps to
reproduce. We aim to acknowledge within 3 working days and to ship a fix or a mitigation
plan within 30 days. We'll credit you in the advisory unless you'd rather we didn't.

## Supported versions

Security fixes land on the latest minor release. Older minors are not backported.

## Handling API keys

This library reads your API key from the `KYCCENTRAL_API_KEY` environment variable, or
from the `apiKey` option. A few things worth knowing:

- **Never ship a key to the browser.** Anything in front-end code is public, including
  values inlined by a bundler from `.env`. Call the API from your server, or put a thin
  proxy in front of it and point the client at that with `baseUrl`.
- **The key is only ever sent to your configured `baseUrl`**, as an `X-API-Key` header,
  over HTTPS. It is never logged by this library.
- **Error messages include the request method and URL, not headers.** A stack trace
  pasted into a bug report will not leak your key — but query strings can contain company
  numbers and names, so redact before sharing.
- **A custom `fetch` sees everything.** If you pass one for logging or tracing, make sure
  it does not record the `X-API-Key` header.
- **Rotate a leaked key immediately** from [Account settings](https://kyccentral.co.uk/account).
  A revoked key stops working within about five minutes, the lifetime of the API's key
  cache.

## Supply chain

This package has **no runtime dependencies** — it uses the platform `fetch`. That is a
deliberate choice: it keeps the transitive attack surface of installing this client at
zero. Releases are published from CI with npm provenance, so you can verify that a
published tarball was built from this repository.

## Handling personal data

This client retrieves data about identifiable people — directors, beneficial owners,
sanctions and insolvency subjects. Responses are returned to your code and are not
cached, persisted or transmitted anywhere else by this library. What happens to them next
is yours to control: applicable data-protection obligations, including UK GDPR, sit with
you as the controller of whatever you store or log.
