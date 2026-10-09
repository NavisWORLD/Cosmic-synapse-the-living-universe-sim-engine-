import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {buildGenome} from '../spark-beasts/genome.mjs';
import {canon,sha256Hex} from '../spark-beasts/hash.mjs';
const data=JSON.parse(readFileSync(new URL('../spark-beasts/data/ibm-fez-20261009-supplement.json',import.meta.url)));
test('actual IBM hardware PUBs are distinct, unaltered, integrity-checked',()=>{
 assert.equal(data.source_class,'RECORDED_IBM_HARDWARE');
 assert.equal(data.job_id,'db4kcfklf4us73c2sjb0');
 assert.deepEqual(data.runs.map(x=>x.pub_index),[0,1]);
 assert.deepEqual(data.runs.map(x=>x.key),['db4kcfklf4us73c2sjb0:bell-zz','db4kcfklf4us73c2sjb0:bell-xx']);
 for(const row of data.runs){
  assert.equal(row.backend,'ibm_fez');
  assert.equal(Object.values(row.counts).reduce((a,b)=>a+b,0),256);
  assert.equal(sha256Hex(canon(row.counts)),row.counts_sha256);
 }
});
test('new Calderscale real IBM Bell XX creature regenerates in original cartridge core',()=>{
 const r=data.runs[1],gen=buildGenome({focus:90,calm:70,spark:90},r,'NavisWORLD-moon-3',10);
 assert.equal(gen.seed,'ccb5b741b54f1951d29608d03557957fed7de31180e1b24daeb6c590e89888d5');
 assert.equal(gen.names[1],'Calderscale');
 assert.equal(gen.body,'dragonling');
});
test('original Emberlet Bell ZZ creature identity remains independently replayable',()=>{
 const gen=buildGenome({focus:40,calm:10,spark:100},data.runs[0],'NavisWORLD-dragon-21',10);
 assert.equal(gen.seed,'a963d61a7e3fba58dab1dca64945ccad2544b3c66615459ab59f786a5b34f908');
 assert.equal(gen.body,'dragonling');
});
