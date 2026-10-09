import {canon, sha256Hex} from './hash.mjs';
/** Recorded IBM Quantum count table. Historical seeds only. */

// Append-only measured sources: existing historical/Fez recipe indices stay fixed.
const SUPPLEMENTS = [
  {
    file: 'ibm-fez-20261009-supplement.json',
    schema: 'lost-cosmos-ibm-fez-20261009-cartridge-supplement-v1',
    job: 'db4kcfklf4us73c2sjb0', backend: 'ibm_fez', shots: 256,
    sourceDigest: 'db2e398585112c5125e3b08c915c3125d7ad4878160c6c6f95d3a7acbb0945ab',
    rowDigests: ['1fc1feaf53498754dbb05253629aa062994fa97f3ffa24a9a82aa8fd53d9f4eb', '253c5771133b9ead7aa71aa381da1fc779ddee2374b3c51de369c5563d19e0ab'],
  },
  {
    file: 'ibm-marrakesh-20261009-supplement.json',
    schema: 'lost-cosmos-ibm-marrakesh-20261009-cartridge-supplement-v1',
    job: 'db4l2uclf4us73c2td10', backend: 'ibm_marrakesh', shots: 4096,
    sourceDigest: '6b5438dc3ad1ab02cd6440822ea8fe89e1b66fa664174454c9471a65196d2910',
    rowDigests: ['9ab6237bef9799575f9ffb557d442e8b2975839b53f7a19848e218ac14adb7b8', '8722018cf2e7c23cb09aea30072eb375dac111d6106fddc6ce27365813cf5e19'],
  },
];

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
  const base=await response.json();
  const original=indexTable(base);
  const joined=[...original.runs],keys=new Set(original.runs.map(row=>row.key));
  for(const spec of SUPPLEMENTS){
    const supplementResponse=await fetch(new URL('./data/'+spec.file,import.meta.url));
    // An unavailable earlier supplement must not move later recipe indices.
    if(!supplementResponse.ok)break;
    const supplement=await supplementResponse.json();
    if(supplement.schema!==spec.schema||
       supplement.source_class!=='RECORDED_IBM_HARDWARE'||
       supplement.job_id!==spec.job||supplement.backend!==spec.backend||
       supplement.counts_digest_sha256!==spec.sourceDigest||
       !Array.isArray(supplement.runs)||supplement.runs.length!==2)
      throw Error('Invalid IBM hardware supplement');
    for(const [pubIndex,row] of supplement.runs.entries()){
      const expected=pubIndex===0?'bell-zz':'bell-xx';
      const counts=row.counts;
      if(row.pub_index!==pubIndex||row.key!==spec.job+':'+expected||
         row.job_id!==spec.job||row.backend!==spec.backend||
         row.num_bits!==2||row.shots!==spec.shots||keys.has(row.key)||
         !counts||Object.keys(counts).length!==4||
         !['00','01','10','11'].every(key=>Number.isInteger(counts[key])&&counts[key]>=0)||
         row.counts_sha256!==spec.rowDigests[pubIndex]||
         sha256Hex(canon(counts))!==row.counts_sha256||
         Object.values(counts).reduce((a,n)=>a+n,0)!==spec.shots)
        throw Error('Corrupted or duplicate IBM hardware run');
      joined.push(row);keys.add(row.key);
    }
  }
  return indexTable({...base,runs:joined});
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
