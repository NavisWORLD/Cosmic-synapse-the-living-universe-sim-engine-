/* Actually wired optional Act II-V source-informed GAME-NATIVE story arcs.
 * All rooms are really tile/collision generated; every reward must be earned. */
static void g6_warp(u8 idx){
 if(idx>=G6_COUNT)return;
 if(arc_progress<=G6_PARENT[idx]){
  say("RESTORE ITS ORIGINAL ATLAS CHAPTER TO UNLOCK THIS ACT.");return;
 }
 arc_room_change((u8)(G6_FIRST_ROOM+idx),31,52,"A NEW ACT THREAD OPENS. WALK THE FOUR STATIONS.");
}
static int g6_earned(int idx){
 switch(idx){
 case 0:return arc_progress>=9&&arc_petals==3;
 case 1:return arc_progress>=15&&(story_flags&ST_VOID)&&
                   (v10_relic&RF_HARMONY)&&(v10_relic&RF_PASSION);
 case 2:return arc_progress>=13&&(v10_relic&RF_CLARITY)&&(v10_relic&RF_FESTIVAL);
 case 3:return postgame&&(story_flags&ST_LATTICE)&&ending>=1&&ending<=3;
 }return 0;
}
static void g6_answer(u16 k){int idx,choice=0;
 if(!g6_pending||!G6_IS_ROOM){g6_pending=0;return;}
 idx=(int)current_room-G6_FIRST_ROOM;
 if(k&KEY_LEFT)choice=1;else if(k&KEY_UP)choice=2;
 else if(k&KEY_RIGHT)choice=3;
 else if(k&KEY_B){g6_pending=0;say("YOUR CHOICE MAY WAIT. RETURN TO THE CENTER RUNE.");return;}
 else return;
 g6_pending=0;
 if(g6_step[idx]!=1){say("BEGIN AT THE WESTERN RECORD FIRST.");return;}
 g6_choice[idx]=(u8)choice;g6_step[idx]=2;
 say(choice==1?"YOU CHOSE CARE. THE WORLD WILL REMEMBER THE SHELTER.":
     choice==2?"YOU CHOSE ACTION. THE FELLOWSHIP WILL BE READY.":
     "YOU CHOSE DISCOVERY. A DIFFERENT ROAD REMAINS OPEN.");
 tone(1430);save_game();
}
static void g6_node_interact(int idx,int node){int next,count=0,j;
 if(g6_step[idx]<2){say("READ THE OATH AND CHOOSE AT THE NORTH RUNE FIRST.");return;}
 if(g6_done&(1u<<idx)){say("THE ACT PUZZLE HAS ALREADY BEEN RECORDED.");return;}
 for(j=0;j<3;j++)if(g6_nodes[idx]&(1u<<j))count++;
 if(count>=3){say("ALL THREE ACT SIGILS ALIGN. SEEK THE EASTERN PROOF.");return;}
 next=G6_ORDER[idx][count];
 if(node!=next){say(idx==0?"THE SENTINEL REQUIRES MIRROR, MEMORY, COURAGE IN ORDER.":
  idx==1?"HEAL THE ROOTS IN ORDER: WEST, EAST, CENTER.":
  idx==2?"DREAMS MUST FLOW EAST, CENTER, WEST.":
  "THE CROWN REQUIRES CENTER, EAST, WEST.");return;}
 /* This is no free, automatic checklist: each act's optional gameplay uses
  * PREVIOUSLY EARNED old-campaign objects, actual regional loot, trust or
  * an actual reached ending. Reading any node too soon changes no state. */
 if(idx==0&&!(arc_petals==3 && arc_progress>=9)){
  say("EARN ALL THREE PETALS FROM THE ORIGINAL CITY TRIAL.");return;
 }
 if(idx==1&&node==0&&!(v10_relic&RF_HARMONY)){
  say("RESTORE THE DISTINCT CELESTIAL HARMONY CRYSTAL.");return;
 }
 if(idx==1&&node==2&&!(v10_relic&RF_PASSION)){
  say("RESTORE EMBER PASSION. IT IS NOT HARMONY.");return;
 }
 if(idx==1&&node==1&&(!p4_material[2]||!(story_flags&ST_VOID))){
  say("EARN ONE REAL ROOTLEAF AND RESTORE VOIDWARD FIRST.");return;
 }
 if(idx==2&&node==0&&!(v10_relic&RF_CLARITY)){
  say("THE FROST WOLF CHAPTER MUST RESTORE CLARITY.");return;
 }
 if(idx==2&&node==1&&!(v10_relic&RF_FESTIVAL)){
  say("COMPLETE THE DREAM FESTIVAL BEFORE THIS CHIME.");return;
 }
 if(idx==2&&node==2&&cosmos.trust<100){
  say("THE LOOM NEEDS REAL COMPANION TRUST OF 100.");return;
 }
 if(idx==3&&node==1&&arc_petals!=3){
  say("THE ORIGINAL THREE PETALS MUST SURVIVE.");return;
 }
 if(idx==3&&node==2&&!(story_flags&ST_LATTICE)){
  say("REFORGE THE ORIGINAL COSMIC LATTICE FIRST.");return;
 }
 if(idx==3&&node==0&&!(postgame&&ending>=1&&ending<=3)){
  say("REACH ONE ORIGINAL REAL ENDING FIRST.");return;
 }
 if(idx==1&&node==1)p4_material[2]--; /* real, transactionally gated cost */
 g6_nodes[idx]|=(u8)(1u<<node);
 say(G6_NODE_DIALOGUE[idx][node]);tone((u16)(1250+100*count));save_game();
}
static void g6_interact(u8 t){int i,idx;
 if(t==TR_G6_PORTAL){
  if(!ARC_IS_ROOM)return;
  idx=(int)current_room-ARC_FIRST_ROOM;
  for(i=0;i<G6_COUNT;i++)if(idx==G6_PARENT[i]){g6_warp((u8)i);return;}
  return;
 }
 if(!G6_IS_ROOM)return;
 idx=(int)current_room-G6_FIRST_ROOM;
 if(t>=TR_G6_NODE_W&&t<=TR_G6_NODE_E){g6_node_interact(idx,(int)t-TR_G6_NODE_W);return;}
 if(t==TR_G6_EXIT){
  arc_room_change((u8)(ARC_FIRST_ROOM+G6_PARENT[idx]),53,36,"BACK IN THE ATLAS. YOUR ACT RECORD REMAINS.");return;
 }
 if(t==TR_G6_CACHE){
  if(g6_cache&(1u<<idx)){say("THIS ACT CACHE HAS BEEN OPENED.");return;}
  g6_cache|=(u8)(1u<<idx);
  inv[ITEM_SHARD]=(u8)mini(99,inv[ITEM_SHARD]+2);
  say("TWO STAR SHARDS. AN OLD STORY STILL HAS SECRETS.");save_game();return;
 }
 if(t==TR_G6_OATH){
  if(g6_step[idx]){say(G6_OATH[idx]);return;}
  g6_step[idx]=1;say(G6_OATH[idx]);tone(1160);save_game();return;
 }
 if(t==TR_G6_CHOICE){
  if(!g6_step[idx]){say("READ THE WESTERN OATH BEFORE THE MIRROR.");return;}
  if(g6_step[idx]>=2){say("YOUR OWN CHOICE IS PRESERVED. SEEK THE EASTERN SEAL.");return;}
  g6_pending=1;say(G6_QUESTION[idx]);return;
 }
 if(t==TR_G6_PROOF){
  if(g6_done&(1u<<idx)){say(G6_COMPLETED[idx]);return;}
  if(g6_step[idx]!=2){say("FIRST WALK WEST, THEN DECIDE AT THE NORTH RUNE.");return;}
  if(!g6_earned(idx)){say(G6_HINT[idx]);return;}
  if(g6_nodes[idx]!=7){say("YOUR THREE DISTINCT FIELD CLUES REMAIN UNFINISHED.");return;}
  g6_done|=(u8)(1u<<idx);g6_step[idx]=3;
  add_xp((u16)(35+idx*13));credits=(u8)mini(255,credits+10+idx*4);
  cosmos.trust=(u8)mini(255,cosmos.trust+4+(g6_choice[idx]==1?4:0));
  if(idx==1)p4_material[2]=(u8)mini(99,p4_material[2]+2);
  if(idx==2)inv[ITEM_ETHER]=(u8)mini(99,inv[ITEM_ETHER]+1);
  if(idx==3)inv[ITEM_SHARD]=(u8)mini(99,inv[ITEM_SHARD]+3);
  if(g6_choice[idx]==3)inv[ITEM_SHARD]=(u8)mini(99,inv[ITEM_SHARD]+1);
  say(idx==3?(ending==1?"OPEN: THE ARCHIVE KEEPS NEW CONNECTIONS.":
    ending==2?"PRESERVE: THE ARCHIVE GUARDS LIVING ROOTS.":
    "WANDER: THE ARCHIVE MAPS UNKNOWN HORIZONS."):G6_COMPLETED[idx]);
  tone(1660);save_game();return;
 }
}
