import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {observeGameFrame} from './frame-observation.mjs';

test('actual native display pixel summary is bounded, not an invented scene label',()=>{
 const canvas={width:240,height:160};
 const pixels=new Uint8ClampedArray(32*24*4);
 for(let i=0;i<pixels.length;i+=4){pixels[i]=20;pixels[i+1]=40;pixels[i+2]=160;pixels[i+3]=255;}
 const doc={createElement:()=>({getContext:()=>({drawImage(source){assert.equal(source,canvas);},getImageData(){return {data:pixels};}})})};
 const o=observeGameFrame(canvas,doc);
 assert.equal(o.status,'observed');
 assert.equal(o.source,'native-emulator-display');
 assert.equal(o.dominant,'blue');
 assert.ok(o.brightness>=0&&o.brightness<=100);
 assert.ok(o.frameChange>=0&&o.frameChange<=100);
 assert.equal(o.enemy,undefined);
 assert.equal(o.image,undefined);
 assert.match(o.limits,/no object or map identification/i);
});
test('unavailable framebuffer does not generate a fictional visual observation',()=>{
 assert.equal(observeGameFrame(null).status,'unavailable');
 const blocked={createElement:()=>({getContext:()=>{throw Error('tainted');}})};
 assert.equal(observeGameFrame({width:240,height:160},blocked).status,'unavailable');
});
test('same-origin bridge only responds to explicit request and verified cloud QBEAST',()=>{
 const gate=readFileSync(new URL('./app.mjs',import.meta.url),'utf8');
 const handheld=readFileSync(new URL('./handheld.mjs',import.meta.url),'utf8');
 assert.match(gate,/event\.origin!==cloudOrigin/);
 assert.match(gate,/event\.data\.qbeast_id!==current\.qbeast\.profile\.id/);
 assert.match(handheld,/sol-spark-observe-request/);
 assert.match(handheld,/observeGameFrame\(frame\)/);
 assert.match(handheld,/createdGameAudioContexts/);
 assert.match(handheld,/context\.state === 'interrupted'/);
});
