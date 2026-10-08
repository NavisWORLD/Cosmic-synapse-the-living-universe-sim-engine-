import test from 'node:test';
import assert from 'node:assert/strict';
import {summarizePixels,grabFrame,observeNativePixels} from './native-observation.mjs';
const frame=(rgb)=>{const values=new Uint8ClampedArray(32*24*4);for(let i=0;i<values.length;i+=4){values.set([...rgb,255],i);}return values;};
test('real raster yields bounded opt-in color signals, never fake object names',()=>{
 const first=frame([20,50,170]),second=frame([25,60,190]);
 const result=summarizePixels(first,second);
 assert.equal(result.status,'observed');
 assert.equal(result.source,'native-emulator-display');
 assert.equal(result.dominant,'blue');
 for(const field of ['brightness','contrast','frameChange'])assert.ok(result[field]>=0&&result[field]<=100);
 assert.deepEqual(Object.keys(result).sort(),['brightness','contrast','dominant','frameChange','source','status'].sort());
});
test('no screenshot, transparent buffer or flat black means unavailable not fabricated',()=>{
 assert.equal(summarizePixels(null,frame([30,30,30])),null);
 assert.equal(summarizePixels(frame([0,0,0]),frame([0,0,0])),null);
 const noCanvas={getElementById:()=>({querySelector:()=>null})};
 assert.equal(grabFrame(noCanvas),null);
});
test('frame sampling respects delayed second read and never discloses raw pixels',async()=>{
 const image=frame([30,100,120]),doc={getElementById:()=>({querySelector:()=>({width:240,height:160})}),createElement:()=>({getContext:()=>({drawImage(){},getImageData(){return {data:image}}})})};
 const v=await observeNativePixels(doc,async ms=>assert.equal(ms,145));
 assert.equal(v.status,'observed');assert.equal('pixels' in v,false);
});
