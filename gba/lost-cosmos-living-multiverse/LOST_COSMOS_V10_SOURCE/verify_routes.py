from collections import deque
W=H=64;FREE,WALL,HAZ=0,1,2

def blank(fill=FREE): return [[fill]*W for _ in range(H)], [[0]*W for _ in range(H)]
def put(c,t,x,y,col=FREE,tr=0):
    if 0<=x<W and 0<=y<H:c[y][x]=col;t[y][x]=tr
def border(c,t):
    for x in range(W):put(c,t,x,0,WALL);put(c,t,x,63,WALL)
    for y in range(H):put(c,t,0,y,WALL);put(c,t,63,y,WALL)
def box(c,t,x0,y0,w,h):
    for x in range(x0,x0+w):put(c,t,x,y0,WALL);put(c,t,x,y0+h-1,WALL)
    for y in range(y0,y0+h):put(c,t,x0,y,WALL);put(c,t,x0+w-1,y,WALL)
def rect(c,t,x0,y0,w,h,col=FREE):
    for y in range(y0,y0+h):
      for x in range(x0,x0+w):put(c,t,x,y,col)
def noise(c,t,seed,count,solid=1):
    for i in range(count):
      x=2+((seed+i*17+i*i*3)%60);y=2+((seed*3+i*29+i*i)%60)
      if c[y][x]==FREE and t[y][x]==0:put(c,t,x,y,WALL if solid else FREE)
def overlay(c,t,w,l):
    if l==0:
      for y in range(2,62):
       for x in range(2,62):
        if ((x*11+y*7+w*13)&31)==0 and c[y][x]==FREE and t[y][x]==0:put(c,t,x,y,WALL)
    elif l==2:
      for y in range(3,61):
       for x in range(3,61):
        if ((x*3+y*11+w*17)&31)==1 and c[y][x]==FREE and t[y][x]==0:put(c,t,x,y,WALL)
def gen(w,l=1):
 c,t=blank()
 if w==0:
  border(c,t)
  for y in range(3,61):put(c,t,31,y,WALL)
  for y in range(28,35):put(c,t,31,y,FREE)
  rect(c,t,8,46,9,7);put(c,t,12,49,FREE,1);box(c,t,19,16,16,13);put(c,t,26,28,FREE,2);rect(c,t,22,19,10,5,WALL);put(c,t,27,22,FREE,8);box(c,t,47,5,12,10);put(c,t,52,14,FREE,9);noise(c,t,7,90)
  for x in range(10,31):put(c,t,x,51)
  for y in range(28,52):put(c,t,26,y,FREE,2 if y==28 else 0)
  for y in range(0,64,8):put(c,t,30,y,WALL)
  for y in range(28,35):put(c,t,30,y);put(c,t,31,y)
 elif w==1:
  border(c,t)
  for y in range(8,58,12):
   for x in range(2,62):
    if (x<16 or x>22) and (x<42 or x>48):put(c,t,x,y,HAZ)
  for x in range(5,60):put(c,t,x,34)
  rect(c,t,5,48,9,7);put(c,t,9,51,FREE,1);box(c,t,42,38,17,18);put(c,t,49,55,FREE,2);put(c,t,20,20,FREE,7);noise(c,t,17,38)
  for x in range(9,50):put(c,t,x,51,FREE,1 if x==9 else 0)
  for y in range(20,52):put(c,t,20,y,FREE,7 if y==20 else 0)
 elif w==2:
  c,t=blank(WALL)
  for y in range(2,62):
   for x in range(2,62):
    if ((x*5+y*3+11)&15)<6:put(c,t,x,y)
  border(c,t)
  for x in range(5,58):put(c,t,x,31)
  rect(c,t,6,49,9,7);put(c,t,10,52,FREE,1);box(c,t,41,9,16,15);put(c,t,48,23,FREE,2);put(c,t,22,45,FREE,7);noise(c,t,23,25,0)
  for x in range(10,49):put(c,t,x,52,FREE,1 if x==10 else 0)
  for y in range(23,53):put(c,t,48,y,FREE,2 if y==23 else 0)
  for y in range(45,53):put(c,t,22,y,FREE,7 if y==45 else 0)
  put(c,t,22,45,FREE,7)
 elif w==3:
  border(c,t)
  for x in range(2,62,7):
   for y in range(3,60,9):put(c,t,x,y,WALL)
  rect(c,t,6,48,9,7);put(c,t,10,51,FREE,1);put(c,t,31,31,FREE,7);box(c,t,44,8,14,12);put(c,t,50,19,FREE,2);noise(c,t,31,70)
  for x in range(10,51):put(c,t,x,51,FREE,1 if x==10 else 0)
  for y in range(19,52):put(c,t,31,y,FREE,7 if y==31 else 0)
  put(c,t,50,19,FREE,2)
 elif w==4:
  border(c,t)
  for y in range(3,61):
   for x in range(3,61):
    if ((x*13+y*7+x*y)&31)<5:put(c,t,x,y,HAZ)
  for x in range(6,56):put(c,t,x,32)
  rect(c,t,7,49,9,7);put(c,t,11,52,FREE,1);box(c,t,43,8,15,15);put(c,t,50,22,FREE,2);put(c,t,24,14,FREE,9)
 elif w==5:
  border(c,t)
  for x in range(8,57,16):
   for y in range(5,58):
    if y not in (15,31,47):put(c,t,x,y,WALL)
  for y in range(16,49,16):
   for x in range(3,61):
    if x not in (16,32,48):put(c,t,x,y,WALL)
  rect(c,t,4,51,9,7);put(c,t,8,54,FREE,1);put(c,t,55,8,FREE,10);put(c,t,16,15,FREE,8);put(c,t,32,31,FREE,8);put(c,t,48,47,FREE,8)
 overlay(c,t,w,l)
 if w==1 and l==0:
  for x in range(20,54):put(c,t,x,20)
  for y in range(10,21):put(c,t,53,y)
  put(c,t,53,10,FREE,4)
 if w==2 and l==0:
  for x in range(22,51):put(c,t,x,45)
  for y in range(12,46):put(c,t,50,y)
  put(c,t,50,12,FREE,5)
 if w==3 and l==2:
  for x in range(31,53):put(c,t,x,31)
  for y in range(11,32):put(c,t,52,y)
  put(c,t,52,11,FREE,6)
 return c,t

