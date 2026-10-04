import { ISLANDS, createBeast, exportSave, readProgress, publicReceipt, ARCHIVE_SHA256 } from './design.mjs';
import { renderSprite, paintSprite } from './sprites.mjs';
import { MuseLink, mockTraits } from '../lost-cosmos/muse.mjs';
const $=id=>document.getElementById(id),scene=$('scene'),ctx=scene.getContext('2d');
let archive,beast,preview,island=0,viewStage=0,source='manual',baseSave=null,progress=null,dirty=false,invalidDraft=false,reaction=null,shelf=[];
const storageKey='sol-nursery-shelf-v1';
const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
const hex=n=>(n>>>0).toString(16).padStart(8,'0');
function status(message,error=false){$('status').textContent=message;$('status').style.color=error?'#ffb2bb':'#95e9e2';}
function config(){return {island,nonce:$('seed').value.trim(),focus:Number($('focus').value),calm:Number($('calm').value),spark:Number($('spark').value)};}
function updateCues(){for(const name of ['focus','calm','spark'])$(name+'-value').value=$(name).value;}
function setInputs(receipt){island=receipt.islandIndex;$('seed').value=receipt.nonce;for(const name of ['focus','calm','spark'])$(name).value=receipt.traits[name];updateCues();source=receipt.source||'manual';$('source-label').textContent=source==='simulated'?'SIMULATED CUES':source==='muse-derived'?'MUSE DERIVED CUES':'MANUAL CUES';}
function canvas(sprite,size=96){const c=document.createElement('canvas');c.width=size;c.height=size;paintSprite(c.getContext('2d'),sprite,0,0,size/32);return c;}
function download(bytes,name,type='application/octet-stream'){const blob=new Blob([bytes],{type}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
function setDraft(){
  updateCues();if(!archive)return;
  try{preview=createBeast(config(),archive);invalidDraft=false;dirty=!beast||preview.publicId!==beast.publicId;viewStage=0;reaction=null;render();status(dirty?'New companion preview. Hatch to keep it.':'Your companion is ready.');}
  catch(error){invalidDraft=true;dirty=true;status(error.message,true);$('hatch').disabled=true;for(const id of ['save','receipt','portrait'])$(id).disabled=true;}
}
function keep(){
  const receipt=publicReceipt(beast,source);shelf=[receipt,...shelf.filter(r=>r.publicId!==receipt.publicId)].slice(0,24);
  let persisted=true;try{localStorage.setItem(storageKey,JSON.stringify(shelf));}catch{persisted=false;}
  drawShelf();return persisted;
}
async function hatch(){
  try{beast=createBeast(config(),archive);preview=beast;dirty=false;invalidDraft=false;viewStage=0;progress=null;baseSave=null;reaction={kind:'hatch',start:performance.now()};await muse.stop();$('muse').textContent='Connect Muse';const persisted=keep();render();status(persisted?`${ISLANDS[beast.island].forms[0]} is yours. Keep the receipt, then take your light into the game.`:'Kept for this visit. This browser could not save your shelf; download the companion receipt to keep it.');}catch(e){status(e.message,true);}
}
function selectReceipt(receipt){
  if(receipt.schema!=='sol-nursery-receipt-v1'||receipt.version!==1||receipt.archive?.sha256!==ARCHIVE_SHA256)throw new Error('Choose a Sol nursery companion receipt.');
  if(!receipt.traits||['focus','calm','spark'].some(name=>!Number.isInteger(receipt.traits[name])))throw new Error('The receipt needs all three whole-number cues.');
  if(!['manual','simulated','muse-derived'].includes(receipt.source))throw new Error('The receipt has an unknown cue source.');
  const candidate=createBeast({island:receipt.islandIndex,nonce:receipt.nonce,focus:receipt.traits?.focus,calm:receipt.traits?.calm,spark:receipt.traits?.spark},archive);
  if(hex(candidate.publicId)!==receipt.publicId||hex(candidate.gameSeed)!==receipt.gameSeed||publicReceipt(candidate).bcp1Hex!==receipt.bcp1Hex)throw new Error('The companion receipt does not match its seed and cues.');
  setInputs({islandIndex:candidate.island,nonce:candidate.nonce,traits:{focus:candidate.focus,calm:candidate.calm,spark:candidate.spark},source:receipt.source});beast=preview=candidate;dirty=false;invalidDraft=false;viewStage=0;progress=null;baseSave=null;reaction=null;render();status('Companion restored. Read its game save to see earned growth.');
}
function drawIslands(){
  $('islands').replaceChildren();
  ISLANDS.forEach((home,i)=>{const b=document.createElement('button');b.className='island';b.type='button';b.setAttribute('aria-pressed',String(i===island));b.setAttribute('aria-label',home.name);const sample=createBeast({...config(),island:i,nonce:$('seed').value.trim()||'SOL'},archive);b.append(canvas(renderSprite(sample),48));const text=document.createElement('span'),strong=document.createElement('strong'),small=document.createElement('small');strong.textContent=home.name;small.textContent=home.forms[0];text.append(strong,small);b.append(text);b.addEventListener('click',()=>{island=i;setDraft();});$('islands').append(b);});
}
function drawStages(){
  $('stages').replaceChildren();const current=dirty?preview:beast,home=ISLANDS[current.island],earned=dirty?0:(progress?.stage||0);
  home.forms.forEach((name,s)=>{const b=document.createElement('button');b.className='stage';b.setAttribute('aria-pressed',String(s===viewStage));b.setAttribute('aria-label',`Preview ${name}`);const number=document.createElement('span');number.className='stage-number';number.textContent=`0${s+1}`;b.append(number,canvas(renderSprite(current,s),112));const p=document.createElement('p');p.className='eyebrow';p.textContent=['FIRST LIGHT','GROWING TOGETHER','FULL BLOOM'][s];const h=document.createElement('h3');h.textContent=name;const gate=document.createElement('p');gate.className='small';gate.textContent=s===0?'Born into the cosmos':s<=earned?'Earned in your game':s===1?'Preview · LV 12 / Bond 55':'Preview · LV 28 / Bond 80';b.append(p,h,gate);b.addEventListener('click',()=>{viewStage=s;reaction=null;render();});$('stages').append(b);});
}
function drawShelf(){
  $('shelf').replaceChildren();
  if(!shelf.length){const p=document.createElement('p');p.className='small';p.textContent='Hatch your first companion to keep a light here.';$('shelf').append(p);return;}
  shelf.forEach(receipt=>{try{const sample=createBeast({island:receipt.islandIndex,nonce:receipt.nonce,...receipt.traits},archive);const b=document.createElement('button');b.append(canvas(renderSprite(sample),48));const text=document.createElement('span');text.textContent=ISLANDS[sample.island].forms[0]+' · '+receipt.publicId.slice(0,4).toUpperCase();b.append(text);b.addEventListener('click',()=>{try{selectReceipt(receipt);}catch(e){status(e.message,true);}});$('shelf').append(b);}catch{/* Ignore obsolete local receipts. */}});
}
function render(){
  const current=dirty?preview:beast;if(!current)return;const home=ISLANDS[current.island],earned=dirty?0:(progress?.stage||0);
  $('origin').textContent=home.name.toUpperCase();$('lineage-island').textContent=home.name.toUpperCase();$('creature-name').textContent=home.forms[viewStage];$('habitat-copy').textContent=home.habitat;
  $('form-label').textContent=['FIRST LIGHT / 01','GROWING TOGETHER / 02','FULL BLOOM / 03'][viewStage];$('state-label').textContent=dirty?'NEW COMPANION PREVIEW':viewStage>earned?'EVOLUTION PREVIEW':'YOUR COMPANION';
  $('level').textContent=`LV ${dirty?1:progress?.level||1}`;$('bond').textContent=`BOND ${dirty?current.bond:progress?.bond??current.bond} / 100`;$('identity').textContent=`ID ${hex(current.publicId).toUpperCase()}`;
  $('save').textContent=baseSave?'↓ Updated journey .sav':'↓ Starter .sav';for(const id of ['save','receipt','portrait'])$(id).disabled=dirty||invalidDraft;$('hatch').disabled=invalidDraft;
  $('journey-note').textContent=baseSave?'Your game progress was read successfully. Updated saves preserve every byte outside the creature art mailbox, including all three manual save slots.':'Starter saves are for a new journey. Reading your own game save enables an updated .sav that preserves your existing journey.';
  $('archive-note').textContent=`Archive SHA-256: ${ARCHIVE_SHA256} · Your window begins at byte ${current.archive.offset}. The repository describes IBM measurements; this nursery verifies the preserved bytes, not the original hardware provenance.`;
  drawIslands();drawStages();drawScene(performance.now());
}
function drawScene(now){
  const current=dirty?preview:beast;if(!current)return;const home=ISLANDS[current.island],t=reduced?0:now/1000;
  ctx.fillStyle='#17223b';ctx.fillRect(0,0,320,208);
  for(let n=0;n<26;n++){const x=(n*47+current.gameSeed%31)%316,y=(n*29+7)%100;ctx.fillStyle=n%3===0?home.accent:'#69829f';ctx.globalAlpha=.3+Math.sin(t*.8+n)*.2;ctx.fillRect(x,y,n%5===0?2:1,1);}ctx.globalAlpha=1;
  ctx.fillStyle='#27334c';for(let n=0;n<6;n++)ctx.fillRect(n*60-10,108+((n*17)%24),64,80);
  ctx.fillStyle='#253a50';ctx.beginPath();ctx.ellipse(160,166,107,22,0,0,Math.PI*2);ctx.fill();
  ctx.fillStyle=home.color;ctx.globalAlpha=.35;ctx.fillRect(72,155,176,3);ctx.globalAlpha=1;
  ctx.fillStyle='#36465e';ctx.fillRect(70,157,180,10);ctx.fillStyle='#202940';ctx.fillRect(82,168,156,8);ctx.fillRect(100,176,120,7);ctx.fillRect(120,183,80,6);
  for(let n=0;n<10;n++){ctx.fillStyle=n%2?home.color:home.accent;const x=76+n*18;ctx.fillRect(x,151-n%3,2,6);ctx.fillRect(x-1,150-n%3,4,2);}
  ctx.fillStyle='#111b30';ctx.beginPath();ctx.ellipse(160,156,26,5,0,0,Math.PI*2);ctx.fill();
  let bounce=reduced?0:Math.round(Math.sin(t*2)*2),blink=!reduced&&now%5400<130?1:0;
  const elapsed=reaction?(now-reaction.start)/1000:100;if(elapsed<2&&!reduced)bounce+=reaction.kind==='play'?Math.round(Math.abs(Math.sin(elapsed*9))*-7):Math.round(Math.sin(elapsed*4)*-2);
  if(reaction?.kind==='rest'&&elapsed<3)blink=1;
  paintSprite(ctx,renderSprite(current,viewStage,blink),112,68+bounce,3);
  if(elapsed<3){ctx.font='12px monospace';ctx.fillStyle=home.accent;ctx.fillText(reaction.kind==='rest'?'z z':reaction.kind==='play'?'✧':'♥',204,90-Math.round(elapsed*9));}
}
const muse=new MuseLink(traits=>{for(const name of ['focus','calm','spark'])$(name).value=traits[name];source='muse-derived';$('source-label').textContent='MUSE DERIVED CUES';setDraft();});
for(const name of ['focus','calm','spark'])$(name).addEventListener('input',()=>{source='manual';$('source-label').textContent='MANUAL CUES';setDraft();});$('seed').addEventListener('input',setDraft);
$('random-seed').addEventListener('click',()=>{const b=crypto.getRandomValues(new Uint32Array(1))[0];$('seed').value='SOL-'+hex(b).toUpperCase();setDraft();});
$('hatch').addEventListener('click',hatch);
$('simulate').addEventListener('click',()=>{const traits=mockTraits();for(const name of ['focus','calm','spark'])$(name).value=traits[name];source='simulated';$('source-label').textContent='SIMULATED CUES';setDraft();status('Simulated band window. These values are not a measurement.');});
$('muse').addEventListener('click',async()=>{try{if(muse.running){await muse.stop();$('muse').textContent='Connect Muse';status('Muse disconnected. Choose cues or hatch the last preview.');}else{await muse.connect();$('muse').textContent='Disconnect Muse';status('Connected. Wait for derived cues, then hatch to keep that snapshot.');}}catch(e){await muse.stop();$('muse').textContent='Connect Muse';status(`${e.message}. Manual cues and simulation are available.`,true);}});
document.querySelectorAll('[data-care]').forEach(button=>button.addEventListener('click',()=>{reaction={kind:button.dataset.care,start:performance.now()};$('care-note').textContent={pet:'A little cheek nuzzle. Your light stays close.',play:'A tiny leap, a shower of sparks. One more?',rest:'A quiet moment together. No timer. No pressure.'}[reaction.kind];drawScene(performance.now());}));
$('save').addEventListener('click',()=>{try{download(exportSave(beast,{baseSave}),`SOL_${beast.callsign}_${baseSave?'JOURNEY':'STARTER'}.sav`);status(baseSave?'Updated journey downloaded. Your roster and manual save slots are preserved.':'Starter save downloaded. Attach it to the GBA game for a new journey.');}catch(e){status(e.message,true);}});
$('receipt').addEventListener('click',()=>download(JSON.stringify(publicReceipt(beast,source),null,2)+'\n',`SOL_${beast.callsign}_${hex(beast.publicId)}.json`,'application/json'));
$('portrait').addEventListener('click',()=>{const c=canvas(renderSprite(beast,viewStage),512);c.toBlob(blob=>{if(blob)download(blob,`SOL_${ISLANDS[beast.island].forms[viewStage]}.png`,'image/png');});});
$('read-save-button').addEventListener('click',()=>$('read-save').click());
$('read-receipt-button').addEventListener('click',()=>$('read-receipt').click());
$('read-save').addEventListener('change',async event=>{const file=event.target.files[0];event.target.value='';if(!file)return;try{if(dirty)throw new Error('Hatch this preview or return to your kept companion first.');if(file.size!==32768)throw new Error('Choose a 32 KB battery .sav, not an emulator save state.');const selected=beast,data=new Uint8Array(await file.arrayBuffer());if(selected!==beast||dirty)throw new Error('The companion changed while reading. Choose the save again.');const earned=readProgress(beast,data);baseSave=data;progress=earned;viewStage=earned.stage;render();status(`Read from your game: level ${earned.level}, bond ${earned.bond}, ${ISLANDS[beast.island].forms[earned.stage]}.`);}catch(e){status(e.message,true);}});
$('read-receipt').addEventListener('change',async event=>{const file=event.target.files[0];event.target.value='';if(!file)return;try{if(file.size>262144)throw new Error('This receipt is too large.');const receipt=JSON.parse(await file.text());selectReceipt(receipt);if(!keep())status('Companion restored for this visit. Keep its receipt; this browser could not save your shelf.');}catch(e){status(e.message,true);}});
addEventListener('pagehide',()=>muse.stop());
async function start(){try{const data=await fetch('archive.json');if(!data.ok)throw new Error('The seed archive could not load.');const json=await data.json();archive=new Uint8Array(json.bytes);const digest=[...new Uint8Array(await crypto.subtle.digest('SHA-256',archive))].map(n=>n.toString(16).padStart(2,'0')).join('');if(digest!==ARCHIVE_SHA256)throw new Error('The preserved seed archive checksum failed.');try{shelf=JSON.parse(localStorage.getItem(storageKey)||'[]');if(!Array.isArray(shelf))shelf=[];}catch{shelf=[];}shelf=shelf.slice(0,24);if(shelf.length){try{selectReceipt(shelf[0]);}catch{await hatch();}}else await hatch();drawShelf();document.documentElement.dataset.ready='true';if(!reduced){const loop=now=>{drawScene(now);requestAnimationFrame(loop);};requestAnimationFrame(loop);}}catch(e){status(e.message,true);}}
start();
