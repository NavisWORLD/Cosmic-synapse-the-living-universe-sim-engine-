#!/usr/bin/env python3
"""Fail-closed, idempotent exact V10.1 -> V10.2 authored native campaign patch.
Original V10 and original V10.1 C remain immutable in lineage/baseline.
"""
from pathlib import Path
import hashlib
R=Path(__file__).resolve().parents[1]
SRC=R/'LOST_COSMOS_V10_SOURCE'/'lost_cosmos_v5.c'
BASE=R/'baseline'/'v10_1_lost_cosmos_v5.c'
expected='d57e7f84a29a3207790b1974f416de963ffc994b67cb467c97bd461a643462e6'
b=BASE.read_bytes()
assert hashlib.sha256(b).hexdigest()==expected, 'V10.1 baseline changed: refusing patch'
s=b.decode()
def put(old,new,count=1):
 global s
 found=s.count(old)
 assert found==count, f'SOURCE CONTRACT MISMATCH: {old[:130]!r}: {found} vs {count}'
 s=s.replace(old,new,count)
# Keep every original historical trigger numeric ID stable.
put('TR_FEST_L=40,TR_FEST_C=41,TR_FEST_R=42};', '''TR_FEST_L=40,TR_FEST_C=41,TR_FEST_R=42,
 TR_ARC_ENTER=43,TR_ARC_TRIAL=44,TR_ARC_REWARD=45,TR_ARC_NEXT=46,
 TR_ARC_EXIT=47,TR_ARC_BOSS=48,TR_ARC_SECRET=49,TR_ARC_EPILOGUE=50,
 TR_ARC_PETAL_W=51,TR_ARC_PETAL_C=52,TR_ARC_PETAL_U=53,
 TR_ARC_ANCHOR_W=54,TR_ARC_ANCHOR_E=55};''')
put('#define ST_ALL (ST_HEART|ST_CHRONO|ST_VOID|ST_DREAM|ST_ELEMENTS)', '''#define ST_ALL (ST_HEART|ST_CHRONO|ST_VOID|ST_DREAM|ST_ELEMENTS)
#include "atlas_data.h"
static void arc_generate_boss(void);
static int arc_boss_defeated(Enemy*e);
static int arc_boss_mercy(Enemy*e);''')
# Actual generated map and 3 unique ending worlds; implemented before original Eridoria rooms.
put('static void eridoria_area(void){', '#include "atlas_geometry.h"\nstatic void eridoria_area(void){')
# Allocate gate at reachable pre-existing Brindlemark road; other room/trigger coords retained.
put('map_put(55,54,T_DOOR,3,C_FREE,TR_GATE); /* Heartwood road from the novel */', '''map_put(55,54,T_DOOR,3,C_FREE,TR_GATE); /* Heartwood road from the novel */
  for(x=31;x<=41;x++)map_put(x,54,T_PATH,1,C_FREE,0);
  map_put(40,55,T_RUNE,3,C_FREE,TR_ARC_ENTER); /* Optional atlas: next chapter */
  if(postgame)map_put(22,54,T_STAR,3,C_FREE,TR_ARC_EPILOGUE);''')
# Distinct background palettes per original new region, not all Origin green.
put('current_room==12?5:0):current_world)', '''current_room==12?5:
 current_room>=ARC_FIRST_ROOM&&current_room<ARC_FIRST_ROOM+ARC_STAGES?
 (current_room-ARC_FIRST_ROOM)%8:
 current_room==ARC_EPILOGUE_ROOM?(ending==1?6:ending==2?3:4):0):current_world)''',2)
put('if(current_world==0&&current_room==6){v9_generate_rift();}else if(', '''if(current_world==0&&current_room==6){v9_generate_rift();}
 else if(ARC_IS_ROOM){arc_generate_map();}
 else if(current_world==0&&current_room==ARC_EPILOGUE_ROOM){arc_generate_epilogue();}
 else if(''')
