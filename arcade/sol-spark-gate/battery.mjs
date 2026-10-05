/** Resume native progress without replacing it with another starter handoff. */
import {verifySparkArt,SPARK_META} from './cartridge.mjs';
import {MAILBOX_OFFSET,profileFromBcp1} from '../lost-cosmos/mailbox.mjs';
import {readProgress} from '../sol-beast-lab/design.mjs';
const word=(b,o)=>new DataView(b.buffer,b.byteOffset,b.byteLength).getUint32(o,true);
const batteryPaths=name=>[`/data/saves/mGBA/${name}.srm`,`/data/saves/mGBA/${name}.gba.srm`,`/data/saves/${name}.srm`,`/data/saves/${name}.gba.srm`];
export function batteryName(bytes){
 verifySparkArt(bytes);
 return `lost-cosmos-${word(bytes,SPARK_META+8).toString(16).padStart(8,'0')}-${word(bytes,SPARK_META+12).toString(16).padStart(8,'0')}`;
}
export function chooseBattery(incoming,cached,{journey=false}={}){
 verifySparkArt(incoming);
 if(!cached||journey)return incoming;
 verifySparkArt(cached);
 if(batteryName(cached)!==batteryName(incoming))throw Error('Saved battery belongs to another Spark companion.');
 if(String.fromCharCode(...cached.subarray(0,4))==='LCV5'){
  if(cached[4]!==5)throw Error('Saved journey version is unsupported.');
  const profile=profileFromBcp1(incoming.slice(MAILBOX_OFFSET+32,MAILBOX_OFFSET+96),{gameSeed:word(incoming,MAILBOX_OFFSET+10)});
  readProgress(profile,cached);
 }else if(!cached.subarray(0,8192).every(v=>v===255))throw Error('Saved journey needs recovery. Export the battery before replacing it.');
 return cached;
}
export function prepareBattery(fs,incoming,{journey=false}={}){
 const name=batteryName(incoming),paths=batteryPaths(name);
 const existing=paths.filter(path=>fs.analyzePath(path).exists);
 // Old adapters prepared both core filename conventions. Prefer earned data.
 const cached=existing.find(path=>String.fromCharCode(...fs.readFile(path).subarray(0,4))==='LCV5')||existing[0];
 let selected=chooseBattery(incoming,cached?fs.readFile(cached):null,{journey});
 // Migrate only a verified matching battery from the older common filename.
 if(!cached&&!journey)for(const path of ['/data/saves/lost-cosmos.srm','/data/saves/lost-cosmos.gba.srm']){
  if(!fs.analyzePath(path).exists)continue;
  try{selected=chooseBattery(incoming,fs.readFile(path));break;}catch{}
 }
 if(!fs.analyzePath('/data/saves').exists)fs.mkdir('/data/saves');
 if(!fs.analyzePath('/data/saves/mGBA').exists)fs.mkdir('/data/saves/mGBA');
 for(const path of paths)fs.writeFile(path,selected);
 return {bytes:selected,resumed:String.fromCharCode(...selected.subarray(0,4))==='LCV5'};
}
export function keepCoreBattery(fs,incoming,corePath){
 const name=batteryName(incoming),paths=batteryPaths(name);
 if(!paths.includes(corePath))throw Error('The native core returned an unsupported battery path.');
 // Once the core reveals its filename, remove our redundant starter alias.
 // Leaving that alias would select stale progress on the next page opening.
 for(const path of paths)if(path!==corePath&&fs.analyzePath(path).exists)fs.unlink(path);
}
