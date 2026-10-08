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


test('live Pages controller assets are cache-busted for mobile clients',()=>{
 const gate=readFileSync(new URL('./index.html',import.meta.url),'utf8');
 const handheld=readFileSync(new URL('./handheld.html',import.meta.url),'utf8');
 assert.match(gate,/handheld\.html\?controller=iphoneaudio40/);
 assert.match(gate,/app\.mjs\?controller=previeworigin41/);
 assert.match(handheld,/handheld\.mjs\?controller=iphoneaudio40/);
});


test('handheld exposes an explicit iPhone Safari audio unlock contract',()=>{
 const handheld=readFileSync(new URL('./handheld.html',import.meta.url),'utf8');
 const runtime=readFileSync(new URL('./handheld.mjs',import.meta.url),'utf8');
 assert.match(handheld,/id="audio"[^>]*aria-pressed="false"[^>]*>🔊 Enable game sound/);
 assert.match(handheld,/iPhone\/iPad/);
 assert.match(runtime,/function emulatorAudioContexts/);
 assert.match(runtime,/context\.resume\(\)/);
 assert.match(runtime,/audioWanted/);
 assert.match(runtime,/gameVolume\(\)/);
});

test('game observation is a validated opt-in relay of native framebuffer numbers only',()=>{
 const gate=readFileSync(new URL('./app.mjs',import.meta.url),'utf8');
 const inner=readFileSync(new URL('./handheld.mjs',import.meta.url),'utf8');
 assert.match(gate,/sol-spark-observe-request/);
 assert.match(gate,/sol-spark-observation/);
 assert.match(gate,/event.origin!==cloudOrigin/);
 assert.match(gate,/current\.qbeast\?\.profile\?\.id/);
 assert.match(inner,/observeNativePixels\(document\)/);
 assert.match(inner,/status:'unavailable'/);
 assert.doesNotMatch(inner,/autonomous.*model.*controller/);
});
test('game speaker probe belongs to the iframe user gesture, not a synthetic parent click',()=>{
 const inner=readFileSync(new URL('./handheld.mjs',import.meta.url),'utf8');
 const doc=readFileSync(new URL('./handheld.html',import.meta.url),'utf8');
 assert.match(doc,/id="test-audio"/);
 assert.match(inner,/speakerContext\.createOscillator\(\)/);
 assert.match(inner,/context\.state === 'interrupted'/);
 assert.match(inner,/source\?\.gain\?\.context/);
 assert.match(inner,/\$\('test-audio'\)\.addEventListener\('click'/);
});
