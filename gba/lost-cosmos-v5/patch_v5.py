"""Deterministic source transformation from published V4 to V5.
Apply to exact source hash and keep old V4 immutable. Reproducible in GitHub CI.
"""
from pathlib import Path
import hashlib,re,argparse
p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--dest',required=True);a=p.parse_args()
src=Path(a.source).read_text(); verified='83bdde8e628ada112f172443336628d988ec977b464d0aadb5249d1e0b6805ca'
actual=hashlib.sha256(src.encode()).hexdigest()
if actual!=verified:raise SystemExit(f'wrong V4 baseline source {actual}; expected {verified}')

def swap(old,new,count=1):
 global src
 seen=src.count(old)
 if seen!=count:raise SystemExit('PATCH FAILED occurrence '+str(seen)+' expected '+str(count)+' for '+old[:130])
 src=src.replace(old,new)

def change_func(start_marker,end_marker,code):
 global src
 a=src.index(start_marker); b=src.index(end_marker,a)
 src=src[:a]+code+src[b:]

swap('#include "qseed.h"','#include "qseed.h"\n#include "v5_art.h"')
swap('SIM EARTH // PIXEL UNIVERSE: THE LOST COSMOS V2','SIM EARTH // PIXEL UNIVERSE: THE LOST COSMOS V5')
swap('#define REG_BG1CNT     (*(volatile u16*)0x0400000A)','#define REG_BG1CNT     (*(volatile u16*)0x0400000A)\n#define REG_BG2CNT     (*(volatile u16*)0x0400000C)')
swap('#define REG_BG1VOFS    (*(volatile u16*)0x04000016)','#define REG_BG1VOFS    (*(volatile u16*)0x04000016)\n#define REG_BG2HOFS    (*(volatile u16*)0x04000018)\n#define REG_BG2VOFS    (*(volatile u16*)0x0400001A)')
swap('#define BG1_ENABLE  (1u<<9)','#define BG1_ENABLE  (1u<<9)\n#define BG2_ENABLE  (1u<<10)\n#define SPACE_PARALLAX_MAP 29')
swap('u8 type,hp,maxhp,damage,active,hurt,elite;','u8 type,hp,maxhp,damage,active,hurt,elite,windup,recover;')
swap('static u8 attack_timer=0,magic_timer=0,workload_tick=0;','static u8 attack_timer=0,magic_timer=0,workload_tick=0,dodge_timer=0,dodge_cooldown=0,heavy_cooldown=0;')
swap('static u32 qi=0;','static u32 qi=0; /* legacy gameplay stream, preserved in SRAM at 120 */\nstatic u32 workload_qi=0; /* isolated reproducible workload stream, persisted at 164 */')
swap('static u8 next_q(void){ u8 v=QSEED[qi++]; if(qi>=QSEED_LEN)qi=0; return v; }',
'''static u8 next_q(void){ u8 v=QSEED[qi++]; if(qi>=QSEED_LEN)qi=0; return v; }
static u8 next_workload(void){u8 v=QSEED[workload_qi++];if(workload_qi>=QSEED_LEN)workload_qi=0;return v;}''')
swap('u8 x=0,prev=next_q();','u8 x=0,prev=next_workload();')
swap('u8 v=(i==0)?prev:next_q();','u8 v=(i==0)?prev:next_workload();')
swap('static void make_bg_tile(int id,int type){ u32 t[8];int x,y;',
'''static void make_bg_tile(int id,int type){ u32 t[8];int x,y;
 if(type>=0&&type<32&&type!=T_WATER&&type!=T_LAVA&&type!=T_HAZARD&&type!=T_PLANT&&type!=T_FOAM&&type!=T_FURNACE){upload_bg_tile(id,V5_TILES[type]);return;}''')
