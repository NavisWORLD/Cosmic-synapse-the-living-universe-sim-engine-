#!/usr/bin/env python3
"""World/warp sweep over every generated map (host source QA, not footage).

For each location the game can put the player in, it builds the real map with
generate_surface(), flood-fills the 10px actor from each arrival point with the
same 2px step geometry the pad uses, and then uses every reachable warp-type
trigger through the real interact()/v11_field_interact()/shift_layer() code.
It records where each warp lands, whether the arrival pixel is standable
(no fake destination), whether the destination has a way back out, and which
warps refuse (with the game's own message). Passes: a fresh campaign just
after the prologue, an all-open state, and progression seeds (ARC chapter k
just restored, G7 thread k unlocked, completion scene k unlocked, V11 beacon k)
that start in the room where that gate has just opened. Locations never reached
in any pass fail the gate as not enterable. Writes artifacts/world_sweep/.
"""
from pathlib import Path
import json, subprocess, sys
R=Path(__file__).resolve().parents[1]
G=R/"LOST_COSMOS_V10_SOURCE"
OUT=R/"artifacts/world_sweep";OUT.mkdir(parents=True,exist_ok=True)
subprocess.run(["python3","host_qa_v5.py"],cwd=G,check=True,capture_output=True,timeout=120)
pre=(G/"host_qa_v5.c").read_text().split("\n#ifdef HOST_QA\nint main(",1)[0]
C=pre+r'''
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#define QCAP 65536
static unsigned char seen[QCAP];static unsigned q[QCAP];
static int stand(int x,int y){if(x<8||y<8||x>503||y>503)return 0;
 return tile_collision_at(x-5,y-5)!=C_WALL&&tile_collision_at(x+5,y-5)!=C_WALL&&tile_collision_at(x-5,y+5)!=C_WALL&&tile_collision_at(x+5,y+5)!=C_WALL;}
typedef struct{u8 w,r,l;s16 x,y;}Arr;
#define NLOC (8*128*3)
static u8 visited[NLOC];static Arr qa_q[4096];static int qh=0,qt=0;static u8 arrivals[NLOC];
static int lid(int w,int r,int l){return (w*128+r)*3+l;}
static int is_warp(int t){return t==TR_SHIP||t==TR_DOOR||t==TR_EXIT||t==TR_LIFT||t==TR_GATE||t==TR_RIFT||t==TR_ARC_ENTER||t==TR_ARC_NEXT||t==TR_ARC_EXIT||t==TR_ARC_EPILOGUE||
 t==TR_G6_PORTAL||t==TR_G6_EXIT||t==TR_G7_PORTAL||t==TR_G7_EXIT||t==TR_G7_NEXT||t==TR_COMP_ENTER||t==TR_COMP_EXIT||t==TR_COMP_NEXT||t==TR_V11_ENTER||t==TR_V11_EXIT||t==TR_V11_NEXT||
 t==TR_BH_ENTER||t==TR_BH_EXIT||(t>=TR_A1_TO_ASCENT&&t<=TR_A1_TO_TEMPLE)||(t>=TR_A1_TO_ASCENT_TOP&&t<=TR_A1_TO_HALL)||t==TR_A1_VAULT_DOOR;}
static int open_mode=0,seed_k=-1;static char seed_f=0;
static void base_state(void){
 init_new_game();init_graphics();intro=0;
 for(int i=0;i<5;i++)cq_set(i,CQ_DONE);cq_set(5,CQ_ACTIVE);pro_flags|=0x1FFF;
 if(open_mode){story_flags=0xFFFF;keys_found=7;v10_relic=0xFFFF;element_mask=15;
  for(int i=5;i<=9;i++)cq_set(i,CQ_DONE);cq_set(10,CQ_ACTIVE);a1_flags=0x7FFF;a1_regent=2;a1_sentries=7;
  arc_progress=ARC_STAGES;completion_done=0xFFFFFFu;v11_beacons=0xFF;
  postgame=1;ending=1;arc_petals=3;arc_route=1;g7_pillars=3;g7_orbs=31;g6_done=0xF;g7_done=0xFFF;
  if(seed_f=='a'){arc_progress=(u8)seed_k;}
  if(seed_f=='g'){g7_done=(u16)((1u<<seed_k)-1u);}
  if(seed_f=='c'){completion_done=(1u<<seed_k)-1u;}
  if(seed_f=='v'){v11_beacons=(u8)((1u<<seed_k)-1u);}
  v11_visited=0xFF;
  if(!lc_party.count){lc_party.count=1;lc_party.active=0;lc_party.slots[0].species=1;lc_party.slots[0].stage=1;lc_party.slots[0].level=5;lc_party.slots[0].identity=0x1234u;}}
}
static void transient(void){game_mode=MODE_SURFACE;pro_ui=0;cinema_active=0;dialogue_timer=0;npc_dialogue_active=0;a1_boss=0;shop_open=0;
 v11_wild=0;v11_shop=0;v11_lore=0;v11_dialogue=0;v11_gameover=0;}
static void load(Arr a){transient();current_world=a.w;current_room=a.r;current_layer=a.l;player.x=a.x;player.y=a.y;generate_surface();transient();player.x=a.x;player.y=a.y;}
static void push(Arr a,const char*via){int k=lid(a.w,a.r,a.l);
 int ok=0;{Arr save={current_world,current_room,current_layer,player.x,player.y};(void)save;}
 if(arrivals[k]>=3)return;
 if(!visited[k])visited[k]=1;arrivals[k]++;qa_q[qt++&4095]=a;(void)via;(void)ok;}
typedef struct{u8 t,tx,ty;s16 px,py;}Trig;static Trig tl[256];static int tn;
static int explore(int x,int y){memset(seen,0,sizeof(seen));tn=0;unsigned h=0,t=0;int k=(y/2)*256+x/2;seen[k]=1;q[t++]=k;
 while(h<t){k=q[h++];x=(k&255)*2;y=(k>>8)*2;player.x=(s16)x;player.y=(s16)y;u8 tr=trigger_near();
  if(tr&&is_warp(tr)){int dup=0;for(int i=0;i<tn;i++)if(tl[i].t==tr&&tl[i].tx==near_trigger_x&&tl[i].ty==near_trigger_y)dup=1;
   if(!dup&&tn<256){tl[tn].t=tr;tl[tn].tx=near_trigger_x;tl[tn].ty=near_trigger_y;tl[tn].px=x;tl[tn].py=y;tn++;}}
  int dx[4]={2,-2,0,0},dy[4]={0,0,2,-2};
  for(int d=0;d<4;d++){int nx=x+dx[d],ny=y+dy[d];if(!stand(nx,ny))continue;int v=(ny/2)*256+nx/2;if(!seen[v]){seen[v]=1;q[t++]=v;}}}
 return t;}
static void flush(void){int n=0;while(pro_ui==4&&n++<30)prologue_update(KEY_A);cinema_active=0;}
static void esc(const char*s){putchar('"');for(;*s;s++){if(*s=='"'||*s=='\\')putchar('\\');putchar(*s);}putchar('"');}
int main(int argc,char**argv){
 open_mode=argc>1;if(argc>3){seed_f=argv[2][0];seed_k=atoi(argv[3]);}base_state();
 /* chapter-just-finished starts: the player is standing in the room whose gate just opened */
 if(seed_f=='a'&&seed_k>=1){Arr a={0,(u8)(ARC_FIRST_ROOM+seed_k-1),1,31*8,52*8};push(a,"arc");}
 if(seed_f=='g'){Arr a={0,(u8)(ARC_FIRST_ROOM+G7_PARENT[seed_k]),1,31*8,52*8};push(a,"g7parent");
  if(seed_k>=1){Arr b={0,(u8)(G7_FIRST_ROOM+seed_k-1),1,31*8,52*8};push(b,"g7");}}
 if(seed_f=='c'&&seed_k>=1){Arr a={0,(u8)(COMPLETION_FIRST_ROOM+seed_k-1),1,31*8,51*8};push(a,"comp");}
 for(int p=0;p<8;p++){spawn_surface(p);Arr a={current_world,current_room,current_layer,player.x,player.y};push(a,"land");}
 {base_state();Arr a={0,2,1,PRO_FORGE_TX*8+8,PRO_FORGE_TY*8+16};push(a,"start");}
 printf("[\n");int first=1;
 while(qh<qt){Arr a=qa_q[qh++&4095];base_state();load(a);
  int sok=stand(a.x,a.y);int n=sok?explore(a.x,a.y):0;
  printf("%s{\"loc\":[%d,%d,%d],\"arrive\":[%d,%d],\"standable\":%d,\"reach\":%d,\"name\":",first?"":",\n",a.w,a.r,a.l,a.x,a.y,sok,n);first=0;
  esc(game_mode==MODE_SURFACE?location_name():"?");printf(",\"warps\":[");
  int count=tn;Trig local[256];memcpy(local,tl,sizeof(Trig)*count);
  for(int i=0;i<count;i++){Trig T=local[i];
   for(int dir=(T.t==TR_LIFT?-1:0);dir<=(T.t==TR_LIFT?1:0);dir+=2){
    base_state();load(a);player.x=T.px;player.y=T.py;dialogue[0]=0;v11_notice[0]=0;
    if(T.t==TR_LIFT)shift_layer(dir);else if(V11_IS_ROOM)v11_field_interact(T.t);else interact();
    flush();
    int space=game_mode==MODE_SPACE;Arr d={current_world,current_room,current_layer,player.x,player.y};
    int moved=space||d.w!=a.w||d.r!=a.r||d.l!=a.l||iabs(d.x-T.px)+iabs(d.y-T.py)>24;
    int ds=space?1:stand(d.x,d.y);
    printf("%s{\"t\":%d,\"at\":[%d,%d],\"to\":[%d,%d,%d],\"pos\":[%d,%d],\"space\":%d,\"moved\":%d,\"standable\":%d,\"msg\":",i||dir>0?",":"",T.t,T.tx,T.ty,d.w,d.r,d.l,d.x,d.y,space,moved,ds);
    esc(dialogue[0]?dialogue:v11_notice);printf("}");
    if(moved&&!space&&ds)push(d,"warp");
   }}
  printf("]}");
 }
 printf("\n]\n");return 0;}
'''
src=G/"world_sweep_host.c";src.write_text(C)
exe=Path("/tmp/world_sweep_host")
subprocess.run(["clang","-DQA_AUTORUN","-DHOST_QA","-O2","-w",str(src),"-o",str(exe)],check=True)
res={}
runs=[("fresh",[]),("open",["open"])]+[(f"arc{k}",["open","a",str(k)]) for k in range(0,17)]+[(f"g7_{k}",["open","g",str(k)]) for k in range(0,12)]+[(f"comp{k}",["open","c",str(k)]) for k in range(0,24)]+[(f"v11_{k}",["open","v",str(k)]) for k in range(0,9)]
for mode,args in runs:
 p=subprocess.run([str(exe)]+args,capture_output=True,text=True,timeout=600)
 if p.returncode:print(p.stderr[-2000:]);raise SystemExit(f"sweep {mode} crashed rc={p.returncode}")
 res[mode]=json.loads(p.stdout)
