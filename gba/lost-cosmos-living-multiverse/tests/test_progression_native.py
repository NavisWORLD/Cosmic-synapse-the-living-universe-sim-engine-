"""Actually execute the current native GBA C engine with the established MMIO host shim;
not real mGBA or iPhone controller footage. Verifies PRG4 SRAM isolation,
five deterministic drops, atomic crafting and 8 distinct active abilities.
"""
from pathlib import Path
import subprocess,tempfile
root=Path(__file__).resolve().parents[1];g=root/'LOST_COSMOS_V10_SOURCE'
subprocess.run(['python3','host_qa_v5.py'],cwd=g,check=True,capture_output=True,timeout=40)
pre=(g/'host_qa_v5.c').read_text().split('\n#ifdef HOST_QA\nint main(',1)[0]
prog=r'''
#include <assert.h>
#include <stdio.h>
#include <string.h>
static void test_atomic_crafting(void){
 init_new_game();init_graphics();intro=0;game_mode=MODE_SURFACE;
 player.hp=3;credits=40;
 for(int i=0;i<5;i++)p4_material[i]=4;
 int old_pot=inv[ITEM_POTION];
 assert(p4_craft(0));assert(inv[ITEM_POTION]==old_pot+1);
 assert(p4_material[2]==2&&credits==38);
 assert(p4_craft(1));assert(inv[ITEM_ETHER]==2);
 assert(p4_craft(2));assert(inv[ITEM_SHARD]==1);
 /* No deduction when roster empty; no ability to train a nonexistent creature. */
 u8 old[5];memcpy(old,p4_material,5);
 assert(!p4_craft(3));assert(memcmp(old,p4_material,5)==0);
 assert(lc_add_wild(&lc_party,1,0x1234)==LC_OK);
 lc_party.slots[0].bond=40;
 assert(p4_craft(3));assert(lc_party.slots[0].bond==52);
 /* Crafted item cap cannot silently consume materials or credits. */
 inv[ITEM_POTION]=99;credits=50;p4_material[2]=6;
 assert(!p4_craft(0));assert(credits==50&&p4_material[2]==6);
 /* No underflow even when an ingredient is zero. */
 p4_material[4]=0;memcpy(old,p4_material,5);
 assert(!p4_craft(2));assert(memcmp(old,p4_material,5)==0);
 enter_pause();pause_page=4;update_pause(KEY_R);assert(pause_page==21);
 update_pause(KEY_DOWN);assert(p4_craft_sel==1);
 update_pause(KEY_B);assert(pause_page==4);
 puts("PASS REAL C four atomic ingredient recipes, no invisible spending, playable items->R workshop and restored inventory");
}
static void test_guaranteed_materials(void){
 init_new_game();intro=0;game_mode=MODE_SURFACE;
 static const u8 classid[5]={EN_EMBER,EN_TIDE,EN_BLOOM,EN_VOID,EN_CROWN};
 for(int i=0;i<5;i++){
  u32 before=qi;spawn_enemy(0,35,34,classid[i],0);
  assert(p4_material[i]==0);enemies[0].hp=1;damage_enemy(&enemies[0],100);
  assert(p4_material[i]==1&&qi==before);enemies[0].active=0;
 }
 current_world=0;current_room=8;
 spawn_enemy(8,22,33,EN_TIDE,1);enemies[8].hp=1;
 damage_enemy(&enemies[8],100);
 assert(p4_material[1]==3);
 assert(p4_research[5]>=1); /* Frost Wolf victory actually recorded */
 puts("PASS REAL C five enemy biome classes yield guaranteed resources, elite Wolf bonus and Frost bestiary research without touching QSEED");
}
static void test_eight_actions_and_turns(void){
 for(int sp=1;sp<=8;sp++){
  init_new_game();init_graphics();intro=0;game_mode=MODE_SURFACE;
  player.hp=3;player_mp=1;
  assert(lc_add_wild(&lc_party,(u8)sp,(u32)(0xEE00+sp))==LC_OK);
  lc_party.active=0;lc_party.slots[0].bond=85;lc_party.slots[0].hp=20;
  lc_party.slots[0].stage=1;
  spawn_enemy(1,25,25,EN_CROWN,0);enemies[1].hp=enemies[1].maxhp=110;
  battle_enter(1);assert(p4_charges==2);
  battle_cursor=5;int prevhp=enemies[1].hp;
  battle_act();
  assert(p4_charges==1&&battle_phase==1);
  if(sp==1||sp==4||sp==5||sp==6||sp==7||sp==8)assert(enemies[1].hp<prevhp);
  if(sp==2)assert(p4_guard==2&&player.hp==4);
  if(sp==3)assert(player.hp>=6);
  if(sp==4||sp==6)assert(battle_timer>=50);
  if(sp==7)assert(player_mp==2);
  if(sp==8)assert(p4_ward==2);
  assert(lc_party.slots[0].xp>0);
  /* Fail-closed no free third ally action. */
  battle_phase=0;enemies[1].hurt=0;battle_cursor=5;if(sp==3)player.hp=2;assert(p4_ally_use(&enemies[1]));
  assert(p4_charges==0);battle_phase=0;
  assert(!p4_ally_use(&enemies[1]));assert(p4_charges==0);
  if(sp==2||sp==4||sp==6){battle_evade=0;p4_guard=1;battle_phase=1;
    battle_timer=0;update_battle(0);assert(player.hp>0&&p4_guard==0);}
 }
 puts("PASS REAL C all 8 distinct actionable ally moves, real enemy HP, ward/heal/slow, XP, bounded 2-charge turn economy");
}
static void test_import_and_sram_backcompat(void){
 init_new_game();init_graphics();intro=0;game_mode=MODE_SURFACE;
 /* Genuine old pre-V10.4 absence: old SRAM stays valid and new page starts empty. */
 inv[ITEM_SHARD]=5;story_flags|=ST_HEART;save_game();
 for(int i=0;i<P4_SRAM_BYTES;i++)SRAM[P4_SRAM+i]=0;
 load_game();assert(inv[ITEM_SHARD]==5&&p4_material[0]==0);
 u8 old[238];for(int i=0;i<238;i++)old[i]=SRAM[i];
 p4_material[0]=12;p4_material[2]=2;p4_research[3]=16;save_game();
 u8 lcr[LC_ROSTER_BYTES],arc[ARC_SRAM_BYTES];
 for(int i=0;i<LC_ROSTER_BYTES;i++)lcr[i]=SRAM[LC_ROSTER_SRAM+i];
 for(int i=0;i<ARC_SRAM_BYTES;i++)arc[i]=SRAM[ARC_SRAM+i];
 init_new_game();load_game();
 assert(p4_material[0]==12&&p4_material[2]==2&&p4_research[3]==16);
 for(int i=0;i<238;i++)assert(old[i]==SRAM[i]);
 for(int i=0;i<LC_ROSTER_BYTES;i++)assert(lcr[i]==SRAM[LC_ROSTER_SRAM+i]);
 for(int i=0;i<ARC_SRAM_BYTES;i++)assert(arc[i]==SRAM[ARC_SRAM+i]);
 /* CRC-correct but invalid material count MUST fail without breaking older saves. */
 SRAM[P4_SRAM+5]=250;
 u8 bytes[P4_SRAM_BYTES];for(int i=0;i<P4_SRAM_BYTES;i++)bytes[i]=SRAM[P4_SRAM+i];
 u32 crc=lc_crc32(bytes,28);for(int i=0;i<4;i++)SRAM[P4_SRAM+28+i]=(u8)(crc>>(8*i));
 p4_restore();assert(p4_material[0]==0&&p4_material[2]==0&&p4_research[3]==0);
 for(int i=0;i<238;i++)assert(old[i]==SRAM[i]);
 for(int i=0;i<LC_ROSTER_BYTES;i++)assert(lcr[i]==SRAM[LC_ROSTER_SRAM+i]);
 for(int i=0;i<ARC_SRAM_BYTES;i++)assert(arc[i]==SRAM[ARC_SRAM+i]);
 LcProfile profile={0};profile.family=2;profile.public_id=0x12598239;profile.stats[0]=72;
 assert(lc_add_import(&lc_party,&profile,0x98987777u)==LC_OK);
 lc_party.active=0;lc_party.slots[0].bond=85;
 spawn_enemy(2,30,30,EN_VOID,0);enemies[2].hp=100;enemies[2].maxhp=100;
 battle_enter(2);battle_cursor=5;battle_act();assert(p4_charges==1&&p4_guard==1);
 assert(lc_party.slots[0].identity==profile.public_id);
 puts("PASS real PRG4 32-byte CRC/limits/migration, untouched historical story + roster + atlas, synthetic imported game profile accessible to ally command");
}
int main(void){test_atomic_crafting();test_guaranteed_materials();test_eight_actions_and_turns();test_import_and_sram_backcompat();return 0;}
'''
with tempfile.TemporaryDirectory(prefix='lc_p4_') as d:
 c=Path(d)/'progression_native_host.c';c.write_text(pre+'\n'+prog)
 binary=Path(d)/'progression_native_host'
 subprocess.run(['clang','-DHOST_QA','-DQA_AUTORUN','-O1','-Wno-unused-function','-I',str(g),str(c),'-o',str(binary)],cwd=g,check=True,timeout=40)
 subprocess.run([str(binary)],cwd=g,check=True,timeout=40)
