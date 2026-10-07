import { loadTable } from '../spark-beasts/runs.mjs';
import { buildGenome } from '../spark-beasts/genome.mjs';
import { loadStore } from '../spark-beasts/store.mjs';
import { sparkRecord, loadCage, saveCage, admit } from '../spark-beasts/trade.mjs?sites=digest43';
import { attachSparkArt } from './cartridge.mjs';
import { readSparkFile, checkedSparkSave } from './spark-file.mjs?sites=digest43';
import { readProgress } from '../sol-beast-lab/design.mjs';
import {normalizeHandheldInput} from './controls.mjs?controller=beastboy39';
import {isTrustedCloudOrigin} from './cloud-origin.mjs?controller=previeworigin41&sites=livingcosmos42';
const $=id=>document.getElementById(id),status=s=>$('status').textContent=s;
let table,current=null,save=null,journey=false;
const embedded=new URLSearchParams(location.search).get('mode')==='handheld';
if(embedded){document.body.classList.add('handheld-only');$('spark').removeAttribute('src');}
let cloudOrigin=null;
window.addEventListener('message',async event=>{
 if(!embedded||event.source!==window.parent||!isTrustedCloudOrigin(event.origin))return;
 if(event.data?.type==='sol-spark-player-state'){
  $('handheld').contentWindow.postMessage({source:'living-universe',type:'sol-player-visibility',active:event.data.active===true},location.origin);return;
 }
 if(event.data?.type==='sol-spark-start'){
  if(!current){status('Send the Beast before starting the cartridge.');return;}
  $('handheld').contentWindow?.postMessage({source:'living-universe',type:'sol-spark-start'},location.origin);
  status('Starting the cartridge with the verified Beast.');
  return;
 }
 if(event.data?.type==='sol-spark-input'){
  const input=normalizeHandheldInput(event.data.button,event.data.down);if(!input)return;
  $('handheld').contentWindow?.postMessage({source:'living-universe',type:'sol-spark-input',button:input.button,down:input.down},location.origin);return;
 }
 if(event.data?.type!=='sol-spark-qbeast')return;
 try{
  if(!table)throw Error('Recorded seed table is still loading.');
  if(typeof event.data.text!=='string'||event.data.text.length>524288)throw Error('Spark handoff is outside its public limit.');
  const beast=await readSparkFile(new TextEncoder().encode(event.data.text),table);beast.qbeast=JSON.parse(event.data.text);
  const ledger=loadCage(localStorage);await admit(ledger,beast.record,'import');saveCage(ledger,localStorage);
  ready(beast,checkedSparkSave(beast,table));cloudOrigin=event.origin;
  window.parent.postMessage({type:'sol-spark-admitted',id:beast.qbeast.profile.id,seed:beast.genome.seed},event.origin);
 }catch(err){status(err.message);window.parent.postMessage({type:'sol-spark-rejected',message:err.message},event.origin);}
});
const download=(name,bytes,type='application/octet-stream')=>{const u=URL.createObjectURL(new Blob([bytes],{type})),a=document.createElement('a');a.href=u;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(u),1000);};
function ready(beast,bytes,earned=false){current=beast;save=bytes;journey=earned;$('companion').textContent=`${beast.genome.names['1']} · ${beast.genome.island}`;$('download').disabled=$('receipt').disabled=false;$('download').textContent=earned?'↓ Journey .sav':'↓ Starter .sav';$('handheld').contentWindow.postMessage({source:'living-universe',type:earned?'sol-spark-journey':'lc-import-save',save:bytes,callsign:beast.record.callsign,species:beast.genome.names['1']},location.origin);status(earned?'Your earned journey and companion art are ready. Reload the handheld before importing another save.':'The verified Beast is in the cartridge. Press Start Lost COSMOS.');}
function storedMatch(bytes){
 const store=loadStore(localStorage);
 for(const b of Object.values(store.beasts)){
  const run=table.runs[b.runIndex];if(!run)continue;
  const genome=buildGenome(b.traits,run,b.userId),record=sparkRecord(genome,b.runIndex,b.xp);
  if(!record.profile.bcp1.every((v,i)=>v===bytes[24864+i]))continue;
  return {genome,record,runIndex:b.runIndex};
 }
 throw new Error('The mailed creature is missing from the local Spark ledger. Keep its .qbeast or receipt and import it here.');
}
window.addEventListener('message',event=>{
 if(event.origin===location.origin&&event.source===$('handheld').contentWindow&&event.data?.source==='living-universe'&&event.data?.type==='sol-spark-input-ack'){
  if(cloudOrigin)window.parent.postMessage({type:'sol-spark-input-ack',button:event.data.button,down:event.data.down,applied:event.data.applied===true},cloudOrigin);
  return;
 }
 if(event.origin!==location.origin||event.source!==$('spark').contentWindow||event.data?.type!=='lc-cage-save')return;
 try{if(!table)throw new Error('The recorded table is still loading.');const raw=event.data.save instanceof Uint8Array?event.data.save:new Uint8Array(event.data.save);if(raw.length!==32768)throw new Error('Invalid battery save size.');const beast=storedMatch(raw);ready(beast,attachSparkArt(raw,beast.genome,beast.runIndex,table));}catch(err){status(err.message);}
});
$('beast-file').addEventListener('change',async()=>{try{if(!table)throw new Error('Wait for the recorded table.');const file=$('beast-file').files[0];if(!file)return;if(file.size>524288)throw new Error('Spark file is too large.');const bytes=new Uint8Array(await file.arrayBuffer());let beast;
 const value=JSON.parse(new TextDecoder().decode(bytes));
 if(value.schema==='sol-spark-art-receipt-v1'){
  const genome=buildGenome(value.traits,table.runs[value.runIndex],value.keeper);if(genome.seed!==value.seed)throw new Error('Receipt seed mismatch.');
  if(value.qbeast){beast=await readSparkFile(new TextEncoder().encode(JSON.stringify(value.qbeast)),table);beast.qbeast=value.qbeast;}else beast={genome,runIndex:value.runIndex,record:sparkRecord(genome,value.runIndex)};
 }else{beast=await readSparkFile(bytes,table);beast.qbeast=value;}
 const ledger=loadCage(localStorage);await admit(ledger,beast.record,'import');saveCage(ledger,localStorage);ready(beast,checkedSparkSave(beast,table));
 }catch(err){status(err.message);}finally{$('beast-file').value='';}});
