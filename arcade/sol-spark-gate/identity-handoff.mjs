/** Public identity and unsigned native SRAM are checked independently. */
import {verifySparkArt} from './cartridge.mjs';
import {batteryName,chooseBattery} from './battery.mjs';
import {MAILBOX_OFFSET,MAILBOX_BYTES,GROWTH_OFFSET,GROWTH_BYTES,profileFromBcp1} from '../lost-cosmos/mailbox.mjs';
import {readProgress} from '../sol-beast-lab/design.mjs';
const word=(b,o)=>new DataView(b.buffer,b.byteOffset,b.byteLength).getUint32(o,true);
function profileIn(bytes){
 verifySparkArt(bytes);
 if(String.fromCharCode(...bytes.subarray(MAILBOX_OFFSET,MAILBOX_OFFSET+4))!=='LCX1'||bytes[MAILBOX_OFFSET+4]!==1||bytes[MAILBOX_OFFSET+5]&~7)throw Error('The native mailbox format is invalid.');
 return profileFromBcp1(bytes.slice(MAILBOX_OFFSET+32,MAILBOX_OFFSET+96),{gameSeed:word(bytes,MAILBOX_OFFSET+10)});
}
function sameProfile(actual,expected){
 if(actual.publicId!==expected.publicId||actual.gameSeed!==expected.gameSeed||!actual.bcp1.every((v,i)=>v===expected.bcp1[i]))throw Error('The saved battery belongs to another companion identity.');
}
export function checkedCloudBattery(text,starter){
 if(typeof text!=='string'||text.length!==43692||!/^[A-Za-z0-9+/]{43691}=$/.test(text))throw Error('The saved journey must be a complete 32 KB native battery.');
 let bytes;try{bytes=Uint8Array.from(atob(text),c=>c.charCodeAt(0));}catch{throw Error('The saved native battery encoding is invalid.');}
 sameProfile(profileIn(bytes),profileIn(starter));
 if(batteryName(bytes)!==batteryName(starter))throw Error('The saved battery namespace belongs to another companion.');
 chooseBattery(starter,bytes);
 if(String.fromCharCode(...bytes.subarray(0,4))!=='LCV5'){
  if(!(bytes[MAILBOX_OFFSET+5]&1))throw Error('The consumed mailbox needs its original native journey save.');
  for(let i=0;i<bytes.length;i++){
   const owned=(i>=MAILBOX_OFFSET&&i<MAILBOX_OFFSET+MAILBOX_BYTES)||(i>=GROWTH_OFFSET&&i<GROWTH_OFFSET+GROWTH_BYTES)||(i>=24704&&i<24832)||i>=31744;
   if(!owned&&bytes[i]!==255)throw Error('The starter touches a protected journey region.');
  }
 }
 return bytes;
}
export function nativeIdentity(bytes,expected){
 const base={publicId:expected.publicId,gameSeed:expected.gameSeed,origin:'local-mailbox'};
 try{
  sameProfile(profileIn(bytes),expected);
  if(String.fromCharCode(...bytes.subarray(1024,1028))==='LCR1'){
   try{return{...base,status:'imported',source:'native-battery-checkpoint',...readProgress(expected,bytes),message:'The checksum-valid native roster contains this companion.'};}
   catch(error){
    if(!String(error?.message).includes('does not belong to your current companion'))throw error;
    return{...base,status:'missing',source:'native-battery-checkpoint',message:'This native roster has no matching companion. Choose CONTINUE with its original save, or recover the matching journey.'};
   }
  }
  if(bytes[MAILBOX_OFFSET+5]&1)return{...base,status:'mailbox-ready',source:'local-mailbox',message:'Verified companion mailbox ready. Start NEW GAME to import it; an imported roster has not been observed yet.'};
  return{...base,status:'missing',source:'native-battery-checkpoint',message:'The mailbox was consumed but a matching saved roster is unavailable. Choose CONTINUE or recover the original journey save.'};
 }catch(error){return{...base,status:'invalid',source:'native-battery-checkpoint',message:String(error?.message||'Native companion verification failed.').slice(0,180)};}
}
