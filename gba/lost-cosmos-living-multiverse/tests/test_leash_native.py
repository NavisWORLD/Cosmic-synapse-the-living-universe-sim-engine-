#!/usr/bin/env python3
"""LEASH OFF native gate (host build of the real game code, not footage).

For every location the world sweep enters, the room is generated with the real
generate_surface(), Arin stands at the sweep's arrival point and the field
beast runs the real buddy_tick() -> leash_tick() and buddy_combat_assist() for
3600 frames (60 s) with the leash off. Then CALL BEAST is used and the beast
must come back within 600 frames. Checked every frame:
  * the beast's tile is never a wall or hazard,
  * Arin's position never changes (the beast cannot push or block him),
  * story/quest/inventory state never changes (the beast sets no flags),
  * no enemy is damaged by the beast while it is more than 72px from Arin.
Also: LCL1 save -> restore is byte-exact, an older save (no LCL1) gets an
empty record with LEASH OFF, and LEASH ON restores the original follower.
Writes artifacts/leash_native/leash_native.json.
"""
from pathlib import Path
import json, subprocess, sys
R=Path(__file__).resolve().parents[1]
G=R/"LOST_COSMOS_V10_SOURCE"
OUT=R/"artifacts/leash_native";OUT.mkdir(parents=True,exist_ok=True)
sweep=R/"artifacts/world_sweep/world_sweep.json"
if not sweep.exists():subprocess.run([sys.executable,str(R/"tests/test_world_sweep.py")],check=True)
subprocess.run(["python3","host_qa_v5.py"],cwd=G,check=True,capture_output=True,timeout=300)
pre=(G/"host_qa_v5.c").read_text().split("\n#ifdef HOST_QA\nint main(",1)[0]
base=(R/"tests/test_world_sweep.py").read_text()
bs=base[base.index("static int open_mode=0"):base.index("static void transient(void)")]
C=pre+r'''
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
'''+bs+r'''
static void transient(void){game_mode=MODE_SURFACE;pro_ui=0;cinema_active=0;dialogue_timer=0;npc_dialogue_active=0;a1_boss=0;shop_open=0;
 v11_wild=0;v11_shop=0;v11_lore=0;v11_dialogue=0;v11_gameover=0;}
typedef struct{u16 sf;u8 keys,elem,cq[CQ_COUNT],inv[ITEM_COUNT],credits,qs,qc;u16 relic,a1,xp;u32 comp;u8 arc;}Snap;
static void snap(Snap*s){memset(s,0,sizeof(*s));s->sf=story_flags;s->keys=keys_found;s->elem=element_mask;memcpy(s->cq,cq_state,CQ_COUNT);memcpy(s->inv,inv,ITEM_COUNT);
 s->credits=credits;s->qs=quest_started;s->qc=quest_completed;s->relic=v10_relic;s->a1=a1_flags;s->xp=player_xp;s->comp=completion_done;s->arc=arc_progress;}
static int bad_tile(void){int t=((cosmos.y>>3)<<6)|((cosmos.x>>3)&63);if(cosmos.x<0||cosmos.y<0||cosmos.x>511||cosmos.y>511)return 1;return collision[t]!=C_FREE;}
int main(int argc,char**argv){int w,r,l,x,y,first=1;
 open_mode=argc>1;if(argc>3){seed_f=argv[2][0];seed_k=atoi(argv[3]);}
 printf("[");
 while(scanf("%d %d %d %d %d",&w,&r,&l,&x,&y)==5){
  base_state();transient();current_world=(u8)w;current_room=(u8)r;current_layer=(u8)l;player.x=(s16)x;player.y=(s16)y;generate_surface();transient();
  player.x=(s16)x;player.y=(s16)y;cosmos.x=(s16)(x+14);cosmos.y=(s16)(y-10);leash_on=0;lf_loc=255;
  Snap a,b;snap(&a);int wall=0,moved_player=0,far_hits=0,maxd=0,tiles=0,i,hp0[10];static u8 seen[4096];memset(seen,0,4096);
  u32 ok0=lf_rec.moves_ok,bl0=lf_rec.moves_blocked;u16 c0=lf_rec.cells,p0=lf_rec.pois,n0=lf_rec.npcs,e0=lf_rec.encounters,np0=lf_rec.no_path;
  for(int f=0;f<3600;f++){frame++;for(i=0;i<10;i++)hp0[i]=enemies[i].active?enemies[i].hp:-1;
   buddy_tick();buddy_combat_assist();
   for(i=0;i<10;i++){int h=enemies[i].active?enemies[i].hp:-1;if(h!=hp0[i]&&iabs(cosmos.x-player.x)+iabs(cosmos.y-player.y)>72)far_hits++;}
   if(bad_tile())wall++;if(player.x!=x||player.y!=y)moved_player++;
   int d=iabs(cosmos.x-player.x)+iabs(cosmos.y-player.y);if(d>maxd)maxd=d;
   int t=((cosmos.y>>3)<<6)|((cosmos.x>>3)&63);if(t>=0&&t<4096&&!seen[t]){seen[t]=1;tiles++;}}
  u16 calls0=lf_rec.calls,ret0=lf_rec.returns,cu0=lf_rec.catchups;leash_call();int back=-1;
  for(int f=0;f<600;f++){frame++;buddy_tick();if(bad_tile())wall++;if(iabs(cosmos.x-player.x)+iabs(cosmos.y-player.y)<=20&&!lf_called){back=f;break;}}
  snap(&b);
  printf("%s{\"loc\":[%d,%d,%d],\"wall_frames\":%d,\"player_moved\":%d,\"state_changed\":%d,\"far_hits\":%d,\"max_dist\":%d,\"tiles\":%d,"
   "\"steps\":%u,\"blocked\":%u,\"cells\":%d,\"pois\":%d,\"npcs\":%d,\"encounters\":%d,\"no_path\":%d,\"call_frames\":%d,\"catchup\":%d,\"returned\":%d,\"calls\":%d}",
   first?"":",\n",w,r,l,wall,moved_player,memcmp(&a,&b,sizeof(a))!=0,far_hits,maxd,tiles,(unsigned)(lf_rec.moves_ok-ok0),(unsigned)(lf_rec.moves_blocked-bl0),
   lf_rec.cells-c0,lf_rec.pois-p0,lf_rec.npcs-n0,lf_rec.encounters-e0,lf_rec.no_path-np0,back,lf_rec.catchups-cu0,lf_rec.returns-ret0,lf_rec.calls-calls0);first=0;fflush(stdout);
 }
 printf("]\n");
 if(argc>1&&!strcmp(argv[1],"save")){} return 0;}
'''
src=G/"leash_native_host.c";src.write_text(C)
exe=Path("/tmp/leash_native_host")
subprocess.run(["clang","-DQA_AUTORUN","-DHOST_QA","-O2","-w",str(src),"-o",str(exe)],check=True)
# Save/restore/migration checks in a second tiny program.
C2=pre+r'''
#include <stdio.h>
#include <string.h>
int main(void){u8 before[sizeof(lf_rec)],after[sizeof(lf_rec)];int ok=1,i;
 init_new_game();
 lf_rec.moves_ok=123456;lf_rec.moves_blocked=7;lf_rec.cells=99;lf_rec.pois=5;lf_rec.secs=300;lf_rec.done[LFG_POI]=5;
 lf_rec.fav_loc[0]=3;lf_rec.fav_cell[0]=21;lf_rec.fav_n[0]=9;lf_rec.slot_loc[0]=3;lf_rec.slot_mask[0][2]=0x5A;leash_on=1;
 memcpy(before,&lf_rec,sizeof(lf_rec));leash_save();leash_reset();leash_restore();memcpy(after,&lf_rec,sizeof(lf_rec));
 int roundtrip=!memcmp(before,after,sizeof(lf_rec))&&leash_on==1;
 /* corrupt one byte: the CRC must reject it and start an empty record */
 SRAM[LF_SRAM+20]^=1;leash_restore();int crc_reject=lf_rec.cells==0&&lf_rec.flags==2&&leash_on==0;
 /* an older save: no LCL1 block */
 for(i=0;i<LF_BYTES;i++)SRAM[LF_SRAM+i]=0;leash_restore();int migrate=lf_rec.cells==0&&lf_rec.flags==2&&leash_on==0&&lf_rec.slot_loc[5]==255;
 /* LEASH ON uses the original follower: after 400 frames the beast is beside Arin */
 base_state();current_world=0;current_room=2;current_layer=1;generate_surface();game_mode=MODE_SURFACE;player.x=31*8;player.y=50*8;cosmos.x=player.x+200;cosmos.y=player.y;leash_on=0;
 leash_toggle();int snapped=iabs(cosmos.x-player.x)+iabs(cosmos.y-player.y)<=24&&leash_on==1;u32 m0=lf_rec.moves_ok;u16 s0=lf_rec.secs;
 for(i=0;i<400;i++){frame++;buddy_tick();}
 /* LEASH ON runs the untouched V11.7 buddy code: no LCL1 counter moves, the beast stays in its old radius */
 int follow=snapped&&lf_rec.moves_ok==m0&&lf_rec.secs==s0&&iabs(cosmos.x-player.x)+iabs(cosmos.y-player.y)<260;
 printf("{\"roundtrip\":%d,\"crc_reject\":%d,\"migrate\":%d,\"leash_on_follows\":%d,\"record_bytes\":%d,\"sram_at\":%d}\n",roundtrip,crc_reject,migrate,follow,LF_BYTES,LF_SRAM);
 return !(roundtrip&&crc_reject&&migrate&&follow);}
'''
C2=C2.replace("int main(void)",base[base.index("static int open_mode=0"):base.index("static void transient(void)")]+"int main(void)")
src2=G/"leash_save_host.c";src2.write_text(C2)
exe2=Path("/tmp/leash_save_host")
subprocess.run(["clang","-DQA_AUTORUN","-DHOST_QA","-O2","-w",str(src2),"-o",str(exe2)],check=True)
p=subprocess.run([str(exe2)],capture_output=True,text=True,timeout=120)
save_check=json.loads(p.stdout)
data=json.loads(sweep.read_text())
groups={}
seen=set()
for mode,rooms in data.items():
 for rm in rooms:
  k=tuple(rm["loc"])
  if k in seen or not rm["standable"]:continue
  seen.add(k);groups.setdefault(mode,[]).append(rm)