$('download').addEventListener('click',()=>{if(save)download(`${current.genome.names['1']}${journey?'_JOURNEY':'_STARTER'}.sav`,save);});
$('receipt').addEventListener('click',()=>{if(current)download(`${current.genome.names['1']}_SPARK_RECEIPT.json`,JSON.stringify({schema:'sol-spark-art-receipt-v1',seed:current.genome.seed,traits:current.genome.inputs.traits,keeper:current.genome.inputs.user_id,runIndex:current.runIndex,forms:current.genome.names,...(current.qbeast?{qbeast:current.qbeast}:{})},null,2),'application/json');});
$('journey').addEventListener('change',async()=>{try{if(!current)throw new Error('Choose the matching Spark companion first.');const file=$('journey').files[0];if(!file)return;if(file.size!==32768)throw new Error('Choose a 32 KB battery save.');const raw=new Uint8Array(await file.arrayBuffer()),progress=readProgress(current.record.profile,raw);ready(current,attachSparkArt(raw,current.genome,current.runIndex,table,{journey:true,...(current.record.seed===current.genome.seed?{record:current.record}:{})}),true);status(`Journey kept: LV ${progress.level}, bond ${progress.bond}, native form ${progress.stage+1}. Download the updated battery save.`);}catch(err){status(err.message);}finally{$('journey').value='';}});
$('reset-player').addEventListener('click',()=>{$('handheld').src='./handheld.html?controller=iphoneaudio40';});
$('handheld').addEventListener('load',()=>{if(save)ready(current,save,journey);});
try{table=await loadTable();
 const approved=await fetch('./public-seeds.json').then(r=>{if(!r.ok)throw Error('Public recorded seeds unavailable.');return r.json()});
 for(const row of approved.runs){if(table.runs.some(r=>r.key===row.k))continue;table.runs.push({key:row.k,backend:row.b,job_id:row.j,pub_index:row.p,num_bits:row.n,shots:row.s,counts_sha256:row.h,counts:Object.fromEntries(row.c.split(',').map(p=>{const[k,v]=p.split(':');return[k,Number(v)]}))});}
 if(embedded)window.parent.postMessage({type:'sol-spark-ready'},'*');
 status('Spark or capture a companion on the left, then send it to the handheld. You can also import a Spark .qbeast from Vercel.');}catch(err){status(err.message);}
