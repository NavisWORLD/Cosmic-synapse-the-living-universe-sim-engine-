import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {loadTable} from '../spark-beasts/runs.mjs';
import {buildGenome} from '../spark-beasts/genome.mjs';
import {canon, sha256Hex} from '../spark-beasts/hash.mjs';
import {readSparkFile, checkedSparkSave} from './spark-file.mjs';
import {verifySparkArt} from './cartridge.mjs';

// Receipt copied unchanged from Beast Box #252 at this immutable source commit.
const SOURCE='https://github.com/NavisWORLD/The-beast-box-/blob/48658f18e220d8b9957305a30aaec5bc3464c3b0/apps/beastbox-cloud/experiment-input/ibm-marrakesh-20261009-longer-receipt.json';
const readJson=url=>JSON.parse(readFileSync(url,'utf8'));
const historical=readJson(new URL('../spark-beasts/data/quantum-runs.json',import.meta.url));
const fez=readJson(new URL('../spark-beasts/data/ibm-fez-20261009-supplement.json',import.meta.url));
const source=readJson(new URL('./fixtures/ibm-marrakesh-20261009-longer-receipt.json',import.meta.url));
const bytes=new Uint8Array(readFileSync(new URL('./fixtures/ibm-marrakesh-noctlet.qbeast',import.meta.url)));
const FILE='ibm-marrakesh-20261009-supplement.json';
const expected={
 schema:'lost-cosmos-ibm-marrakesh-20261009-cartridge-supplement-v1',
 source_class:'RECORDED_IBM_HARDWARE',job_id:'db4l2uclf4us73c2td10',backend:'ibm_marrakesh',
 counts_digest_sha256:'6b5438dc3ad1ab02cd6440822ea8fe89e1b66fa664174454c9471a65196d2910',
 source_receipt_url:SOURCE,
 runs:['bell-zz','bell-xx'].map((basis,pub_index)=>{
  const counts=source.measurements[basis.replace('-','_')];
  return {key:`db4l2uclf4us73c2td10:${basis}`,backend:'ibm_marrakesh',job_id:'db4l2uclf4us73c2td10',pub_index,num_bits:2,shots:4096,counts,counts_sha256:sha256Hex(canon(counts))};
 }),
};

// Node cannot fetch file: URLs. Only the transport is replaced; the real loader,
// genome, QBEAST validator and cartridge adapter run against their actual bytes.
function localFetch(t, overrides=new Map()) {
 t.mock.method(globalThis,'fetch',async url=>{
  const name=new URL(url).pathname.split('/').at(-1);
  if(overrides.has(name)) {
   const value=overrides.get(name);
   return value===null?new Response('',{status:404}):Response.json(value);
  }
  try{return new Response(readFileSync(url));}
  catch(error){if(error.code==='ENOENT')return new Response('',{status:404});throw error;}
 });
}

test('Noctlet QBEAST enters the existing cartridge with its exact genome and public identity',async t=>{
 localFetch(t);
 const table=await loadTable(),beast=await readSparkFile(bytes,table),save=checkedSparkSave(beast,table);
 assert.equal(beast.genome.seed,'be68cd2a140fe2e7845459c220909297614a874515f4fda2351df41880a7eb17');
 assert.equal(beast.genome.names[1],'Noctlet');
 assert.equal(beast.genome.names[2],'Vesperwing');
 assert.equal(beast.genome.body,'dragonling');
 assert.equal(beast.record.publicId,0x82fbc8ff);
 assert.equal(beast.runIndex,historical.runs.length+3);
 assert.equal(verifySparkArt(save),true);
 assert.deepEqual(save.slice(24864,24928),beast.record.profile.bcp1);
 assert.equal(new DataView(save.buffer).getUint32(24712,true),0x82fbc8ff);
 assert.equal(beast.record.growth.layer,0);
 assert.equal(beast.record.growth.points,0);
 assert.equal(beast.record.growth.grown,false);
});

