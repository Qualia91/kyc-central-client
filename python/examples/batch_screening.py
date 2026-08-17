"""Screen a company's officers and beneficial owners against sanctions lists.

Shows the batch endpoint, which screens up to 500 names against a single request
rather than one request per name — the difference between staying inside your rate
limit and exhausting it.

Run with:

    export KYCCENTRAL_API_KEY="your_key"
    python examples/batch_screening.py 00445790
"""

from __future__ import annotations

import sys

from kyccentral import KYCCentral


def collect_names(client: KYCCentral, company_number: str) -> list[str]:
    """Every officer and PSC name attached to a company."""
    names: list[str] = []

    officers = client.companies.officers(company_number)
    for officer in officers.get("items", []):
        # Resigned officers are still worth screening for historic exposure.
        if name := officer.get("name"):
            names.append(name)

    pscs = client.companies.persons_with_significant_control(company_number)
    for psc in pscs.get("items", []):
        if name := psc.get("name"):
            names.append(name)

    # De-duplicate while preserving order, since a person can be both officer and PSC.
    return list(dict.fromkeys(names))


def main(company_number: str) -> int:
    with KYCCentral() as client:
        status = client.sanctions.status()
        if not status.get("available"):
            print("Sanctions screening is not currently available.", file=sys.stderr)
            return 1

        names = collect_names(client, company_number)
        if not names:
            print("No officers or PSCs found for this company.")
            return 0

        print(f"Screening {len(names)} name(s) in one request…\n")
        results = client.sanctions.screen_names(names)

    hits = 0
    for name in names:
        matches = results.get(name) or results.get("results", {}).get(name) or []
        if matches:
            hits += 1
            print(f"{name}: {len(matches)} candidate match(es)")
            for match in matches:
                score = match.get("score")
                label = match.get("name") or match.get("caption") or "?"
                dataset = match.get("dataset") or match.get("source") or "?"
                print(f"    {label}  [{dataset}]  score={score}")
        else:
            print(f"{name}: no match")

    print()
    if hits:
        print(f"{hits} name(s) produced candidate matches — all require analyst review.")
        print("Sanctions lists carry aliases and transliterations; a hit is not a finding.")
    else:
        print("No candidate matches.")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <company_number>", file=sys.stderr)
        raise SystemExit(64)
    raise SystemExit(main(sys.argv[1]))
