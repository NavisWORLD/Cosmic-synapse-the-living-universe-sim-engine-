// Headless closed-loop harness: JS port of CSTStateEngine.update (SIM EARTH 7.08) with seeded synthetic sensors,
// calling the REAL CSTClosedLoop couplings. World = biosphere + storm; outcomes measured after T ticks.
import {createRequire} from 'node:module';
export function loadLoop(src){const f=new Function('globalThis',src+';return globalThis.CSTClosedLoop;');return f({})}
const cl=(x,a=0,b=1)=>x<a?a:x>b?b:x,fract=x=>x-Math.floor(x);
export function simulate(CL,tape,{seed=7,T=6000,dt=1/30,flags={},quantum='recorded',init=null,bell=null,bellMode='recorded',qsrc=null}={}){
 const F={...CL.FLAGS,...flags,quantum};const sr=CL.mulberry32(seed*7919+1);const gauss=()=>{let u=sr()||1e-9,v=sr();return Math.sqrt(-2*Math.log(u))*Math.cos(2*Math.PI*v)};
 const qs=qsrc||(quantum==='legacy'?null:CL.quantumSource(quantum,tape,seed*31+5));const bs=bell?CL.bellSource(bellMode,bell,seed*17+3):null;let bellSum=0;
 let w=init?Float64Array.from(init.w):new Float64Array(12).fill(.5),mem=init?Float64Array.from(init.mem):new Float64Array(12),L={x:.1,y:.2,z:.3},prev=0,hebbPrev=.25;
 const world={biosphere:.4,storm:.1};const grav=1,rad=.1,res=.6;let stormInt=0,moodSum={joy:0,curiosity:0,fear:0,calm:0,mischief:0};
 const v=new Float64Array(54);
 for(let t=0;t<T;t++){
  const avg=cl(.3+.2*Math.sin(t*.01+seed)+.05*gauss()),bass=avg*.8,mid=avg*.6,treb=avg*.4,flat=.25,lum=.4+.1*Math.sin(t*.003),mot=cl(Math.abs(.1*gauss()));
  const fm=cl(avg*1.8),ph=Math.atan2(mid-bass+Math.sin(t*dt*.11)*.05,treb+.05)*1.2;let dp=ph-prev;dp=((dp+Math.PI)%(2*Math.PI)+2*Math.PI)%(2*Math.PI)-Math.PI;const pv=cl(dp/Math.max(.001,dt)/8,-1,1);prev=ph;
  const bio=world.biosphere,storm=world.storm;
  const ent=cl(1-Math.abs(fm-lum*.9)),val=cl(.5+(lum-.5)*.55+(bio-.4)*.28,-1,1),aro=cl(fm*.75+mot*.55+storm*.25),dom=cl(.45+grav*.08),psi=cl(avg*1.8),phiH=.6,av=cl(1-Math.abs(aro-mot*.8-lum*.2));
  const ms=1.7e12+Math.floor(t*dt*1000);const qe=qs?qs.next():fract(Math.sin((ms%100000)*.000071+.5+fm*5)*43758.5453);
  const v12=[fm,ph,flat,pv,ent,val,aro,dom,psi,phiH,av,qe];
  CL.lorenzStep(L,dt*.035,{arousal:aro,qe},F);
  const chaos=cl(Math.hypot(L.x,L.y,L.z)/55),anomaly=cl(storm*.15+chaos*.18),memC=cl(1-Math.abs(bio-mem[0])),nov=cl(Math.abs(qe-mem[1])*.9+anomaly*.5);
  const inst=cl(chaos*.4+flat*.25+storm*.4);let coh=cl(ent*.28+av*.26+memC*.2+(1-inst)*.26);coh=CL.coherenceFeedback(coh,hebbPrev,F);
  const hebb=cl(w.reduce((s,x)=>s+x,0)/12*coh),plast=cl(.15+nov*.65+(1-coh)*.2),att=cl(aro*.35+nov*.4+coh*.25),cur=cl(nov*.7+res*.3),avoid=cl(rad*.35+storm*.35+inst*.3);
  const predE=cl(Math.abs(mem[2]-coh)),lr=cl(.03+plast*.17),reson=cl((phiH+ent+coh+memC)/4),sing=cl(Math.abs(pv)*.25+inst*.35+(1-coh)*.4);
  const adapt=[hebb,plast,att,cur,avoid,cl(.7+bio*.3),cl(1-anomaly*.6),cl(t*dt/60/120),predE,lr,reson,sing];
  v12.forEach((x,i)=>v[i]=x);v[15]=chaos;v[40]=inst;v[41]=coh;adapt.forEach((x,i)=>v[42+i]=x);
  for(let i=0;i<12;i++){w[i]=cl(w[i]+lr*(adapt[i]*v12[i]-w[i])*.02);mem[i]+=(v12[i]-mem[i])*cl(dt*.15)}
  hebbPrev=hebb;CL.coupleWorld(world,v,dt,F);if(bs){const pr=bs.next(aro>.5?1:0,cur>.5?1:0);bellSum+=pr/T;CL.bellCouple(world,v,pr,dt,F)}stormInt+=world.storm*dt;const m=CL.creatureMood(v);for(const k in m)moodSum[k]+=m[k]/T;
 }
 return{weights:Array.from(w),mem:Array.from(mem),bellMean:bellSum,biosphere:world.biosphere,storm:world.storm,stormTime:stormInt,...Object.fromEntries(Object.entries(moodSum).map(([k,x])=>['mood_'+k,x])),qLabel:qs?qs.label:'LEGACY_SIN_HASH'};
}
