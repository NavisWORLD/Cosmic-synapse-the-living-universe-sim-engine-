/* FIVE ADDITIONAL PLAYER-TRIGGERED NATIVE SIDE QUESTS, one per actual world hub.
 * These are explicitly new GAME ecosystem quests; NOT manuscript quotations.
 * Only validated story state or INVENTORY pays the shrine, no RnG-gated artifacts. */
static void eco_shrine_interact(void){
 int idx=(int)current_world-1;u32 seed;LcResult result;
 if(current_room!=0||current_layer!=1||idx<0||idx>=5)return;
 if(lc_sanctuary_mask&(1u<<idx)){
  say("THIS SANCTUARY IS ALIVE. THE BOND HAS BEEN RECORDED.");return;
 }
 if(lc_party.count>=LC_ROSTER_CAP){
  say("ROSTER FULL: RELEASE A WILD FRIEND FROM THE ROSTER FIRST.");return;
 }
 if(idx==0&&inv[ITEM_SHARD]<2){say("FORGE VOW: OFFER TWO STAR SHARDS.");return;}
 if(idx==1&&!(story_flags&ST_CHRONO)){
  say("TIDE OATH: RESTORE THE CHRONOHEART FIRST.");return;
 }
 if(idx==2&&inv[ITEM_CORE]==0&&cosmos.trust<160){
  say("ROOT RITE: OFFER A CORE OR EARN 160 COSMOS TRUST.");return;
 }
 if(idx==3&&!(story_flags&ST_VOID)){
  say("VOID MIRROR: FIND THE VOIDWARD SIGIL FIRST.");return;
 }
 if(idx==4&&(keys_found&7)!=7){
  say("SKY PACT: RECOVER ALL THREE AXIS KEYS FIRST.");return;
 }
 seed=0x53414e30u|(u32)(idx+1);
 result=lc_add_wild(&lc_party,(u8)(idx+1),seed);
 if(result!=LC_OK){say("THIS SPECIES IS ALREADY HERE. NOTHING SPENT.");return;}
 p4_record_species((u8)(idx+1));
 /* Only commit the consumable when the real roster addition succeeded. */
 if(idx==0)inv[ITEM_SHARD]-=2;
 if(idx==2&&inv[ITEM_CORE])inv[ITEM_CORE]--;
 lc_party.slots[lc_party.count-1].bond=70;
 lc_party.slots[lc_party.count-1].flags|=4u;
 lc_party.active=(u8)(lc_party.count-1);lc_party_sel=lc_party.active;
 lc_sanctuary_mask|=(u8)(1u<<idx);
 cosmos.trust=(u8)mini(255,cosmos.trust+8);
 inv[ITEM_SHARD]=(u8)mini(99,inv[ITEM_SHARD]+1);
 add_xp((u16)(20+idx*5));
 say(idx==0?"THE FORGELING WAKES IN THE REBUILT FORGE.":
     idx==1?"TIDEWISP JOINS YOU BESIDE THE CHRONOHEART.":
     idx==2?"ROOTKIN ANSWERS THE FORESTS KINDNESS.":
     idx==3?"VOIDMOTH EMERGES FROM THE MENDED MIRROR.":
       "SKYSPARK CHOOSES THE OPEN SKY.");
 tone((u16)(1360+idx*110));save_game();
}