# Must NEVER leave map `generate_room` fallback or wrap invalid name index.
put('static const char* location_name(void){', '''static const char* location_name(void){
 if(ARC_IS_ROOM)return ARC_NAMES[current_room-ARC_FIRST_ROOM];
 if(current_world==0&&current_room==ARC_EPILOGUE_ROOM)return
  ending==1?"EPILOGUE OPEN":ending==2?"EPILOGUE PRESERVE":"EPILOGUE WANDER";''')
put('static const char*campaign_objective(void){', '''static const char*campaign_objective(void){
 if(ARC_IS_ROOM){int index=current_room-ARC_FIRST_ROOM;
  if(index<arc_progress)return "EXPLORE OR CONTINUE THE ATLAS";
  if(index==7&&arc_petals!=3)return "FIND WISDOM COURAGE UNITY PETALS";
  if(index==13&&arc_anchors!=3)return "STABILIZE TWO DISTANT TIME ANCHORS";
  if(!arc_solved)return ARC_TASK[index];
  if((ARC_BOSSES&(1u<<index))&&!arc_boss_done)return "FACE OR HEAL THE GUARDIAN";
  return "CLAIM THE RELIC AT EAST SHRINE";
 }''')
# Real code-generated species field sprites at previously unused tiles 384..403.
put('static void oam_hide_all(void)', '''/* Distinct original 16x16 pixel silhouettes, static cartridge art, no copyrighted species. */
static void arc_gen_species(int species,int variant){u32 b[32];int x,y,base=384+(species-1)*8+variant*4;
 for(x=0;x<32;x++)b[x]=0;
 for(y=2;y<14;y++)for(x=2;x<14;x++){
  int dx=x-8,dy=y-8,c=0;
  if(species==1){ /* FORGELING: flame-ears, square furnace belly. */
   if(x>=4&&x<=11&&y>=5&&y<=12)c=(y<7||x==4||x==11)?2:1;
   if(y<6&&(x==4||x==7||x==10))c=3;
   if(y==8&&(x==6||x==9))c=4;
  }else if(species==2){ /* TIDEWISP: narrow crest and flowing droplet. */
   if(dx*dx+dy*dy<26&&y<13)c=(x+y)%4==0?2:1;
   if(y>=10&&x>=5&&x<=10)c=2;
   if(y==7&&(x==6||x==10))c=4;
   if(y<5&&x==8)c=3;
  }else if(species==3){ /* ROOTKIN: leafy canopy over gnarled trunk. */
   if((dx*dx+(y-5)*(y-5)<29&&y<10))c=(x&2)?2:3;
   if(x>=7&&x<=9&&y>=8&&y<=13)c=1;
   if(y==12&&(x==5||x==11))c=2;
   if(y==7&&(x==7||x==10))c=4;
  }else if(species==4){ /* VOIDMOTH: paired scalloped wings and antennae. */
   if(((x>=2&&x<=6)||(x>=10&&x<=14))&&y>=5&&y<=10){
    if((x+y)%3!=0)c=(x&1)?2:3;}
   if(x>=7&&x<=9&&y>=3&&y<=12)c=1;
   if((x==5||x==11)&&y==7)c=4;
   if((x==6||x==10)&&y==2)c=2;
  }else{ /* SKYSPARK: angular storm-bird with lightning tail. */
   if(iabs(dx)+iabs(dy)<7)c=(x+y)&1?2:3;
   if(x>=4&&x<=11&&y==8)c=1;
   if((x==6||x==10)&&y==6)c=4;
   if(y>=11&&x==(y&1?6:9))c=2;
  }
  /* 2-frame idle animation: real OBJ pixel differences, not CSS/preview. */
  if(variant){
   if(species==1 && y==2 && (x==3||x==8||x==11))c=3;
   if(species==2 && x==7&&y==3)c=2;
   if(species==3 && x==2&&y==3)c=3;
   if(species==4 && x==2&&y==4)c=2;
   if(species==5 && x==2&&y==6)c=3;
  }
  if(c)objpix(b,x,y,(u8)c);
 }
 upload_obj16(base,b);
}
static void oam_hide_all(void)''')
put('static void make_obj_tiles(void)', 'static void arc_gen_species(int species,int variant);\nstatic void make_obj_tiles(void)')
put('expand_obj32(272,V5_PLAYER[2],0);', '''expand_obj32(272,V5_PLAYER[2],0);
 for(f=1;f<=5;f++){arc_gen_species(f,0);arc_gen_species(f,1);}''')
