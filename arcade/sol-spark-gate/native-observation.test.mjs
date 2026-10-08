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

test('WebGL cleared backbuffer falls back to on-demand composited stream; every track stops',async()=>{
 const empty=frame([0,0,0]),shown=frame([75,155,205]);let current=null,stopped=0,paused=0;
 const track={stop(){stopped++}},stream={getTracks:()=>[track]};
 const source={width:240,height:160,captureStream:rate=>{assert.equal(rate,12);return stream}};
 const video={videoWidth:240,videoHeight:160,muted:false,srcObject:null,play:()=>Promise.resolve(),pause:()=>{paused++}};
 const doc={
  getElementById:()=>({querySelector:()=>source,querySelectorAll:()=>[source]}),
  createElement:type=>type==='video'?video:{
   width:0,height:0,
   getContext:()=>({
    drawImage:x=>{current=x},
    getImageData:()=>({data:current===video?shown:empty})
   })
  }
 };
 const result=await observeNativePixels(doc,async()=>{});
 assert.equal(result.status,'observed');
 assert.equal(result.dominant,'blue');
 assert.equal(stopped,1);assert.equal(paused,1);assert.equal(video.srcObject,null);
 assert.ok(!('pixels' in result));
});
