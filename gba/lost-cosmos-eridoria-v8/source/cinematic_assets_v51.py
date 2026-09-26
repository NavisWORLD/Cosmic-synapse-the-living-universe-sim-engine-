"""Original cinematic backgrounds for the native GBA cartridge.
Native 240x160 4bpp palettes/tiles are generated from original 960x640
source paintings. All art is offline, original, deterministic and reproducible.
This is cinematic pre-rendered 2D, never an assertion of GBA 4K/3D.
"""
from PIL import Image, ImageDraw, ImageFilter
from pathlib import Path
import math, random
ROOT=Path(__file__).resolve().parent
W,H,SS=240,160,4
SCENES=('awakening','warp','origin','ember','tide','bloom','black_garden','synapse_crown','dream_veil','eldoria','malakar')
# Deliberately curated indexed palettes. Index 0 is never used in final BG2 tiles.
PALETTES=[
 #  0 transparent, 1 deep, 2 space, 3 mist, 4 horizon, 5 dark structure, 6 shadow, 7 mids, 8 bright, 9 accent, 10 bright accent, 11 white, 12-15 glows/detail
 [(0,0,0),(5,7,21),(13,17,48),(30,33,73),(54,48,99),(16,25,53),(23,43,70),(50,73,104),(97,123,163),(41,134,172),(83,201,221),(232,238,233),(102,66,150),(168,105,181),(226,165,169),(244,206,127)],
 [(0,0,0),(6,9,27),(13,20,54),(38,25,78),(66,47,106),(16,30,70),(35,62,111),(55,92,153),(103,140,193),(72,180,197),(130,225,222),(241,245,242),(137,67,188),(202,107,221),(239,170,224),(248,211,149)],
 [(0,0,0),(10,24,35),(22,43,61),(43,79,95),(82,117,116),(19,53,50),(30,76,64),(60,108,76),(114,153,91),(70,164,123),(129,213,166),(240,235,190),(99,92,65),(154,123,78),(218,174,100),(249,220,151)],
 [(0,0,0),(21,10,29),(48,13,36),(79,25,43),(128,39,45),(60,32,35),(107,51,32),(165,72,35),(219,115,39),(215,67,35),(242,133,56),(255,224,146),(120,50,82),(167,56,72),(238,86,62),(255,185,84)],
 [(0,0,0),(5,21,43),(16,41,69),(22,65,94),(40,105,136),(16,50,69),(19,88,116),(52,130,151),(87,170,176),(42,172,191),(124,214,215),(222,249,232),(56,80,134),(81,133,181),(124,185,219),(179,232,236)],
 [(0,0,0),(7,27,38),(16,60,54),(36,96,73),(59,136,82),(17,69,50),(34,100,73),(69,145,85),(124,176,99),(72,189,132),(171,220,132),(246,237,186),(75,81,136),(111,124,181),(177,167,212),(239,204,228)],
 [(0,0,0),(6,6,17),(16,13,33),(30,21,47),(47,32,66),(13,18,35),(36,30,64),(73,43,95),(103,58,125),(88,70,152),(158,100,184),(227,192,234),(61,25,83),(111,45,132),(183,63,170),(233,127,195)],
 [(0,0,0),(6,12,32),(19,29,64),(35,58,96),(63,93,142),(22,48,77),(34,76,118),(61,113,155),(123,170,193),(67,179,181),(137,221,209),(231,242,220),(95,76,156),(155,112,192),(217,154,193),(248,210,151)],
 # Dream Veil: rose and ultramarine skies, iridescent white archways
 [(0,0,0),(9,7,32),(28,17,68),(53,30,106),(88,49,134),(25,21,72),(62,51,122),(117,83,166),(169,119,208),(105,175,222),(194,230,241),(251,245,225),(112,62,140),(192,110,194),(249,174,216),(254,223,159)],
 # Eldoria: luminous turquoise forests and gold crystal architecture
 [(0,0,0),(4,23,31),(12,50,57),(25,82,85),(52,117,99),(18,58,54),(33,101,72),(84,157,115),(137,197,145),(62,196,170),(164,235,194),(248,246,202),(121,113,76),(174,147,78),(236,194,110),(255,227,156)],
 # Malakar: angular black-red hall, indigo energy and radiant captured heart
 [(0,0,0),(12,4,22),(37,9,41),(70,12,67),(111,24,76),(44,12,34),(90,24,57),(154,44,80),(198,67,93),(173,44,151),(243,128,177),(249,219,202),(96,33,113),(171,58,162),(251,114,122),(255,191,104)],
]
# Paint at 4x: high-res paintings are the production assets, indexed images actual GBA inputs.
# Deliberately varied landscape composition with painterly illumination, layered depth and fine silhouettes.
def painting(sid):
 rng=random.Random(7419+sid*803)
 p=PALETTES[sid]
 im=Image.new('RGB',(W*SS,H*SS),p[1]);d=ImageDraw.Draw(im)
 S=lambda n:int(n*SS)
 def poly(pts,c):d.polygon([(S(x),S(y)) for x,y in pts],fill=c)
 def oval(bb,c,outline=None,width=1):d.ellipse(tuple(S(z) for z in bb),fill=c,outline=outline,width=S(width))
 def line(points,c,width=1):d.line([(S(x),S(y)) for x,y in points],fill=c,width=S(width),joint='curve')
 # Discrete atmospheric gradients preserve 4bpp tile reuse and still feel painterly.
 for y in range(H):
  if sid in (0,1,6,7,8,10):band=(y*3)//110
  else:band=(y*3)//98
  col=p[min(4,1+band)]
  d.rectangle((0,S(y),S(W),S(y+1)),fill=col)
 if sid in (0,1,6,7,8,10):
  for i in range(95):
   x=rng.randrange(W);y=rng.randrange(112)
   v=10 if i%5==0 else (8 if i%3 else 11)
   radius=(i%11==0)
   oval((x,y,x+(1 if radius else .4),y+(1 if radius else .4)),p[v])
 # luminous rim-lit celestial bodies and scenic silhouette shapes
 if sid==0:
  # enormous planet: layered penumbra, offset halo and thin planetary rings
  for r,col in ((47,p[4]),(43,p[3]),(38,p[7]),(35,p[8]),(32,p[6])):
   oval((164-r,68-r,164+r,68+r),col)
  oval((145,36,189,60),p[3]);oval((141,64,196,79),p[7]);oval((159,79,182,86),p[3])
  for dy,c in ((0,p[13]),(2,p[9]),(5,p[12])):
   line([(113,98+dy),(125,91+dy),(154,88+dy),(190,85+dy),(217,90+dy)],c,1)
  # Ruined antenna silhouettes on the left foreground.
  poly([(0,126),(13,111),(25,118),(39,99),(48,114),(62,104),(81,133),(103,118),(123,160),(0,160)],p[5])
  for x,ht in ((9,22),(33,33),(59,27),(79,21)):
   d.rectangle((S(x),S(139-ht),S(x+4),S(160)),fill=p[6]);line([(x-3,133-ht),(x+2,129-ht),(x+7,133-ht)],p[10],1)
  line([(18,155),(45,134),(64,142),(87,126),(104,153)],p[9],1)
 elif sid==1:
  cx,cy=120,76
  for r,c in ((65,3),(56,4),(50,7),(43,12),(38,6),(30,3),(24,2),(14,1)):
   oval((cx-r,cy-r//2,cx+r,cy+r//2),p[c])
  for j in range(78):
   x=rng.randrange(W);y=rng.randrange(H)
   dx=x-cx;dy=y-cy
   if abs(dx)<30 and abs(dy)<17:continue
   col=p[(8,10,13,15)[j%4]]
   line([(x,y),(x+int(dx*.16),y+int(dy*.16))],col,1+(j%9==0))
  oval((110,66,130,86),p[1]);oval((116,71,124,79),p[11])
 else:
  # planetary atmosphere, distant bodies and silhouettes, distinct per planet
  sun_x=(179 if sid%2 else 53);sun_y=51+(sid*4)%16
  for rr,v in ((28,3),(21,4),(14,8),(9,11)):
   oval((sun_x-rr,sun_y-rr,sun_x+rr,sun_y+rr),p[v])
  for layer in range(3):
   horizon=93+layer*21
   color=p[5+layer]
   pts=[(0,H),(0,horizon-5)]
   for x in range(0,W+12,12):
    ht=rng.randrange(4,18+layer*3)
    pts.extend([(x,horizon-ht),(x+6,horizon-ht//2),(x+12,horizon-8)])
   pts.extend([(W,H)])
   poly(pts,color)
  # each biome gets distinctive landmarks, intricate silhouette highlights
  if sid==2:
   # Origin: shattered observatory and gigantic ivy arch
   poly([(30,151),(39,95),(48,88),(55,141),(76,144),(86,160)],p[5]);oval((28,90,51,110),p[6]);oval((33,95,49,108),p[9])
   for x,h in ((111,52),(129,43),(143,31),(155,58)):
    d.rectangle((S(x),S(148-h),S(x+6),S(155)),fill=p[5]);line([(x,148-h),(x+3,146-h),(x+6,148-h)],p[10],1)
   for i in range(18):
    x=6+(i*19)%233;y=112+(i*11)%41
    line([(x,y),(x+2,y-5),(x+5,y-8)],p[9],1)
  elif sid==3:
   # Ember: industrial furnace towers, smoke and lava ribbon
   for x,top,w in ((34,68,14),(68,89,18),(126,48,15),(185,71,16)):
    poly([(x,147),(x+3,top),(x+w,top-2),(x+w+5,151)],p[5])
    for y in range(top+9,139,12):
     d.rectangle((S(x+4),S(y),S(x+w),S(y+3)),fill=p[12])
   for delta in (0,9):
    line([(0,152+delta),(39,141+delta),(101,152+delta),(155,139+delta),(219,152+delta),(240,148+delta)],p[10 if delta else 9],2)
   for x in (49,133,203):
    for j in range(3):oval((x-6-j*4,37-j*10,x+6+j*5,51-j*10),p[3])
  elif sid==4:
   # Tide: elevated archival city, luminous bridges and waterways
   for x,y,w in ((30,87,20),(76,74,17),(125,83,26),(186,64,18)):
    d.rectangle((S(x),S(y),S(x+w),S(148)),fill=p[5]);oval((x-3,y-12,x+w+3,y+8),p[7]);
    for yy in range(y+12,140,14):line([(x+5,yy),(x+w-4,yy)],p[10],1)
   for y in (138,144,151):
    line([(0,y),(44,y-2),(92,y+1),(144,y-2),(210,y+2),(240,y)],p[9 if y==144 else 8],1)
  elif sid==5:
   # Bloom: vast mushroom canopy, iridescent vertical forests and blooms
   for x,top,w in ((22,63,36),(93,76,27),(172,53,45),(223,86,24)):
    line([(x,160),(x+3,top+14)],p[5],3)
    oval((x-w//2,top,x+w//2,top+22),p[9]);oval((x-w//2+3,top+2,x+w//2-3,top+9),p[10])
    for j in range(4):oval((x-w//3+j*5,top+3,x-w//3+j*5+3,top+6),p[11])
   for i in range(16):
    x=(i*29)%W;y=123+(i*9)%30
    oval((x,y,x+5,y+5),p[13 if i%2 else 10]);line([(x+2,y+3),(x+2,y+8)],p[9])
  elif sid==6:
   # Black Garden: shattered geometric monoliths in a folded universe
   for i,(x,tall) in enumerate(((14,92),(56,74),(106,94),(162,82),(206,66))):
    poly([(x,155),(x+8,155-tall//2),(x+17,155-tall),(x+22,146)],p[5])
    line([(x+4,144),(x+17,155-tall)],p[13 if i%2 else 9],1)
   for x,y in ((32,32),(96,49),(187,39)):
    line([(x-12,y-9),(x+11,y+5),(x-3,y+14),(x-12,y-9)],p[10],1)
  elif sid==8:
   # Dream: immense rings, silver arch, and three symbolic trial monoliths.
   for x,h,c in ((31,74,p[9]),(111,104,p[10]),(193,82,p[13])):
    poly([(x-12,157),(x-9,156-h),(x+9,153-h),(x+14,157)],p[5])
    oval((x-10,150-h,x+10,163-h),c)
   for r in (53,43,32):oval((67-r//2,99-r//2,67+r//2,99+r//2),p[12 if r==53 else 7],width=2)
   for x in range(0,240,20):line([(x,153),(x+8,141),(x+15,150)],p[9],1)
  elif sid==9:
   # Eldoria: towering glass trees, four elemental fountains and gilded roots.
   for x,h in ((18,62),(53,83),(91,51),(139,96),(196,73),(219,49)):
    poly([(x-5,157),(x-4,151-h),(x+4,151-h),(x+9,160)],p[5]);oval((x-20,139-h,x+20,165-h),p[7]);oval((x-13,142-h,x+14,158-h),p[9])
   for x,col in ((38,p[12]),(91,p[9]),(153,p[14]),(209,p[10])):
    poly([(x-11,155),(x,127),(x+12,155)],col);line([(x,144),(x,119)],p[11],2)
  elif sid==10:
   # Malakar as a striking silhouette, framed by split heart rays.
   for r,c in ((47,p[12]),(36,p[13]),(26,p[8]),(20,p[10])):oval((173-r,61-r,173+r,61+r),c)
   poly([(51,159),(61,86),(75,51),(83,78),(92,45),(111,89),(125,158)],p[5]);
   poly([(59,102),(77,42),(83,85),(92,52),(103,105),(112,160),(40,160)],p[6])
   oval((76,64,88,76),p[14]);line([(65,118),(118,88),(159,112)],p[14],2)
  else:
   # Crown: enormous central spire and branching cosmic circuitry
   poly([(79,160),(94,113),(107,97),(115,37),(128,37),(136,97),(156,116),(168,160)],p[5])
   poly([(109,112),(116,51),(126,51),(133,114)],p[7]);oval((114,39,129,56),p[10]);
   for x in (16,35,192,212):
    poly([(x,160),(x+5,96),(x+13,89),(x+19,160)],p[6]);line([(x+6,101),(x+13,95)],p[10],1)
   for j in range(7):
    y=116+j*6;line([(3,y),(80,y+2),(117,y),(155,y+2),(235,y)],p[9 if j%2 else 12],1)
 # atmospheric small luminous motifs on foreground, respecting palette reuse
 if sid!=1:
  for i in range(16):
   x=(i*37+sid*19)%W;y=115+(i*13)%40
   oval((x,y,x+1,y+1),p[10 if i%3 else 11])
 return im

def quantize(src,palette):
 # Restricted curated palette is critical to match hardware. No hidden full-color paths.
 pal_img=Image.new('P',(16,1))
 flat=[v for rgb in palette for v in rgb]+[0]*(768-48)
 pal_img.putpalette(flat)
 low=src.resize((W,H),Image.Resampling.BICUBIC)
 indexed=low.quantize(palette=pal_img,dither=Image.Dither.NONE)
 # GBA text BG color index zero is transparent, replace it with deep background.
 arr=bytearray(indexed.tobytes())
 for i,v in enumerate(arr):
  if v==0:arr[i]=1
 im=Image.frombytes('P',(W,H),bytes(arr));im.putpalette(flat)
 return im

def pack_scene(im):
 data=im.tobytes();lookup={};tiles=[];maps=[]
 for ty in range(20):
  for tx in range(30):
   packed=[]
   for y in range(8):
    for xx in (0,2,4,6):
     a=data[(ty*8+y)*W+tx*8+xx]
     b=data[(ty*8+y)*W+tx*8+xx+1]
     packed.append(a|(b<<4))
   key=bytes(packed)
   if key not in lookup:
    lookup[key]=len(tiles);tiles.append(key)
   maps.append(lookup[key])
 assert len(tiles)<=512,(len(tiles),'GBA charblock2 tile overflow')
 return tiles,maps

def main():
 all_tiles=[];maps=[];counts=[];offsets=[];palettes=[]
 for sid,scene in enumerate(SCENES):
  src=painting(sid)
  src.save(ROOT/f'V51_source_{scene}_960x640.png')
  im=quantize(src,PALETTES[sid]);im.save(ROOT/f'V51_GBA_indexed_{scene}_240x160.png')
  tt,mm=pack_scene(im)
  offsets.append(len(all_tiles));counts.append(len(tt));all_tiles+=tt;maps.append(mm)
  palettes.append([sum((c>>3)<<(i*5) for i,c in enumerate(rgb)) for rgb in PALETTES[sid]])
  print(f'{scene:16s}: {len(tt):3d} unique tiles; {len(tt)*32:6d} uncompressed graphics bytes')
 assert len(all_tiles)<7200
 hdr=['/* Generated with cinematic_assets_v51.py: original 960x640 paintings reduced into real GBA 4bpp scenes. */',
      '#ifndef CINEMATIC_ASSETS_V51_H','#define CINEMATIC_ASSETS_V51_H',
      f'#define V51_SCENE_COUNT {len(SCENES)}',
      f'static const u16 V51_SCENE_OFFSETS[{len(SCENES)}]={{'+','.join(str(z) for z in offsets)+'};',
      f'static const u16 V51_SCENE_COUNTS[{len(SCENES)}]={{'+','.join(str(z) for z in counts)+'};',
      f'static const u16 V51_SCENE_COLORS[{len(SCENES)}][16]={{'+','.join('{'+','.join(f'0x{z:04x}' for z in pal)+'}' for pal in palettes)+'};',
      f'static const u16 V51_SCENE_MAPS[{len(SCENES)}][600]={{']
 for mm in maps:hdr.append('{'+','.join(str(z) for z in mm)+'},')
 hdr.append('};')
 hdr.append('static const u32 V51_SCENE_TILES[][8]={')
 for t in all_tiles:
  w=[int.from_bytes(t[j:j+4],'little') for j in range(0,32,4)]
  hdr.append('{'+','.join(f'0x{v:08x}u' for v in w)+'},')
 hdr.append('};\n#endif')
 (ROOT/'cinematic_assets_v51.h').write_text('\n'.join(hdr))
 print('CINEMATIC_ATLAS_TOTAL:',len(all_tiles),'tiles;',len(all_tiles)*32,'bytes')
 # Honest comparison sheet: high-resolution source vs actual indexed 240x160 output.
 sheet=Image.new('RGB',(W*4*2,H*4*2),(5,8,22))
 for i,sid in enumerate((0,3)):
  source=Image.open(ROOT/f'V51_source_{SCENES[sid]}_960x640.png')
  final=Image.open(ROOT/f'V51_GBA_indexed_{SCENES[sid]}_240x160.png').convert('RGB').resize((W*4,H*4),Image.Resampling.NEAREST)
  sheet.paste(source,(0,i*H*4));sheet.paste(final,(W*4,i*H*4))
 sheet.save(ROOT/'V51_source_vs_native_indexed.png')
if __name__=='__main__':main()
