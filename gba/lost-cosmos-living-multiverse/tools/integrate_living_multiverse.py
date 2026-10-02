"""Non-destructive reviewed V10 -> V10.1 creature integration.
Patch only exact identified anchors in the author's recovered real V10 C source.
"""
from pathlib import Path
import hashlib
root=Path(__file__).resolve().parents[1]
p=root/'LOST_COSMOS_V10_SOURCE'/'lost_cosmos_v5.c'
s=p.read_text()
BASE='65880121335c2a32b1e647fed38a745d0b64e3fa001b3744228063ef33d59b4d'
if hashlib.sha256(s.encode()).hexdigest()!=BASE:
 raise SystemExit('FAIL CLOSED: integrated only against original exact V10 C hash')

def once(old,new):
 global s
 count=s.count(old)
 if count!=1:raise SystemExit(f'FAIL CLOSED patch anchor count={count}: {old[:130]!r}')
 s=s.replace(old,new,1)

once('#include "cinematic_assets_v51.h"', '''#include "cinematic_assets_v51.h"
/* Original, allocation-free C99 Beast Box and Eridoria party subsystem.
   Included as one TU to preserve historical hosted test harness compilation. */
#include "lc_creature.h"
#include "lc_creature.c"
#if defined(LC_IMPORTED_COMPANION)
#include "imported_companion.h"
#endif''')

once('static QuantumState qstate;', '''static QuantumState qstate;
/* LIVING MULTIVERSE 011: new 12-slot party; old V9 one-bond fields remain
   authoritative when loading historical saves and are never renumbered. */
#define LC_ROSTER_SRAM 1024
#define LC_IMPORT_OBJ_TILE 512
#define LC_IMPORT_OBJ_PAL 15
static LcRoster lc_party;
static u8 lc_party_sel=0;
static const char *lc_species_name(u8 n){
 static const char *const wild[5]={"FORGELING","TIDEWISP","ROOTKIN","VOIDMOTH","SKYSPARK"};
 static const char *const imported[7]={"NEBULA","AURORA","VOID","PLASMA","MEMORY","SIGNAL","STARLIGHT"};
 if(n>=1&&n<=5)return wild[n-1];
 if(n>=128&&n<=134)return imported[n-128];
 return "UNKNOWN";
}
/* Mercy in the existing V10 guardian encounters now actually registers a
   bonded creature; a full party still permits the main story's mercy path. */
static LcResult lc_recruit_mercy(u8 type,u8 world,u8 room){
 if(lc_party.count>=LC_ROSTER_CAP)return LC_FULL;
 u8 species=(u8)(1+type%5);
 u32 seed=0x4d450000u|((u32)world<<12)|((u32)room<<4)|(type&15u);
 LcResult result=lc_add_wild(&lc_party,species,seed);
 if(result==LC_OK){
  lc_party.active=(u8)(lc_party.count-1);
  lc_party_sel=lc_party.active;
  lc_party.slots[lc_party.active].bond=80;
  lc_party.slots[lc_party.active].flags|=4u; /* trusted mercy recruitment */
 }
 return result;
}
static void lc_add_exported_profile(void){
#if defined(LC_IMPORT_HAS_BCP1)
 LcProfile g;
 if(lc_parse_bcp1(lc_imported_companion_bcp1,LC_BCP_BYTES,&g)==LC_OK)
  (void)lc_add_import(&lc_party,&g,LC_IMPORT_SEED_HASH);
#endif
}
/* Only the imported 64x64 PORTRAIT uses OBJ bank 15 and reserved tile 512..767.
   The established 16x16 field sprites keep their original allocator/indices. */
static void lc_upload_import_art(void){
#if defined(LC_IMPORTED_COMPANION)
 volatile u16 *dst=(volatile u16*)OBJ_VRAM32;
 unsigned i;
 for(i=0;i<4096;i++){
  dst[LC_IMPORT_OBJ_TILE*16+i]=(u16)lc_imported_companion_tiles[i*2] |
   (u16)((u16)lc_imported_companion_tiles[i*2+1]<<8);
 }
#endif
}
static void lc_draw_import_portrait(int x,int y){
#if defined(LC_IMPORTED_COMPANION)
 int i;for(i=0;i<16;i++)OBJ_PALETTE[LC_IMPORT_OBJ_PAL*16+i]=
  (u16)lc_imported_companion_palette[2*i]|
  (u16)((u16)lc_imported_companion_palette[2*i+1]<<8);
 OAM16[42*4]=(u16)(y&255);
 OAM16[42*4+1]=(u16)((x&511)|(3u<<14)); /* square 64x64 */
 OAM16[42*4+2]=(u16)(LC_IMPORT_OBJ_TILE+(cosmos.mood&3)*64 +
   (LC_IMPORT_OBJ_PAL<<12));
#else
 (void)x;(void)y;
#endif
}
''')

