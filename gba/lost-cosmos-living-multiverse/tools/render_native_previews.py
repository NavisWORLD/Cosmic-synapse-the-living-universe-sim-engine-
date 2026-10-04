#!/usr/bin/env python3
"""Actual HOST-emulated C engine VRAM tilemap/OBJ memory preview renderer.
NOT an mGBA screenshot or evidence of hardware/Delta acceptance.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import struct,subprocess
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[1]
G=R/'LOST_COSMOS_V10_SOURCE'
P=R/'previews'
P.mkdir(exist_ok=True)
# Native HOST QA source is generated from the CURRENT engine, never static mock data.
subprocess.run(['python3','host_qa_v5.py'],cwd=G,check=True,stdout=subprocess.DEVNULL,timeout=35)
pre=(G/'host_qa_v5.c').read_text().split('\n#ifdef HOST_QA\nint main(',1)[0]
code=r'''
#include <stdio.h>
int main(int argc,char**argv){FILE*file;int i,x,y;u16 n;
 if(argc!=2)return 2;
 file=fopen(argv[1],"wb");if(!file)return 4;
 init_new_game();init_graphics();current_world=0;current_layer=1;
 game_mode=MODE_SURFACE;
 for(i=0;i<ARC_STAGES;i++){
  current_room=(u8)(ARC_FIRST_ROOM+i);generate_surface();
  fwrite((void*)HOST_BG_PALETTE,2,256,file);
  for(y=0;y<64;y++)for(x=0;x<64;x++){
   n=screenblock(BG_MAP_BASE+(x>>5)+((y>>5)<<1))[(y&31)*32+(x&31)];
   fwrite(&n,2,1,file);
  }
 }
 fwrite((void*)HOST_VRAM,1,0x4000,file);
 for(i=1;i<=5;i++){
  fwrite((void*)(HOST_OBJ_PALETTE+(4+i)*16),2,16,file);
  fwrite((void*)(HOST_VRAM+0x10000+(384+(i-1)*8)*32),1,128,file);
  fwrite((void*)(HOST_VRAM+0x10000+(384+(i-1)*8+4)*32),1,128,file);
 }
 fclose(file);return 0;
}'''
with TemporaryDirectory(prefix='cosmos_hostpreview_') as td:
 td=Path(td);(td/'hostmap.c').write_text(pre+code)
 subprocess.run(['clang','-O2','-DHOST_QA','-DQA_AUTORUN',f'-I{G}',str(td/'hostmap.c'),'-o',str(td/'hostmap')],check=True,timeout=40)
 subprocess.run([str(td/'hostmap'),str(td/'native_render.bin')],check=True,timeout=30)
 buf=(td/'native_render.bin').read_bytes()
room_names=['FOREST THRESHOLD','TRIAL CAVERN','SENTINEL HALL','WHISPER MIRRORS',
 'SILVER TOMES','THE WORLD TREE','HARMONY GROVE','PETAL GATEWAY',
 'THREE TRIALS','VERDANT ALTAR','TWILIGHT PASS','DAWN-DUSK MARK',
 'DREAM MEADOW','CHRONO ANNEX','VOIDWARD RUINS','TWILIGHT CITADEL']
fonts='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
regular=ImageFont.truetype(fonts,14) if Path(fonts).exists() else None
small=ImageFont.truetype(fonts,12) if Path(fonts).exists() else None
header=ImageFont.truetype(fonts,25) if Path(fonts).exists() else None
w=1192;bw=280;bh=308
atlas=Image.new('RGB',(w,1338),(8,12,29));a=ImageDraw.Draw(atlas)
a.text((31,20),'LOST COSMOS  /  THE ERIDORIA ATLAS',font=header,fill=(225,232,245))
a.text((31,62),'16 actual procedural GBA engine tilemaps  •  64 × 64 native tiles each',font=regular,fill=(99,227,222))
index=0
for rid in range(16):
 pal=struct.unpack_from('<256H',buf,index);index+=512
 ent=struct.unpack_from('<4096H',buf,index);index+=8192
 if rid==0:
  tile_raw=buf[16*(512+8192):16*(512+8192)+0x4000]
 # BG palette is BGR555 from real host engine; transparent tile index0 still visible as BG palette0.
 tile_cache={}
 def rgb15(v):return ((v&31)*255//31,((v>>5)&31)*255//31,((v>>10)&31)*255//31)
 img=Image.new('RGB',(512,512))
 for yy in range(64):
  for xx in range(64):
   cell=ent[yy*64+xx];tid=cell&1023;pi=(cell>>12)&15
   k=(tid,pi)
   if k not in tile_cache:
    bt=Image.new('RGB',(8,8));pix=bt.load();start=tid*32
    for ty in range(8):
     for tx in range(8):
      v=tile_raw[start+ty*4+tx//2] if start+ty*4+tx//2<len(tile_raw) else 0
      c=(v>>4) if tx&1 else (v&15)
      pix[tx,ty]=rgb15(pal[pi*16+c])
    tile_cache[k]=bt
   img.paste(tile_cache[k],(xx*8,yy*8))
 x=20+(rid%4)*294;y=100+(rid//4)*305
 thumb=img.resize((256,256),Image.Resampling.NEAREST)
 atlas.paste(thumb,(x,y+32))
 a.rounded_rectangle((x,y-1,x+256,y+28),radius=5,fill=(24,40,60))
 a.text((x+9,y+7),f'{rid+1:02d}   {room_names[rid]}',fill=(235,241,251),font=small)
 a.rectangle((x,y+32,x+255,y+287),outline=(52,112,131),width=1)
a.text((25,1321),'DEVELOPMENT PREVIEW — rendered from the actual native C engine tile/VRAM data. Not an emulator screenshot.',fill=(173,184,208),font=small)
output=P/'LOST_COSMOS_V10_2_NATIVE_MAP_ATLAS_PREVIEW.png';atlas.save(output)
index+=0x4000
species=['FORGELING','TIDEWISP','ROOTKIN','VOIDMOTH','SKYSPARK']
show=Image.new('RGB',(1250,382),(8,12,29));d=ImageDraw.Draw(show)
d.text((24,17),'BEAST BOX / THE FIVE ORIGINAL NATIVE SPECIES',font=header,fill=(225,232,245))
d.text((24,60),'Ten REAL GBA OBJ sprite frames / five creatures x two animated poses',font=regular,fill=(99,227,222))
for s in range(5):
 pal=struct.unpack_from('<16H',buf,index);index+=32
 frames=[]
 for pose in range(2):
  b=buf[index:index+128];index+=128
  f=Image.new('RGBA',(16,16),(0,0,0,0));p=f.load()
  for y in range(16):
   for x in range(16):
    off=((y//8)*2+(x//8))*32+(y%8)*4+(x%8)//2
    v=b[off];c=(v>>4) if x&1 else v&15
    if c:
     z=pal[c]
     p[x,y]=((z&31)*255//31,((z>>5)&31)*255//31,((z>>10)&31)*255//31,255)
  frames.append(f)
 xx=20+s*248
 d.rounded_rectangle((xx,106,xx+235,352),radius=13,fill=(18,32,52),outline=(51,117,147),width=2)
 for pose,f in enumerate(frames):
  show.paste(f.resize((104,104),Image.Resampling.NEAREST),(xx+8+pose*114,155),f.resize((104,104),Image.Resampling.NEAREST))
  d.text((xx+41+pose*114,268),'IDLE '+str(pose+1),font=small,fill=(148,181,213))
 d.text((xx+16,126),species[s],font=regular,fill=(255,236,191))
 d.text((xx+20,308),'16×16  •  4bpp OBJ',font=small,fill=(119,209,207))
d.text((23,363),'Engine memory visualization, not footage of physical hardware or Delta.',font=small,fill=(177,185,208))
output2=P/'LOST_COSMOS_V10_2_NATIVE_CREATURE_SPRITES.png';show.save(output2)
print('ATLAS',output,output.stat().st_size,'bytes')
print('CREATURES',output2,output2.stat().st_size,'bytes')
print('ROOMS',len(room_names),'FRAMES',5*2,'RAW bytes',len(buf))
