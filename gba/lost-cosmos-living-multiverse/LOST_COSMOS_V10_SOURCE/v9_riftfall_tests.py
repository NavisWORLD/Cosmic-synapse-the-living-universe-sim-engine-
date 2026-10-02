"""Native engine C hosted in mapped GBA memory: V9 RPG, arena, save and RNG gates."""
from pathlib import Path
import subprocess
R=Path(__file__).resolve().parent
src=(R/'host_qa_v5.c').read_text().split('\n#ifdef HOST_QA\nint main(',1)[0]
src+=r'''
#include <assert.h>
#include <stdio.h>
int main(void){int i,j;u32 workload;
 init_new_game();init_graphics();current_world=0;current_room=0;generate_surface();intro=0;
 /* New optional portal coexists with existing Origin map. */
 assert(trigger[mi(17,45)]==TR_RIFT);
 assert(trigger[mi(21,48)]!=TR_RIFT);
 assert(V51_SCENE_COUNT>=12&&V51_SCENE_COUNTS[11]>150);
 {u32 seed=workload_qi;u32 r=v9_next();assert(v9_next()!=r);assert(seed==workload_qi);}
 /* Travel to true arena and preserve core world identity. */
 game_mode=MODE_SURFACE;v9_rift_travel();
 assert(current_world==0&&current_room==6 && trigger[mi(31,53)]==TR_RIFT);
 assert(v9_wave==1 && enemies[0].active && enemies[2].active);
 assert(BG_PALETTE[2]!=0);
 /* Player action: jump and slam one nearby mob without crossing walls. */
 v9_start_jump();assert(v9_jump==24 && v9_jump_cd==40);
 enemies[0].x=player.x+3;enemies[0].y=player.y+2;
 enemies[0].hp=enemies[0].maxhp=20;
 {int before=enemies[0].hp;v9_air_slam();assert(enemies[0].hp<before&&v9_jump==0);}
 /* Taming requires a wounded ordinary beast; elites cannot be captured. */
 enemies[0].hp=enemies[0].maxhp;
 v9_bond(&enemies[0]);assert(!v9_bonded&&enemies[0].active);
 enemies[0].hp=1;enemies[0].maxhp=20;
 v9_bond(&enemies[0]);assert(v9_bonded&&v9_bond_type==enemies[0].type&&!enemies[0].active);
 /* Each wave is actual enemies, not just a title. */
 v9_wave_delay=0;for(i=0;i<10;i++)enemies[i].active=0;
 v9_rift_tick();assert(v9_wave==2&&enemies[0].active&&enemies[3].active);
 v9_wave_delay=0;for(i=0;i<10;i++)enemies[i].active=0;
 v9_rift_tick();assert(v9_wave==3&&enemies[0].active&&enemies[4].active);
 v9_wave_delay=0;for(i=0;i<10;i++)enemies[i].active=0;
 v9_rift_tick();assert(v9_wave==4&&enemies[0].active&&enemies[0].elite);
 /* Rare gear stays on the floor and guaranteed legendary drop cannot be buried. */
 for(i=0;i<8;i++){drops[i].active=1;drops[i].type=ITEM_COUNT;drops[i].rarity=0;}
 enemies[0].x=player.x+3;enemies[0].y=player.y+3;
 enemy_die(&enemies[0]);assert(v9_completed==1 && v9_best_wave==4);
 {int n=0;for(i=0;i<8;i++)if(drops[i].active&&drops[i].type==ITEM_COUNT&&drops[i].rarity==4)n++;
 assert(n==1);}
 collect_drops();assert(v9_loot[4]==1&&v9_equipped==4&&weapon_bonus()>=8);
 /* Item can be equipped, dumped to SRAM and round-tripped. */
 v9_gear_sel=4;game_mode=MODE_PAUSE;pause_page=16;update_pause(KEY_A);
 assert(v9_equipped==4&&v9_loot[4]==1);save_game();assert(SRAM[211]==0xA9&&SRAM[226]==v9_crc()&&save_valid());
 {u32 r=v9_rng;v9_bonded=0;v9_loot[4]=0;v9_completed=0;v9_best_wave=0;v9_rng=1;
 load_game();assert(v9_bonded==1&&v9_loot[4]==1&&v9_completed==1&&v9_best_wave==4&&v9_rng==r);}
 /* Corrupting only new V9 checksum cannot invalidate old saves. */
 SRAM[226]^=1;assert(save_valid());load_game();assert(!v9_completed&&!v9_bonded&&v9_loot[4]==0);
 /* Exit portal returns to the original world; legacy world triggers remain. */
 current_world=0;current_room=6;v9_rift_travel();
 assert(current_world==0&&current_room==0&&trigger[mi(17,45)]==TR_RIFT);
 assert(player.x==16*8&&player.y==48*8);
  /* V9 branch must still load verified original V7 SRAM unchanged. */
 {FILE*f=fopen("qa_fixtures/v7_mgba_boot1.sav","rb");assert(f);
 assert(fread((void*)HOST_SRAM,1,32768,f)==32768);fclose(f);
 init_new_game();assert(save_valid());load_game();assert(SRAM[5]&1&&!v9_completed&&!v9_bonded);
 }
 puts("PASS V9 native C: Origin portal, 4-wave Riftfall, jump-slam, tame requirements, legendary drop, gear equip, independent RNG, checksummed saves, V7 import, 12 cinematics");
 return 0;
}
'''
(R/'v9_riftfall_qa.c').write_text(src)
subprocess.run(['clang','-DQA_AUTORUN','-DHOST_QA','-O2','-Wno-unused-function','v9_riftfall_qa.c','-o','v9_riftfall_qa'],cwd=R,check=True)
subprocess.run([str(R/'v9_riftfall_qa')],cwd=R,check=True)
