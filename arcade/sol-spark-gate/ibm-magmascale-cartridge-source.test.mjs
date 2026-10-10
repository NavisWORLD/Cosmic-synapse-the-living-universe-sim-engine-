import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {loadTable} from '../spark-beasts/runs.mjs';
import {readSparkFile,checkedSparkSave} from './spark-file.mjs';
import {verifySparkArt} from './cartridge.mjs';
import {sha256Hex,canon} from '../spark-beasts/hash.mjs';
const FILE='ibm-magmascale-20261009-supplement.json',JOB='db4nlt2mb58s7389er6g';
const read=p=>JSON.parse(readFileSync(new URL(p,import.meta.url),'utf8'));
const historical=read('../spark-beasts/data/quantum-runs.json');
const source=read('./fixtures/ibm-magmascale-20261009-receipt.json');
const measured=read('../spark-beasts/data/'+FILE);
const bytes=new Uint8Array(readFileSync(new URL('./fixtures/ibm-magmascale-20261009.qbeast',import.meta.url)));
const umbra=new Uint8Array(readFileSync(new URL('./fixtures/ibm-final-live-umbrascale.qbeast',import.meta.url)));
const piston=new Uint8Array(readFileSync(new URL('./fixtures/ibm-pistonwyrm-20261009.qbeast',import.meta.url)));
function localFetch(t,overrides=new Map()){
 t.mock.method(globalThis,'fetch',async url=>{
  const n=new URL(url).pathname.split('/').at(-1);
  if(overrides.has(n)){const val=overrides.get(n);return val===null?new Response('',{status:404}):Response.json(val);}
  try{return new Response(readFileSync(url));}catch(e){if(e.code==='ENOENT')return new Response('',{status:404});throw e;}
 });
}
test('third NEW real IBM hardware fixture matches recorded physical counts and hash',async t=>{
 localFetch(t);const table=await loadTable();
 assert.equal(source.source_class,'RECORDED_IBM_HARDWARE');assert.equal(source.job_status,'DONE');assert.equal(source.job_id,JOB);assert.equal(source.shot_count,16384);
 assert.equal(sha256Hex(canon(source.measurements)),source.counts_digest_sha256);
 assert.equal(source.counts_digest_sha256,'d6d39ff479cd9aaf4d80eb16cb42bb393ea17fe2eaa9e23cdb151245165fd9d6');
 assert.equal(measured.source_receipt_url,'https://github.com/NavisWORLD/The-beast-box-/actions/runs/38005372001/artifacts/11650509285');
 assert.equal(table.runs.length,historical.runs.length+18);
 assert.deepEqual(table.runs.slice(0,historical.runs.length),historical.runs);assert.deepEqual(table.totals,historical.totals);
 for(const [index,basis] of ['bell_zz','bell_xx'].entries()){
  const row=measured.runs[index];
  assert.equal(row.pub_index,index);assert.deepEqual(row.counts,source.measurements[basis]);assert.equal(row.counts_sha256,sha256Hex(canon(row.counts)));assert.deepEqual(table.byKey.get(row.key),row);
 }
});
test('three real measured dragons have distinct exact QBEAST identity in original native cartridge',async t=>{
 localFetch(t);const table=await loadTable();
 const third=await readSparkFile(bytes,table),thirdSave=checkedSparkSave(third,table);
 assert.equal(third.genome.names[1],'Magmascale');
 assert.equal(third.genome.names[2],'Emberclaw');
 assert.equal(third.genome.seed,'98d38e4ca857ffbd878a57eb8f6b8dc5be199b1e9f565dc56945579bc9d5e358');
 assert.equal(third.genome.body,'dragonling');assert.equal(third.record.publicId,0xe9850e96);
 assert.equal(third.runIndex,historical.runs.length+9);
 assert.equal(verifySparkArt(thirdSave),true);assert.equal(new DataView(thirdSave.buffer).getUint32(24712,true),0xe9850e96);
 const old1=await readSparkFile(umbra,table),old2=await readSparkFile(piston,table);
 assert.equal(old1.record.publicId,0x8546076e);assert.equal(old2.record.publicId,0xd41e5bd4);
 assert.equal(old1.runIndex,historical.runs.length+5);assert.equal(old2.runIndex,historical.runs.length+7);
 assert.equal(verifySparkArt(checkedSparkSave(old1,table)),true);
 assert.equal(verifySparkArt(checkedSparkSave(old2,table)),true);
});
test('unavailable Magmascale supplement refuses its admission but leaves prior two intact',async t=>{
 localFetch(t,new Map([[FILE,null]]));
 const table=await loadTable();assert.equal(table.runs.length,historical.runs.length+8);
 assert.equal((await readSparkFile(umbra,table)).record.publicId,0x8546076e);
 assert.equal((await readSparkFile(piston,table)).record.publicId,0xd41e5bd4);
 await assert.rejects(()=>readSparkFile(bytes,table),/Recorded run is not in this cartridge table/);
});
for(const [label,mutate] of [
 ['source class',x=>{x.source_class='SIMULATOR';}],
 ['source digest',x=>{x.counts_digest_sha256='0'.repeat(64);}],
 ['backend',x=>{x.backend='rigetti.sim.qvm';}],
 ['job id',x=>{x.job_id='wrong';}],
 ['rehashed altered measurements',x=>{x.runs[1].counts['00']++;x.runs[1].counts['11']--;x.runs[1].counts_sha256=sha256Hex(canon(x.runs[1].counts));}],
 ['duplicate row',x=>{x.runs[1]=structuredClone(x.runs[0]);}],
])test('Magmascale corrupted '+label+' is refused',async t=>{
 const bad=structuredClone(measured);mutate(bad);localFetch(t,new Map([[FILE,bad]]));
 await assert.rejects(()=>loadTable(),/IBM hardware (supplement|run)/);
});
test('forged third dragon progress never enters native cartridge',async t=>{
 localFetch(t);const table=await loadTable(),bad=JSON.parse(new TextDecoder().decode(bytes));
 bad.progress.bond=100;await assert.rejects(()=>readSparkFile(new TextEncoder().encode(JSON.stringify(bad)),table),/digest/);
});
