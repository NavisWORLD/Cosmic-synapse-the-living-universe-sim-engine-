/* V10.4 native creature combat + source-independent deterministic material/crafting.
   Game-only adaptation, never a claim about manuscript-origin science. No malloc.
   Caller includes after main world/party/atlas globals, before SRAM/battle functions. */
#ifndef LOST_COSMOS_PROGRESSION_V104_H
#define LOST_COSMOS_PROGRESSION_V104_H
static const char*const P4_RECIPE[4]={
 "FIELD POTION", "RESTORING ETHER", "GUARANTEED STAR SHARD", "COMPANION TRAINING"};
static const char*const P4_COSTS[4]={
 "ROOT 2 + 2 CREDITS", "TIDE 2 ORE 1 + 4 CREDITS",
 "VOID 1 SKY 1 + 2 CREDITS", "ROOT 1 TIDE 1 SKY 1"};
/* Index: EMBER ORE / TIDE GLASS / ROOTLEAF / VOID DUST / SKY ASH. */
static const u8 P4_RECIPE_MAT[4][5]={{0,0,2,0,0},{1,2,0,0,0},
 {0,0,0,1,1},{0,1,1,0,1}};
static const u8 P4_RECIPE_CREDITS[4]={2,4,2,0};
/* p4_save and p4_restore NEVER touch original V10, LCR1 or ARC2 SRAM pages. */
static void p4_reset(void){int i;for(i=0;i<5;i++)p4_material[i]=0;
 for(i=0;i<8;i++)p4_research[i]=0;
 p4_guard=p4_ward=p4_slow=p4_charges=p4_craft_sel=0;
}
static void p4_record_species(u8 species){if(species>=1&&species<=8){
 u8*v=&p4_research[species-1];if(*v<99)(*v)++;}}
static void p4_enemy_loot(Enemy*e){u8 index,species;
 /* Guaranteed after actual victory, not a random rare/progression gate. */
 switch(e->type){case EN_EMBER:index=0;break;
 case EN_TIDE:index=1;break;case EN_BLOOM:index=2;break;
 case EN_VOID:index=3;break;default:index=4;break;}
 if(p4_material[index]<99)p4_material[index]++;
 /* Each elite victory earns one additional world-appropriate rare resource. */
 if(e->elite){int bonus=(current_world==0&&current_room==8)?1:
   (current_world==0&&current_room==9)?0:
   (current_world==7&&current_room==10)?3:4;
  if(p4_material[bonus]<99)p4_material[bonus]++;}
 species=(current_world==0&&current_room==8&&e->elite)?6:
   (current_world==0&&current_room==9&&e->elite)?7:
   (current_world==7&&current_room==10&&e->elite)?8:eco_species_for_enemy(e->type);
 p4_record_species(species);
}
static int p4_craft(u8 recipe){int i;const char*err="GATHER MATERIALS FROM BATTLES FIRST.";
 if(recipe>=4)return 0;
 for(i=0;i<5;i++)if(p4_material[i]<P4_RECIPE_MAT[recipe][i]){say(err);return 0;}
 if(credits<P4_RECIPE_CREDITS[recipe]){say("NEED MORE QUEST CREDITS.");return 0;}
 if(recipe<3 && inv[recipe==0?ITEM_POTION:recipe==1?ITEM_ETHER:ITEM_SHARD]>=99){
  say("PACK FULL. NOTHING SPENT.");return 0;}
 if(recipe==3 &&(!lc_party.count || lc_party.slots[lc_party.active].bond>=100)){
  say("SELECT A CREATURE NEEDING TRUST FIRST.");return 0;}
 for(i=0;i<5;i++)p4_material[i]-=P4_RECIPE_MAT[recipe][i];
 credits=(u8)(credits-P4_RECIPE_CREDITS[recipe]);
 if(recipe==0)inv[ITEM_POTION]++;
 else if(recipe==1)inv[ITEM_ETHER]++;
 else if(recipe==2)inv[ITEM_SHARD]++;
 else{
  LcCreature*c=&lc_party.slots[lc_party.active];c->bond=(u8)mini(100,c->bond+12);
  if(c->species<128)cosmos.trust=(u8)mini(255,cosmos.trust+2);
 }
 say(recipe==0?"ROOTLEAF BREWED INTO A FIELD POTION.":
     recipe==1?"TIDE AND ORE BECAME AN ETHER.":
     recipe==2?"VOID AND SKY FORM A CERTAIN STAR SHARD.":
     "YOUR ACTIVE COMPANIONS TRUST HAS DEEPENED.");
 return 1;
}
/* Standalone independent 32-byte PRG4 page: header/version, 5 inventory counts,
   8 bestiary research counts; bytes 18..27 RESERVED ZERO, CRC32 last four. */
