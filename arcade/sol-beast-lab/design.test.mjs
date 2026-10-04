import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { ISLANDS, createBeast, exportSave, readProgress, ARCHIVE_SHA256 } from './design.mjs';
import { renderSprite, packTiles } from './sprites.mjs';
import { MAILBOX_OFFSET, MAILBOX_BYTES, crc32, profileFromBcp1 } from '../lost-cosmos/mailbox.mjs';

const archive = new Uint8Array(JSON.parse(readFileSync(new URL('./archive.json', import.meta.url))).bytes);
const birth = (island = 0, extra = {}) => createBeast({ island, nonce: 'CORY-SOL-001', focus: 65, calm: 72, spark: 48, ...extra }, archive);
test('the nursery replays the exact preserved 8192-byte cartridge archive', () => {
  assert.equal(archive.length, 8192);
  assert.equal(createHash('sha256').update(archive).digest('hex'), ARCHIVE_SHA256);
});
test('all eight island lineages produce valid, deterministic, balanced public imports and distinct three-stage art', () => {
  assert.equal(ISLANDS.length, 8);
  const identities = new Set(), silhouettes = new Set();
  for (let island = 0; island < 8; island++) {
    const a = birth(island), b = birth(island);
    assert.deepEqual(a, b);
    identities.add(a.publicId);
    profileFromBcp1(a.bcp1);
    assert.equal([...a.bcp1.slice(8,18)].reduce((n,v)=>n+v,0),500);
    assert.equal(ISLANDS[island].forms.length,3);
    const stages = Array.from({length:3}, (_,s)=>renderSprite(a,s));
    assert.notDeepEqual(stages[0].pixels,stages[1].pixels);
    assert.notDeepEqual(stages[1].pixels,stages[2].pixels);
    silhouettes.add([...stages[0].pixels].map(n=>Number(n>0)).join(''));
    const sav = exportSave(a);
    assert.equal(sav.length,32768);
    assert.equal(sav[MAILBOX_OFFSET+5],3);
    const mail = sav.slice(MAILBOX_OFFSET,MAILBOX_OFFSET+MAILBOX_BYTES);
    assert.equal(new DataView(mail.buffer).getUint32(640,true),crc32(mail.slice(0,640)));
    assert.deepEqual(mail.slice(128,640),packTiles(stages[0].pixels));
    assert.ok(stages[0].pixels.every(n=>n<13)); // Signature palette entries never become visible.
  }
  assert.equal(identities.size,8);
  assert.equal(silhouettes.size,8);
});
test('trait directions are meaningful without inflating the fixed stat budget', () => {
  for(const [trait,indexes] of [['focus',[2,3]],['calm',[0,4]],['spark',[1,5]]]) {
    const low=birth(0,{[trait]:0}), high=birth(0,{[trait]:100});
    const score=b=>indexes.reduce((n,i)=>n+b.bcp1[8+i],0);
    assert.ok(score(high)>score(low),trait);
  }
  for(const bad of [-1,101,NaN,1.5,'50']) assert.throws(()=>birth(0,{focus:bad}));
  assert.throws(()=>birth(8)); assert.throws(()=>birth(0,{nonce:''}));
  assert.notEqual(birth().publicId,birth(0,{nonce:'CORY-SOL-002'}).publicId);
});
function earnedSave(beast) {
  const sav=exportSave(beast); sav.fill(0x39,0,MAILBOX_OFFSET);
  const r=sav.subarray(1024,1276); r.fill(0); r.set([76,67,82,49,1,1,0,0]);
  r.set([beast.species,2,28,85],8); const dv=new DataView(r.buffer,r.byteOffset,r.byteLength);
  dv.setUint16(12,180,true); dv.setUint32(16,beast.publicId,true); dv.setUint32(20,beast.gameSeed,true);
  r[24]=90; r[25]=70; r[26]=beast.family; dv.setUint32(248,crc32(r.slice(0,248)),true);
  sav[MAILBOX_OFFSET+5]=6;
  new DataView(sav.buffer).setUint32(MAILBOX_OFFSET+640,crc32(sav.slice(MAILBOX_OFFSET,MAILBOX_OFFSET+640)),true);
  return sav;
}
test('reading earned game growth preserves every journey byte outside the mailbox', () => {
  const beast=birth(), old=earnedSave(beast), progress=readProgress(beast,old);
  assert.equal(progress.stage,2); assert.equal(progress.level,28); assert.equal(progress.bond,85);
  const next=exportSave(beast,{baseSave:old});
  assert.deepEqual(next.slice(0,MAILBOX_OFFSET),old.slice(0,MAILBOX_OFFSET));
  assert.deepEqual(next.slice(MAILBOX_OFFSET+MAILBOX_BYTES),old.slice(MAILBOX_OFFSET+MAILBOX_BYTES));
  assert.deepEqual(next.slice(MAILBOX_OFFSET+128,MAILBOX_OFFSET+640),packTiles(renderSprite(beast,2).pixels));
  const bad=old.slice(); bad[1032]^=1; assert.throws(()=>readProgress(beast,bad),/checksum/);
  assert.throws(()=>readProgress(birth(1),old),/belong/);
  assert.throws(()=>exportSave(beast,{baseSave:new Uint8Array(2)}));
});
