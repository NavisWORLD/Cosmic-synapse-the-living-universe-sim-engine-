import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {loadTable} from '../spark-beasts/runs.mjs';
import {readSparkFile,checkedSparkSave} from './spark-file.mjs';
import {sha256Hex,canon} from '../spark-beasts/hash.mjs';
import {batteryName} from './battery.mjs';
const historical=JSON.parse(readFileSync(new URL('../spark-beasts/data/quantum-runs.json',import.meta.url)));
function localFetch(t,tamper=false){t.mock.method(globalThis,'fetch',async url=>{
 if(tamper&&String(url).includes('ibm-bone-pig-20261010-supplement.json')){
  const source=JSON.parse(readFileSync(url));source.runs[0].counts['00']++;return Response.json(source);
 }
 try{return new Response(readFileSync(url));}catch(e){if(e.code==='ENOENT')return new Response('',{status:404});throw e;}
});}
test('original Mr Bone Pig is appended without shifting established native source indices',async t=>{
 localFetch(t);const table=await loadTable();
 assert.equal(table.runs.length,historical.runs.length+20);
 assert.deepEqual(table.runs.slice(0,historical.runs.length),historical.runs);
 assert.deepEqual(table.totals,historical.totals);
 const row=table.byKey.get('db4pa784qg6s73c2g5vg:bell-xx');assert.ok(row);
 assert.equal(row.backend,'ibm_marrakesh');assert.equal(row.shots,4096);
 assert.equal(row.counts_sha256,sha256Hex(canon(row.counts)));
 const beast=await readSparkFile(new Uint8Array(readFileSync(new URL('./fixtures/ibm-bone-pig-20261010.qbeast',import.meta.url))),table);
 assert.equal(beast.genome.seed,'28a3f13ee58a62a78bf2b03143f2d88210ad037e325870e947037f2a0331222c');
 assert.equal(beast.record.publicId,0x62603ee3);assert.equal(beast.genome.body,'pup');assert.equal(beast.genome.names[1],'Rimepup');
 assert.match(batteryName(checkedSparkSave(beast,table)),/^lost-cosmos-62603ee3-/);
});
test('tampered recorded Pig counts are rejected',async t=>{
 localFetch(t,true);await assert.rejects(()=>loadTable(),/IBM hardware/);
});