(OUT/"world_sweep.json").write_text(json.dumps(res,indent=1))
problems=[];summary={}
for mode,rooms in res.items():
 locs={tuple(r["loc"]) for r in rooms}
 summary[mode]={"locations":len(locs),"warps":sum(len(r["warps"]) for r in rooms)}
 for r in rooms:
  if not r["standable"]:problems.append((mode,"arrival in a wall",r["loc"],r["arrive"]))
  for w in r["warps"]:
   if w["moved"] and not w["space"] and not w["standable"]:problems.append((mode,"warp lands in a wall",r["loc"],w))
  if r["standable"] and not any(w["moved"] for w in r["warps"]):problems.append((mode,"no working exit",r["loc"],r["name"]))
summary["problems"]=problems
universe=[(0,r,1) for r in list(range(0,10))+[12]+list(range(13,78))+[90,91,92,93,94]]+[(w,0,1) for w in range(1,8)]
reached=set()
for mode,rooms in res.items():
 if mode!="fresh":reached|={tuple(r["loc"]) for r in rooms}
summary["open_not_reached"]=[u for u in universe if u not in reached]
summary["reached_any_pass"]=len(reached)
(OUT/"world_sweep_summary.json").write_text(json.dumps(summary,indent=1))
print(json.dumps({"fresh":summary["fresh"],"open":summary["open"],"reached_any_pass":summary["reached_any_pass"],"not_reached":[list(u) for u in summary["open_not_reached"]]}));print("problems:",len(problems))
for p in problems:print(" ",p)
if problems or summary["open_not_reached"]:
 raise SystemExit(f"world sweep failed: {len(problems)} problems, {len(summary['open_not_reached'])} rooms never entered")
print("PASS world sweep:",summary["reached_any_pass"],"locations entered")
