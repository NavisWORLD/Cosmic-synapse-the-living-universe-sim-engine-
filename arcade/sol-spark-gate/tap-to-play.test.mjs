import test from 'node:test';import assert from 'node:assert/strict';import {readFileSync} from 'node:fs';
const src=readFileSync(new URL('./handheld.mjs',import.meta.url),'utf8'),html=readFileSync(new URL('./handheld.html',import.meta.url),'utf8');
test('missing MediaRecorder cannot abort cartridge start',()=>{assert.match(src,/typeof window\.MediaRecorder==='undefined'/);assert.ok(src.indexOf('MediaRecorder')<src.indexOf('function installEmulator'));});
test('START message shows an in-frame tap target that resumes existing audio contexts (no new context)',()=>{
 const gate=src.slice(src.indexOf('function tapGate'),src.indexOf('async function unlockGameAudio'));
 assert.match(gate,/unlockGameAudio\(\)/);assert.doesNotMatch(gate,/new (window\.)?(AudioContext|webkitAudioContext)/);
 assert.match(src,/installEmulator\(state\.save,\{autoStart:true\}\);\n\s*\/\/ Show the in-frame tap target[^\n]*\n\s*setTimeout\(\(\)=>\{if\(!state\.audioWanted\|\|audioLocked\(\)\)tapGate\(true\);\},0\);/);
 assert.match(src,/document\.body\.appendChild\(gate\)/);
});
test('Beast Box can mute without a gesture; sound/options row is hidden in the player frame',()=>{assert.match(src,/data\.type==='sol-spark-audio-mute'/);assert.match(html,/\.player-frame \.row:not\(\.legacy-inputs\)\{display:none\}/);});