# The native new SRAM block is disjoint from all actual recovered V10 offsets 0..237.
once('static int save_valid_v2(void){', '''static void lc_save_roster(void){
 u8 bytes[LC_ROSTER_BYTES];unsigned i;
 if(lc_roster_encode(&lc_party,bytes,sizeof bytes)!=LC_OK)return;
 for(i=0;i<LC_ROSTER_BYTES;i++)SRAM[LC_ROSTER_SRAM+i]=bytes[i];
}
static void lc_restore_roster(void){
 u8 bytes[LC_ROSTER_BYTES];unsigned i;
 for(i=0;i<LC_ROSTER_BYTES;i++)bytes[i]=SRAM[LC_ROSTER_SRAM+i];
 if(lc_roster_decode(bytes,sizeof bytes,&lc_party)!=LC_OK){
  /* Missing/corrupt new party MUST NOT invalidate legacy character/quest save. */
  lc_roster_init(&lc_party);
  if(v9_bonded){
   u8 species=(u8)(1+v9_bond_type%5);
   if(lc_add_wild(&lc_party,species,0x11223344u+(u32)v9_bond_type)==LC_OK)
    lc_party.slots[0].bond=65;
  }
  lc_add_exported_profile();
 }
 lc_party_sel=lc_party.count?lc_party.active:0;
}
static int save_valid_v2(void){''')
# Close exact legacy v10 SRAM write function, extending only beyond previously used 0..237.
once('SRAM[237]=(u8)(0x72^SRAM[233]^SRAM[234]^SRAM[235]^SRAM[236]^SRAM[200]^SRAM[201]);}',
     'SRAM[237]=(u8)(0x72^SRAM[233]^SRAM[234]^SRAM[235]^SRAM[236]^SRAM[200]^SRAM[201]);\n lc_save_roster();}')

once('touch_mode=(!old_v3&&!old_v4&&((SRAM[168]&0xFE)==0xC0))?',
     'lc_restore_roster();\n touch_mode=(!old_v3&&!old_v4&&((SRAM[168]&0xFE)==0xC0))?')
# V2 legacy save extension: init_new_game already initializes party; no old bonded data existed.

once('static void save_game(void);', 'static void lc_save_roster(void);\nstatic void save_game(void);')

once('static void add_xp(u16 n){player_xp=(u16)clampi(player_xp+n,0,60000);level_check();}',
 '''static void add_xp(u16 n){
 player_xp=(u16)clampi(player_xp+n,0,60000);
 if(lc_party.count)(void)lc_reward_xp(&lc_party,lc_party.active,(u16)(1+n/2));
 level_check();
}''')