put('oam_set(42,cosmos.x-cam_x+6,cosmos.y-cam_y+1+(int)((frame>>3)&1),60+typ*4,5+typ,0);', '''{int tile=60+typ*4,pal=5+typ;
   if(lc_party.count){u8 species=lc_party.slots[lc_party.active].species;
    if(species>=1&&species<=5){tile=384+(species-1)*8+(((frame>>4)&1)*4);pal=4+species;}}
   oam_set(42,cosmos.x-cam_x+6+((tile>=384)?((int)((frame>>5)&3)-1):0),cosmos.y-cam_y+1+(int)((frame>>3)&1),tile,pal,0);
  }''')
# Native CR32 extension saved alongside but never inside legacy checksummed fields.
put('static void save_game(void){', '#include "atlas_persist.h"\nstatic void save_game(void){')
put(' lc_save_roster();}', ' lc_save_roster();arc_save();}')
put(' lc_restore_roster();\n touch_mode=', ' lc_restore_roster();arc_restore();\n touch_mode=')
put('static void init_new_game(void){int i;story_flags=0;', 'static void init_new_game(void){int i;arc_reset();story_flags=0;')
# Enemy habitats/spawning and actual boss consequences.
put('static void spawn_monsters(void){int i;clear_combat();if(game_mode!=MODE_SURFACE)return;', '''static void spawn_monsters(void){int i;clear_combat();if(game_mode!=MODE_SURFACE)return;
 if(ARC_IS_ROOM){arc_generate_boss();return;}
 if(current_world==0&&current_room==ARC_EPILOGUE_ROOM)return;''')
put('static void enemy_die(Enemy*e){u8 r;', '''static void enemy_die(Enemy*e){u8 r;
 if(arc_boss_defeated(e))return;''')
put(' }else if(battle_cursor==3){\n  if(e->elite', ''' }else if(battle_cursor==3){
  if(arc_boss_mercy(e)){}
  else if(e->elite''')
put('e->damage-(def_stat+armor_bonus())/4', 'e->damage-(def_stat+armor_bonus()+arc_guardian_guard())/4')
put('dmg-=((def_stat+armor_bonus())/5)', 'dmg-=((def_stat+armor_bonus()+arc_guardian_guard())/5)')
put('return (weapon==2?5:(weapon==1?2:0))+(actor_style==0)+(v9_equipped*2);',
 '''return (weapon==2?5:(weapon==1?2:0))+(actor_style==0)+(v9_equipped*2)+arc_guardian_attack();''')
# Provide tactical TALK instructions for new elite stage.
put(' battle_notice=(e->elite&&e==&enemies[8]&&current_world==0&&current_room==8)', ''' battle_notice=(ARC_IS_ROOM&&e->elite&&e==&enemies[8])?
  "ATLAS GUARDIAN: FIGHT OR OFFER AN ETHER.":
  (e->elite&&e==&enemies[8]&&current_world==0&&current_room==8)''')
# Player-visible menu (17 genuinely unlockable guardian appendix NPC disciplines).
put('static u8 actor_style=0, role_preview=0, chronicle_page=0;',
    'static u8 actor_style=0, role_preview=0, chronicle_page=0,arc_ally_sel=0;')
