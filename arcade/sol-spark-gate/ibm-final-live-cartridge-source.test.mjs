import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {loadTable} from '../spark-beasts/runs.mjs';
import {readSparkFile,checkedSparkSave} from './spark-file.mjs';
import {verifySparkArt} from './cartridge.mjs';
import {canon,sha256Hex} from '../spark-beasts/hash.mjs';
const FILE='ibm-final-live-20261009-supplement.json';
const read=p=>JSON.parse(readFileSync(new URL(p,import.meta.url),'utf8'));
const source=read('./fixtures/ibm-final-live-20261009-receipt.json');
const historical=read('../spark-beasts/data/quantum-runs.json');
const bytes=new Uint8Array(readFileSync(new URL('./fixtures/ibm-final-live-umbrascale.qbeast',import.meta.url)));
function localFetch(t,mutate=null){
 t.mock.method(globalThis,'fetch',async url=>{
  try{
   const value=JSON.parse(readFileSync(url,'utf8'));
   if(new URL(url).pathname.endsWith('/'+FILE)&&mutate)mutate(value);
   return Response.json(value);
  }catch(e){if(e.code==='ENOENT')return new Response('',{status:404});throw e;}
 });
}
test('fresh Umbrascale enters the real cartridge save with its measured identity after all prior sources',async t=>{
 localFetch(t);
 const table=await loadTable(),beast=await readSparkFile(bytes,table),save=checkedSparkSave(beast,table);
 assert.equal(beast.genome.names[1],'Umbrascale');
 assert.equal(beast.genome.body,'dragonling');
 assert.equal(beast.runIndex,historical.runs.length+5);
 assert.equal(table.runs.length,historical.runs.length+6);
 assert.equal(new DataView(save.buffer).getUint32(24712,true),0x8546076e);
 assert.equal(verifySparkArt(save),true);
 assert.deepEqual(table.runs.slice(0,historical.runs.length),historical.runs);
 assert.deepEqual(table.totals,historical.totals);
});
test('fresh source retains the exact physical count receipt and both pinned PUBs',()=>{
 const supplement=read('../spark-beasts/data/'+FILE);
 assert.equal(source.job_status,'DONE');
 assert.equal(sha256Hex(canon(source.measurements)),source.counts_digest_sha256);
 assert.equal(supplement.counts_digest_sha256,source.counts_digest_sha256);
 for(const [i,basis] of ['bell_zz','bell_xx'].entries()){
  assert.equal(supplement.runs[i].pub_index,i);
  assert.deepEqual(supplement.runs[i].counts,source.measurements[basis]);
  assert.equal(supplement.runs[i].counts_sha256,sha256Hex(canon(source.measurements[basis])));
 }
});
test('fresh supplement refuses rehashed replacement measurements before admission',async t=>{
 localFetch(t,data=>{data.runs[1].counts['00']--;data.runs[1].counts['11']++;data.runs[1].counts_sha256=sha256Hex(canon(data.runs[1].counts));});
 await assert.rejects(()=>loadTable(),/IBM hardware run/);
});
