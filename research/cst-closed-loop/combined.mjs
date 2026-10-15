// Combined loop: train on ALL archived workloads, then ablate on world outcomes.
// Usage: node research/cst-closed-loop/combined.mjs research/cst-closed-loop/tape_all.json research/cst-closed-loop/chsh_receipt.json
import {readFileSync} from 'node:fs';import {loadLoop,simulate} from './sim.mjs';
const html=readFileSync(new URL('../../standalone/SIM_EARTH_7_08_REALITY_BODY.html',import.meta.url),'utf8');
const CL=loadLoop(html.match(/<script id="cst-closed-loop">([\s\S]*?)<\/script>/)[1]);
const tapeAll=JSON.parse(readFileSync(process.argv[2],'utf8'));const chsh=JSON.parse(readFileSync(process.argv[3],'utf8'));
const mean=a=>a.reduce((s,x)=>s+x,0)/a.length,sd=a=>{const m=mean(a);return Math.sqrt(a.reduce((s,x)=>s+(x-m)**2,0)/(a.length-1))};
// 1) TRAIN: one pass over every archived hardware run (256 ticks each), then every SIMULATED run (labelled), then the new CHSH run in the Bell channel.
const nHw=tapeAll.hardware.length,nSim=tapeAll.simulated.length;
let st=simulate(CL,tapeAll,{seed:1,T:nHw*256,quantum:'recorded'});
const simTape={hardware:tapeAll.simulated};st=simulate(CL,simTape,{seed:2,T:nSim*256,quantum:'recorded',init:{w:st.weights,mem:st.mem}});
st=simulate(CL,tapeAll,{seed:3,T:18000,quantum:'recorded',init:{w:st.weights,mem:st.mem},bell:chsh,flags:{bellOn:true}});
const trained={w:st.weights,mem:st.mem};
console.log(`TRAINED on ${nHw} recorded IBM hardware runs + ${nSim} SIMULATED Rigetti runs + CHSH job ${chsh.job_id}; ticks=${(nHw+nSim)*256+18000}`);
console.log('trained weights:',trained.w.map(x=>x.toFixed(3)).join(' '));
// 2) ABLATE from the trained state. Use 12-bit hardware runs so joint bit structure exists.
const tape12={hardware:tapeAll.hardware.filter(r=>r.num_bits===12),simulated:tapeAll.simulated};
const SEEDS=[...Array(20)].map((_,i)=>201+i),T=18000,keys=['biosphere','stormTime','mood_joy','mood_curiosity','mood_fear','mood_calm','mood_mischief'];
const run=o=>SEEDS.map(seed=>simulate(CL,o.tape||tape12,{seed,T,init:o.untrained?null:trained,bell:chsh,flags:{bellOn:true,...(o.flags||{})},quantum:o.quantum||'recorded',bellMode:o.bellMode||'recorded'}));
const base=run({});
console.log('baseline means:',keys.map(k=>`${k}=${mean(base.map(r=>r[k])).toFixed(4)}`).join(' '),' bell<AB>=',mean(base.map(r=>r.bellMean)).toFixed(4));
const C={'qe: PRNG resampling recorded JOINT histogram':{quantum:'matched'},'qe: PRNG independent bits, matched MARGINALS only':{quantum:'marginals'},'qe: uniform PRNG':{quantum:'prng'},
 'Bell: PRNG matched per-setting JOINT (reproduces S)':{bellMode:'matched'},'Bell: closest local-hidden-variable (|S|<=2)':{bellMode:'lhv'},'Bell channel off':{flags:{bellOn:false}},
 'untrained weights (no history)':{untrained:true},'Lorenz->world off':{flags:{lorenzOut:false}},'Hebbian->world off':{flags:{hebbOut:false}},'state->world off (open loop)':{flags:{worldOn:false}}};
console.log('Cell = Glass Δ (mean change / between-seed SD of baseline); * = paired change > 2 SE; (relative change).');
console.log('| condition | '+keys.join(' | ')+' |');console.log('|---|'+keys.map(()=>'---').join('|')+'|');
for(const[name,o]of Object.entries(C)){const r=run(o);console.log(`| ${name} | `+keys.map(k=>{const d=r.map((x,i)=>x[k]-base[i][k]),m=mean(d),s=sd(d),sb=sd(base.map(x=>x[k])),bm=mean(base.map(x=>x[k]));return `${(m/(sb||1e-12)).toFixed(2)}${Math.abs(m)>2*s/Math.sqrt(d.length)?'*':''} (${(100*m/bm).toFixed(1)}%)`}).join(' | ')+' |')}
const lhv=CL.bellSource('lhv',chsh,1);console.log('recorded S=',chsh.chsh.S.toFixed(4),'LHV-model S=',lhv.S.toFixed(4));