once('static void v9_bond(Enemy*e){\n if(e->elite || e->hp*2>e->maxhp){say("WEAKEN AN ORDINARY BEAST FIRST.");return;}\n v9_bonded=1;',
 '''static void v9_bond(Enemy*e){
 if(e->elite || e->hp*2>e->maxhp){say("WEAKEN AN ORDINARY BEAST FIRST.");return;}
 if(lc_party.count>=LC_ROSTER_CAP){say("ROSTER FULL. 12 FRIENDS MAX. KEEP YOUR BEAST FREE.");return;}
 {
  u8 species=(u8)(1+e->type%5);
  u32 seed=(u32)v9_rng ^ ((u32)(frame+1)<<16) ^ ((u32)e->x<<2) ^
    ((u32)e->y<<10) ^ (u32)kill_count;
  LcResult add=lc_add_wild(&lc_party,species,seed);
  if(add==LC_DUPLICATE)add=lc_add_wild(&lc_party,species,seed+1u);
  if(add!=LC_OK){say("CREATURE COULD NOT JOIN. NO PROGRESS LOST.");return;}
  lc_party.active=(u8)(lc_party.count-1);
  lc_party_sel=lc_party.active;
  lc_party.slots[lc_party.active].bond=65; /* actually bonded by prior battle */
 }
 v9_bonded=1;''')

# Replace single existing generic ally boost with real selected creature-specific game stats.
once('damage_enemy(&enemies[best],1+(qstate.burst>150)+(v9_bonded?1:0));',
 '''{
 int damage=1+(qstate.burst>150)+(v9_bonded?1:0);
 if(lc_party.count){
  const LcCreature *c=&lc_party.slots[lc_party.active];
  if(c->bond>=55){
   unsigned raw=lc_damage(c->attack,enemies[best].type*6+15,
                           c->affinity,enemies[best].type);
   damage=1+(int)(raw/16u)+(int)c->stage;
   if(damage>9)damage=9;
  }
 }
 damage_enemy(&enemies[best],damage);
}''')

once('if(v9_bonded)oam_set(42,cosmos.x-cam_x+6,cosmos.y-cam_y+1+(int)((frame>>3)&1),60+v9_bond_type*4,5+v9_bond_type,0);',
 '''if(v9_bonded||lc_party.count){
  u8 typ=v9_bond_type;
  if(lc_party.count)typ=(u8)(lc_party.slots[lc_party.active].species%EN_COUNT);
  oam_set(42,cosmos.x-cam_x+6,cosmos.y-cam_y+1+(int)((frame>>3)&1),60+typ*4,5+typ,0);
 }''')

# New page from existing COSMOS page R: add WITHOUT changing menu item numbering.
once('else if(pause_page==15){\n  ui_clear();ui_frame(0,19,15);',
 '''else if(pause_page==18){
  ui_clear();ui_frame(0,19,15);ui_text(2,1,"CREATURE COLLECTION",14);
  ui_text(2,2,"12-SLOT OFFLINE ROSTER",13);
  if(!lc_party.count)ui_text(2,5,"BOND WITH A WEAK WILD BEAST",15);
  for(i=0;i<lc_party.count;i++){
   int y=4+i;
   ui_text(2,y,lc_party_sel==i?">":" ",13);
   ui_text(4,y,lc_species_name(lc_party.slots[i].species),
    i==lc_party.active?14:15);
  }
  if(lc_party.count){
   LcCreature *c=&lc_party.slots[lc_party_sel];
   ui_text(18,4,"LV",13);ui_num(21,4,c->level,15);
   ui_text(18,5,"TR",13);ui_num(21,5,c->bond,15);
   ui_text(18,6,"AT",13);ui_num(21,6,c->attack,15);
   ui_text(18,7,"EV",13);ui_num(21,7,c->stage,15);
  }
#if defined(LC_IMPORTED_COMPANION)
  ui_text(18,8,"BB PIXEL",13);
  lc_draw_import_portrait(168,82);
#else
  ui_text(17,8,"NO BB ART",13);
#endif
  ui_text(2,17,"A SET L TRUST SEL EVOLVE",14);
  ui_text(2,18,"B BACK  SHARDS TRAIN BOND",13);
 }
 else if(pause_page==15){
  ui_clear();ui_frame(0,19,15);''')

