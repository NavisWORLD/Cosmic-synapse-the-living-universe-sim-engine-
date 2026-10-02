"""Assert-locked one-time original, reproducible GBA pixel-art Heartwood ending illustration."""
from pathlib import Path
root=Path(__file__).resolve().parent
p=root/'cinematic_assets_v51.py';s=p.read_text()
a="'brindlemark_forge','brindlemark_siege')"
b="'brindlemark_forge','brindlemark_siege','heartwood_heart')"
assert s.count(a)==1;s=s.replace(a,b)
a=" [(0,0,0),(8,9,22),(22,19,48),(54,28,63),(88,31,75),(24,30,55),(58,54,84),(115,56,93),(161,93,112),(53,134,188),(111,214,230),(239,229,216),(96,36,141),(184,63,161),(247,112,119),(255,204,133)],\n]"
b=""" [(0,0,0),(8,9,22),(22,19,48),(54,28,63),(88,31,75),(24,30,55),(58,54,84),(115,56,93),(161,93,112),(53,134,188),(111,214,230),(239,229,216),(96,36,141),(184,63,161),(247,112,119),(255,204,133)],
 # Original Heartwood: midnight evergreen, green lightning, sacred golden heart.
 [(0,0,0),(5,19,26),(13,39,36),(22,69,57),(42,103,70),(14,48,42),(29,83,51),(56,126,76),(125,158,77),(42,187,125),(133,232,162),(244,240,200),(88,85,64),(173,139,65),(231,195,88),(255,240,146)],
]"""
assert s.count(a)==1;s=s.replace(a,b)
a='  elif sid==12:\n   # Brindlemark forge:'
b='''  elif sid==14:
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
   # Brindlemark forge:'''
assert s.count(a)==1;s=s.replace(a,b)
p.write_text(s)

p=root/'lost_cosmos_v5.c';s=p.read_text()
a='''  say(v10_hw_choice==2?"BALANCE RESTORED WITHOUT BLOOD. COSMOS REMEMBERS THE SPIRIT.":"BALANCE RESTORED. YOUR CHOICE WILL REMAIN IN THIS WOOD.");'''
b='''#ifndef QA_AUTORUN
  cinema_start(14,145); /* Original authored Heartwood crystal restoration. */
#endif
  say(v10_hw_choice==2?"BALANCE RESTORED WITHOUT BLOOD. COSMOS REMEMBERS THE SPIRIT.":"BALANCE RESTORED. YOUR CHOICE WILL REMAIN IN THIS WOOD.");'''
assert s.count(a)==1;s=s.replace(a,b)
p.write_text(s)

p=root/'v10_presentation_tests.py';s=p.read_text()
assert s.count('assert(V51_SCENE_COUNT==14);')==1
s=s.replace('assert(V51_SCENE_COUNT==14);','assert(V51_SCENE_COUNT==15);')
assert s.count('assert(V51_SCENE_COUNTS[12]>100&&V51_SCENE_COUNTS[13]>100);')==1
s=s.replace('assert(V51_SCENE_COUNTS[12]>100&&V51_SCENE_COUNTS[13]>100);','assert(V51_SCENE_COUNTS[12]>100&&V51_SCENE_COUNTS[13]>100&&V51_SCENE_COUNTS[14]>100);')
p.write_text(s)
print('Added original index-14 real 4bpp Heartwood novel scene and real gameplay trigger; updated QA')
