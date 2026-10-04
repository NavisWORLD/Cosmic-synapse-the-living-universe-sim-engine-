/** Recorded IBM Quantum count table. Historical seeds only. */

export function indexTable(table) {
  if (!table || table.schema !== 'lost-cosmos-quantum-runs-v2' || !Array.isArray(table.runs)) {
    throw new Error('Unexpected quantum table');
  }
  return {
    claim: table.claim_boundary,
    totals: table.totals,
    runs: table.runs,
    byKey: new Map(table.runs.map((run) => [run.key, run])),
  };
}

export async function loadTable() {
  const url = new URL('./data/quantum-runs.json', import.meta.url);
  const response = await fetch(url);
  if (!response.ok) throw new Error('The recorded quantum table is not on this device yet');
  return indexTable(await response.json());
}

export function runChoices(table, limit = 24) {
  const picked = [];
  const seen = new Set();
  const want = (run) => run.num_bits >= 5 || picked.length < 8;
  for (const run of table.runs) {
    if (!want(run)) continue;
    const tag = `${run.backend}:${run.num_bits}`;
    if (seen.has(tag) && run.num_bits === 1) continue;
    seen.add(tag);
    picked.push(run);
    if (picked.length >= limit) break;
  }
  return picked;
}