once('if(pause_page==13&&(newk&KEY_L)){pause_page=17;return;}',
 '''if(pause_page==18){
  if(newk&KEY_UP&&lc_party.count){lc_party_sel=(u8)(lc_party_sel?lc_party_sel-1:lc_party.count-1);}
  if(newk&KEY_DOWN&&lc_party.count){lc_party_sel=(u8)(lc_party_sel+1>=lc_party.count?0:lc_party_sel+1);}
  if(newk&KEY_A&&lc_party.count){
   lc_party.active=lc_party_sel;
   v9_bonded=(u8)(lc_party.slots[lc_party.active].bond>=55);
   v9_bond_type=(u8)(lc_party.slots[lc_party.active].species%EN_COUNT);
   save_game();
  }
  if(newk&KEY_L&&lc_party.count){
   LcCreature *c=&lc_party.slots[lc_party_sel];
   if(inv[ITEM_SHARD]>=2){
    LcResult v=lc_bond(&lc_party,lc_party_sel,
       (u8)(c->species>=128?(c->species-128)%3:c->species%3),
       (u8)mini(100,65+player_level));
    if(v==LC_OK){
     inv[ITEM_SHARD]-=2;
     if(lc_party_sel==lc_party.active&&c->bond>=55)v9_bonded=1;
     say("TRAINING SUCCEEDED. YOUR TRUST GREW.");save_game();
    }else say("BOND TRIAL NOT READY.");
   }else say("TWO SHARDS ARE NEEDED TO TRAIN.");
  }
  if(newk&KEY_SELECT&&lc_party.count){
   u8 catalyst=(u8)(current_world==0&&current_room==7?1:
    current_world==2?2:current_world==4?3:0);
   if(lc_evolve(&lc_party,lc_party_sel,catalyst)==LC_OK){
    say("YOUR CREATURE EVOLVED. ITS POWERS CHANGED.");save_game();
   }else say("LEVEL OR BOND TOO LOW TO EVOLVE.");
  }
  if(newk&KEY_B){pause_page=2;set_world_palette(current_world);}
  return;
 }
 if(pause_page==2&&(newk&KEY_R)){pause_page=18;lc_party_sel=lc_party.active;return;}
 if(pause_page==13&&(newk&KEY_L)){pause_page=17;return;}''')

once('ui_text(2,17,"B BACK",13);}\n else if(pause_page==3)',
     'ui_text(2,16,"R CREATURE COLLECTION",14);ui_text(2,17,"B BACK",13);}\n else if(pause_page==3)')

once('make_all_tiles();make_obj_tiles();oam_hide_all();',
     'make_all_tiles();make_obj_tiles();lc_upload_import_art();oam_hide_all();')

once('for(i=0;i<5;i++)v9_loot[i]=0;\n current_world=0;',
     'for(i=0;i<5;i++)v9_loot[i]=0;\n lc_roster_init(&lc_party);lc_party_sel=0;lc_add_exported_profile();\n current_world=0;')

once('      if(current_room==10){v10_realm_choices|=4;v9_bonded=1;v9_bond_type=EN_BLOOM;}','      if(current_room==10){v10_realm_choices|=4;v9_bonded=1;v9_bond_type=EN_BLOOM;}\n      LcResult mercy_added=lc_recruit_mercy(v9_bond_type,current_world,current_room);')

once('add_xp(24);save_game();battle_notice="YOU BROKE THE CURSE WITHOUT KILLING THE GUARDIAN.";','add_xp(24);save_game();battle_notice=mercy_added==LC_FULL?"GUARDIAN SPARED. PARTY FULL.":"YOU BROKE THE CURSE WITHOUT KILLING THE GUARDIAN.";')

once('v9_bonded=1;v9_bond_type=EN_BLOOM;    cosmos.trust=','v9_bonded=1;v9_bond_type=EN_BLOOM;    LcResult mercy_added=lc_recruit_mercy(EN_BLOOM,current_world,current_room);    cosmos.trust=')

once('battle_notice="YOU HEALED THE GUARDIAN. IT WALKS WITH YOU.";','battle_notice=mercy_added==LC_FULL?"GUARDIAN HEALED. PARTY FULL.":"YOU HEALED THE GUARDIAN. IT WALKS WITH YOU.";')

p.write_text(s)
print('V10.1 integration patched exact verified V10 engine:',hashlib.sha256(s.encode()).hexdigest())
