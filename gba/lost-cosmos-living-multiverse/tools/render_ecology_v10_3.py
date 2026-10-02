#!/usr/bin/env python3
"""Host-replay REAL ARM7 game engine's generated cartridge-native 4bpp OBJ tile buffers.
No pixel art is invented by this preview script; not a real mGBA or hardware screenshot.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
from PIL import Image, ImageDraw, ImageFont
import subprocess,struct
r=Path(__file__).resolve().parents[1];g=r/'LOST_COSMOS_V10_SOURCE';p=r/'previews';p.mkdir(exist_ok=True)
subprocess.run(['python3','host_qa_v5.py'],cwd=g,check=True,stdout=subprocess.DEVNULL,timeout=45)
s=(g/'host_qa_v5.c').read_text().split('\n#ifdef HOST_QA\nint main(',1)[0]
code='''
#include <stdio.h>
int main(int argc,char**argv){FILE*f;if(argc!=2)return 2;
 f=fopen(argv[1],"wb");if(!f)return 4;
 init_new_game();init_graphics();current_world=0;current_layer=1;current_room=2;generate_surface();
 for(int k=1;k<=8;k++){
  int pal=k<=5?4+k:k==6?7:k==7?6:8;
  fwrite((void*)(HOST_OBJ_PALETTE+pal*16),2,16,f);
  for(int st=0;st<3;st++)for(int phase=0;phase<2;phase++)
   fwrite((void*)(HOST_VRAM+0x10000+(384+(k-1)*24+st*8+phase*4)*32),1,128,f);
 }
 fclose(f);return 0;
}
'''
with TemporaryDirectory(prefix='lc_v103_original_sprites_') as td:
 d=Path(td);(d/'host.c').write_text(s+code)
 subprocess.run(['clang','-O2','-DHOST_QA','-DQA_AUTORUN',f'-I{g}',str(d/'host.c'),'-o',str(d/'host')],check=True,timeout=60)
 subprocess.run([str(d/'host'),str(d/'pixels.bin')],check=True,timeout=30)
 b=(d/'pixels.bin').read_bytes()
assert len(b)==8*(32+6*128)
fonts='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
load=lambda n:ImageFont.truetype(fonts,n) if Path(fonts).exists() else None
big,med,small=load(30),load(19),load(13)
base=['FORGELING','TIDEWISP','ROOTKIN','VOIDMOTH','SKYSPARK','FROST WOLF','EMBER PHOENIX','HOLLOW WRAITH']
evolved=[['HEARTHCUB','SOLFORGE'],['RILLWISP','DEEPTIDE'],['THORNBARK','WORLDROOT'],['NIGHTMOTH','ECLIPSEMOTH'],['STORMWING','SKYFORGE'],['FROSTFANG','GLACIAL KING'],['SUNPLUME','ASHEN PHOENIX'],['DUSKSPIRIT','VEILKEEPER']]
img=Image.new('RGB',(1140,1360),(9,13,28));a=ImageDraw.Draw(img)
a.text((26,16),'LOST COSMOS  /  EIGHT LIVING SPECIES',font=big,fill=(221,238,255))
a.text((28,59),'48 actual native GBA sprites: 8 species x 3 evolution forms x 2 animated poses',font=med,fill=(95,227,218))
a.text((28,88),'Each silhouette and evolution glow is produced by the actual native game engine.',font=small,fill=(178,198,218))
pos=0
for i in range(8):
 pal=struct.unpack_from('<16H',b,pos);pos+=32
 rowtop=124+i*148
 if i%2==0:a.rounded_rectangle((16,rowtop-4,1125,rowtop+137),radius=14,fill=(18,31,53))
 a.text((28,rowtop+7),f'{i+1:02d} {base[i]}',font=med,fill=(242,225,170))
 forms=[base[i]]+evolved[i]
 for st in range(3):
  x=306+st*274
  a.text((x+17,rowtop+8),f'{forms[st]}  /  STAGE {st}',font=small,fill=(163,204,229))
  for ph in range(2):
   raw=b[pos:pos+128];pos+=128
   f=Image.new('RGBA',(16,16),(0,0,0,0));pix=f.load()
   for y in range(16):
    for xx in range(16):
     n=((y//8)*2+(xx//8))*32+(y%8)*4+(xx%8)//2
     color=(raw[n]>>4) if xx%2 else (raw[n]&15)
     if color:
      val=pal[color];pix[xx,y]=((val&31)*255//31,((val>>5)&31)*255//31,((val>>10)&31)*255//31,255)
   scale=f.resize((92,92),Image.Resampling.NEAREST)
   img.paste(scale,(x+ph*112,rowtop+34),scale)
   a.text((x+ph*112+28,rowtop+129),'POSE '+str(ph+1),font=small,fill=(170,195,216))
a.text((28,1324),'ACTUAL C-ENGINE PIXEL BUFFER REPLAY. Development visualization only; NOT emulator footage or Delta proof.',font=small,fill=(175,186,211))
out=p/'LOST_COSMOS_V10_3_NATIVE_EVOLUTION_SPRITES.png';img.save(out,optimize=True)
rootout=Path('/mnt/data/LOST_COSMOS_V10_3_NATIVE_EVOLUTION_SPRITES.png');rootout.write_bytes(out.read_bytes())
print('PASS: actual native source-derived sprites',len(b),'raw bytes for 48 sprites:',out,rootout.stat().st_size,'PNG bytes')
