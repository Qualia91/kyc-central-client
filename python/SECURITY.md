# Security policy

## Reporting a vulnerability

Please report security issues privately to **security@kyccentral.co.uk**, or through
[GitHub private vulnerability reporting](https://github.com/qualia91/kyccentral-python/security/advisories/new).

Do not open a public issue for a security problem.

Include what you can: affected version, a description of the issue, and steps to
reproduce. We aim to acknowledge within 3 working days and to ship a fix or a mitigation
plan within 30 days. We'll credit you in the advisory unless you'd rather we didn't.

## Supported versions

Security fixes land on the latest minor release. Older minors are not backported.

## Handling API keys

This library reads your API key from the `KYCCENTRAL_API_KEY` environment variable, or
from the `api_key` argument. A few things worth knowing:

- **The key is only ever sent to your configured `base_url`**, as an `X-API-Key` header,
  over HTTPS. It is never logged by this library.
- **Exception messages include the request method and URL, not headers.** A traceback
  posted in a bug report will not leak your key — but query strings can contain company
  numbers and names, so redact before sharing.
- **Redirects are followed.** If you point `base_url` at a host you don't control, your
  key travels there. Only set `base_url` to a KYC Central endpoint or your own proxy.
- **Rotate a leaked key immediately** from [Account settings](https://kyccentral.co.uk/account).
  A revoked key stops working within about five minutes, the lifetime of the API's key
  cache.

## Handling personal data

This client retrieves data about identifiable people — directors, beneficial owners,
sanctions and insolvency subjects. Responses are returned to your process and are not
cached, written to disk or transmitted anywhere else by this library. What happens to
them next is yours to control: applicable data-protection obligations, including UK GDPR,
sit with you as the controller of whatever you store or log.
