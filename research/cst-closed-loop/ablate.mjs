// Usage: node research/cst-closed-loop/ablate.mjs  (reads the module + seed tape straight out of the canonical HTML)
import {readFileSync} from 'node:fs';import {loadLoop,simulate} from './sim.mjs';
const html=readFileSync(new URL('../../standalone/SIM_EARTH_7_08_REALITY_BODY.html',import.meta.url),'utf8');
const src=html.match(/<script id="cst-closed-loop">([\s\S]*?)<\/script>/)[1];const tape=JSON.parse(html.match(/<script type="application\/json" id="cst-seed-tape">([\s\S]*?)<\/script>/)[1]);
const CL=loadLoop(src);
const SEEDS=[...Array(20)].map((_,i)=>101+i);const keys=['biosphere','stormTime','mood_joy','mood_curiosity','mood_fear','mood_calm','mood_mischief'];
const T=18000;const run=o=>SEEDS.map(seed=>simulate(CL,tape,{seed,T,...o}));
const mean=a=>a.reduce((s,x)=>s+x,0)/a.length,sd=a=>{const m=mean(a);return Math.sqrt(a.reduce((s,x)=>s+(x-m)**2,0)/(a.length-1))};
// paired Cohen's d (same sensor seed in both arms): mean(diff)/sd(diff); dz
const base=run({});const C={
 'quantum: PRNG (uniform)':{quantum:'prng'},'quantum: PRNG resampling recorded histogram':{quantum:'matched'},'quantum: legacy sin-hash':{quantum:'legacy'},
 'quantum: constant 0.5':{quantum:'const'},'quantum: Rigetti SIMULATED':{quantum:'simulated'},
 'Lorenz input off':{flags:{lorenzIn:false}},'Lorenz->world off':{flags:{lorenzOut:false}},'Hebbian->state off':{flags:{hebbIn:false}},'Hebbian->world off':{flags:{hebbOut:false}},'state->world off (open loop)':{flags:{worldOn:false}}};
const fmt=x=>(Math.abs(x)>=100?x.toFixed(0):x.toFixed(2));
console.log('baseline (recorded IBM seeds), 20 seeds x 18000 ticks (600 s sim @30fps):',keys.map(k=>`${k}=${mean(base.map(r=>r[k])).toFixed(4)}`).join(' '));
console.log('Cell = Glass Δ (mean change / between-seed SD of baseline); * = paired change > 2 SE; (relative change of mean).');console.log('| condition | '+keys.join(' | ')+' |');console.log('|---|'+keys.map(()=>'---').join('|')+'|');
for(const[name,o]of Object.entries(C)){const r=run(o);console.log(`| ${name} | `+keys.map(k=>{const d=r.map((x,i)=>x[k]-base[i][k]);const s=sd(d);const m=mean(d);const sb=sd(base.map(x=>x[k]));const bm=mean(base.map(x=>x[k]));const g=m/(sb||1e-12);const sig=Math.abs(m)>2*s/Math.sqrt(d.length);return `${g.toFixed(2)}${sig?'*':''} (${(100*m/bm).toFixed(1)}%)`}).join(' | ')+' |')}
