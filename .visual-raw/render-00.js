class SimRenderer{
 constructor(canvas,app){
  this.canvas=canvas;this.ctx=canvas.getContext('2d',{alpha:false});this.app=app;this.dpr=1;this.stars=[];this.quality=1;this.lastRenderMs=12;this.biomeCache=new Map();this.resize();addEventListener('resize',()=>this.resize());this.reseedStars();
 }
 resize(){const w=innerWidth,h=innerHeight;this.dpr=Math.min(1.7,devicePixelRatio||1);this.canvas.width=Math.round(w*this.dpr);this.canvas.height=Math.round(h*this.dpr);this.canvas.style.width=w+'px';this.canvas.style.height=h+'px';this.ctx.setTransform(this.dpr,0,0,this.dpr,0,0);this.w=w;this.h=h;this.quality=w<760?.72:1}
 reseedStars(){const r=seeded('SIM707','stars');this.stars=[];for(let i=0;i<760;i++)this.stars.push({x:r(),y:r(),s:.18+r()*1.9,a:.16+r()*.84,p:r()*PI*2,h:r()<.08?42:r()<.1?210:190})}
 terrain(x,z){const p=this.app.planet;let h=fbm(p.seed,x,z)*p.terrain*18;h+=Math.sin((x+z)*.006+hash32(p.seed)%100)*p.terrain*3;h+=noise1(p.seed+'::continental',x*.0024,z*.0024)*p.terrain*7-3.4*p.terrain;if(p.name==='Earth')h-=2;if(p.name==='Mars')h+=1.8*Math.sin(x*.011)*Math.cos(z*.008);if(['Jupiter','Saturn','Uranus','Neptune'].includes(p.name))h*=.08;return h}
 slopeAt(x,z){const d=1.4;return clamp(Math.hypot(this.terrain(x+d,z)-this.terrain(x-d,z),this.terrain(x,z+d)-this.terrain(x,z-d))/(d*9))}
 climate(x,z,h){
  const p=this.app.planet,s=this.app.sensors;const lat=s.loc.ok&&p.name==='Earth'?Math.abs(s.loc.lat)/90:Math.abs(Math.sin((z+hash32(p.seed)%4000)*.00032));
  const macro=noise1(p.seed+'::moist',x*.004,z*.004),micro=noise1(p.seed+'::wet',x*.026,z*.026);const moisture=clamp(p.water*.62+macro*.42+micro*.12-p.wind*.08);
  const lapse=Math.max(0,h)*.68;const temp=p.tempC-lat*42-lapse;return{lat,moisture,temp};
 }
 biomeAt(x,z,h){
  const p=this.app.planet;const waterLine=-1.2;if(p.atmo>50&&p.radiusKm>15000)return 'cloud_deck';if(p.water>.18&&h<=waterLine)return h<waterLine-5?'deep_ocean':'shallow_water';
  const c=this.climate(x,z,h);if(p.atmo<.015||p.tempC>120||p.tempC<-185)return p.tempC<-120?'ice_barren':'barren';
  if(c.temp<-15)return c.moisture>.48?'snowfield':'tundra';if(h>18*p.terrain&&c.temp<12)return 'alpine';
  if(c.temp>30&&c.moisture<.23)return 'desert';if(c.temp>24&&c.moisture>.68)return 'rainforest';if(c.moisture>.76&&Math.abs(h-waterLine)<3.5)return 'wetland';
  if(c.moisture>.55)return c.temp<10?'conifer_forest':'temperate_forest';if(c.moisture>.30)return 'grassland';return 'scrub';
 }
 materialPalette(b){
  const P={
   deep_ocean:[205,70,18],shallow_water:[194,66,30],cloud_deck:[38,38,56],snowfield:[205,20,86],ice_barren:[200,20,72],tundra:[74,22,42],alpine:[33,18,38],desert:[38,52,54],rainforest:[125,58,25],wetland:[101,46,29],conifer_forest:[124,45,23],temperate_forest:[104,52,29],grassland:[82,52,38],scrub:[64,34,38],barren:[25,20,39]
  };return P[b]||[this.app.planet.hue,this.app.planet.sat*.5,this.app.planet.light];
 }
 surfaceColor(x,z,h,dist,t){
  const p=this.app.planet,b=this.biomeAt(x,z,h),pal=this.materialPalette(b);let H=pal[0],S=pal[1],L=pal[2];const grain=(noise1(p.seed+'::grain',x*.19,z*.19)-.5)*10;
  if(b==='deep_ocean'||b==='shallow_water'){const wave=Math.sin(x*.16+z*.09+t*.0018)+Math.sin(z*.23-t*.0012);L+=wave*1.9+grain*.18;S+=4;}
  else{L+=grain+(h*.16);if(b==='snowfield')L+=noise1(p.seed+'snow',x*.08,z*.08)*6;if(b==='desert')H+=grain*.22;}
  const fog=clamp(dist/(p.atmo>.2?360:520));const horizonL=26+this.app.lightFactor*24;L=lerp(L,horizonL,fog*.62);S*=1-fog*.52;const light=.68+.32*this.app.lightFactor;L*=light;
  return `hsl(${(H+360)%360} ${clamp(S,0,96)}% ${clamp(L,3,92)}%)`;
 }
 drawStars(t,alpha=1){const c=this.ctx;for(const s of this.stars){const tw=.52+.48*Math.sin(t*.0012+s.p);c.globalAlpha=alpha*s.a*tw;c.fillStyle=`hsl(${s.h} 85% 90%)`;c.fillRect(s.x*this.w,s.y*this.h,s.s,s.s)}c.globalAlpha=1}
