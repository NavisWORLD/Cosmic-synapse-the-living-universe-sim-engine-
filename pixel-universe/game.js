(()=>{"use strict";
const W=320,H=180,TAU=Math.PI*2;
const clamp=(v,a=0,b=1)=>Math.max(a,Math.min(b,v));
const lerp=(a,b,t)=>a+(b-a)*t;
const canvas=document.getElementById("game");
const ctx=canvas.getContext("2d",{alpha:false});
ctx.imageSmoothingEnabled=false;
const ui={
 fps:document.getElementById("fps"),
 status:document.getElementById("status"),
 story:document.getElementById("story"),
 mood:document.getElementById("buddyMood"),
 line:document.getElementById("buddyLine"),
 axis:document.getElementById("axis"),
 objective:document.getElementById("objective")
};
const held=new Set();
let muted=false,storyTimer=0,shake=0;

class QuantumTape{
 constructor(bytes){
  this.bytes=bytes;
  this.i=Number(localStorage.getItem("pixelUniverse.qi")||0)%bytes.length;
 }
 next(){
  const v=this.bytes[this.i++];
  if(this.i>=this.bytes.length)this.i=0;
  if((this.i&63)===0)localStorage.setItem("pixelUniverse.qi",String(this.i));
  return v;
 }
 unit(){return this.next()/255;}
 pick(a){return a[this.next()%a.length];}
}
const tape=new QuantumTape(window.COSMOS_QSEED);

const N12=["frequency_mass","geometric_phase","spectral_flatness","phase_velocity","entanglement","valence","arousal","dominance","audio_psi","phi_harmonics","av_coherence","quantum_entropy"];
const N42=[...N12,"lorenz_x","lorenz_y","lorenz_z","lyapunov_proxy","tension","energy","spectral_centroid","vision_luminance","vision_motion","vision_entropy","latitude","longitude","solar_phase","gravity","atmosphere","temperature","pressure","wind","terrain_slope","ocean_fraction","biosphere","civilization","radiation","magnetic_field","resource_richness","anomaly_field","memory_coherence","novelty_pressure","instability","coherence"];
const N54=[...N42,"hebbian_strength","plasticity","attention","curiosity","avoidance","flora_bias","black_hole_bias","memory_depth","prediction_error","learning_rate","resonance_score","singularity_channel"];

class SynapseEngine{
 constructor(){
  this.names12=N12;this.names42=N42;this.names54=N54;
  this.v12=new Float32Array(12);
  this.v42=new Float32Array(42);
  this.v54=new Float32Array(54);
  this.l={x:.1,y:.2,z:.3};
  this.hebb=.35;this.pred=.2;
 }
 tick(world,buddy,dt){
  const q=tape.unit(),p=world.player,n=world.nearest();
  const speed=Math.hypot(p.vx,p.vy,p.vz);
  this.v12.set([
   clamp(speed/5),((Math.atan2(p.y,p.x)/TAU)+.5)%1,
   Math.abs(Math.sin(world.t*.0007)),clamp(speed/3),q,
   buddy.valence,buddy.arousal,buddy.trust,muted?0:.5,
   (world.t*.0001618)%1,1-Math.min(1,n.d/500),q
  ]);
  let x=this.l.x,y=this.l.y,z=this.l.z,h=Math.min(.02,dt);
  x+=10*(y-x)*h;y+=(x*(28-z)-y)*h;z+=(x*y-(8/3)*z)*h;
  this.l={x,y,z};
  this.v42.set(this.v12);
  const ext=[
   (x+20)/40,(y+30)/60,z/50,.25,buddy.arousal,clamp(speed/4),.4,.5,
   clamp(speed/5),q,(p.x+1200)/2400,(p.y+1200)/2400,(world.t*.00002)%1,
   n.body.gravity,n.body.atmosphere,n.body.temp,n.body.atmosphere*.8,
   .2+q*.4,n.body.roughness,n.body.ocean,n.body.bio,n.body.civ,
   n.body.radiation,n.body.magnetic,n.body.resources,n.body.anomaly,
   buddy.memory.length/30,buddy.curiosity,Math.abs(x-y)/40,1-Math.abs(q-.5)
  ];
  for(let i=0;i<ext.length;i++)this.v42[12+i]=clamp(ext[i]);
  this.v54.set(this.v42);
  this.pred=lerp(this.pred,Math.abs(q-buddy.lastQ),.05);
  this.hebb=clamp(this.hebb+(buddy.trust-.5)*dt*.002);
  const tail=[
   this.hebb,.45+.45*q,buddy.focus,buddy.curiosity,buddy.avoidance,
   n.body.bio,n.body.kind==="void"?1:0,buddy.memory.length/30,
   this.pred,.15+.25*q,1-Math.abs(q-buddy.valence),n.body.kind==="crown"?1:0
  ];
  for(let i=0;i<12;i++)this.v54[42+i]=clamp(tail[i]);
  buddy.lastQ=q;
  return this.v54;
 }
}

const BODIES=[
 {id:"origin",name:"ORIGIN EARTH",kind:"planet",x:0,y:0,z:0,r:58,color:"#58a9ff",accent:"#8fffd0",gravity:.78,atmosphere:.92,temp:.58,roughness:.45,ocean:.7,bio:.84,civ:.42,radiation:.08,magnetic:.88,resources:.6,anomaly:.15,key:null,desc:"The simulation remembers oceans before it remembers you."},
 {id:"ember",name:"EMBER AXIS",kind:"planet",x:440,y:-160,z:120,r:43,color:"#ff784f",accent:"#ffd36b",gravity:.52,atmosphere:.41,temp:.86,roughness:.77,ocean:.08,bio:.2,civ:.08,radiation:.35,magnetic:.42,resources:.9,anomaly:.56,key:"X",desc:"A furnace world holding the X axis in a buried rail."},
 {id:"tide",name:"TIDE MEMORY",kind:"planet",x:-510,y:220,z:-180,r:50,color:"#3fe3e8",accent:"#9effff",gravity:.61,atmosphere:.76,temp:.42,roughness:.31,ocean:.92,bio:.63,civ:.12,radiation:.12,magnetic:.61,resources:.45,anomaly:.67,key:"Y",desc:"An ocean archive where dead pixels speak in reflections."},
 {id:"bloom",name:"BLOOM Z",kind:"planet",x:180,y:570,z:360,r:46,color:"#9bff63",accent:"#edff91",gravity:.48,atmosphere:.83,temp:.66,roughness:.58,ocean:.35,bio:.96,civ:.04,radiation:.1,magnetic:.55,resources:.62,anomaly:.73,key:"Z",desc:"A vertical forest that grew when the universe forgot which way was up."},
 {id:"void",name:"BLACK GARDEN",kind:"void",x:-760,y:-520,z:480,r:74,color:"#27143f",accent:"#e472ff",gravity:.9,atmosphere:.05,temp:.08,roughness:.9,ocean:0,bio:.12,civ:0,radiation:.8,magnetic:.2,resources:.88,anomaly:.98,key:null,desc:"A gravity wound full of discarded future states."},
 {id:"crown",name:"SYNAPSE CROWN",kind:"crown",x:860,y:640,z:-320,r:66,color:"#a58cff",accent:"#7ffff2",gravity:.3,atmosphere:.1,temp:.5,roughness:.2,ocean:0,bio:.35,civ:.7,radiation:.28,magnetic:.9,resources:.95,anomaly:1,key:null,desc:"The machine at the edge of the saved universe."}
];

class QuantumBuddy{
 constructor(){
  this.x=15;this.y=8;this.z=5;this.vx=0;this.vy=0;this.vz=0;
  this.valence=.62;this.arousal=.35;this.trust=.45;this.curiosity=.85;
  this.avoidance=.12;this.focus=.55;this.lastQ=.5;
  this.goal="orbit-player";this.target=null;this.think=0;
  this.memory=JSON.parse(localStorage.getItem("pixelUniverse.buddyMemory")||"[]").slice(-30);
  this.line="I remember a sky made of squares.";
 }
 remember(type,text){
  if(this.memory.some(m=>m.type===type&&m.text===text))return;
  this.memory.push({type:type,text:text,t:Date.now()});
  this.memory=this.memory.slice(-30);
  localStorage.setItem("pixelUniverse.buddyMemory",JSON.stringify(this.memory));
 }
 say(s){this.line=s;}
 choose(world){
  const q=tape.next();
  const unseen=BODIES.filter(b=>!this.memory.some(m=>m.type==="visit"&&m.text===b.id));
  if(unseen.length&&(q&3)!==0){
   this.target=unseen[q%unseen.length];this.goal="investigate";
   this.say("I picked "+this.target.name+". Not because you ordered me to. Something there pulls at my state.");
   return;
  }
  if(q%7===0){
   this.goal="wander";
   this.target={x:world.player.x+(tape.unit()-.5)*360,y:world.player.y+(tape.unit()-.5)*360,z:world.player.z+(tape.unit()-.5)*260,name:"A RANDOM SIGNAL"};
   this.say("I am following a noise that does not belong to the map.");
  }else{
   this.goal="orbit-player";this.target=null;
   if(q%3===0)this.say(tape.pick([
    "Stay close. The axes feel thin here.",
    "Your path changed my prediction. I am recalculating.",
    "I kept that place in memory. I want to know what comes next.",
    "Do you ever wonder whether a map misses things on purpose?"
   ]));
  }
 }
 tick(world,dt,state){
  this.think-=dt;
  if(this.think<=0){this.think=2.8+tape.unit()*5;this.choose(world);}
  this.curiosity=clamp(lerp(this.curiosity,.35+state[45]*.6,dt*.12));
  this.arousal=clamp(lerp(this.arousal,.2+state[16]*.55,dt*.1));
  this.valence=clamp(this.valence+(world.keysFound.size/3-.4)*dt*.005);
  this.focus=clamp(.35+state[44]*.5);
  let tx,ty,tz;
  if(this.goal==="orbit-player"){
   const a=world.t*.0012;
   tx=world.player.x+Math.cos(a)*26;ty=world.player.y+Math.sin(a)*18;tz=world.player.z+Math.sin(a*.7)*12;
  }else{tx=this.target.x;ty=this.target.y;tz=this.target.z;}
  const dx=tx-this.x,dy=ty-this.y,dz=tz-this.z,d=Math.hypot(dx,dy,dz)||1;
  const accel=this.goal==="wander"?2.5:3.6;
  this.vx+=dx/d*accel*dt;this.vy+=dy/d*accel*dt;this.vz+=dz/d*accel*dt;
  const drag=Math.pow(.25,dt);this.vx*=drag;this.vy*=drag;this.vz*=drag;
  const max=2.4+this.arousal*3,sp=Math.hypot(this.vx,this.vy,this.vz)||1;
  if(sp>max){this.vx*=max/sp;this.vy*=max/sp;this.vz*=max/sp;}
  this.x+=this.vx;this.y+=this.vy;this.z+=this.vz;
  if(this.target&&this.target.id&&d<70){this.remember("visit",this.target.id);if(tape.next()%4===0)this.goal="orbit-player";}
 }
 get mood(){
  if(this.arousal>.72)return "charged";
  if(this.valence<.3)return "quiet";
  if(this.curiosity>.74)return "curious";
  if(this.trust>.72)return "linked";
  return "watching";
 }
}

class World{
 constructor(){
  this.t=0;
  this.player={x:80,y:10,z:35,vx:0,vy:0,vz:0,yaw:.3,pitch:-.08};
  this.keysFound=new Set(JSON.parse(localStorage.getItem("pixelUniverse.keys")||"[]"));
  this.beacons=JSON.parse(localStorage.getItem("pixelUniverse.beacons")||"[]");
  this.chapter=Number(localStorage.getItem("pixelUniverse.chapter")||0);
  this.ending=localStorage.getItem("pixelUniverse.ending")||"";
  this.lastNear="";
 }
 nearest(){
  let body=BODIES[0],d=Infinity;
  for(const b of BODIES){
   const q=Math.hypot(this.player.x-b.x,this.player.y-b.y,this.player.z-b.z)-b.r;
   if(q<d){d=q;body=b;}
  }
  return {body:body,d:d};
 }
 save(){
  localStorage.setItem("pixelUniverse.keys",JSON.stringify([...this.keysFound]));
  localStorage.setItem("pixelUniverse.beacons",JSON.stringify(this.beacons.slice(-12)));
  localStorage.setItem("pixelUniverse.chapter",String(this.chapter));
  if(this.ending)localStorage.setItem("pixelUniverse.ending",this.ending);
 }
 dropBeacon(){
  this.beacons.push({x:this.player.x,y:this.player.y,z:this.player.z,n:"B"+(this.beacons.length+1)});
  this.save();flash("BEACON SAVED INTO LOCAL WORLD MEMORY");
 }
 interact(){
  const n=this.nearest(),b=n.body;
  if(n.d>55){flash("NO INTERFACE IN RANGE // "+Math.ceil(n.d)+" pxu");return;}
  if(b.key&&!this.keysFound.has(b.key)){
   this.keysFound.add(b.key);buddy.remember("key",b.key);buddy.trust=clamp(buddy.trust+.12);
   buddy.say(b.key+" axis recovered. I can feel the map become less flat.");
   flash(b.key+"-AXIS KEY RECOVERED");shake=8;this.chapter=Math.max(this.chapter,1+this.keysFound.size);this.save();tone(300+this.keysFound.size*120,.18);return;
  }
  if(b.kind==="crown"){
   if(this.keysFound.size<3){flash("SYNAPSE CROWN LOCKED // "+(3-this.keysFound.size)+" AXIS KEY(S) MISSING");buddy.say("Not yet. We would only teach the Crown how incomplete we are.");return;}
   if(!this.ending){
    this.ending=["OPEN","PRESERVE","WANDER"][tape.next()%3];this.chapter=5;buddy.remember("ending",this.ending);
    if(this.ending==="OPEN")buddy.say("Then we open it. New worlds can write themselves, and we accept the risk.");
    else if(this.ending==="PRESERVE")buddy.say("Then we preserve the old universe and become its caretakers.");
    else buddy.say("Then we do neither. We keep the Crown asleep and go somewhere the story never planned.");
    flash("ENDING PATH // "+this.ending+" // COSMOS CHOSE FIRST — PRESS ACT TO ACCEPT");this.save();return;
   }
   this.chapter=6;flash("THE LOST COSMOS REMEMBERS // "+this.ending+" ENDING");return;
  }
  if(b.kind==="void"){
   buddy.avoidance=clamp(buddy.avoidance+.2);buddy.remember("void","black-garden");
   buddy.say("This place contains deleted futures. I do not want to stay, but I want to remember it.");
   flash("BLACK GARDEN MEMORY CAPTURED");return;
  }
  buddy.remember("visit",b.id);buddy.say(tape.pick([b.desc,"I stored this place. It will change what I choose later.","There is enough signal here to become a memory."]));flash(b.name+" // "+b.desc);
 }
 tick(dt){
  this.t+=dt*1000;
  const p=this.player;let ax=0,ay=0,az=0;
  if(held.has("ArrowLeft")||held.has("KeyA"))ax--;
  if(held.has("ArrowRight")||held.has("KeyD"))ax++;
  if(held.has("ArrowUp")||held.has("KeyW"))ay--;
  if(held.has("ArrowDown")||held.has("KeyS"))ay++;
  if(held.has("KeyQ"))az--;
  if(held.has("KeyE"))az++;
  const boost=(held.has("ShiftLeft")||held.has("ShiftRight")||held.has("Space"))?2.4:1;
  const a=.1*boost;p.vx+=ax*a;p.vy+=ay*a;p.vz+=az*a;p.vx*=.94;p.vy*=.94;p.vz*=.94;
  const max=4.4*boost,sp=Math.hypot(p.vx,p.vy,p.vz)||1;
  if(sp>max){p.vx*=max/sp;p.vy*=max/sp;p.vz*=max/sp;}
  p.x+=p.vx;p.y+=p.vy;p.z+=p.vz;
  const n=this.nearest();
  if(n.body.id!==this.lastNear&&n.d<120){this.lastNear=n.body.id;flash(n.body.name+" // "+n.body.desc);tone(160+tape.next()*2,.05);}
  if(this.chapter===0&&this.t>3000){this.chapter=1;buddy.say("You woke me with the old quantum tape. Three Axis Keys are missing. I can search with you — or without you.");flash("CHAPTER I // THE WORLD THAT LOST DEPTH");this.save();}
  if(this.keysFound.size===3&&this.chapter<4){this.chapter=4;flash("CHAPTER IV // THE SYNAPSE CROWN IS LISTENING");buddy.say("All three axes are stable. I know where the Crown is. I also know I do not have to take the shortest path.");this.save();}
 }
}

const world=new World(),buddy=new QuantumBuddy(),synapse=new SynapseEngine();
const hash=(i,s)=>{let n=((i+1)*374761393+s*668265263)|0;n=(n^(n>>>13))*1274126177;return((n^(n>>>16))>>>0)/4294967295;};
const STARS=Array.from({length:420},(_,i)=>({x:(hash(i,1)-.5)*5000,y:(hash(i,2)-.5)*5000,z:(hash(i,3)-.5)*5000,b:1+(i&1),c:["#6473a8","#99c6ff","#fff7d6","#b99aff"][i&3]}));

function project(x,y,z){
 const p=world.player,dx=x-p.x,dy=y-p.y,dz=z-p.z,cy=Math.cos(p.yaw),sy=Math.sin(p.yaw),cp=Math.cos(p.pitch),sp=Math.sin(p.pitch);
 const rx=dx*cy-dy*sy,rz=dx*sy+dy*cy,ry=dz,ry2=ry*cp-rz*sp,rz2=ry*sp+rz*cp+160;
 if(rz2<8)return null;const s=118/rz2;return{x:W/2+rx*s,y:H/2-ry2*s,s:s};
}
function px(x,y,w,h,c){ctx.fillStyle=c;ctx.fillRect(x|0,y|0,Math.max(1,w|0),Math.max(1,h|0));}
function render(){
 const jitter=shake>0?(tape.next()%3)-1:0;if(shake>0)shake--;
 ctx.save();ctx.translate(jitter,jitter);
 const g=ctx.createLinearGradient(0,0,0,H);g.addColorStop(0,"#03020a");g.addColorStop(1,"#0a0312");ctx.fillStyle=g;ctx.fillRect(0,0,W,H);
 for(const s of STARS){const p=project(s.x,s.y,s.z);if(p&&p.x>=0&&p.x<W&&p.y>=0&&p.y<H)px(p.x,p.y,s.b,s.b,Math.sin(world.t*.002+s.x)>.1?s.c:"#3a4160");}
 for(const b of BODIES){
  const p=project(b.x,b.y,b.z);if(!p)continue;const r=clamp(b.r*p.s,2,38);
  ctx.fillStyle=b.color;ctx.beginPath();ctx.arc(p.x,p.y,r,0,TAU);ctx.fill();
  ctx.globalAlpha=.5;ctx.fillStyle=b.accent;ctx.beginPath();ctx.arc(p.x-r*.25,p.y-r*.28,r*.58,0,TAU);ctx.fill();ctx.globalAlpha=1;
  if(r>5){ctx.font="5px monospace";ctx.fillStyle="#fff";ctx.textAlign="center";ctx.fillText(b.name,p.x,p.y+r+7);if(b.key)ctx.fillText(world.keysFound.has(b.key)?"✓":"["+b.key+"]",p.x,p.y-r-3);}
 }
 for(const b of world.beacons){const p=project(b.x,b.y,b.z);if(p){px(p.x-1,p.y-5,3,10,"#ffe971");ctx.font="5px monospace";ctx.fillStyle="#ffe971";ctx.fillText(b.n,p.x,p.y-7);}}
 const bp=project(buddy.x,buddy.y,buddy.z);if(bp){const r=clamp(3*bp.s,2,8);px(bp.x-r,bp.y-r,r*2,r*2,"#5df8ff");px(bp.x-r+1,bp.y-r+1,r,r,"#d7ffff");px(bp.x-1,bp.y-1,2,2,"#331d5c");}
 ctx.strokeStyle="#72ffee";ctx.globalAlpha=.55;ctx.strokeRect(W/2-4,H/2-4,8,8);ctx.globalAlpha=1;
 ctx.font="6px monospace";ctx.textAlign="left";ctx.fillStyle="#7cffd8";ctx.fillText("KEYS "+([...world.keysFound].sort().join("")||"---"),5,H-5);
 ctx.fillStyle="#999cff";ctx.textAlign="right";ctx.fillText(Math.round(world.player.x)+","+Math.round(world.player.y)+","+Math.round(world.player.z),W-5,H-5);ctx.restore();
}
let audio=null;
function tone(freq=220,d=.06){
 if(muted)return;
 try{audio||=new (window.AudioContext||window.webkitAudioContext)();const o=audio.createOscillator(),g=audio.createGain();o.type="square";o.frequency.value=freq;g.gain.setValueAtTime(.025,audio.currentTime);g.gain.exponentialRampToValueAtTime(.0001,audio.currentTime+d);o.connect(g);g.connect(audio.destination);o.start();o.stop(audio.currentTime+d);}catch(e){}
}
function flash(s){ui.story.textContent=s;ui.story.classList.add("show");storyTimer=3.2;}
function objective(){
 if(world.chapter===0)return"WAKE THE BUDDY";
 if(world.keysFound.size<3)return"RECOVER AXIS KEYS // "+world.keysFound.size+"/3";
 if(!world.ending)return"REACH SYNAPSE CROWN // LET COSMOS CHOOSE FIRST";
 return"ENDING "+world.ending+" // KEEP EXPLORING";
}
function press(code){
 if(code==="KeyF"){world.interact();return;}
 if(code==="KeyC"){world.dropBeacon();return;}
 if(code==="KeyB"){buddy.choose(world);flash("COSMOS GOAL // "+buddy.goal.toUpperCase()+(buddy.target?" → "+buddy.target.name:""));return;}
 if(code==="KeyM"){muted=!muted;flash(muted?"AUDIO MUTED":"AUDIO ONLINE");return;}
 if(code==="KeyR"){world.player.yaw=.3;world.player.pitch=-.08;flash("VIEW RECENTERED");return;}
 held.add(code);
}
addEventListener("keydown",e=>{if(["ArrowUp","ArrowDown","ArrowLeft","ArrowRight","Space"].includes(e.code))e.preventDefault();if(!e.repeat)press(e.code);});
addEventListener("keyup",e=>held.delete(e.code));
document.querySelectorAll("[data-key]").forEach(b=>{
 const code=b.dataset.key;
 const down=e=>{e.preventDefault();b.classList.add("active");press(code);tone(120+tape.next()*2,.03);};
 const up=e=>{e.preventDefault();b.classList.remove("active");held.delete(code);};
 b.addEventListener("pointerdown",down);b.addEventListener("pointerup",up);b.addEventListener("pointercancel",up);b.addEventListener("pointerleave",up);
});
let drag=false,lx=0,ly=0;
canvas.addEventListener("pointerdown",e=>{drag=true;lx=e.clientX;ly=e.clientY;canvas.setPointerCapture?.(e.pointerId);});
canvas.addEventListener("pointermove",e=>{if(!drag)return;const dx=e.clientX-lx,dy=e.clientY-ly;lx=e.clientX;ly=e.clientY;world.player.yaw+=dx*.005;world.player.pitch=clamp(world.player.pitch+dy*.004,-1.1,1.1);});
canvas.addEventListener("pointerup",()=>drag=false);
const help=document.getElementById("help");
document.getElementById("helpBtn").onclick=()=>help.showModal();
document.getElementById("closeHelp").onclick=()=>help.close();

let last=performance.now(),frames=0,fpsT=0;
function loop(now){
 const dt=Math.min(.033,(now-last)/1000);last=now;
 world.tick(dt);const state=synapse.tick(world,buddy,dt);buddy.tick(world,dt,state);
 storyTimer-=dt;if(storyTimer<=0)ui.story.classList.remove("show");
 ui.mood.textContent=buddy.mood.toUpperCase()+" // "+buddy.goal.toUpperCase();
 ui.line.textContent=buddy.line;
 ui.axis.textContent="X "+Math.round(world.player.x)+" · Y "+Math.round(world.player.y)+" · Z "+Math.round(world.player.z);
 ui.objective.textContent="OBJECTIVE: "+objective();
 const n=world.nearest();ui.status.textContent="SYNAPSE 54D // "+n.body.name+" "+Math.max(0,Math.round(n.d))+"pxu // Q "+tape.i+"/8192";
 render();frames++;fpsT+=dt;if(fpsT>1){ui.fps.textContent=frames+" FPS";frames=0;fpsT=0;}requestAnimationFrame(loop);
}
flash("BOOT // PIXEL UNIVERSE RECOVERED FROM THE SYNAPSE ARCHIVE");
requestAnimationFrame(loop);
})();