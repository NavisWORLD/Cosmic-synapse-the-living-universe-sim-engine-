import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { buildGenome } from '../spark-beasts/genome.mjs';
import { sparkRecord, cageSave, buildSave, buildGrowth, attachGrowth } from '../spark-beasts/trade.mjs';
import { sparkSave, attachSparkArt, verifySparkArt, cartridgeSprite, SPARK_META, SPARK_TILES } from './cartridge.mjs';
import { crc32 } from '../lost-cosmos/mailbox.mjs';
const table=JSON.parse(readFileSync(new URL('../spark-beasts/data/quantum-runs.json',import.meta.url)));
const genome=buildGenome({focus:65,calm:72,spark:48},table.runs[0],'CORY');
test('the GBA import includes the actual Spark creature art',()=>{
 const original=cageSave(sparkRecord(genome,0),buildSave,buildGrowth,attachGrowth),sav=sparkSave(genome,0,table);
 assert.equal(sav[24837]&2,2);
 assert.deepEqual(sav.slice(24864,24928),original.slice(24864,24928));
 assert.deepEqual(sav.slice(25476,25540),original.slice(25476,25540));
 assert.deepEqual(sav.slice(24960,25472),cartridgeSprite(genome,1).tiles);
 assert.notDeepEqual(sav.slice(SPARK_TILES,SPARK_TILES+512),sav.slice(SPARK_TILES+512));
 assert.equal(verifySparkArt(sav),true);
});
test('journey updates preserve every byte outside the art receipt and supplied mailbox art',()=>{
 const sav=sparkSave(genome,0,table),p=sparkRecord(genome,0).profile;
 const r=sav.subarray(1024,1276);r.fill(0);r.set([76,67,82,49,1,1,0,0]);r.set([p.species,2,28,85],8);
 const dv=new DataView(r.buffer,r.byteOffset,r.byteLength);dv.setUint32(16,p.publicId,true);dv.setUint32(20,p.gameSeed,true);r[26]=p.family;dv.setUint32(248,crc32(r.slice(0,248)),true);
 sav.fill(0x5a,8192,24704);sav.fill(0x35,25600,31744);
 const next=attachSparkArt(sav,genome,0,table,{journey:true});
 for(let i=0;i<32768;i++)if(!(i>=24704&&i<24832)&&!(i>=24928&&i<25476)&&i!==24837&&i<31744)assert.equal(next[i],sav[i],`byte ${i}`);
 const bad=sav.slice();bad[1040]^=1;assert.throws(()=>attachSparkArt(bad,genome,0,table,{journey:true}),/checksum/);
 for(const o of [24704,24708,24712,24724,24928,31744]){const bad=next.slice();bad[o]^=1;assert.throws(()=>verifySparkArt(bad));}
});
test('all eight island shapes reduce to deterministic 32px cartridge art',()=>{
 const islands=new Set();
 for(let i=0;i<80&&islands.size<8;i++){
  const g=buildGenome({focus:(i*17)%101,calm:(i*23)%101,spark:(i*31)%101},table.runs[i],'CORY');
  islands.add(g.island);const s=sparkSave(g,i,table);assert.equal(verifySparkArt(s),true);
  for(let stage=1;stage<=3;stage++){const a=cartridgeSprite(g,stage);assert.deepEqual(a,cartridgeSprite(g,stage));assert.ok(a.pixels.some(p=>p>0));assert.equal(a.tiles.length,512);}
 }
 assert.equal(islands.size,8);
});
