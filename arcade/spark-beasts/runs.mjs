import {canon, sha256Hex} from './hash.mjs';
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
  const base=await response.json();
  const original=indexTable(base);
  const supplementResponse=await fetch(new URL('./data/ibm-fez-20261009-supplement.json',import.meta.url));
  if(!supplementResponse.ok)return original;
  const supplement=await supplementResponse.json();
  if(supplement.schema!=='lost-cosmos-ibm-fez-20261009-cartridge-supplement-v1'||
     supplement.source_class!=='RECORDED_IBM_HARDWARE'||
     supplement.job_id!=='db4kcfklf4us73c2sjb0'||
     !Array.isArray(supplement.runs)||supplement.runs.length!==2)
     throw Error('Invalid IBM hardware supplement');
  const joined=[...original.runs],keys=new Set(original.runs.map(row=>row.key));
  for(const row of supplement.runs){
    const expected=row.pub_index===0?'bell-zz':row.pub_index===1?'bell-xx':null;
    if(!expected||row.key!==row.job_id+':'+expected||
       row.job_id!==supplement.job_id||row.backend!=='ibm_fez'||
       row.num_bits!==2||row.shots!==256||keys.has(row.key)||
       sha256Hex(canon(row.counts))!==row.counts_sha256||
       Object.values(row.counts||{}).reduce((a,n)=>a+n,0)!==256)
      throw Error('Corrupted or duplicate IBM hardware run');
    joined.push(row);keys.add(row.key);
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