def reach(c,a,b):
 q=deque([a]);seen={a}
 while q:
  p=q.popleft()
  if p==b:return True
  x,y=p
  for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
   n=(x+dx,y+dy)
   if 0<=n[0]<64 and 0<=n[1]<64 and c[n[1]][n[0]]!=WALL and n not in seen:seen.add(n);q.append(n)
 return False
checks=[('origin ship',0,1,(10,51),(12,49)),('origin ruin',0,1,(10,51),(26,28)),('ember lift',1,1,(10,51),(20,20)),('ember X',1,0,(20,20),(53,10)),('tide lift',2,1,(10,52),(22,45)),('tide Y',2,0,(22,45),(50,12)),('bloom lift',3,1,(10,51),(31,31)),('bloom Z',3,2,(31,31),(52,11)),('black structure',4,1,(10,52),(50,22)),('crown core',5,1,(10,54),(55,8))]
for name,w,l,a,b in checks:
 c,_=gen(w,l)
 if not reach(c,a,b):raise SystemExit('FAIL route: '+name)
 print('PASS route:',name)

trigger_checks=[
 ("origin door",0,1,(26,28),2),("origin ship trigger",0,1,(12,49),1),
 ("ember ship trigger",1,1,(9,51),1),("ember lift trigger",1,1,(20,20),7),("ember X trigger",1,0,(53,10),4),
 ("tide ship trigger",2,1,(10,52),1),("tide lift trigger",2,1,(22,45),7),("tide Y trigger",2,0,(50,12),5),
 ("bloom ship trigger",3,1,(10,51),1),("bloom lift trigger",3,1,(31,31),7),("bloom Z trigger",3,2,(52,11),6),
 ("black secret trigger",4,1,(24,14),9),("crown core trigger",5,1,(55,8),10),
]
for name,w,l,(x,y),expected in trigger_checks:
 c,t=gen(w,l)
 if t[y][x]!=expected: raise SystemExit(f"FAIL trigger: {name} got {t[y][x]} expected {expected}")
 print('PASS trigger:',name)

# RPG elite encounters must occupy traversable positions in their key layers.
for world,layer,start,guardian in [(1,0,(20,20),(49,12)),(2,0,(22,45),(49,12)),(3,2,(31,31),(48,14))]:
 c,t=gen(world,layer)
 if c[guardian[1]][guardian[0]]!=FREE or not reach(c,start,guardian):
  raise SystemExit(f"FAIL elite guardian accessibility: world {world} at {guardian}")
 print(f"PASS elite guardian accessible: world {world}")
