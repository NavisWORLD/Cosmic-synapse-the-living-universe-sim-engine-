import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {loadTable} from '../spark-beasts/runs.mjs';
import {readSparkFile,checkedSparkSave} from './spark-file.mjs';
import {verifySparkArt} from './cartridge.mjs';
import {sha256Hex,canon} from '../spark-beasts/hash.mjs';

const FILE='ibm-pistonwyrm-20261009-supplement.json',JOB='db4n37g4qg6s73c2de00';
const read=path=>JSON.parse(readFileSync(new URL(path,import.meta.url),'utf8'));
const historical=read('../spark-beasts/data/quantum-runs.json');
const receipt=read('./fixtures/ibm-pistonwyrm-20261009-receipt.json');
const pinned=read('../spark-beasts/data/'+FILE);
const bytes=new Uint8Array(readFileSync(new URL('./fixtures/ibm-pistonwyrm-20261009.qbeast',import.meta.url)));
const umbra=new Uint8Array(readFileSync(new URL('./fixtures/ibm-final-live-umbrascale.qbeast',import.meta.url)));
const SOURCE='https://github.com/NavisWORLD/The-beast-box-/actions/runs/38001957043/artifacts/11649882762';
function localFetch(t,overrides=new Map()){
 t.mock.method(globalThis,'fetch',async url=>{
  const name=new URL(url).pathname.split('/').at(-1);
  if(overrides.has(name)){const value=overrides.get(name);return value===null?new Response('',{status:404}):Response.json(value);}
  try{return new Response(readFileSync(url));}
  catch(e){if(e.code==='ENOENT')return new Response('',{status:404});throw e;}
 });
}
test('Pistonwyrm measured source is pinned to original physical job and preserves historical source order',async t=>{
 localFetch(t);
 const table=await loadTable();
 assert.equal(receipt.job_id,JOB);assert.equal(receipt.backend_name,'ibm_fez');
 assert.equal(receipt.source_class,'RECORDED_IBM_HARDWARE');assert.equal(receipt.job_status,'DONE');
 assert.equal(receipt.shot_count,16384);assert.equal(sha256Hex(canon(receipt.measurements)),receipt.counts_digest_sha256);
 assert.equal(receipt.counts_digest_sha256,'d084218f57511e33070fbbf82a055d74bf77636b6c07eaa82bd6f1d1208a18d9');
 assert.equal(pinned.source_receipt_url,SOURCE);
 assert.equal(pinned.counts_digest_sha256,receipt.counts_digest_sha256);
 assert.deepEqual(table.runs.slice(0,historical.runs.length),historical.runs);
 assert.equal(table.runs.length,historical.runs.length+12);
 assert.deepEqual(table.totals,historical.totals);
 for(const [pub,basis] of ['bell_zz','bell_xx'].entries()){
  const row=pinned.runs[pub];
  assert.equal(row.pub_index,pub);assert.deepEqual(row.counts,receipt.measurements[basis]);
  assert.equal(row.counts_sha256,sha256Hex(canon(row.counts)));
  assert.deepEqual(table.byKey.get(row.key),row);
  assert.equal(row.shots,4096);
 }
});

test('Pistonwyrm and Umbrascale both enter unmodified real cartridge with distinct exact identities',async t=>{
 localFetch(t);
 const table=await loadTable();
 const piston=await readSparkFile(bytes,table),pistonSave=checkedSparkSave(piston,table);
 const first=await readSparkFile(umbra,table),firstSave=checkedSparkSave(first,table);
 assert.equal(piston.genome.names[1],'Pistonwyrm');
 assert.equal(piston.genome.names[2],'Boltwing');
 assert.equal(piston.genome.body,'dragonling');
 assert.equal(piston.genome.seed,'e0126de4ff158eca0966e7627917001d5d355ca7139ec64375f2343cb954623a');
 assert.equal(piston.record.publicId,0xd41e5bd4);
 assert.equal(piston.runIndex,historical.runs.length+7);
 assert.equal(first.record.publicId,0x8546076e);
 assert.equal(first.runIndex,historical.runs.length+5);
 assert.equal(verifySparkArt(pistonSave),true);
 assert.equal(verifySparkArt(firstSave),true);
 assert.equal(new DataView(pistonSave.buffer).getUint32(24712,true),0xd41e5bd4);
 assert.equal(new DataView(firstSave.buffer).getUint32(24712,true),0x8546076e);
 assert.notEqual(piston.genome.seed,first.genome.seed);
});
test('if Pistonwyrm source is unavailable, past Umbrascale cartridge remains valid and Pistonwyrm is refused',async t=>{
 localFetch(t,new Map([[FILE,null]]));
 const table=await loadTable();
 assert.equal(table.runs.length,historical.runs.length+6);
 assert.equal((await readSparkFile(umbra,table)).genome.names[1],'Umbrascale');
 await assert.rejects(()=>readSparkFile(bytes,table),/Recorded run is not in this cartridge table/);
});
for(const [label,mutate] of [
 ['wrong hardware identity',x=>{x.job_id='another-job';}],
 ['source count digest',x=>{x.counts_digest_sha256='0'.repeat(64);}],
 ['wrong backend',x=>{x.backend='rigetti.sim.qvm';}],
 ['wrong PUB order',x=>{x.runs.reverse();}],
 ['rehashed replacement counts',x=>{x.runs[1].counts['00']++;x.runs[1].counts['11']--;x.runs[1].counts_sha256=sha256Hex(canon(x.runs[1].counts));}],
 ['missing measurement shot',x=>{x.runs[1].counts['00']--; }],
 ['duplicate PUB',x=>{x.runs[1]=structuredClone(x.runs[0]);}],
])test('new physical source rejects '+label+' before cartridge admission',async t=>{
 const bad=structuredClone(pinned);mutate(bad);localFetch(t,new Map([[FILE,bad]]));
 await assert.rejects(()=>loadTable(),/IBM hardware (supplement|run)/);
});
test('forged Pistonwyrm progress is not allowed into the native game',async t=>{
 localFetch(t);const table=await loadTable(),fake=JSON.parse(new TextDecoder().decode(bytes));
 fake.progress.bond=100;
 await assert.rejects(()=>readSparkFile(new TextEncoder().encode(JSON.stringify(fake)),table),/digest/);
});