static void p4_save(void){u8 b[P4_SRAM_BYTES];u32 crc;unsigned i;
 for(i=0;i<P4_SRAM_BYTES;i++)b[i]=0;
 b[0]='P';b[1]='R';b[2]='G';b[3]='4';b[4]=1;
 for(i=0;i<5;i++)b[5+i]=p4_material[i];
 for(i=0;i<8;i++)b[10+i]=p4_research[i];
 crc=lc_crc32(b,28);for(i=0;i<4;i++)b[28+i]=(u8)(crc>>(i*8));
 for(i=0;i<P4_SRAM_BYTES;i++)SRAM[P4_SRAM+i]=b[i];
}
static void p4_restore(void){u8 b[P4_SRAM_BYTES];u32 crc;unsigned i;
 p4_reset();for(i=0;i<P4_SRAM_BYTES;i++)b[i]=SRAM[P4_SRAM+i];
 crc=(u32)b[28]|((u32)b[29]<<8)|((u32)b[30]<<16)|((u32)b[31]<<24);
 if(b[0]!='P'||b[1]!='R'||b[2]!='G'||b[3]!='4'||b[4]!=1||lc_crc32(b,28)!=crc)return;
 for(i=0;i<5;i++)if(b[5+i]>99)return;
 for(i=0;i<8;i++)if(b[10+i]>99)return;
 for(i=18;i<28;i++)if(b[i]!=0)return;
 for(i=0;i<5;i++)p4_material[i]=b[5+i];
 for(i=0;i<8;i++)p4_research[i]=b[10+i];
}
/* Forward declarations remain exactly scoped to the original engine. */
static void damage_enemy(Enemy*,int);
/* ALREADY-BONDED, active, gameplay-only species-specific and actually selectable.
   All eight unique actions execute different native effects; imported fictional game
   stat profiles use a bounded fallback (never access personal memory/signals). */
static int p4_ally_use(Enemy*e){LcCreature*c;u8 s;int dmg=0;
 if(!lc_party.count){battle_notice="BOND A CREATURE FIRST.";return 0;}
 if(!p4_charges){battle_notice="YOUR ALLY NEEDS TO REST.";return 0;}
 c=&lc_party.slots[lc_party.active];s=c->species;
 if(c->bond<35||!c->hp){battle_notice="THIS ALLY NEEDS TRUST OR HEALING.";return 0;}
 /* Never consume a turn when the selected support has no useful result. */
 if(s==3&&player.hp>=max_hp){battle_notice="ROOTKIN: YOU ARE ALREADY HEALTHY.";return 0;}
 p4_charges--;
 switch(s){
 case 1: dmg=2+(c->attack/8)+c->stage+(e->elite?2:0);
   battle_notice="FORGELING SHATTERS THE GUARD!";break;
 case 2: p4_guard=(u8)mini(3,p4_guard+2);
   player.hp=(u8)mini(max_hp,player.hp+1);
   battle_notice="TIDEWISP RAISES A TWO-HIT TIDAL GUARD!";break;
 case 3: player.hp=(u8)mini(max_hp,player.hp+3+c->stage);
   battle_notice="ROOTKIN RESTORES ARINS STRENGTH!";break;
 case 4: p4_guard=(u8)mini(3,p4_guard+1);p4_slow=1;dmg=2+c->stage;
   battle_notice="VOIDMOTH VANISHES AND MISDIRECTS!";break;
 case 5: dmg=3+2*c->stage+c->attack/8+(e->type==EN_CROWN?2:0);
   battle_notice="SKYSPARK FIRES A CHAIN LIGHTNING ARC!";break;
 case 6: dmg=1+c->stage;p4_guard=(u8)mini(3,p4_guard+1);p4_slow=1;
   battle_notice="FROST WOLF HOLDS THE ENEMY IN ICE!";break;
 case 7: player.hp=(u8)mini(max_hp,player.hp+2+c->stage);
   player_mp=(u8)mini(max_mp,player_mp+1);dmg=2+c->stage;
   battle_notice="PHOENIX FIRE MENDS AND STRIKES!";break;
 case 8: p4_ward=(u8)mini(3,p4_ward+2);dmg=1+c->stage;
   battle_notice="HOLLOW WRAITH CLEARS THE CURSE!";break;
 default:if(s>=LC_SPECIES_IMPORTED){dmg=1+c->attack/12+c->stage;
   p4_guard=(u8)mini(3,p4_guard+1);
   battle_notice="IMPORTED GAME COMPANION SUPPORTS ARIN!";}
  else{battle_notice="UNKNOWN CREATURE. TURN PRESERVED.";p4_charges++;return 0;}
 }
 (void)lc_reward_xp(&lc_party,lc_party.active,(u16)(2+c->stage));
 if(dmg>0){e->hurt=0;damage_enemy(e,dmg);}return 1;
}
#endif
