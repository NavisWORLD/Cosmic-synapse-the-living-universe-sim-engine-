import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {buildGenome} from '../spark-beasts/genome.mjs';
import {sparkRecord} from '../spark-beasts/trade.mjs';
import {sparkSave} from './cartridge.mjs';
import {crc32,MAILBOX_OFFSET} from '../lost-cosmos/mailbox.mjs';
const {checkedCloudBattery,nativeIdentity}=await import('./identity-handoff.mjs');
const table=JSON.parse(readFileSync(new URL('../spark-beasts/data/quantum-runs.json',import.meta.url)));
const genome=buildGenome({focus:65,calm:72,spark:48},table.runs[0],'CORY');
const starter=sparkSave(genome,0,table),profile=sparkRecord(genome,0).profile;
function earned(){
 const bytes=starter.slice();bytes.set([76,67,86,53,5]);
 const r=bytes.subarray(1024,1276);r.fill(0);r.set([76,67,82,49,1,1,0,0]);r.set([profile.species,2,28,85],8);
 const dv=new DataView(r.buffer,r.byteOffset,r.byteLength);dv.setUint32(16,profile.publicId,true);dv.setUint32(20,profile.gameSeed,true);r[26]=profile.family;dv.setUint32(248,crc32(r.subarray(0,248)),true);
 bytes.fill(0x5a,8192,24000);return bytes;
}
const encode=bytes=>Buffer.from(bytes).toString('base64');
test('a cloud native handoff preserves every earned battery byte',()=>{
 const bytes=earned();assert.deepEqual(checkedCloudBattery(encode(bytes),starter),bytes);
 assert.deepEqual(checkedCloudBattery(encode(starter),starter),starter);
});
test('wrong identity, malformed encoding and damaged roster are rejected before native installation',()=>{
 const other=sparkSave(buildGenome({focus:1,calm:2,spark:3},table.runs[1],'OTHER'),1,table);
 const corrupt=earned();corrupt[1040]^=1;
 for(const input of [null,'',encode(other),encode(corrupt),'x'.repeat(43692),'not-a-battery'])assert.throws(()=>checkedCloudBattery(input,starter));
});
test('a verified starter is mailbox-ready, never claimed as an imported native companion',()=>{
 const status=nativeIdentity(starter,profile);
 assert.equal(status.status,'mailbox-ready');assert.equal(status.source,'local-mailbox');
 assert.equal(status.publicId,profile.publicId);assert.equal(status.gameSeed,profile.gameSeed);
});
test('only a valid matching native roster confirms the imported identity and real progress',()=>{
 const bytes=earned(),status=nativeIdentity(bytes,profile);
 assert.equal(status.status,'imported');assert.equal(status.source,'native-battery-checkpoint');
 assert.equal(status.level,28);assert.equal(status.stage,2);
 const bad=bytes.slice();bad[1040]^=1;assert.equal(nativeIdentity(bad,profile).status,'invalid');
 const foreign={...profile,gameSeed:profile.gameSeed^1};assert.equal(nativeIdentity(bytes,foreign).status,'invalid');
});
test('a consumed mailbox without matching roster reports missing with an explicit recovery action',()=>{
 const bytes=starter.slice();bytes[MAILBOX_OFFSET+5]&=~1;
 new DataView(bytes.buffer).setUint32(MAILBOX_OFFSET+640,crc32(bytes.subarray(MAILBOX_OFFSET,MAILBOX_OFFSET+640)),true);
 const status=nativeIdentity(bytes,profile);assert.equal(status.status,'missing');assert.match(status.message,/CONTINUE|save|recover/i);
});
