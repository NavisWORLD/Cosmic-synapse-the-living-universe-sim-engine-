import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {buildGenome} from '../spark-beasts/genome.mjs';
import {sparkRecord} from '../spark-beasts/trade.mjs';
import {sparkSave} from './cartridge.mjs';
import {crc32} from '../lost-cosmos/mailbox.mjs';
import {batteryName,chooseBattery,prepareBattery} from './battery.mjs';
const table=JSON.parse(readFileSync(new URL('../spark-beasts/data/quantum-runs.json',import.meta.url)));
const genome=buildGenome({focus:65,calm:72,spark:48},table.runs[0],'CORY');
const starter=sparkSave(genome,0,table),profile=sparkRecord(genome,0).profile;
function journey(){
 const save=starter.slice();save.set([76,67,86,53,5]);save.fill(0x5a,8192,24000);
 const r=save.subarray(1024,1276);r.fill(0);r.set([76,67,82,49,1,1,0,0]);r.set([profile.species,2,28,85],8);
 const dv=new DataView(r.buffer,r.byteOffset,r.byteLength);dv.setUint32(16,profile.publicId,true);dv.setUint32(20,profile.gameSeed,true);r[26]=profile.family;dv.setUint32(248,crc32(r.slice(0,248)),true);
 return save;
}
test('returning with a starter retains every earned native battery byte',()=>{
 const earned=journey();assert.equal(chooseBattery(starter,earned),earned);
 assert.deepEqual(chooseBattery(starter,earned),earned);
 assert.equal(chooseBattery(starter,earned,{journey:true}),starter);
 const other=sparkSave(buildGenome({focus:1,calm:2,spark:3},table.runs[1],'OTHER'),1,table);
 assert.notEqual(batteryName(starter),batteryName(other));assert.throws(()=>chooseBattery(starter,other),/another/);
 const corrupt=earned.slice();corrupt[1040]^=1;assert.throws(()=>chooseBattery(starter,corrupt),/checksum/);
});
test('namespace migration keeps unrelated and damaged batteries untouched',()=>{
 const earned=journey(),old='/data/saves/lost-cosmos.srm',files=new Map([[old,earned]]);
 const fs={analyzePath:p=>({exists:p==='/data/saves'||files.has(p)}),mkdir(){},readFile:p=>files.get(p),writeFile:(p,b)=>files.set(p,b)};
 assert.equal(prepareBattery(fs,starter).resumed,true);assert.equal(files.get(old),earned);
 assert.deepEqual(files.get(`/data/saves/${batteryName(starter)}.srm`),earned);
 const corrupt=earned.slice();corrupt[1040]^=1;const path=`/data/saves/${batteryName(starter)}.srm`;files.set(path,corrupt);
 assert.throws(()=>prepareBattery(fs,starter));assert.equal(files.get(path),corrupt);
});
