const ellipse=(x,y,cx,cy,rx,ry)=>(x-cx)**2*ry*ry+(y-cy)**2*rx*rx<=rx*rx*ry*ry;
const rect=(x,y,l,t,r,b)=>x>=l&&x<=r&&y>=t&&y<=b;
function shape(x,y,seed,meta,s) {
  const i=meta&7,calm=(meta>>5)&3,spark=(meta>>7)&3,w=(seed>>2)&1;
  if(ellipse(x,y,15,18-s,7+s+w,7+s+Number(calm>=2))) return true;
  if(rect(x,y,10-s,24+s,13,26+s)||rect(x,y,17,24+s,20+s,26+s)) return true;
  if(i===0 && ((y>=5-s&&y<=12&&Math.abs(x-9)<=(y-4+s)/2)||(y>=5-s&&y<=12&&Math.abs(x-21)<=(y-4+s)/2)||ellipse(x,y,5,22,3+s,2+spark))) return true;
  if(i===1 && (ellipse(x,y,10,9-s,3,4)||ellipse(x,y,20,9-s,3,4)||rect(x,y,14,4-s,15,9)||ellipse(x,y,17,5-s,3+s,2))) return true;
  if(i===2 && (ellipse(x,y,9,9-s,3,4)||ellipse(x,y,21,9-s,3,4)||rect(x,y,11,5-s,19,7)||rect(x,y,11,3-s,12,6)||rect(x,y,15,2,16,6)||rect(x,y,18,3-s,19,6))) return true;
  if(i===3 && (ellipse(x,y,10,7,2+s,5+s)||ellipse(x,y,20,7,2+s,5+s)||ellipse(x,y,24,22,3,3))) return true;
  if(i===4 && (ellipse(x,y,9,9-s,3+s,3+s)||ellipse(x,y,21,9-s,3+s,3+s)||rect(x,y,4-s,16,7,21)||rect(x,y,24,16,26+s,21))) return true;
  if(i===5 && (ellipse(x,y,6,20-s,3+s,4+s)||ellipse(x,y,24,20-s,3+s,4+s)||ellipse(x,y,15,7-s,2+s,3)||rect(x,y,14,26,16,28))) return true;
  if(i===6 && (ellipse(x,y,7,17,4+s,6+s)||ellipse(x,y,23,17,4+s,6+s)||rect(x,y,10,5-s,11,10)||rect(x,y,19,5-s,20,10)||ellipse(x,y,9,5-s,2,2)||ellipse(x,y,21,5-s,2,2))) return true;
  if(i===7 && (rect(x,y,3-s,12,7,14)||rect(x,y,2,17,7,19)||rect(x,y,4-s,22,8,24)||rect(x,y,23,12,27+s,14)||rect(x,y,23,17,28,19)||rect(x,y,22,22,26+s,24)||ellipse(x,y,15,7-s,2+s,3))) return true;
  return false;
}
export function colorAt(x,y,seed,meta,stage,blink=0) {
  const s=Math.max(0,Math.min(2,stage)),i=meta&7,focus=(meta>>3)&3;
  if(!shape(x,y,seed,meta,s)) return 0;
  if(!shape(x-1,y,seed,meta,s)||!shape(x+1,y,seed,meta,s)||!shape(x,y-1,seed,meta,s)||!shape(x,y+1,seed,meta,s)) return 1;
  if(y<10-s) return i===1?10:i===2?8:3;
  const eyeY=14-s,eyes=(x>=11&&x<=12)||(x>=18&&x<=19);
  if(eyes&&y>=eyeY&&y<=eyeY+2) return blink?((y===eyeY+1)?7:2):((y===eyeY&&((x===11)||(x===18)))?4:7);
  if(y===eyeY+3&&(x===9||x===10||x===20||x===21)) return 6;
  if((x===15||x===16)&&y===eyeY+4) return 7;
  if(i===5 && rect(x,y,14,eyeY+3,16,eyeY+3)) return 8;
  if(s===2&&y===21&&x>=13&&x<=17) return focus>=2?9:8;
  if(ellipse(x,y,15,23-s,4+s,3+s)) return 12;
  if(x<10||x>21) return i===6?10:5;
  if(((seed>>4)&1)&&x===14&&y===11-s) return 8;
  return x+y<30-s?3:2;
}
const RGB5=(r,g,b)=>(Math.round(r/255*31))|(Math.round(g/255*31)<<5)|(Math.round(b/255*31)<<10);
const COLORS=['f6af75','86d9aa','d0b7ff','b6e9ff','e5ae89','ff9f9a','aea5e9','85ddd7'];
const rgb=hex=>[0,2,4].map(n=>parseInt(hex.slice(n,n+2),16));
export function renderSprite(beast,stage=0,blink=0) {
  const base=rgb(COLORS[beast.island]),jitter=((beast.gameSeed>>8)&15)-7;
  const tone=add=>RGB5(...base.map((n,i)=>Math.max(0,Math.min(255,n+add+(i===2?jitter:0)))));
  const palette=new Uint16Array([0,RGB5(24,24,47),tone(0),tone(32),RGB5(255,250,236),tone(-36),RGB5(255,154,181),RGB5(32,27,48),RGB5(255,216,126),RGB5(121,239,238),tone(-8),RGB5(251,239,190),RGB5(...base.map(n=>Math.round(n*.35+255*.65))),0x2d35,0x16c7,(beast.meta&0x67ff)|(stage<<11)]);
  const pixels=Uint8Array.from({length:1024},(_,n)=>colorAt(n%32,Math.floor(n/32),beast.gameSeed,beast.meta,stage,blink));
  return {pixels,palette};
}
export function packTiles(pixels) {
  const out=new Uint8Array(512);
  for(let y=0;y<32;y++) for(let x=0;x<32;x+=2) out[(Math.floor(y/8)*4+Math.floor(x/8))*32+(y%8)*4+Math.floor(x%8/2)]=pixels[y*32+x]|(pixels[y*32+x+1]<<4);
  return out;
}
export function paintSprite(ctx,sprite,x,y,scale=1) {
  for(let py=0;py<32;py++) for(let px=0;px<32;px++) {
    const index=sprite.pixels[py*32+px]; if(!index) continue; const c=sprite.palette[index];
    ctx.fillStyle=`rgb(${(c&31)*255/31},${((c>>5)&31)*255/31},${((c>>10)&31)*255/31})`;
    ctx.fillRect(x+px*scale,y+py*scale,scale,scale);
  }
}
