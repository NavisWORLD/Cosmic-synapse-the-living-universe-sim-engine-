import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {loadTable} from '../spark-beasts/runs.mjs';
import {readSparkFile,checkedSparkSave} from './spark-file.mjs';
import {verifySparkArt} from './cartridge.mjs';
import {canon,sha256Hex} from '../spark-beasts/hash.mjs';
const FILE='ibm-zeref-heart-sound-20261010-supplement.json';
const read=p=>JSON.parse(readFileSync(new URL(p,import.meta.url),'utf8'));
const source=read('./fixtures/zeref-heart-sound-20261010-physics.json');
const historical=read('../spark-beasts/data/quantum-runs.json');
const bytes=new Uint8Array(readFileSync(new URL('./fixtures/zeref-heart-sound-20261010.qbeast',import.meta.url)));
function localFetch(t,mutate=null){
 t.mock.method(globalThis,'fetch',async url=>{
  try{const value=JSON.parse(readFileSync(url,'utf8'));if(new URL(url).pathname.endsWith('/'+FILE)&&mutate)mutate(value);return Response.json(value);}
  catch(e){if(e.code==='ENOENT')return new Response('',{status:404});throw e;}
 });
}
test('new Zeref genome is admitted by the native cartridge after every existing measured source',async t=>{
 localFetch(t);const table=await loadTable(),beast=await readSparkFile(bytes,table),save=checkedSparkSave(beast,table);
 assert.equal(beast.genome.names[1],'Scorchwyrm');assert.equal(beast.genome.body,'dragonling');
 assert.equal(beast.runIndex,historical.runs.length+13);assert.equal(table.runs.length,historical.runs.length+18);
 assert.equal(new DataView(save.buffer).getUint32(24712,true),0xdeada969);assert.equal(verifySparkArt(save),true);
 assert.deepEqual(table.runs.slice(0,historical.runs.length),historical.runs);assert.deepEqual(table.totals,historical.totals);
});
test('the new cartridge supplement retains both exact physical source PUBs',()=>{
 const supplement=read('../spark-beasts/data/'+FILE);
 assert.equal(source.job_status,'DONE');assert.equal(source.physical_job_total_shots,20480);
 assert.equal(sha256Hex(canon(source.measurements)),source.counts_digest_sha256);
 for(const [i,basis] of ['bell_zz','bell_xx'].entries())assert.deepEqual(supplement.runs[i].counts,source.measurements[basis]);
});
test('a rehashed replacement measurement cannot enter the native game',async t=>{
 localFetch(t,data=>{data.runs[1].counts['00']--;data.runs[1].counts['11']++;data.runs[1].counts_sha256=sha256Hex(canon(data.runs[1].counts));});
 await assert.rejects(()=>loadTable(),/IBM hardware run/);
});
