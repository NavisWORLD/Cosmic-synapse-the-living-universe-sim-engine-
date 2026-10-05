import test from 'node:test';import assert from 'node:assert/strict';import {readFileSync} from 'node:fs';
import {readSparkFile,checkedSparkSave} from './spark-file.mjs';import {verifySparkArt} from './cartridge.mjs';
import {sparkRecord} from '../spark-beasts/trade.mjs';import {buildGenome} from '../spark-beasts/genome.mjs';
const table=JSON.parse(readFileSync(new URL('../spark-beasts/data/quantum-runs.json',import.meta.url)));
test('checked Spark records retain their public identity and starter forms',()=>{const genome=buildGenome({focus:65,calm:72,spark:48},table.runs[0],'CORY'),record=sparkRecord(genome,0);assert.equal(verifySparkArt(checkedSparkSave({genome,record,runIndex:0},table)),true);});
test('public Spark files reject unsupported cards before admission',async()=>{
 await assert.rejects(()=>readSparkFile(new Uint8Array(524289),table),/large/);
 await assert.rejects(()=>readSparkFile(new TextEncoder().encode('{}'),table),/Choose a Spark/);
});
test('the current Vercel QBEAST1 golden creature reaches the cartridge with the same public identity',async()=>{
 const bytes=new Uint8Array(readFileSync(new URL('./fixtures/vercel-spark.qbeast',import.meta.url))),beast=await readSparkFile(bytes,table);
 const sav=checkedSparkSave(beast,table);assert.equal(verifySparkArt(sav),true);
 assert.deepEqual(sav.slice(24864,24928),beast.record.profile.bcp1);
 const bad=JSON.parse(new TextDecoder().decode(bytes));bad.progress.bond=100;
 await assert.rejects(()=>readSparkFile(new TextEncoder().encode(JSON.stringify(bad)),table),/digest/);
 bad.profile.seed='0'.repeat(64);await assert.rejects(()=>readSparkFile(new TextEncoder().encode(JSON.stringify(bad)),table),/reproduce/);
});
