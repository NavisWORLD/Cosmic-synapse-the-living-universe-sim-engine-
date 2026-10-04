import { fnv1a, crc32, expectedGenesis, applyTraits, buildBcp1, buildMailbox, MAILBOX_OFFSET, MAILBOX_BYTES } from '../lost-cosmos/mailbox.mjs';
import { renderSprite, packTiles } from './sprites.mjs';

export const ARCHIVE_SHA256 = '9bcecc3732fe48107554cc2041cff6088f418290fb850ec0c9b89cdc375f54c8';
export const STAT_NAMES = ['HP','Energy','Signal','Memory','Resonance','Agility','Chaos','Stability','Curiosity','Evolution'];
export const ISLANDS = [
  { name:'Eridoria Prime', short:'Prime', family:3, forms:['Cinderkip','Hearthpaw','Solwarden'], color:'#f6af75', accent:'#ffda85', habitat:'A warm forge, a softer heart.', gift:'A bright tail and little ember ears.' },
  { name:'Hollow Verdance', short:'Verdance', family:4, forms:['Leaflet','Mossmew','Verdantwhisk'], color:'#86d9aa', accent:'#d5f4a1', habitat:'The forest keeps every small kindness.', gift:'Leaf ears and a blooming crest.' },
  { name:'The Crown', short:'Crown', family:6, forms:['Coronet','Halofox','Crownkeeper'], color:'#d0b7ff', accent:'#ffe2a0', habitat:'Royal skies. Very unroyal mischief.', gift:'A tiny crown that grows with trust.' },
  { name:'The Pale Expanse', short:'Expanse', family:1, forms:['Flurry','Snowfluff','Glacierbun'], color:'#b6e9ff', accent:'#e2fbff', habitat:'Warm paws against an endless winter.', gift:'Long ears and an enormous winter fluff.' },
  { name:'Rust Meridian', short:'Meridian', family:5, forms:['Coglet','Coppercub','Gearheart'], color:'#e5ae89', accent:'#ffdc8f', habitat:'A clockwork friend with a curious nose.', gift:'Round bolt ears and a little gear charm.' },
  { name:'Cinder Drift', short:'Drift', family:3, forms:['Pipflare','Emberwing','Sunphoenix'], color:'#ff9f9a', accent:'#ffd67d', habitat:'Every brave step begins as a flicker.', gift:'Stubby wings that become a sunburst.' },
  { name:'Umbral Deep', short:'Umbral', family:2, forms:['Duskdrop','Velvetmoth','Moonveil'], color:'#aea5e9', accent:'#d7caff', habitat:'The dark has room for gentle things.', gift:'Velvet wings and soft moon antennae.' },
  { name:'The Shattered Reef', short:'Reef', family:0, forms:['Bubblefin','Tidepup','Reefwarden'], color:'#85ddd7', accent:'#f9b6d8', habitat:'A pocket of wonder in a broken ocean.', gift:'Coral gills, a fin, and bubble cheeks.' },
];
const hex = n => (n>>>0).toString(16).padStart(8,'0');
const read32 = (b,o) => new DataView(b.buffer,b.byteOffset,b.byteLength).getUint32(o,true);
function transfer(stats, from, to, count) {
  for(let n=0;n<count;n++) if(stats[from]>20 && stats[to]<80) { stats[from]--; stats[to]++; }
}
export function createBeast({ island=0, nonce, focus=50, calm=50, spark=50 }, archive) {
  if(!Number.isInteger(island)||island<0||island>=8) throw new Error('Choose one of the eight islands.');
  for(const value of [focus,calm,spark]) if(!Number.isInteger(value)||value<0||value>100) throw new Error('Traits must be whole numbers from 0 to 100.');
  if(typeof nonce!=='string'||!nonce.trim()||nonce.length>96) throw new Error('Seed phrase must contain 1–96 characters.');
  if(!(archive instanceof Uint8Array)||archive.length!==8192) throw new Error('The preserved seed archive is missing.');
  const offset=fnv1a(`sol-window-v1|${nonce}|${island}`)%8192;
  const window=Array.from({length:32},(_,i)=>archive[(offset+i)%8192]);
  const base=`sol-genome-v1|${ARCHIVE_SHA256}|${island}|${nonce}|${window.join('.')}`;
  const genesis=expectedGenesis(base), stats=genesis.stats.slice();
  for(const [value,targets,donors] of [[focus,[2,3],[6,9]],[calm,[0,4],[6,8]],[spark,[1,5],[3,7]]]) {
    const shift=Math.trunc((value-50)/5);
    for(let i=0;i<2;i++) transfer(stats,shift>=0?donors[i]:targets[i],shift>=0?targets[i]:donors[i],Math.abs(shift));
  }
  const seed=`${base}|${focus}|${calm}|${spark}`, publicId=fnv1a(`sol-identity-v1|${seed}`)||1;
  const gameSeed=fnv1a(`sol-art-v1|${seed}`)||1, family=ISLANDS[island].family;
  const meta=0x6000|island|(Math.min(3,Math.floor(focus/25))<<3)|(Math.min(3,Math.floor(calm/25))<<5)|(Math.min(3,Math.floor(spark/25))<<7)|((gameSeed&3)<<9);
  const bcp1=buildBcp1({family,stats,temper:applyTraits(genesis.temper,focus,calm,spark),hue:Math.max(-32,Math.min(31,Math.floor((spark-calm)/2))),publicId});
  return {schema:'sol-nursery-v1',island,nonce,focus,calm,spark,seed,publicId,gameSeed,family,species:128+family,bcp1,meta,callsign:ISLANDS[island].forms[0].toUpperCase().slice(0,12),archive:{sha256:ARCHIVE_SHA256,offset,windowHex:window.map(n=>n.toString(16).padStart(2,'0')).join('')},stage:0,level:1,bond:10+Math.floor(focus/20)+Math.floor(calm/25)};
}
export function readProgress(beast, save) {
  if(!(save instanceof Uint8Array)||save.length!==32768) throw new Error('Choose a 32 KB battery .sav exported by the game.');
  const r=save.subarray(1024,1276);
  if(String.fromCharCode(...r.subarray(0,4))!=='LCR1'||r[4]!==1||r[5]>12||r[7]||(r[5]?r[6]>=r[5]:r[6]!==0)) throw new Error('No valid native creature roster in this save.');
  if(crc32(r.subarray(0,248))!==read32(r,248)) throw new Error('The creature roster checksum failed.');
  let found=null; const seen=new Set();
  for(let i=0;i<r[5];i++) {
    const p=r.subarray(8+i*20,28+i*20), id=read32(p,8);
    if(!id||seen.has(id)||!((p[0]>=1&&p[0]<=8)||(p[0]>=128&&p[0]<=134))||p[1]>2||!p[2]||p[2]>60||p[3]>100||p[18]>6) throw new Error('The roster contains an invalid creature.');
    seen.add(id);
    if(id===beast.publicId) {
      if(p[0]!==beast.species||read32(p,12)!==beast.gameSeed) throw new Error('This creature seed does not belong to your nursery companion.');
      found={stage:p[1],level:p[2],bond:p[3],hp:p[4]|p[5]<<8,xp:p[6]|p[7]<<8,attack:p[16],defense:p[17]};
    }
  }
  if(!found) throw new Error('This save does not belong to your current companion. Load its nursery receipt first.');
  return found;
}
export function exportSave(beast,{baseSave=null}={}) {
  const stage=baseSave?readProgress(beast,baseSave).stage:0;
  const sprite=renderSprite(beast,stage), mail=buildMailbox(beast);
  mail[5]=3; // Existing LCX1 ready + custom art. The cartridge owns the roster.
  const dv=new DataView(mail.buffer); sprite.palette.forEach((c,i)=>dv.setUint16(96+i*2,c,true));
  mail.set(packTiles(sprite.pixels),128); dv.setUint32(640,crc32(mail.subarray(0,640)),true);
  const sav=baseSave?baseSave.slice():new Uint8Array(32768).fill(255);
  sav.set(mail,MAILBOX_OFFSET);
  if(MAILBOX_OFFSET+MAILBOX_BYTES>25600) throw new Error('Mailbox crosses the manual save boundary.');
  return sav;
}
export function publicReceipt(beast,source='manual') {
  return {schema:'sol-nursery-receipt-v1',version:1,island:ISLANDS[beast.island].name,islandIndex:beast.island,nonce:beast.nonce,traits:{focus:beast.focus,calm:beast.calm,spark:beast.spark},source,publicId:hex(beast.publicId),gameSeed:hex(beast.gameSeed),archive:beast.archive,forms:ISLANDS[beast.island].forms,stats:Object.fromEntries(STAT_NAMES.map((n,i)=>[n,beast.bcp1[8+i]])),bcp1Hex:[...beast.bcp1].map(n=>n.toString(16).padStart(2,'0')).join(''),meaning:'Derived game cues and archived seed replay. No raw EEG, live quantum link, consciousness claim, or medical interpretation.'};
}