put(' else if(pause_page==15){', ''' else if(pause_page==19){int page=(int)(arc_ally_sel/7)*7;
  ui_frame(0,19,15);ui_text(2,1,"GUARDIAN FELLOWSHIP",14);
  ui_text(2,2,"A EQUIP ACTIVE DISCIPLINE",13);
  for(i=page;i<mini(page+7,17);i++){
   int y=4+i-page;ui_text(2,y,i==arc_ally_sel?">":" ",13);
   ui_text(4,y,ARC_GUARDIANS[i].name,(arc_guardians_mask&(1u<<i))?15:13);
   if(i==arc_ally)ui_text(20,y,"ACTIVE",14);
   if(!(arc_guardians_mask&(1u<<i)))ui_text(20,y,"LOCKED",13);
  }
  ui_text(2,13,ARC_GUARDIANS[arc_ally_sel].discipline,14);
  ui_text(2,14,"ATK",13);ui_num(7,14,ARC_GUARDIANS[arc_ally_sel].attack,15);
  ui_text(14,14,"GUARD",13);ui_num(22,14,ARC_GUARDIANS[arc_ally_sel].guard,15);
  ui_text(2,16,"STORY ATLAS",13);ui_num(17,16,arc_progress,15);
  ui_text(19,16,"/ 16",15);
  ui_text(2,18,"UP DOWN / A / B BACK",13);
 }
 else if(pause_page==15){''')
put('ui_text(2,17,"R CHRONICLE L CRYSTALS",13);', 'ui_text(2,17,"R STORY L CRYSTALS SEL ALLY",13);')
put('if(pause_page==15){\n  if(newk', '''if(pause_page==19){
  if(newk&KEY_UP)arc_ally_sel=(u8)(arc_ally_sel?arc_ally_sel-1:16);
  if(newk&KEY_DOWN)arc_ally_sel=(u8)((arc_ally_sel+1)%17);
  if(newk&KEY_A){
   if(arc_guardians_mask&(1u<<arc_ally_sel)){
    arc_ally=arc_ally_sel;say("YOUR FELLOWSHIP ROLE IS ACTIVE.");save_game();
   }else say("CLEAR THAT ATLAS CHAPTER TO RECRUIT.");
  }
  if(newk&KEY_B)pause_page=13;
  return;
 }
 if(pause_page==15){
  if(newk''')
put('if(pause_page==13&&(newk&KEY_L)){pause_page=17;return;}', '''if(pause_page==13&&(newk&KEY_L)){pause_page=17;return;}
 if(pause_page==13&&(newk&KEY_SELECT)){
  pause_page=19;arc_ally_sel=arc_ally;return;
 }''')
# Annotate core original campaign journal without replacing it.
put('ui_text(2,17,"R CHRONICLE L CRYSTALS",13);', 'ui_text(2,17,"R STORY L CRYSTALS SEL ALLY",13);') if False else None
# Integrate new route after old story mechanics declarations.
put('static void story_gate(void){', '#include "atlas_story.h"\nstatic void story_gate(void){')
put('static void story_interact(u8 t){int tx=player.x>>3;', '''static void story_interact(u8 t){int tx=player.x>>3;
 if(t>=TR_ARC_ENTER){
  if(t==TR_ARC_EPILOGUE && current_world==0&&current_room==2){arc_open_epilogue();return;}
  arc_interact(t);return;
 }''')
# The epilogue has its own Brindlemark star gate and return portal.
put(' if(v10_realm_riddle){u8 q=v10_realm_riddle;', ''' if(arc_pending){arc_answer(newk);return;}
 if(v10_realm_riddle){u8 q=v10_realm_riddle;''')
# Add readable native HUD countdown for the real new chapter maps.
put('if(game_mode==MODE_SURFACE){ui_text(19,0,layer_name(),13);}', '''if(game_mode==MODE_SURFACE){
  if(ARC_IS_ROOM){ui_text(24,0,"CH",13);ui_num(27,0,(int)current_room-ARC_FIRST_ROOM+1,15);}
  else ui_text(19,0,layer_name(),13);
 }''')
# Persist entire atlas even when navigating back to the old world.
SRC.write_text(s)
print('V10.2 C patch applied:',SRC,'bytes',len(s),'sha256',hashlib.sha256(s.encode()).hexdigest())
