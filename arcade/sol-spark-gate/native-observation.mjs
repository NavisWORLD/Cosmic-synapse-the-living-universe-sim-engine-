/** Bounded visual signal from the actual native EmulatorJS canvas.
 * No DOM game cheats, world-state oracle, classification, raw-image upload or model call.
 * Inspired by the NavisWORLD virtual camera / Zelda observation-action research.
 */
const SIZE = 32, HEIGHT = 24;
const clamp = x => Math.max(0, Math.min(100, Math.round(x)));
export function summarizePixels(first, second) {
 if (!first || !second || first.length!==second.length || first.length!==SIZE*HEIGHT*4)
  return null;
 let n=0,sum=0,squares=0,r=0,g=0,b=0,change=0,visible=0;
 for(let i=0;i<first.length;i+=4){
  const a=second[i],c=second[i+1],d=second[i+2];
  const l=.2126*a+.7152*c+.0722*d;
  if(second[i+3]===0)continue;
  n++;sum+=l;squares+=l*l;r+=a;g+=c;b+=d;
  change+=(Math.abs(first[i]-a)+Math.abs(first[i+1]-c)+Math.abs(first[i+2]-d))/3;
  if(a>10||c>10||d>10)visible++;
 }
 if(n<SIZE*HEIGHT/2||visible<8)return null;
 const brightness=clamp(sum/(n*255)*100),contrast=clamp(Math.sqrt(Math.max(0,squares/n-(sum/n)**2))/128*100);
 const mean=[r/n,g/n,b/n],largest=Math.max(...mean),lowest=Math.min(...mean);
 const dominant=largest-lowest<18?'mixed':['red','green','blue'][mean.indexOf(largest)];
 return {status:'observed',source:'native-emulator-display',brightness,contrast,dominant,frameChange:clamp(change/(n*255)*100)};
}
export function grabFrame(doc=globalThis.document){
 const game=doc?.getElementById('game'),source=game?.querySelector('canvas');
 if(!source||!source.width||!source.height)return null;
 const scratch=doc.createElement('canvas');scratch.width=SIZE;scratch.height=HEIGHT;
 const context=scratch.getContext('2d',{willReadFrequently:true});
 if(!context)return null;
 try{
  context.drawImage(source,0,0,SIZE,HEIGHT);
  return context.getImageData(0,0,SIZE,HEIGHT).data;
 }catch{return null;} // Browser may deny or clear a WebGL framebuffer readback.
}
/** Native RetroArch core screenshot avoids an already-cleared WebGL backbuffer.
 * EmulatorJS GameManager.screenshot() returns PNG bytes; they are decoded only
 * in this sandbox, summarized, and never sent to the parent or model.
 */
async function coreFrame(doc){
 const view=doc?.defaultView||globalThis;
 const gm=view.EJS_emulator?.gameManager;
 if(typeof gm?.screenshot!=='function'||typeof view.createImageBitmap!=='function')return null;
 let bitmap;
 try{
  const raw=await gm.screenshot();
  const bytes=raw instanceof ArrayBuffer?new Uint8Array(raw):
   ArrayBuffer.isView(raw)?new Uint8Array(raw.buffer,raw.byteOffset,raw.byteLength):null;
  if(!bytes||bytes.length<16||bytes.length>2_000_000||
     bytes[0]!==137||bytes[1]!==80||bytes[2]!==78||bytes[3]!==71)return null;
  bitmap=await view.createImageBitmap(new Blob([bytes],{type:'image/png'}));
  const scratch=doc.createElement('canvas');scratch.width=SIZE;scratch.height=HEIGHT;
  const ctx=scratch.getContext('2d',{willReadFrequently:true});if(!ctx)return null;
  ctx.drawImage(bitmap,0,0,SIZE,HEIGHT);
  return ctx.getImageData(0,0,SIZE,HEIGHT).data;
 }catch{return null}
 finally{try{bitmap?.close?.();}catch{}}
}

function videoRead(doc,video) {
 if(!video?.videoWidth||!video?.videoHeight)return null;
 const scratch=doc.createElement('canvas');scratch.width=SIZE;scratch.height=HEIGHT;
 const ctx=scratch.getContext('2d',{willReadFrequently:true});if(!ctx)return null;
 try{ctx.drawImage(video,0,0,SIZE,HEIGHT);return ctx.getImageData(0,0,SIZE,HEIGHT).data;}
 catch{return null;}
}
/** Only while the player explicitly asks to look: create a local muted canvas
 * stream, sample two composited frames, then immediately stop every track.
 * Safari/WebKit or GPU restrictions can make this unavailable; never fake pixels.
 */
async function streamFrames(doc,delay){
 const source=[...(doc?.getElementById('game')?.querySelectorAll('canvas')||[])]
  .filter(x=>x.width&&x.height&&typeof x.captureStream==='function')
  .sort((a,b)=>b.width*b.height-a.width*a.height)[0];
 if(!source)return null;
 let stream,video;
 try{
  stream=source.captureStream(12);
  if(!stream?.getTracks?.().length)return null;
  video=doc.createElement('video');
  video.muted=true;video.autoplay=true;video.playsInline=true;
  video.srcObject=stream;
  if(typeof video.play==='function')await Promise.race([
   Promise.resolve(video.play()).catch(()=>undefined),delay(650)
  ]);
  await delay(170);
  let first=videoRead(doc,video);
  if(!first){await delay(200);first=videoRead(doc,video);}
  if(!first)return null;
  await delay(145);
  return summarizePixels(first,videoRead(doc,video));
 }catch{return null}
 finally{
  if(video){try{video.pause?.();}catch{}video.srcObject=null;}
  for(const track of stream?.getTracks?.()||[])try{track.stop();}catch{}
 }
}
export async function observeNativePixels(doc=globalThis.document,delay=ms=>new Promise(ok=>setTimeout(ok,ms))){
 const first=grabFrame(doc);
 if(first){
  await delay(145);
  const result=summarizePixels(first,grabFrame(doc));
  if(result)return result;
 }
 // Prefer the actual native-core screenshot: this reads the current visible
 // game framebuffer, not undiscovered memory, future rewards or map metadata.
 const coreA=await coreFrame(doc);
 if(coreA){
  await delay(145);
  const coreResult=summarizePixels(coreA,await coreFrame(doc));
  if(coreResult)return coreResult;
 }
 // Finally try the actual presented compositor stream on implementations
 // without a native screenshot API. Both fallbacks remain explicit and bounded.
 return streamFrames(doc,delay);
}
