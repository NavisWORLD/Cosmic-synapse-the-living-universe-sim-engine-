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
  {
    file: 'ibm-final-live-20261009-supplement.json',
    schema: 'lost-cosmos-ibm-final-live-20261009-cartridge-supplement-v1',
    job: 'db4m3bslf4us73c2ui9g', backend: 'ibm_fez', shots: 4096,
    sourceDigest: 'cf0a4973c0dbc074fc11a6bc7ce8439ecd61248c1a5c96a63571725c61e8b25b',
    rowDigests: ['64afa7f43c593c0d41758bb36b02f64bacf41441fa7dcf75ea49632dd02b5150', '85c22950478b53047cd3398e4e8a32a6e4e0c6f8ffc746c5eef76e8b82079add'],
  },
  {
    file: 'ibm-pistonwyrm-20261009-supplement.json',
    schema: 'lost-cosmos-ibm-pistonwyrm-20261009-cartridge-supplement-v1',
    job: 'db4n37g4qg6s73c2de00', backend: 'ibm_fez', shots: 4096,
    sourceDigest: 'd084218f57511e33070fbbf82a055d74bf77636b6c07eaa82bd6f1d1208a18d9',
    rowDigests: ['55b08466e641cb8c25bb0a32f7a576f4d585abe78f7352808cc9551e4b4e3c6c','916d1da1a468d7ae7186304cab805983ed42ff36996723c2670277718c84eb7a'],
  },
  {
    file: 'ibm-magmascale-20261009-supplement.json',
    schema: 'lost-cosmos-ibm-magmascale-20261009-cartridge-supplement-v1',
    job: 'db4nlt2mb58s7389er6g', backend: 'ibm_fez', shots: 4096,
    sourceDigest: 'd6d39ff479cd9aaf4d80eb16cb42bb393ea17fe2eaa9e23cdb151245165fd9d6',
    rowDigests: ['05d68e876d185e002e5b810b662057352a8800e9eb24e31a36ae3dda8d687b98','f9c94b48ad85a5517175b9f64ae0f81844819bc11aa04646244127c9db891538'],
  },
  {
    file: 'ibm-umbralet-music12d-20261009-supplement.json',
    schema: 'lost-cosmos-ibm-audio-cst12-umbralet-20261009-cartridge-supplement-v1',
    job: 'db4og3slf4us73c319h0', backend: 'ibm_fez', shots: 4096,
    sourceDigest: '2ac2025a72f6d376783aded12561370260d5285fb697ecd2040c31f4ebcbb8d7',
    rowDigests: ['8eb3a18ffb9ce08189bcaf401f3d394bd936d8ad187856e5cab999dc11a14432','f89e093ce5f8a6f5546c28760bd36a8f2501e382ed43ac14cf829b400db4629d'],
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
