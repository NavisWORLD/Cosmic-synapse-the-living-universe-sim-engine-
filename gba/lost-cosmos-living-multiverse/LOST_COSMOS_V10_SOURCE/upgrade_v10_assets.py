from pathlib import Path
p=Path(__file__).with_name('cinematic_assets_v51.py')
s=p.read_text()
a="'malakar','riftfall')"
b="'malakar','riftfall','brindlemark_forge','brindlemark_siege')"
assert s.count(a)==1;s=s.replace(a,b)
needle=' # Paint at 4x: high-res paintings are the production assets, indexed images actual GBA inputs.'
# add palettes by insert before closing list just above Paint comment
before='[(0,0,0),(6,7,24),(19,11,45),(33,18,72),(56,27,99),(17,28,58),(40,52,96),(76,58,132),(103,96,181),(32,175,195),(89,238,214),(235,248,231),(113,37,143),(200,62,190),(251,143,204),(255,220,133)],\n]'
after='''[(0,0,0),(6,7,24),(19,11,45),(33,18,72),(56,27,99),(17,28,58),(40,52,96),(76,58,132),(103,96,181),(32,175,195),(89,238,214),(235,248,231),(113,37,143),(200,62,190),(251,143,204),(255,220,133)],
 # New authored frames: warm forge vs. siege. Original palette assets, 4bpp conversion.
 [(0,0,0),(13,10,25),(37,19,36),(69,37,40),(103,55,42),(47,35,40),(90,61,50),(147,98,52),(215,155,73),(52,147,169),(105,208,214),(249,230,192),(96,59,105),(174,107,82),(250,181,75),(255,241,182)],
 [(0,0,0),(8,9,22),(22,19,48),(54,28,63),(88,31,75),(24,30,55),(58,54,84),(115,56,93),(161,93,112),(53,134,188),(111,214,230),(239,229,216),(96,36,141),(184,63,161),(247,112,119),(255,204,133)],
]'''
assert s.count(before)==1;s=s.replace(before,after)
old='''  elif sid==11:
   # Riftfall: the world is ripped into an impossible portal behind Arin.'''
new='''  elif sid==12:
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
   # Riftfall: the world is ripped into an impossible portal behind Arin.'''
assert s.count(old)==1;s=s.replace(old,new)
p.write_text(s)
print('v10 14-scene pixel-art generator patched')
