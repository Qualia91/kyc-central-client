/**
 * Screen a company's officers and beneficial owners against sanctions lists.
 *
 * Shows the batch endpoint, which screens up to 500 names in a single request
 * rather than one request per name — the difference between staying inside your
 * rate limit and exhausting it.
 *
 * Run with:
 *
 *     export KYCCENTRAL_API_KEY="your_key"
 *     npx tsx examples/batch-screening.ts 00445790
 */

import { KYCCentral } from '../src/index.js';

async function collectNames(client: KYCCentral, companyNumber: string): Promise<string[]> {
  const [officers, pscs] = await Promise.all([
    client.companies.officers(companyNumber),
    client.companies.pscs(companyNumber),
  ]);

  const names: string[] = [
    // Resigned officers are still worth screening for historic exposure.
    ...(officers.items ?? []).map((officer: { name?: string }) => officer.name),
    ...(pscs.items ?? []).map((psc: { name?: string }) => psc.name),
  ].filter((name): name is string => Boolean(name));

  // De-duplicate while preserving order, since a person can be both officer and PSC.
  return [...new Set(names)];
}

async function main(companyNumber: string): Promise<number> {
  const client = new KYCCentral();

  const status = await client.sanctions.status();
  if (!status.available) {
    console.error('Sanctions screening is not currently available.');
    return 1;
  }

  const names = await collectNames(client, companyNumber);
  if (names.length === 0) {
    console.log('No officers or PSCs found for this company.');
    return 0;
  }

  console.log(`Screening ${names.length} name(s) in one request…\n`);
  const results = await client.sanctions.screenNames(names);

  let hits = 0;
  for (const name of names) {
    const matches = results[name] ?? results.results?.[name] ?? [];
    if (matches.length > 0) {
      hits += 1;
      console.log(`${name}: ${matches.length} candidate match(es)`);
      for (const match of matches) {
        const label = match.name ?? match.caption ?? '?';
        const dataset = match.dataset ?? match.source ?? '?';
        console.log(`    ${label}  [${dataset}]  score=${match.score}`);
      }
    } else {
      console.log(`${name}: no match`);
    }
  }

  console.log();
  if (hits > 0) {
    console.log(`${hits} name(s) produced candidate matches — all require analyst review.`);
    console.log('Sanctions lists carry aliases and transliterations; a hit is not a finding.');
  } else {
    console.log('No candidate matches.');
  }
  return 0;
}

const companyNumber = process.argv[2];
if (!companyNumber) {
  console.error('usage: batch-screening.ts <company_number>');
  process.exit(64);
}

main(companyNumber).then(
  (code) => process.exit(code),
  (error) => {
    console.error(error);
    process.exit(1);
  },
);
