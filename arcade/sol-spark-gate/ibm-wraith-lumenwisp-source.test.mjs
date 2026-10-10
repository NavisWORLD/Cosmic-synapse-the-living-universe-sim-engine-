import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {loadTable} from '../spark-beasts/runs.mjs';
import {sha256Hex,canon} from '../spark-beasts/hash.mjs';

const historical=JSON.parse(readFileSync(new URL('../spark-beasts/data/quantum-runs.json',import.meta.url),'utf8'));
const sources=[
 {file:'ibm-wraith-20261010-supplement.json',job:'db4rg5klf4us73c34tqg',digest:'de17933e5400a6c18467bd3a454af5f32147135f517c8ef656fc0e5d36ec5377'},
 {file:'ibm-lumenwisp-20261010-supplement.json',job:'db4sba4lf4us73c36910',digest:'62effbad67bf75e985c0250e0c8a6b1d94f92d8c9e46d25e52a81975461bcce7',parent:'bb-4a61a8d5'},
];
function localFetch(t,overrides=new Map()){
 t.mock.method(globalThis,'fetch',async url=>{
  const name=new URL(url).pathname.split('/').at(-1);
  if(overrides.has(name)){const v=overrides.get(name);return v===null?new Response('',{status:404}):Response.json(v);}
  try{return new Response(readFileSync(url));}catch(e){if(e.code==='ENOENT')return new Response('',{status:404});throw e;}
 });
}
test('Wraith and NEW physical Lumenwisp are genuine independently sourced additive IBM jobs',async t=>{
 localFetch(t);const table=await loadTable();
 assert.equal(table.runs.length,historical.runs.length+18);
 assert.deepEqual(table.runs.slice(0,historical.runs.length),historical.runs);
 assert.deepEqual(table.totals,historical.totals);
 for(let index=0;index<sources.length;index++){
  const source=sources[index],actual=JSON.parse(readFileSync(new URL('../spark-beasts/data/'+source.file,import.meta.url),'utf8'));
  assert.equal(actual.source_class,'RECORDED_IBM_HARDWARE');
  assert.equal(actual.job_id,source.job);assert.equal(actual.counts_digest_sha256,source.digest);
  if(source.parent)assert.equal(actual.parent_qbeast_id,source.parent);
  const expectedIndex=historical.runs.length+14+index*2;
  for(let pub=0;pub<2;pub++){
   const row=actual.runs[pub];
   assert.equal(row.pub_index,pub);assert.equal(row.shots,4096);assert.equal(row.backend,'ibm_marrakesh');
   assert.equal(row.counts_sha256,sha256Hex(canon(row.counts)));
   assert.deepEqual(table.runs[expectedIndex+pub],row);
   assert.deepEqual(table.byKey.get(row.key),row);
  }
 }
});
test('missing Wraith source leaves earlier native table safe and refuses later Lumenwisp source',async t=>{
 localFetch(t,new Map([['ibm-wraith-20261010-supplement.json',null]]));
 const table=await loadTable();
 assert.equal(table.runs.length,historical.runs.length+14);
 assert.equal(table.byKey.has('db4sba4lf4us73c36910:bell-xx'),false);
});
for(const [file,change] of [
 ['ibm-wraith-20261010-supplement.json',o=>{o.runs[0].counts['00']++;}],
 ['ibm-lumenwisp-20261010-supplement.json',o=>{o.parent_qbeast_id='bb-counterfeit';o.runs[0].job_id='WRONG';}],
 ['ibm-lumenwisp-20261010-supplement.json',o=>{o.runs[1].counts['01']+=1;o.runs[1].counts_sha256=sha256Hex(canon(o.runs[1].counts));}],
])test('reject tampered new physical source '+file,async t=>{
 const source=JSON.parse(readFileSync(new URL('../spark-beasts/data/'+file,import.meta.url),'utf8'));change(source);
 localFetch(t,new Map([[file,source]]));
 await assert.rejects(()=>loadTable(),/IBM hardware (supplement|run)/);
});