change_func('static void gen_player_frame(', 'static void refresh_player_frames(', '''static void gen_player_frame(int base,int face,int step){
 u32 b[32];int x,y,i;const u32*frame_art=V5_PLAYER[face*2+step];
 for(i=0;i<32;i++)b[i]=frame_art[i];
 /* Equipment overlays retain V4's mechanical progression while preserving authored sprites. */
 if(armor){for(y=8;y<=11;y++){objpix(b,4,y,6);objpix(b,11,y,6);}for(x=6;x<=9;x++)objpix(b,x,11,3);}
 if(charm){objpix(b,7,9,4);objpix(b,8,9,4);}
 if(weapon){int wx=face==2?1:13;for(y=5;y<=11;y++)objpix(b,wx,y,6);
  objpix(b,wx-1,10,3);objpix(b,wx+1,10,3);
  if(weapon==2){objpix(b,wx,4,4);objpix(b,wx,3,6);}}
 upload_obj16(base,b);
}
''')
change_func('static void gen_buddy_frame(', 'static void gen_ship_frame(', '''static void gen_buddy_frame(int base,int mood){upload_obj16(base,V5_BUDDY[mood&3]);}
''')
change_func('static void gen_enemy_frame(', 'static void gen_item_frame(', '''static void gen_enemy_frame(int base,int type){upload_obj16(base,V5_ENEMIES[type%EN_COUNT]);}
''')
change_func('static void gen_npc_frame(', 'static void make_obj_tiles(', '''static void gen_npc_frame(int base,int kind,int frame_phase){upload_obj16(base,V5_NPCS[(kind&3)*2+(frame_phase&1)]);}
static void gen_alert_frame(int base){u32 b[32];int i;for(i=0;i<32;i++)b[i]=0;
 for(i=2;i<=9;i++){objpix(b,7,i,4);objpix(b,8,i,4);}objpix(b,7,12,6);objpix(b,8,12,6);
 upload_obj16(base,b);
}
''')
swap('gen_npc_frame(96+f*8,f,1);} }','gen_npc_frame(96+f*8,f,1);} gen_alert_frame(124); }')
swap('OBJ_PALETTE[4]=RGB5(31,10,18);','OBJ_PALETTE[4]=RGB5(31,10,18);OBJ_PALETTE[5]=RGB5(10,10,17);OBJ_PALETTE[6]=RGB5(30,30,18);')
swap('OBJ_PALETTE[(1+i)*16+5+i]=WORLDS[w].accent;',
     'OBJ_PALETTE[(1+i)*16+4]=WORLDS[w].accent;OBJ_PALETTE[(1+i)*16+5]=RGB5(5,7,13);OBJ_PALETTE[(1+i)*16+6]=RGB5(31,31,24);')
swap('OBJ_PALETTE[i*16+4]=RGB5(31,8,8);','OBJ_PALETTE[i*16+4]=RGB5(31,8,8);OBJ_PALETTE[i*16+5]=RGB5(5,5,9);OBJ_PALETTE[i*16+6]=RGB5(31,28,16);')
swap('OBJ_PALETTE[i*16+5]=RGB5(5,6,11);','OBJ_PALETTE[i*16+5]=RGB5(5,6,11);OBJ_PALETTE[i*16+6]=RGB5(31,29,20);')
# Never let presentation choices consume gameplay or the workload clock.
swap('SONGS[game_mode==MODE_SPACE?5:WORLDS[current_world].music][n]+(next_q()&7)',
     'SONGS[game_mode==MODE_SPACE?5:WORLDS[current_world].music][n]+(frame&7)')
swap('tone((u16)(1500+(next_q()<<1)))','tone((u16)(1500+((((u8)dialogue[0])+(u8)frame)&31)*5))')
swap('q=(u8)(next_q()^qstate.parity^((u8)frame)+n->id*23);',
     'q=(u8)(qstate.parity^((u8)(frame>>1))+n->id*23);')
swap('static void buddy_speak_context(void){u8 q=qpick(5);',
     'static void buddy_speak_context(void){u8 q=(u8)((qstate.parity+current_world+(frame>>4))%5);')
