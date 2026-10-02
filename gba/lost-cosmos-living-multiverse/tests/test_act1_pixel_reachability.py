"""Exact-source native-MMIO regression: NPC reachability with the *real 10px actor footprint*.
Tile-only BFS misses inaccessible 8px doors. This is NOT emulator footage.
"""
from pathlib import Path
import collections
import subprocess

ROOT = Path(__file__).resolve().parents[1]
GAME = ROOT / "LOST_COSMOS_V10_SOURCE"
subprocess.run(["python3", "host_qa_v5.py"], cwd=GAME, check=True,
               capture_output=True, timeout=70)
prelude = (GAME / "host_qa_v5.c").read_text().split("\n#ifdef HOST_QA\nint main(", 1)[0]
dump = prelude + r"""
#include <stdio.h>
int main(void){
 init_new_game();init_graphics();intro=0;game_mode=MODE_SURFACE;
 for(int r=2;r<=4;r++){
  current_world=0;current_room=r;current_layer=1;player.x=88;player.y=416;
  generate_surface();
  printf("ROOM %d %d\n",r,npc_count);
  for(int i=0;i<npc_count;i++)
   printf("NPC %d %d %d\n",npc_runtime[i].id,npc_runtime[i].x,npc_runtime[i].y);
  printf("COLLISION ");
  for(int i=0;i<4096;i++)printf("%c",'0'+collision[i]);
  printf("\n");
 }
 return 0;
}
"""
source = GAME / "act1_pixel_geometry_host.c"
source.write_text(dump)
exe = GAME / "act1_pixel_geometry_host"
subprocess.run(["clang", "-O2", "-DHOST_QA", "-DQA_AUTORUN",
                "-Wno-unused-function", source.name, "-o", exe.name],
               cwd=GAME, check=True, timeout=50)
lines = subprocess.run([str(exe)], cwd=GAME, check=True,
                       text=True, capture_output=True, timeout=15).stdout.splitlines()
rooms, room = {}, None
for line in lines:
    if line.startswith("ROOM "):
        room = int(line.split()[1])
        rooms[room] = {"npcs": {}}
    elif line.startswith("NPC "):
        _, identity, x, y = line.split()
        rooms[room]["npcs"][int(identity)] = (int(x), int(y))
    elif line.startswith("COLLISION "):
        rooms[room]["board"] = bytes(int(c) for c in line.split()[1])
        assert len(rooms[room]["board"]) == 4096

def stand(board, x, y):
    return 8 <= x <= 503 and 8 <= y <= 503 and all(
        board[(yy >> 3) * 64 + (xx >> 3)] != 1
        for xx, yy in ((x-5,y-5),(x+5,y-5),(x-5,y+5),(x+5,y+5))
    )

def reachable(board, start):
    queue = collections.deque([start])
    seen = {start}
    while queue:
        x, y = queue.popleft()
        for point in ((x+2,y),(x-2,y),(x,y+2),(x,y-2)):
            if point not in seen and stand(board, *point):
                seen.add(point)
                queue.append(point)
    return seen

for room, identity, start in ((2,14,(88,416)),(3,16,(88,416)),(4,17,(248,416))):
    record = rooms[room]
    npc = record["npcs"][identity]
    seen = reachable(record["board"], start)
    others = [p for i,p in record["npcs"].items() if i != identity]
    goals = [p for p in seen
             if abs(p[0]-npc[0])+abs(p[1]-npc[1]) < 30
             and all(abs(p[0]-npc[0])+abs(p[1]-npc[1]) <=
                     abs(p[0]-o[0])+abs(p[1]-o[1]) for o in others)]
    print(f"ROOM {room}: NPC {identity} at {npc}, genuine 10px-footprint interaction positions={len(goals)}")
    assert goals, f"ACT I softlock: NPC {identity} is unreachable from {start} in room {room}"
print("PASS native C/real actor-footprint: Brindlemark, Ravenswood Oakwood, Cragstone")
