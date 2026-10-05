// Reuse Spark's existing byte-compatible SHA; validation remains mandatory in an HTTP parent.
import {sha256Hex as syncSha256} from '../spark-beasts/hash.mjs';
export async function sha256Hex(input){
 const bytes=typeof input==='string'?new TextEncoder().encode(input):input instanceof Uint8Array?input:new Uint8Array(input);
 if(!globalThis.crypto?.subtle)return syncSha256(bytes);
 const digest=await crypto.subtle.digest('SHA-256',bytes);
 return [...new Uint8Array(digest)].map(b=>b.toString(16).padStart(2,'0')).join('');
}