# New save version, old cartridges remain migratable.
swap('static u8 save_checksum_v4(void){','static u8 save_checksum_v4(void){',1)
swap('static void save_game(void){int i,o=40;',
'''static u8 save_checksum_v5(void){int i;u8 s=0x6D;for(i=0;i<190;i++)if(i!=126&&i!=127)s=(u8)(s+SRAM[i]+(i*7));return s;}
static void save_game(void){int i,o=40;''')
swap("SRAM[3]='4';SRAM[4]=4;","SRAM[3]='5';SRAM[4]=5;")
swap('SRAM[162]=npc_recent;','SRAM[162]=npc_recent;sw32(164,workload_qi);')
swap('SRAM[190]=save_checksum_v4();','SRAM[190]=save_checksum_v5();')
swap('static int save_valid(void){return SRAM[0]==\'L\'&&SRAM[1]==\'C\'&&SRAM[2]==\'V\'&&SRAM[3]==\'4\'&&SRAM[4]==4&&SRAM[190]==save_checksum_v4();}',
'''static int save_valid_v4(void){return SRAM[0]=='L'&&SRAM[1]=='C'&&SRAM[2]=='V'&&SRAM[3]=='4'&&SRAM[4]==4&&SRAM[190]==save_checksum_v4();}
static int save_valid(void){return SRAM[0]=='L'&&SRAM[1]=='C'&&SRAM[2]=='V'&&SRAM[3]=='5'&&SRAM[4]==5&&SRAM[190]==save_checksum_v5();}''')
swap('if(save_valid()||save_valid_v3()){int old_v3=save_valid_v3();',
     'if(save_valid()||save_valid_v4()||save_valid_v3()){int old_v3=save_valid_v3(),old_v4=save_valid_v4();')
swap('if(old_v3){quest_started=quest_completed=0;npc_seen=0;npc_recent=0;save_game();}', 'if(old_v3){quest_started=quest_completed=0;npc_seen=0;npc_recent=0;}')
swap('else{quest_started=SRAM[158];quest_completed=SRAM[159];npc_seen=(u16)SRAM[160]|((u16)SRAM[161]<<8);npc_recent=SRAM[162];}',
     'else{quest_started=SRAM[158];quest_completed=SRAM[159];npc_seen=(u16)SRAM[160]|((u16)SRAM[161]<<8);npc_recent=SRAM[162];}workload_qi=(old_v3||old_v4)?qi:sr32(164);if(workload_qi>=QSEED_LEN)workload_qi=0;if(old_v3||old_v4)save_game();')
swap('quest_started=quest_completed=0;npc_seen=0;npc_recent=0;save_game();}}',
     'quest_started=quest_completed=0;npc_seen=0;npc_recent=0;workload_qi=qi;save_game();}}')
swap('cosmos.focus=130;current_world=0;',
     'cosmos.focus=130;dodge_timer=dodge_cooldown=heavy_cooldown=0;workload_qi=0;current_world=0;')