test('both measured Marrakesh PUBs append after historical and Fez rows without changing totals or indices',async t=>{
 localFetch(t);
 const table=await loadTable();
 assert.deepEqual(table.runs.slice(0,historical.runs.length),historical.runs);
 assert.deepEqual(table.runs.slice(historical.runs.length,historical.runs.length+2),fez.runs);
 assert.deepEqual(table.runs.slice(historical.runs.length+2,historical.runs.length+4),expected.runs);
 assert.equal(table.runs.length,historical.runs.length+18);
 assert.deepEqual(table.totals,historical.totals);
 assert.equal(table.claim,historical.claim_boundary);
 for(const row of expected.runs)assert.deepEqual(table.byKey.get(row.key),row);
});

test('Marrakesh supplement exactly matches the independently source-digested four-PUB receipt',()=>{
 const data=readJson(new URL('../spark-beasts/data/'+FILE,import.meta.url));
 assert.equal(source.job_status,'DONE');
 assert.equal(source.shot_count,16384);
 assert.equal(sha256Hex(canon(source.measurements)),expected.counts_digest_sha256);
 assert.equal(data.counts_digest_sha256,source.counts_digest_sha256);
 assert.equal(data.source_receipt_url,SOURCE);
 assert.deepEqual(data.runs,expected.runs);
 assert.deepEqual(data.runs.map(row=>row.counts_sha256),[
  '9ab6237bef9799575f9ffb557d442e8b2975839b53f7a19848e218ac14adb7b8',
  '8722018cf2e7c23cb09aea30072eb375dac111d6106fddc6ce27365813cf5e19',
 ]);
});

test('missing Marrakesh source preserves old replay and refuses Noctlet admission',async t=>{
 localFetch(t,new Map([[FILE,null]]));
 const table=await loadTable();
 assert.equal(table.runs.length,historical.runs.length+2);
 assert.equal(buildGenome({focus:90,calm:70,spark:90},table.runs.at(-1),'NavisWORLD-moon-3').seed,'ccb5b741b54f1951d29608d03557957fed7de31180e1b24daeb6c590e89888d5');
 await assert.rejects(()=>readSparkFile(bytes,table),/Recorded run is not in this cartridge table/);
});

test('missing Fez source never shifts later Marrakesh recipe indices',async t=>{
 localFetch(t,new Map([['ibm-fez-20261009-supplement.json',null]]));
 const table=await loadTable();
 assert.deepEqual(table.runs,historical.runs);
 await assert.rejects(()=>readSparkFile(bytes,table),/Recorded run is not in this cartridge table/);
});

for(const [label,mutate] of [
 ['source class',data=>{data.source_class='SIMULATOR';}],
 ['source digest',data=>{data.counts_digest_sha256='0'.repeat(64);}],
 ['backend',data=>{data.runs[1].backend='ibm_fez';}],
 ['job',data=>{data.runs[1].job_id='another-job';}],
 ['shots',data=>{data.runs[1].shots=256;}],
 ['counts digest',data=>{data.runs[1].counts['00']++;}],
 ['rehashed replacement counts',data=>{data.runs[1].counts['00']++;data.runs[1].counts['11']--;data.runs[1].counts_sha256=sha256Hex(canon(data.runs[1].counts));}],
 ['duplicate PUB',data=>{data.runs[1]=structuredClone(data.runs[0]);}],
 ['reordered PUBs',data=>{data.runs.reverse();}],
])test(`Marrakesh source rejects corrupted ${label} before admission`,async t=>{
 const bad=structuredClone(expected);mutate(bad);
 localFetch(t,new Map([[FILE,bad]]));
 await assert.rejects(()=>loadTable(),/IBM hardware (supplement|run)/);
});

test('a forged Noctlet progress claim remains subject to the existing QBEAST digest authority',async t=>{
 localFetch(t);
 const table=await loadTable(),bad=JSON.parse(new TextDecoder().decode(bytes));
 bad.progress.bond=100;
 await assert.rejects(()=>readSparkFile(new TextEncoder().encode(JSON.stringify(bad)),table),/digest/);
});
