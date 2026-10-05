/** Sol's additive cartridge adapter. Grok's genome, renderer and ledger stay authoritative. */
import {renderBeast} from './public-render.mjs';
import { renderSprite } from '../spark-beasts/render.mjs';
import { sparkRecord, cageSave, buildSave, buildGrowth, attachGrowth, genomeFromRecipe } from '../spark-beasts/trade.mjs';
import { crc32, MAILBOX_OFFSET, MAILBOX_BYTES } from '../lost-cosmos/mailbox.mjs';
import { readProgress } from '../sol-beast-lab/design.mjs';
import { packTiles } from '../sol-beast-lab/sprites.mjs';
import { buildGenome } from '../spark-beasts/genome.mjs';

export const SPARK_META=24704, SPARK_TILES=31744;
export const GAITS=['bob','hop','sway','float','wobble','scuttle','pulse'];
const TEMPER=['Playful','Curious','Serene','Gentle','Fierce','Bold','Dreamy','Steadfast'];
const read32=(b,o)=>new DataView(b.buffer,b.byteOffset,b.byteLength).getUint32(o,true);
const write32=(b,o,v)=>new DataView(b.buffer,b.byteOffset,b.byteLength).setUint32(o,v>>>0,true);

function reduced(genome,stage,eyes,publicSpark=false) {
 const image=publicSpark?{width:64,height:64,rgba:renderBeast(genome,stage,eyes||'open')}:renderSprite(genome,stage,{shadow:false,...(eyes?{eyes}:{})});
 if(image.width!==64||image.height!==64||image.rgba.length!==16384) throw new Error('Unexpected Spark sprite size.');
 const rgb=new Uint16Array(1024), opaque=new Uint8Array(1024);
 for(let y=0;y<32;y++)for(let x=0;x<32;x++) {
  const samples=[0,1,64,65].map(d=>((y*2)*64+x*2+d)*4).filter(i=>image.rgba[i+3]>=128);
  if(!samples.length)continue;
  const channels=[0,1,2].map(c=>Math.round(samples.reduce((n,i)=>n+image.rgba[i+c],0)/samples.length/255*31));
  rgb[y*32+x]=channels[0]|channels[1]<<5|channels[2]<<10; opaque[y*32+x]=1;
 }
 return {rgb,opaque};
}
const distance=(a,b)=>[0,5,10].reduce((n,s)=>n+(((a>>s)&31)-((b>>s)&31))**2,0);
export function cartridgeSprite(genome,stage,publicSpark=false) {
 const image=reduced(genome,stage,null,publicSpark), counts=new Map();
 image.rgb.forEach((v,i)=>{if(image.opaque[i])counts.set(v,(counts.get(v)||0)+1);});
 const colors=[...counts.keys()].sort((a,b)=>a-b), palette=[0];
 // Preserve the darkest outline, then select distinct colors by weighted distance.
 if(colors.length)palette.push(colors.reduce((a,b)=>[0,5,10].reduce((n,s)=>n+((a>>s)&31)-((b>>s)&31),0)<=0?a:b));
 while(palette.length<16&&palette.length<=colors.length) {
  let best=-1,score=-1;
  for(const c of colors)if(!palette.slice(1).includes(c)) {
   const s=Math.min(...palette.slice(1).map(p=>distance(c,p)))*Math.sqrt(counts.get(c));
   if(s>score){score=s;best=c;}
  }
  if(best<0)break;palette.push(best);
 }
 while(palette.length<16)palette.push(0);
 const pixels=new Uint8Array(1024);
 image.rgb.forEach((v,i)=>{if(image.opaque[i]){let best=1;for(let p=2;p<16;p++)if(distance(v,palette[p])<distance(v,palette[best]))best=p;pixels[i]=best;}});
 const closed=reduced(genome,stage,'closed',publicSpark), changed=[];
 for(let y=0;y<32;y++)for(let x=0;x<32;x++)if(image.rgb[y*32+x]!==closed.rgb[y*32+x]||image.opaque[y*32+x]!==closed.opaque[y*32+x])changed.push([x,y]);
 // Divide separated eye columns into two small blink regions. Side poses need one.
 const columns=[...new Set(changed.map(p=>p[0]))].sort((a,b)=>a-b);let split=32,gap=1;
 for(let i=1;i<columns.length;i++)if(columns[i]-columns[i-1]>gap){gap=columns[i]-columns[i-1];split=columns[i];}
 const eyes=[];
 for(const group of [changed.filter(p=>p[0]<split),changed.filter(p=>p[0]>=split)]) {
  if(!group.length){eyes.push(0,0,0,0);continue;}
  const xs=group.map(p=>p[0]),ys=group.map(p=>p[1]),x=Math.min(...xs),y=Math.min(...ys);
  eyes.push(x,y,Math.max(...xs)-x+1,Math.max(...ys)-y+1);
 }
 return {pixels,palette,tiles:packTiles(pixels),eyes};
}
function artChecksum(save) {
 const body=new Uint8Array(1696);body.set(save.subarray(SPARK_META,SPARK_META+128));body.fill(0,20,24);
 body.set(save.subarray(SPARK_TILES,32768),128);body.set(save.subarray(MAILBOX_OFFSET+96,MAILBOX_OFFSET+640),1152);
 return crc32(body);
}
export function verifySparkArt(save) {
 if(!(save instanceof Uint8Array)||save.length!==32768)throw new Error('Choose a 32 KB GBA battery save.');
 const m=save.subarray(SPARK_META,SPARK_META+128),mail=save.subarray(MAILBOX_OFFSET,MAILBOX_OFFSET+MAILBOX_BYTES);
 if(String.fromCharCode(...m.slice(0,4))!=='SPK1'||m[4]!==1||m[5]!==2||m[6]||m[7])throw new Error('Unsupported Spark art receipt.');
 if(read32(m,8)!==read32(mail,56)||read32(m,12)!==read32(mail,10)||read32(m,16)!==read32(mail,92))throw new Error('Spark art belongs to a different companion.');
 if(!(mail[5]&2)||crc32(mail.slice(0,640))!==read32(mail,640)||artChecksum(save)!==read32(m,20))throw new Error('Spark art checksum failed.');
 for(let i=32;i<56;i+=4)if(m[i]+m[i+2]>32||m[i+1]+m[i+3]>32)throw new Error('Invalid Spark blink region.');
 if(m[56]>6||m[57]<1||m[58]>7||m[59]>3||m[62]>3||m[63]>15)throw new Error('Invalid Spark animation or voice.');
 for(const [o,n] of [[MAILBOX_OFFSET+96,32],[SPARK_META+64,64]])for(let i=0;i<n;i+=2)if(save[o+i+1]&128)throw new Error('Invalid RGB5 palette.');
 return true;
}
export function attachSparkArt(input,genome,runIndex,table,{journey=false,record:checkedRecord=null}={}) {
 if(!(input instanceof Uint8Array)||input.length!==32768)throw new Error('Choose a 32 KB GBA battery save.');
 const record=checkedRecord||sparkRecord(genome,runIndex),rebuilt=checkedRecord?{genome:buildGenome(genome.inputs.traits,table.runs[runIndex],genome.inputs.user_id)}:genomeFromRecipe(record.seed,table);
 if(!rebuilt||rebuilt.genome.seed!==genome.seed)throw new Error('This genome cannot be rebuilt from its public Spark recipe.');
 if(checkedRecord&&checkedRecord.seed!==genome.seed)throw new Error('The checked creature does not match this Spark seed.');
 const mail=input.subarray(MAILBOX_OFFSET,MAILBOX_OFFSET+MAILBOX_BYTES);
 if(String.fromCharCode(...mail.slice(0,4))!=='LCX1'||mail[4]!==1||crc32(mail.slice(0,640))!==read32(mail,640))throw new Error('The cartridge mailbox checksum failed.');
 if(read32(mail,10)!==record.profile.gameSeed||!record.profile.bcp1.every((v,i)=>v===mail[32+i]))throw new Error('This save belongs to a different Spark creature.');
 if(journey)readProgress(record.profile,input);
 const save=input.slice(),m=new Uint8Array(128),dv=new DataView(m.buffer);
 m.set([83,80,75,49,1,2,0,0]);write32(m,8,record.publicId);write32(m,12,record.profile.gameSeed);write32(m,16,read32(record.profile.bcp1,60));
 m.set(Uint8Array.from(genome.seed.slice(0,16).match(/../g).map(v=>parseInt(v,16))),24);
 const forms=[1,2,3].map(s=>cartridgeSprite(genome,s,!!checkedRecord));
 for(let i=0;i<3;i++)m.set(forms[i].eyes,32+i*8);
 m[56]=Math.max(0,GAITS.indexOf(genome.behavior.gait));m[57]=Math.max(1,Math.min(255,Math.round(genome.behavior.tempo_hz*32)));
 m[58]=Math.max(0,TEMPER.indexOf(genome.temperament));m[59]=Math.min(3,genome.behavior.amplitude_px);
 const hz=genome.voice.base_hz||genome.voice.base_pitch_hz||440;dv.setUint16(60,Math.max(1,Math.min(2047,Math.round(2048-131072/hz))),true);
 const wave=['sine','triangle','square','sawtooth'].indexOf(genome.voice.wave);m[62]=wave<0?2:wave;m[63]=8;
 const patched=save.subarray(MAILBOX_OFFSET,MAILBOX_OFFSET+MAILBOX_BYTES);patched[5]|=2;
 forms[0].palette.forEach((v,i)=>new DataView(save.buffer).setUint16(MAILBOX_OFFSET+96+i*2,v,true));patched.set(forms[0].tiles,128);
 write32(patched,640,crc32(patched.slice(0,640)));
 for(let i=1;i<3;i++){forms[i].palette.forEach((v,p)=>dv.setUint16(64+(i-1)*32+p*2,v,true));save.set(forms[i].tiles,SPARK_TILES+(i-1)*512);}
 save.set(m,SPARK_META);write32(save,SPARK_META+20,artChecksum(save));verifySparkArt(save);return save;
}
export function sparkSave(genome,runIndex,table) {
 const record=sparkRecord(genome,runIndex);
 return attachSparkArt(cageSave(record,buildSave,buildGrowth,attachGrowth),genome,runIndex,table);
}