# Save version fixed, assertions will use existing two boot marker and complete RPG route.
swap('THE LOST COSMOS V4','THE LOST COSMOS V5')
swap('SRAM_V113 // V4','SRAM_V113 // V5')
swap('ui_text(2,17,"A OPEN   B RESUME",13);','ui_text(2,16,"B+A HEAVY  B+SEL DODGE",14);ui_text(2,17,"A OPEN   B RESUME",13);')
# Combat: heavy/evade action based on explicit button chord, guard windups only attack when completed.
swap('e->active=1;e->hurt=0;','e->active=1;e->hurt=0;e->windup=0;e->recover=0;')
swap('e->hurt=10;if(!e->hp)','e->hurt=10;e->windup=0;e->recover=e->elite?22:14;if(!e->hp)')
swap('static void cast_magic(void){', '''static void player_heavy_attack(void){int i,ax=player.x,ay=player.y,dx=0,dy=0;
 if(heavy_cooldown)return;
 heavy_cooldown=38;attack_timer=17;
 if(player.face==0)dy=-30;else if(player.face==1)dy=30;else if(player.face==2)dx=-30;else dx=30;
 ax+=dx;ay+=dy;
 for(i=0;i<10;i++)if(enemies[i].active&&iabs(enemies[i].x-ax)<26&&iabs(enemies[i].y-ay)<26)
  damage_enemy(&enemies[i],str_stat+weapon_bonus()+3);
 tone(1350);
}
static void player_dodge(u16 k){int dx=0,dy=0,i;
 if(dodge_cooldown)return;
 if(k&KEY_LEFT)dx=-1;else if(k&KEY_RIGHT)dx=1;
 if(k&KEY_UP)dy=-1;else if(k&KEY_DOWN)dy=1;
 if(!dx&&!dy){if(player.face==0)dy=-1;else if(player.face==1)dy=1;else if(player.face==2)dx=-1;else dx=1;}
 dodge_cooldown=35;dodge_timer=16;
 for(i=0;i<5;i++){int nx=player.x+dx*3,ny=player.y+dy*3;
  if(can_stand(nx,ny)){player.x=(s16)nx;player.y=(s16)ny;}else break;}
 tone(1080);
}
static void cast_magic(void){''')
# forward can_stand declared after player_heavy, ensure prototype.
swap('static void player_dodge(u16 k){','static int can_stand(int x,int y);\nstatic void player_dodge(u16 k){')
change_func('static void enemy_tick(', 'static void buddy_combat_assist(', '''static void enemy_tick(void){int i;
 if(game_mode!=MODE_SURFACE||current_room)return;
 for(i=0;i<10;i++){Enemy*e=&enemies[i];int dx,dy,d;
  if(!e->active)continue;
  if(e->hurt)e->hurt--;
  d=iabs(e->x-player.x)+iabs(e->y-player.y);
  if(e->recover){e->recover--;continue;}
  if(e->windup){
   --e->windup;
   if(!e->windup){
    /* Foe hits only in the telegraphed direction and after a readable windup. */
    dx=player.x-e->x;dy=player.y-e->y;
    if(iabs(dx)<24&&iabs(dy)<24&&(dx*e->vx+dy*e->vy)>=0&&!dodge_timer)
      hurt_player(signi(e->x-player.x),signi(e->y-player.y));
    e->recover=(u8)(e->elite?24:38);
   }
   continue;
  }
  if(d<29){e->windup=(u8)(e->elite?28:20);e->vx=(s8)signi(player.x-e->x);e->vy=(s8)signi(player.y-e->y);continue;}
  if(d<120&&(frame&3)==0){dx=signi(player.x-e->x);dy=signi(player.y-e->y);
   if(can_stand(e->x+dx,e->y))e->x+=(s16)dx;
   if(can_stand(e->x,e->y+dy))e->y+=(s16)dy;}
 }
}
''')
swap('static void hurt_player(int dx,int dy){int dmg;if(player.hurt)return;',
     'static void hurt_player(int dx,int dy){int dmg;if(player.hurt||dodge_timer)return;')
# Bare surface render tracks alert sprite slots 48..57; won't leak into space.
swap('if(player.hurt&&(frame&2))OAM16[0]=0x0200;',
     'if(player.hurt&&(frame&2))OAM16[0]=0x0200;')
swap('if(npc_dialogue_active){oam_set(40,8,110,92+NPCS[npc_dialogue_id].kind*8,12+NPCS[npc_dialogue_id].kind,0);}else OAM16[40*4]=0x0200;',
'''if(npc_dialogue_active){oam_set(40,8,110,92+NPCS[npc_dialogue_id].kind*8,12+NPCS[npc_dialogue_id].kind,0);}else OAM16[40*4]=0x0200;
 for(i=0;i<10;i++){if(enemies[i].active&&enemies[i].windup&&((frame&7)<5))
  oam_set(48+i,enemies[i].x-cam_x-8,enemies[i].y-cam_y-28,124,11,0);
  else OAM16[(48+i)*4]=0x0200;}
''')
swap('while(oi<12){OAM16[oi*4]=0x0200;oi++;}}',
'''while(oi<12){OAM16[oi*4]=0x0200;oi++;}
 for(i=12;i<58;i++)OAM16[i*4]=0x0200;
 REG_BG2HOFS=(u16)(camx>>1);REG_BG2VOFS=(u16)(camy>>1);}
''')
# 32x32 sparse starfield parallax BG2 in space; surface always disables.
space_start=src.index('static void generate_space(')
space_end=src.index('/* ---------- sound ---------- */',space_start)
section=src[space_start:space_end]
old='REG_BG1CNT=(u16)((UI_TILE_CB<<2)|(UI_MAP_BASE<<8));ui_clear();REG_DISPCNT=MODE0|BG0_ENABLE|BG1_ENABLE|OBJ_ENABLE|OBJ_1D_MAP;}'
new='''REG_BG1CNT=(u16)((UI_TILE_CB<<2)|(UI_MAP_BASE<<8));REG_BG2CNT=(u16)(1|(BG_TILE_CB<<2)|(SPACE_PARALLAX_MAP<<8));
 for(y=0;y<32;y++)for(x=0;x<32;x++){int h=((x*37+y*19+x*y*5)^0x25)&63;
  screenblock(SPACE_PARALLAX_MAP)[y*32+x]=h<2?map_attr(T_STAR,2):map_attr(T_VOID,0);}
 ui_clear();REG_DISPCNT=MODE0|BG0_ENABLE|BG1_ENABLE|BG2_ENABLE|OBJ_ENABLE|OBJ_1D_MAP;}'''
