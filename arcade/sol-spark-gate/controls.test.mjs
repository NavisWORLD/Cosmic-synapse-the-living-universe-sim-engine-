import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {HANDHELD_INPUTS,normalizeHandheldInput,applyHandheldInput} from './controls.mjs';

test('every Beast Boy control maps to the existing EmulatorJS GBA index',()=>{
 assert.deepEqual(HANDHELD_INPUTS,{up:4,down:5,left:6,right:7,a:8,b:0,start:3,select:2,l:10,r:11});
 const calls=[],gm={simulateInput:(player,index,value)=>calls.push([player,index,value])};
 for(const [button,index] of Object.entries(HANDHELD_INPUTS)){
  assert.deepEqual(normalizeHandheldInput(button,true),{button,index,down:true});
  assert.equal(applyHandheldInput(gm,button,true),true);
  assert.equal(applyHandheldInput(gm,button,false),true);
 }
 assert.equal(calls.length,20);
 assert.equal(normalizeHandheldInput('nope',true),null);
 assert.equal(normalizeHandheldInput('a','true'),null);
 assert.equal(applyHandheldInput(gm,'nope',true),false);
});


test('live Pages controller assets are cache-busted for Android/tablet clients',()=>{
 const gate=readFileSync(new URL('./index.html',import.meta.url),'utf8');
 const handheld=readFileSync(new URL('./handheld.html',import.meta.url),'utf8');
 assert.match(gate,/handheld\.html\?controller=beastboy39/);
 assert.match(gate,/app\.mjs\?controller=beastboy39/);
 assert.match(handheld,/handheld\.mjs\?controller=beastboy39/);
});