def args_for(mode):
 if mode=="fresh":return []
 if mode=="open":return ["open"]
 for pre_,f in (("arc","a"),("g7_","g"),("comp","c"),("v11_","v")):
  if mode.startswith(pre_):return ["open",f,mode[len(pre_):]]
 raise SystemExit("unknown sweep mode "+mode)
rooms=[]
for mode,rms in groups.items():
 inp="".join(f'{r["loc"][0]} {r["loc"][1]} {r["loc"][2]} {r["arrive"][0]} {r["arrive"][1]}\n' for r in rms)
 p=subprocess.run([str(exe)]+args_for(mode),input=inp,capture_output=True,text=True,timeout=1200)
 if p.returncode:print(p.stderr[-2000:]);raise SystemExit(f"leash host crashed in {mode}")
 for r in json.loads(p.stdout):r["mode"]=mode;rooms.append(r)
fail=[]
for r in rooms:
 for k in ("wall_frames","player_moved","state_changed","far_hits"):
  if r[k]:fail.append((r["loc"],k,r[k]))
 if r["loc"]==[0,90,1]:r["beast_home"]="own Beast Home behaviour; the leash does not apply";continue
 if r["call_frames"]<0:fail.append((r["loc"],"did not come back on call",r))
roam=[r for r in rooms if r["max_dist"]>48]
summary={"locations":len(rooms),"save":save_check,"failures":fail,
 "roamed_more_than_48px":len(roam),"total_tiles":sum(r["tiles"] for r in rooms),"total_steps":sum(r["steps"] for r in rooms),
 "total_blocked":sum(r["blocked"] for r in rooms),"total_pois":sum(r["pois"] for r in rooms),"total_npcs":sum(r["npcs"] for r in rooms),
 "total_encounters":sum(r["encounters"] for r in rooms),"total_no_path":sum(r["no_path"] for r in rooms),
 "catchups":sum(r["catchup"] for r in rooms),"call_frames_max":max(r["call_frames"] for r in rooms),
 "call_frames_mean":round(sum(max(0,r["call_frames"]) for r in rooms)/max(1,len(rooms)),1)}
(OUT/"leash_native.json").write_text(json.dumps({"summary":summary,"rooms":rooms},indent=1))
print(json.dumps(summary,indent=1))
if fail or not all(save_check[k] for k in ("roundtrip","crc_reject","migrate","leash_on_follows")):raise SystemExit("LEASH native gate failed")
if len(roam)*10<len(rooms)*8:raise SystemExit(f"beast roamed beyond 48px in only {len(roam)}/{len(rooms)} locations")
print("PASS leash native:",len(rooms),"locations")
