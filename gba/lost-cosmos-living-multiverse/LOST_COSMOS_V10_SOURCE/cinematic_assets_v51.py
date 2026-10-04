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
SCENES=('awakening','warp','origin','ember','tide','bloom','black_garden','synapse_crown','dream_veil','eldoria','malakar','riftfall','brindlemark_forge','brindlemark_siege','heartwood_heart','glacial_clarity','phoenix_passion','hollow_earth','celestial_harmony','dream_festival','ending_open','ending_preserve','ending_wander')
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
 # Riftfall: original prismatic cyan/magenta/gold fractured dimension.
 [(0,0,0),(6,7,24),(19,11,45),(33,18,72),(56,27,99),(17,28,58),(40,52,96),(76,58,132),(103,96,181),(32,175,195),(89,238,214),(235,248,231),(113,37,143),(200,62,190),(251,143,204),(255,220,133)],
 # New authored frames: warm forge vs. siege. Original palette assets, 4bpp conversion.
 [(0,0,0),(13,10,25),(37,19,36),(69,37,40),(103,55,42),(47,35,40),(90,61,50),(147,98,52),(215,155,73),(52,147,169),(105,208,214),(249,230,192),(96,59,105),(174,107,82),(250,181,75),(255,241,182)],
 [(0,0,0),(8,9,22),(22,19,48),(54,28,63),(88,31,75),(24,30,55),(58,54,84),(115,56,93),(161,93,112),(53,134,188),(111,214,230),(239,229,216),(96,36,141),(184,63,161),(247,112,119),(255,204,133)],
 # Original Heartwood: midnight evergreen, green lightning, sacred golden heart.
 [(0,0,0),(5,19,26),(13,39,36),(22,69,57),(42,103,70),(14,48,42),(29,83,51),(56,126,76),(125,158,77),(42,187,125),(133,232,162),(244,240,200),(88,85,64),(173,139,65),(231,195,88),(255,240,146)],
 # Frost wolf and Clarity: royal ultramarine ice, cyan light, cold silver.
 [(0,0,0),(7,16,39),(14,33,76),(33,60,113),(67,108,155),(21,43,92),(31,76,126),(67,132,180),(119,193,218),(68,212,227),(163,239,247),(248,250,243),(64,79,151),(125,138,203),(173,227,252),(244,246,225)],
 # Phoenix and Passion: black volcanic obsidian, orange-gold fire.
 [(0,0,0),(20,5,20),(45,9,31),(86,23,37),(130,37,36),(60,23,39),(108,36,33),(177,68,28),(227,117,26),(233,70,43),(255,172,65),(255,232,175),(124,27,77),(193,42,59),(247,104,57),(255,224,119)],
 # Earth memory and Hollow Grove: deep moss, opal water, luminescent roots.
 [(0,0,0),(6,24,27),(13,53,46),(36,87,61),(57,118,80),(20,62,43),(46,91,70),(82,143,98),(137,188,127),(71,181,164),(150,221,179),(247,238,195),(83,108,90),(155,162,100),(208,193,122),(249,239,177)],
 # Celestial Harmony: brass observatory and deep cobalt starlit heavens.
 [(0,0,0),(6,12,39),(21,27,72),(38,55,108),(62,84,147),(20,39,69),(46,69,105),(89,130,158),(143,177,194),(66,175,219),(155,224,234),(247,238,193),(108,82,146),(174,138,177),(225,193,152),(251,232,166)],
 # Dream Festival: iridescent lavender and turquoise musical lights.
 [(0,0,0),(16,10,47),(38,27,87),(66,49,124),(104,70,153),(49,37,91),(73,79,127),(127,117,170),(183,166,208),(89,188,210),(175,231,223),(253,241,225),(133,72,182),(220,116,200),(254,174,217),(253,223,138)],
 # Open: innumerable free civilizations each has its own color in a restored lattice.
 [(0,0,0),(4,18,37),(15,40,67),(40,89,115),(67,136,148),(20,62,74),(32,113,113),(83,164,142),(145,205,160),(58,207,201),(168,231,211),(247,242,210),(104,79,160),(173,128,198),(221,167,207),(255,226,145)],
 # Preserve: intact enclosed Crown in deep blue, restored stone and warm homes.
 [(0,0,0),(11,16,37),(26,38,71),(40,65,97),(69,91,125),(30,43,65),(58,73,92),(103,132,142),(167,185,172),(84,173,175),(166,223,203),(252,241,208),(110,95,143),(185,154,166),(227,188,139),(255,225,153)],
 # Wander: uncharted prismatic night voyage, a ship among nebulas and unknown moons.
 [(0,0,0),(4,7,28),(18,13,56),(42,27,85),(71,44,111),(25,28,71),(49,67,105),(95,111,150),(154,171,188),(59,174,212),(156,224,233),(245,240,224),(116,63,165),(194,105,187),(239,160,194),(255,217,146)],
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
  elif sid==15:
   # Crystal of Clarity rises from the mirror lake; frost wolf can be spared.
   poly([(0,150),(34,115),(55,126),(77,100),(91,133),(124,95),(166,122),(194,97),(240,139),(240,160),(0,160)],p[5])
   for x,h in ((4,45),(38,76),(77,55),(169,69),(209,83),(234,44)):
    poly([(x-8,144),(x-4,144-h),(x+10,153-h),(x+16,155)],p[6])
    line([(x-4,144-h),(x+4,154-h)],p[9],1)
   poly([(12,146),(49,121),(88,136),(139,119),(207,130),(240,143),(240,160),(0,160)],p[8])
   for i in range(14):
    y=139+i;line([(0,y),(80,y+((i*7)%5)),(133,y-2),(240,y+1)],p[9 if i%3==0 else 7],1)
   for r,col in ((35,p[3]),(27,p[7]),(19,p[9]),(12,p[11])):oval((128-r,72-r,128+r,72+r),col)
   poly([(127,40),(141,63),(133,97),(125,110),(114,91),(113,63)],p[14]);line([(125,49),(120,91)],p[11],2)
   # Readable wolf silhouette with silver eye and reflected outline.
   poly([(30,140),(35,116),(47,109),(56,87),(64,106),(77,110),(90,97),(99,120),(93,139)],p[1])
   poly([(38,116),(51,108),(60,94),(65,115),(83,115)],p[7]);oval((53,113,57,117),p[11]);line([(31,139),(101,139)],p[10],1)
  elif sid==16:
   # Ember Caverns Phoenix: wings rise from basalt crown around Passion.
   for i in range(5):
    x=9+i*57;poly([(x,155),(x+6,90-i%2*16),(x+21,130),(x+36,158)],p[5])
    line([(x+8,103),(x+15,131)],p[9],1)
   for y in (127,140,150):
    line([(0,y),(62,y-9),(97,y+2),(164,y-11),(240,y-3)],p[10 if y==140 else 9],2)
   for r,c in ((45,p[4]),(38,p[12]),(30,p[7]),(21,p[15])):
    oval((132-r,70-r,132+r,70+r),c)
   # Original phoenix silhouette drawn as a fiery Y with feather blades.
   poly([(119,106),(109,86),(81,76),(48,44),(81,56),(101,59),(108,41),(120,58),(133,35),(145,59),(173,50),(212,33),(189,72),(157,86),(138,106),(140,133),(127,116)],p[14])
   poly([(119,106),(80,85),(59,65),(107,80),(120,58),(130,80),(188,62),(169,85),(139,108)],p[9])
   oval((119,67,136,82),p[15]);oval((132,74,135,78),p[1]);line([(128,82),(131,113)],p[11],2)
   for i in range(18):
    x=18+(i*43)%208;y=14+(i*19)%114;line([(x,y),(x+2,y-6)],p[14 if i%2 else 10],1)
   poly([(126,118),(135,107),(144,129),(130,145),(116,132)],p[11])
  elif sid==17:
   # Hollow Grove: mirror pool presents lost Eldoria under the roots.
   for x,h in ((10,66),(51,91),(91,69),(171,88),(211,73),(237,54)):
    poly([(x-10,158),(x-2,153-h),(x+10,153-h),(x+17,157)],p[5])
    for j in range(3):oval((x-23-j*3,135-h-j*5,x+21+j*3,160-h-j*4),p[6 if j%2 else 7])
   poly([(0,141),(18,127),(59,134),(108,125),(168,132),(217,121),(240,145),(240,160),(0,160)],p[9])
   for y in (130,136,144,151,158):line([(0,y),(53,y+1),(131,y-4),(221,y+2),(240,y)],p[10 if y%2 else 8],1)
   # Root shrine, fractured Earth crystal, reflection lines.
   poly([(106,159),(114,117),(109,89),(120,74),(133,88),(128,118),(145,159)],p[5])
   for a in (((118,113),(86,102),(63,80)),((129,113),(154,98),(175,78))):line(a,p[7],4)
   for r,c in ((29,p[3]),(23,p[7]),(17,p[9]),(12,p[11])):oval((122-r,85-r,122+r,85+r),c)
   poly([(123,62),(137,78),(132,102),(121,114),(107,101),(106,81)],p[14]);line([(123,65),(116,106)],p[11],2)
   for x in range(8,237,19):oval((x,149+(x%6),x+3,152+(x%6)),p[9])
  elif sid==18:
   # Celestial Peak stone observatory; Harmony binds distinct worlds.
   for j in range(7):
    x=(j*49+12)%240;y=19+(j*11)%70
    oval((x,y,x+1,y+1),p[11]);line([(x-3,y),(x+4,y)],p[9],1)
   poly([(0,160),(8,124),(39,92),(72,110),(101,72),(121,91),(147,67),(181,96),(211,73),(240,108),(240,160)],p[6])
   for x in (24,53,184,222):
    poly([(x-5,159),(x,103-(x%4)*13),(x+9,159)],p[5]);line([(x,117),(x+4,117)],p[9],1)
   # Two fractured nested brass observatory rings plus center radiant relic.
   for r,c in ((46,p[7]),(39,p[5]),(33,p[13]),(26,p[3])):
    oval((126-r,86-r,126+r,86+r),c,width=3)
   for x1,y1,x2,y2 in ((126,40,126,129),(80,85,172,85),(94,56,158,114),(96,114,157,53)):
    line([(x1,y1),(x2,y2)],p[14],1)
   for r,c in ((18,p[4]),(13,p[9]),(8,p[11])):oval((126-r,86-r,126+r,86+r),c)
   poly([(126,63),(135,85),(126,106),(116,85)],p[15])
   poly([(32,160),(40,134),(49,132),(61,157)],p[1]);oval((41,124,50,135),p[11]);line([(58,140),(84,117)],p[15],2)
  elif sid==19:
   # Nyssa's original Dream Festival—three literal switch lanterns and song.
   for x in range(10,240,32):
    line([(x,14),(x+11,39),(x+26,14)],p[10],1)
    for dx in (0,11,26):
     oval((x+dx-4,12+dx%7,x+dx+5,21+dx%7),p[13 if dx else 10])
   poly([(0,160),(0,117),(29,112),(61,126),(93,118),(137,123),(169,112),(202,121),(240,112),(240,160)],p[5])
   for x,roof,c in ((12,98,p[7]),(62,84,p[8]),(167,81,p[13]),(214,101,p[7])):
    poly([(x,145),(x+3,roof+11),(x+13,roof),(x+22,roof+11),(x+25,145)],p[6])
    line([(x+3,roof+11),(x+13,roof),(x+22,roof+11)],c,2)
    oval((x+8,roof+22,x+18,roof+32),p[10])
   # Three playable switch lanterns arranged central, west and east.
   for x,y,c in ((119,60,p[15]),(50,105,p[9]),(192,106,p[13])):
    line([(x,145),(x,y+8)],p[6],2)
    for r in (15,11,7):oval((x-r,y-r,x+r,y+r),c if r==7 else p[7])
    oval((x-3,y-3,x+3,y+3),p[11])
   for i in range(28):
    x=(i*37+11)%240;y=(i*19+32)%142
    oval((x,y,x+1.4,y+1.4),p[10 if i%2 else 14])
  elif sid==20:
   # OPEN: a constellation of discrete island worlds restores pathways while
   # preserving different architectural silhouettes and palette identities.
   for j,(x,y,rr,c) in enumerate(((34,59,28,9),(100,40,22,13),(188,56,32,10),(137,100,24,14))):
    for r,col in ((rr+11,p[3]),(rr+4,p[7]),(rr,p[c])):oval((x-r,y-r,x+r,y+r),col)
    oval((x-rr+4,y-rr//3,x+rr-4,y+rr//3),p[2])
    for k in range(3):
     xx=x-rr//2+k*rr//2
     poly([(xx,y+rr//2),(xx+3,y-rr//5-k*2),(xx+9,y+rr//2)],p[5])
   for pts,col in (([(34,59),(100,40),(137,100),(188,56)],p[9]),
                   ([(34,59),(137,100),(100,40)],p[14]),
                   ([(100,40),(188,56)],p[10])):
    line(pts,col,2)
   for x,y in ((45,33),(83,97),(216,21),(177,117),(18,102)):
    oval((x-1,y-1,x+1,y+1),p[11]);line([(x-4,y),(x+4,y)],p[10],1)
   # Arin and COSMOS on the bridge between worlds.
   poly([(0,160),(75,130),(108,128),(165,157),(240,160)],p[5])
   poly([(77,149),(79,130),(87,117),(94,119),(101,149)],p[1]);oval((84,110,93,121),p[11])
   line([(100,138),(117,109)],p[15],2);oval((111,113,125,127),p[9]);oval((116,116,121,122),p[11])
  elif sid==21:
   # PRESERVE: a repaired sacred lattice protects towns and diverse lives.
   for x,ht,w in ((10,68,31),(56,95,39),(120,120,32),(169,85,37),(211,71,26)):
    poly([(x,154),(x+5,145-ht),(x+w//2,137-ht),(x+w-6,145-ht),(x+w,155)],p[5])
    poly([(x+5,145-ht),(x+w//2,137-ht),(x+w-6,145-ht)],p[14])
    for yy in range(max(9,150-ht),146,18):line([(x+9,yy),(x+w-9,yy)],p[9],1)
   for r,c in ((58,p[3]),(46,p[4]),(35,p[8]),(28,p[2])):oval((128-r,67-r,128+r,67+r),c)
   # Shards of a once-fractured dome close as a complete golden openwork crown.
   for r in (56,48,40):oval((128-r,65-r,128+r,65+r),p[14] if r!=48 else p[10],width=2)
   for j in range(8):
    theta=j*math.pi/4; xx=128+int(math.cos(theta)*52); yy=65+int(math.sin(theta)*52)
    line([(xx,yy),(128,65)],p[9],1)
   poly([(128,29),(138,54),(131,90),(126,103),(116,82),(119,56)],p[11])
   poly([(0,157),(37,142),(83,151),(124,139),(177,151),(221,140),(240,152),(240,160),(0,160)],p[7])
  elif sid==22:
   # WANDER: hand-authored silhouette of the LUNA-ARC ship crosses an unclaimed sky.
   for r,c in ((40,p[3]),(33,p[12]),(29,p[4]),(22,p[7])):oval((179-r,51-r,179+r,51+r),c)
   for j in range(78):
    x=rng.randrange(240);y=rng.randrange(136)
    if (j%13)==0:
     line([(x-2,y),(x+3,y)],p[11],1);line([(x,y-2),(x,y+3)],p[9],1)
    else:oval((x,y,x+.8,y+.8),p[(9,10,14,15)[j%4]])
   poly([(0,159),(0,117),(23,101),(43,116),(75,108),(110,123),(140,116),(170,135),(208,119),(240,138),(240,160)],p[5])
   # Original LUNA ARC dart: glass bridge, two independently lit engines.
   poly([(61,86),(86,62),(145,53),(174,71),(147,92),(104,100)],p[7])
   poly([(96,74),(119,53),(144,63),(149,75),(116,85)],p[8])
   poly([(61,86),(34,72),(53,95),(74,98),(102,91)],p[6])
   poly([(157,73),(188,64),(173,91),(143,91)],p[6])
   line([(83,67),(139,58),(170,73)],p[10],2)
   for x,y in ((60,86),(168,83)):
    for rr,c in ((16,p[3]),(11,p[13]),(6,p[10])):oval((x-rr,y-rr//2,x+rr,y+rr//2),c)
   line([(82,103),(69,117),(56,123)],p[14],2)
  elif sid==14:
   # The original novel's Heartwood Woods, p.20, Crystal of Balance.
   # 4x-authored pixels convert to genuine 240x160 indexed BG2 cartridge image.
   # Massive luminous Yggdrasil-inspired ORIGINAL sacred tree: roots carry the
   # three dimensional axes into the ground. Distinct from existing Bloom art.
   poly([(0,160),(0,109),(31,94),(62,115),(84,89),(111,113),(145,91),
         (182,107),(216,92),(240,105),(240,160)],p[5])
   for x,top,r in ((15,41,21),(47,50,30),(188,32,25),(227,50,27)):
    line([(x,155),(x-3,top+16)],p[5],4)
    oval((x-r,top-r//3,x+r,top+r),p[6])
    oval((x-r+5,top-r//3-3,x+r-5,top+r-9),p[3])
   # Trunk, roots, split branches, visible green halo.
   for rr,c in ((69,p[3]),(61,p[4]),(54,p[7]),(49,p[2])):
    oval((122-rr,73-rr//2,122+rr,73+rr//2),c)
   poly([(112,140),(118,92),(110,69),(122,53),(134,63),(125,91),(138,133),
         (156,160),(130,151),(119,132),(108,160),(82,160)],p[5])
   for points in (
      [(119,77),(95,62),(75,58),(54,36)],[(119,81),(102,47),(94,31),(79,13)],
      [(125,73),(146,52),(175,45),(195,22)],[(124,89),(145,77),(175,81),(205,68)]):
    line(points,p[6],5);line(points,p[7],2)
   for j in range(24):
    x=(j*43+41)%240;y=(j*29)%97
    oval((x-1,y-2,x+2,y+1),p[9 if j%3 else 14])
   # Crystal of Balance at the convergence of the roots; central gold/cyan.
   for rr,c in ((29,p[4]),(23,p[7]),(17,p[9]),(11,p[11])):
    oval((120-rr,100-rr,120+rr,100+rr),c)
   poly([(120,65),(133,91),(126,116),(119,130),(107,109),(108,92)],p[14])
   poly([(120,68),(121,117),(116,124),(111,107),(110,91)],p[11])
   # Arin and the rescued forest companion in the lower left.
   poly([(33,160),(34,136),(43,125),(51,131),(58,160)],p[1]);oval((39,117,48,130),p[11]);
   line([(52,151),(71,123)],p[15],2)
   poly([(72,159),(74,143),(81,137),(90,141),(98,159)],p[6]);
   oval((77,133,87,145),p[9]);oval((85,134,89,139),p[11])
  elif sid==12:
   # Brindlemark forge: an original lived-in building, not a generic nebula.
   # Hearthlight at left, broken stained-glass LUNA-ARC frame at right.
   poly([(0,160),(0,66),(18,53),(44,47),(69,58),(86,79),(240,76),(240,160)],p[5])
   for x,top in ((24,49),(93,61),(164,56),(219,52)):
    d.rectangle((S(x),S(top),S(x+9),S(159)),fill=p[6]);line([(x-2,top),(x+11,top)],p[7],2)
   poly([(0,145),(240,145),(240,160),(0,160)],p[3]);
   for yy in (146,150,156):line([(0,yy),(240,yy)],p[2],1)
   # molten iron: light from the anvil and broken dimensional crystal.
   poly([(18,148),(27,113),(62,113),(71,148)],p[7]);poly([(28,118),(43,102),(59,118)],p[14]);
   for r,c in ((25,12),(21,9),(17,10),(11,15)):
    oval((173-r,89-r,173+r,89+r),p[c])
   for xx in (151,165,177,192):line([(xx,71),(xx+5,115)],p[8 if xx%2 else 13],1)
   # Arin silhouette repairing a blade, standing by luminous forge.
   poly([(80,156),(83,116),(93,99),(110,110),(114,155)],p[1]);oval((88,91,102,105),p[11]);
   line([(108,127),(138,99)],p[15],3);line([(137,92),(142,106)],p[10],2)
   # COSMOS first signal: one small distinct beacon.
   oval((125,70,146,91),p[9]);oval((132,76,139,83),p[11]);
   for x in range(8,228,21):line([(x,157),(x+9,151)],p[4],1)
  elif sid==13:
   # Siege: distant fractured sky behind the village; no text baked into art.
   poly([(0,160),(0,89),(20,71),(53,86),(91,67),(124,74),(166,61),(195,78),(240,55),(240,160)],p[5])
   for r,col in ((55,p[4]),(43,p[12]),(34,p[13]),(26,p[2]),(15,p[1])):
    oval((142-r,65-r,142+r,65+r),col)
   for j in range(21):
    x=(j*37)%240;y=(j*13)%130
    line([(x,y),(x+7,y+12),(x-1,y+21)],p[9 if j%2 else 14],1)
   # Brindlemark rooftops, watchtower and a battle lane in isometric perspective.
   for x,w,h in ((15,37,34),(61,40,53),(175,35,47),(218,28,33)):
    poly([(x,141),(x,141-h),(x+w//2,131-h-10),(x+w,141-h),(x+w,141)],p[6])
    line([(x,141-h),(x+w//2,131-h-10),(x+w,141-h)],p[14],2)
    for dy in (9,22):line([(x+9,135-h+dy),(x+18,135-h+dy)],p[10],2)
   poly([(61,160),(107,114),(151,114),(199,160)],p[3]);
   for yy in (128,139,152):line([(0,yy+9),(240,yy+5)],p[7],1)
   # Shadow of a raider on raised battlement, bright lance and shield.
   poly([(152,130),(154,92),(159,82),(170,85),(177,132)],p[1]);oval((155,75,169,87),p[2]);
   line([(173,108),(195,68)],p[14],2);oval((139,93,153,112),p[7])
  elif sid==11:
   # Riftfall: the world is ripped into an impossible portal behind Arin.
   # Chromatic concentric rings communicate depth despite true 2D GBA limits.
   cx,cy=144,78
   for radius,c in ((72,5),(63,7),(55,12),(49,13),(42,9),(36,10),(30,3),(24,2)):
    oval((cx-radius,cy-radius,cx+radius,cy+radius),p[c])
   for j in range(36):
    theta=j*math.pi/18;rx=math.cos(theta);ry=math.sin(theta)
    r0=35+(j%4)*4;r1=61+(j%3)*7
    line([(cx+int(rx*r0),cy+int(ry*r0)),(cx+int(rx*r1),cy+int(ry*r1))],p[9 if j%3==0 else (13 if j%3==1 else 15)],1+(j%9==0))
   # Astral fractures converge on the center, a stylized Rift guardian.
   for j in range(11):
    x=18+j*21;y=25+(j*17)%68
    poly([(x,y),(x+6,y-12),(x+12,y-8),(x+9,y+10)],p[3 if j%2 else 7])
    line([(x+3,y-8),(x+7,y+5)],p[10],1)
   # Unsettling silhouette: two horned crests, eyes and long tapering pauldrons.
   poly([(133,111),(136,82),(128,66),(121,54),(134,68),(144,60),(154,67),(169,54),(162,79),(157,112)],p[1])
   oval((137,77,152,88),p[2]);oval((138,78,143,81),p[14]);oval((149,78,154,81),p[10])
   poly([(135,94),(117,87),(103,116),(117,113),(122,138),(164,137),(170,105),(188,116),(172,87),(156,94)],p[2])
   # Foreground tiled corridor converges toward the door in perspective.
   poly([(0,159),(240,159),(161,115),(124,115)],p[5])
   for width in (0,9,19,35,54):
    line([(120-width,159),(143-int(width*.36),117)],p[9 if width%2 else 13],1)
    line([(120+width,159),(143+int(width*.36),117)],p[7],1)
   for y in (129,137,148,158):line([(0,y),(240,y)],p[7 if y%2 else 12],1)
   # Arin and COSMOS at lower left: readable black silhouette + 2px warm signal.
   poly([(57,151),(59,126),(67,115),(75,119),(81,137),(84,159),(51,159)],p[1])
   oval((62,106,73,119),p[11]);poly([(60,118),(76,120),(83,142),(57,144)],p[6])
   line([(80,142),(91,109)],p[15],2);line([(91,109),(89,122)],p[10],1)
   oval((91,114,100,123),p[9]);oval((94,115,97,118),p[11])
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
 assert len(all_tiles)<11000
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