if section.count(old)!=1:raise SystemExit('space starfield patch failed')
src=src[:space_start]+section.replace(old,new)+src[space_end:]
swap('static void update_surface(u16 k,u16 newk){int speed=(k&KEY_B)?3:2,dx=0,dy=0;u8 t;',
     'static void update_surface(u16 k,u16 newk){int speed=(k&KEY_B)?3:2,dx=0,dy=0;u8 t;if(dodge_timer)dodge_timer--;if(dodge_cooldown)dodge_cooldown--;if(heavy_cooldown)heavy_cooldown--;')
# mGBA autorun must hit V5-only telegraph and heavy/dodge paths before V4's route.
swap('npc_advance();npc_advance();npc_advance();qa_require((quest_started&1)!=0,0x64);npc_close();',
'''npc_advance();npc_advance();npc_advance();qa_require((quest_started&1)!=0,0x64);npc_close();
   {u32 replay_before=workload_qi;u8 hp_before=player.hp;
    player.x=80;player.y=408;clear_combat();spawn_enemy(9,8,51,EN_GLITCH,0);
    enemy_tick();qa_require(enemies[9].windup>0&&player.hp==hp_before,0x68);
    dodge_cooldown=0;player_dodge(KEY_B|KEY_RIGHT);qa_require(dodge_timer>0&&player.hp==hp_before,0x69);
    player.face=2;heavy_cooldown=0;player_heavy_attack();
    qa_require(!enemies[9].active&&workload_qi==replay_before,0x6A);
    clear_combat();dodge_timer=0;dodge_cooldown=heavy_cooldown=0;
   }''')
swap('if(newk&KEY_A){int ni=npc_near();if(t)interact();else if(ni>=0)npc_speak(ni);else if(enemy_near_player(36))player_attack();else if(iabs(cosmos.x-player.x)<18&&iabs(cosmos.y-player.y)<18)buddy_speak_context();else player_attack();}if(newk&KEY_SELECT)drop_beacon();',
'''if(newk&KEY_A){int ni=npc_near();
 if(k&KEY_B){if(t==TR_NONE&&ni<0)player_heavy_attack();} /* B+A never triggers travel/NPC. */
 else if(t)interact();else if(ni>=0)npc_speak(ni);else if(enemy_near_player(36))player_attack();
 else if(iabs(cosmos.x-player.x)<18&&iabs(cosmos.y-player.y)<18)buddy_speak_context();else player_attack();}
 if(newk&KEY_SELECT){if(k&KEY_B)player_dodge(k);else drop_beacon();}''')
# Add control hints in visible on-screen RPG HUD.
swap('ui_text(1,19,"L POTION",14);','ui_text(1,19,"L POTION",14);')
swap('ui_text(9,4,"SIM EARTH",14);','ui_text(9,4,"SIM EARTH",14);')
# V5 source does not attempt a false 4K raster; authored indexed assets improve the 240x160 screen.
Path(a.dest).write_text(src)
print('V5 source',a.dest,'bytes',len(src),'sha256',hashlib.sha256(src.encode()).hexdigest())
