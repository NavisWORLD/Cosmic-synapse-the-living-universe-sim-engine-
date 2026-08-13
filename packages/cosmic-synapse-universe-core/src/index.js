export const PHI=(1+Math.sqrt(5))/2;
export const clamp=(x,a=0,b=1)=>Math.max(a,Math.min(b,x));
export function hash32(s){s=String(s);let h=2166136261>>>0;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619)}return h>>>0}
export function mulberry32(seed){let a=seed>>>0;return()=>{a|=0;a=a+0x6D2B79F5|0;let t=a;t=Math.imul(t^t>>>15,t|1);t^=t+Math.imul(t^t>>>7,t|61);return((t^t>>>14)>>>0)/4294967296}}
export function seeded(...parts){return mulberry32(hash32(parts.join('|')))}
export function universeDNA({engineVersion='0.1.0',masterSeed='',worldSeed='',fixedStep=1/60,externalSnapshotHash='',commandHash=''}){const canonical=JSON.stringify({engineVersion,masterSeed,worldSeed,fixedStep,externalSnapshotHash,commandHash});return{canonical,hash:hash32(canonical).toString(16).padStart(8,'0')}}
export function normalizeSensorSummary(p={}){return{t:Number(p.t)||Date.now(),audioAvg:clamp(Number(p.audioAvg)||0),bass:clamp(Number(p.bass)||0),mid:clamp(Number(p.mid)||0),treble:clamp(Number(p.treble)||0),luminance:clamp(Number(p.luminance)||0),motion:clamp(Number(p.motion)||0),entropy:clamp(Number(p.entropy)||0),lat:Number.isFinite(Number(p.lat))?Number(p.lat):null,lon:Number.isFinite(Number(p.lon))?Number(p.lon):null}}
