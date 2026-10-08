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
export async function observeNativePixels(doc=globalThis.document,delay=ms=>new Promise(ok=>setTimeout(ok,ms))){
 const first=grabFrame(doc);
 if(!first)return null;
 await delay(145);
 const second=grabFrame(doc);
 return summarizePixels(first,second);
}
