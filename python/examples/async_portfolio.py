"""Assess a portfolio of companies concurrently with the async client.

Bounded concurrency matters here: the API rate-limits subscribers to 60 assessments a
minute, and firing an unbounded `gather` at it just converts throughput into 429s.

Run with:

    export KYCCENTRAL_API_KEY="your_key"
    python examples/async_portfolio.py 00445790 02627406 03824658
"""

from __future__ import annotations

import asyncio
import sys

from kyccentral import Assessment, AsyncKYCCentral, KYCCentralError, RateLimitError

MAX_CONCURRENT = 5


async def assess_one(
    client: AsyncKYCCentral, company_number: str, semaphore: asyncio.Semaphore
) -> tuple[str, Assessment | None, str | None]:
    async with semaphore:
        try:
            return company_number, await client.kyc.assess(company_number), None
        except RateLimitError as exc:
            # The client already retried with backoff; reaching here means the quota
            # or limit is genuinely exhausted rather than momentarily tight.
            wait = f" (retry after {exc.retry_after}s)" if exc.retry_after else ""
            return company_number, None, f"rate limited{wait}"
        except KYCCentralError as exc:
            return company_number, None, str(exc)


async def main(company_numbers: list[str]) -> int:
    semaphore = asyncio.Semaphore(MAX_CONCURRENT)

    async with AsyncKYCCentral() as client:
        results = await asyncio.gather(*(assess_one(client, n, semaphore) for n in company_numbers))

    failures = 0
    print(f"{'Company':<12} {'Risk':<10} {'Flags':<6} Name")
    print("-" * 70)
    for company_number, assessment, error in results:
        if assessment is None:
            failures += 1
            print(f"{company_number:<12} {'ERROR':<10} {'-':<6} {error}")
            continue

        risk = assessment.risk_level.value
        if assessment.is_partial:
            risk += "*"
        print(
            f"{company_number:<12} {risk:<10} {len(assessment.flags):<6} {assessment.company_name}"
        )

    if any(a is not None and a.is_partial for _, a, _ in results):
        print("\n* incomplete — an upstream source timed out, so absent flags prove nothing.")

    return 1 if failures else 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"usage: {sys.argv[0]} <company_number> [company_number …]", file=sys.stderr)
        raise SystemExit(64)
    raise SystemExit(asyncio.run(main(sys.argv[1:])))
