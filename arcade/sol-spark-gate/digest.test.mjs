import test from 'node:test';
import assert from 'node:assert/strict';
import {createHash,webcrypto} from 'node:crypto';
import {sha256Hex} from './digest.mjs';
test('public file and cartridge hashes remain exact without secure-context WebCrypto',async()=>{
 const original=Object.getOwnPropertyDescriptor(globalThis,'crypto');
 try{Object.defineProperty(globalThis,'crypto',{value:{},configurable:true});
 for(const bytes of [new Uint8Array(),new TextEncoder().encode('QBEAST1\\0Spark ⚛'),Uint8Array.from({length:32768},(_,i)=>i%251)])assert.equal(await sha256Hex(bytes),createHash('sha256').update(bytes).digest('hex'));
 }finally{if(original)Object.defineProperty(globalThis,'crypto',original);else delete globalThis.crypto;}
});
test('WebCrypto and the existing Spark SHA produce identical release checksums',async()=>{
 const original=Object.getOwnPropertyDescriptor(globalThis,'crypto');
 try{Object.defineProperty(globalThis,'crypto',{value:webcrypto,configurable:true});assert.equal(await sha256Hex('Spark ⚛'),createHash('sha256').update('Spark ⚛').digest('hex'));}
 finally{if(original)Object.defineProperty(globalThis,'crypto',original);else delete globalThis.crypto;}
});
