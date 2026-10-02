/* Real native, player-controlled GAME-adapted optional literary sequences. */
static void g7_warp(int idx){
 if(idx<0||idx>=G7_COUNT)return;
 if(arc_progress<=G7_PARENT[idx]){
  say("FINISH THE CORRESPONDING ORIGINAL ATLAS CHAPTER FIRST.");return;
 }
 if(idx && !(g7_done&(1u<<(idx-1)))){
  say("RESTORE THE PREVIOUS ORIGINAL STORY THREAD FIRST.");return;
 }
 arc_room_change((u8)(G7_FIRST_ROOM+idx),31,52,
  "READ THE WESTERN STORY OATH. YOUR EARLIER PAGES REMAIN.");
}
static int g7_earned(int idx){
 if(arc_progress<=G7_PARENT[idx])return 0;
 switch(idx){
 case 0:return !!(story_flags&ST_HEART);
 case 1:return !!(story_flags&ST_CITY);
 case 2:return !!((story_flags&ST_CITY)&&(story_flags&ST_COURAGE));
 case 3:return arc_route>=1&&arc_route<=3;
 case 4:return arc_petals==3;
 case 5:return !!(story_flags&ST_DREAM);
 case 6:return !!((v10_relic&RF_HARMONY)&&(v10_relic&RF_PASSION));
 case 7:return !!(v10_relic&RF_GROVE_WRAITH);
 case 8:return !!((v10_relic&RF_EARTH)&&(story_flags&ST_ELEMENTS));
 case 9:return !!(v10_relic&RF_FESTIVAL);
 case 10:return !!((story_flags&ST_VOID)&&(story_flags&ST_CHRONO)&&g7_pillars==3);
 case 11:return !!((story_flags&ST_LATTICE)&&postgame&&ending>=1&&ending<=3&&g7_orbs==31);
 }return 0;
}
static void g7_answer(u16 keys){int choice=0,idx;
 if(!g7_pending||!G7_IS_ROOM){g7_pending=0;return;}
 idx=(int)current_room-G7_FIRST_ROOM;
 if(keys&KEY_LEFT)choice=1;else if(keys&KEY_UP)choice=2;
 else if(keys&KEY_RIGHT)choice=3;
 else if(keys&KEY_B){g7_pending=0;say("RETURN WHEN YOUR CHOICE IS READY.");return;}
 else return;
 g7_pending=0;
 if(g7_step[idx]!=1)return;
 g7_choice[idx]=(u8)choice;g7_step[idx]=2;
 say(choice==1?"CARE LEAVES A PATH BACK TO THOSE WHO NEED YOU.":
     choice==2?"YOUR COMPANIONS TAKE THEIR PLACES BESIDE YOU.":
     "THERE IS STILL SOMETHING NEW TO LEARN HERE.");
 tone(1210);save_game();
}
static void g7_node(int idx,int node){int first=(idx&1)?1:0;
 if(g7_done&(1u<<idx)){say("THIS STORY MEMORY IS ALREADY RESTORED.");return;}
 if(g7_step[idx]!=2){say("READ THE OATH AND DECIDE AT THE NORTH RUNE FIRST.");return;}
 if(g7_nodes[idx]&(1u<<node)){say("THE GLYPH REMEMBERS YOUR LAST VISIT.");return;}
 if((!g7_nodes[idx]&&node!=first)||
    (g7_nodes[idx]&&node==first)){say("FOLLOW THE CHAPTERS TWO DISTANT RUNES IN ORDER.");return;}
 if(idx==1&&node==first &&!inv[ITEM_POTION]){
  say("CARRY A REAL POTION FROM THE WOODLAND SUPPLY ROUTE.");return;
 }
 if(idx==6&&node!=first){if(!p4_material[2]){
   say("RESTORE A REAL ROOTLEAF BY EXPLORING OR CRAFTING.");return;}
   p4_material[2]--; /* Actual earned, single spent crafting resource. */
 }
 if(idx==8&&node==first &&!(v10_relic&RF_FESTIVAL)){
  say("EARN THE ORIGINAL DREAM FESTIVAL SEAL FIRST.");return;
 }
 g7_nodes[idx]|=(u8)(1u<<node);
 say(G7_NODE_LINE[idx]);tone((u16)(1160+idx*45+node*110));save_game();
}
static void g7_sigil_interact(int n){
 if(current_room!=G7_FIRST_ROOM+9||g7_step[9]!=2)return;
 if(g7_sigils&(1u<<n)){say("THIS SIGIL HAS BEEN REGISTERED.");return;}
 if(g7_sigils!=(u8)((1u<<n)-1u)){
  say("VALTARA THEN LIBRARY THEN CATACOMBS THEN OBSERVATORY.");return;
 }
 if(n==0&&!(story_flags&ST_VOID)){
  say("RECLAIM THE ORIGINAL VOIDWARD SIGIL FIRST.");return;}
 if(n==1&&!(story_flags&ST_CHRONO)){
  say("RECOVER THE REAL CHRONOHEART FIRST.");return;}
 if(n==2&&arc_anchors!=3){
  say("STABILIZE BOTH REAL CHRONO ANNEX TIME ANCHORS.");return;}
 if(n==3&&!(v10_relic&RF_HARMONY)){
  say("RESTORE THE DISTINCT CELESTIAL HARMONY CRYSTAL.");return;}
 g7_sigils|=(u8)(1u<<n);say("A PHYSICAL VOIDWARD SIGIL IS RESTORED.");
 tone((u16)(900+n*180));save_game();
}
static void g7_orb_interact(int n){
 static const char*const names[5]={"LIGHT","SOUND","ELEMENTS","TIME","UNITY"};
 if(current_room!=G7_FIRST_ROOM+11||g7_step[11]!=2)return;
 if(g7_orbs&(1u<<n)){say("THIS COSMIC ORB IS ALREADY RESONANT.");return;}
 if(g7_orbs!=(u8)((1u<<n)-1u)){
  say("FOLLOW LIGHT SOUND ELEMENTS TIME UNITY IN ORDER.");return;}
 if((n==0&&!(story_flags&ST_HEART))||
    (n==1&&!(v10_relic&RF_FESTIVAL))||
    (n==2&&!(story_flags&ST_ELEMENTS))||
    (n==3&&!(story_flags&ST_CHRONO))||
    (n==4&&arc_petals!=3)){
  say("THAT ORB NEEDS ITS ORIGINAL REALM PROOF FIRST.");return;
 }
 g7_orbs|=(u8)(1u<<n);
 say(names[n]);tone((u16)(1060+n*160));save_game();
}
static void g7_pillar_interact(void){
 if(current_room!=G7_FIRST_ROOM+10||g7_step[10]!=2)return;
 if(g7_pillars==3){say("THREE REAL BATTLE VICTORIES SECURED ALL PILLARS.");return;}
 if(g7_pillars==0){
   if(!(story_flags&ST_LATTICE)){say("RESTORE THE ORIGINAL LATTICE FIRST.");return;}
   g7_pillars=1;g7_pillar_kills=kill_count;
   say("PILLAR ONE STANDS. DEFEAT A REAL ENEMY, RETURN.");save_game();return;
 }
 if((u16)kill_count<=g7_pillar_kills){
   say("EARN A GENUINE ENCOUNTER VICTORY BEFORE THIS PILLAR.");return;}
 g7_pillars++;g7_pillar_kills=kill_count;
 say(g7_pillars==3?"ALL THREE PILLARS STAND. CLAIM THE EASTERN PROOF.":
   "THE NEXT PILLAR RISES. WIN ONE MORE REAL ENCOUNTER.");
 tone(1740);save_game();
}
static void g7_interact(u8 t){int i,idx;
 if(t==TR_G7_PORTAL){
  if(!ARC_IS_ROOM)return;
  idx=(int)current_room-ARC_FIRST_ROOM;
  for(i=0;i<G7_COUNT;i++)if(G7_PARENT[i]==idx){g7_warp(i);return;}
  return;
 }
 if(!G7_IS_ROOM)return;
 idx=(int)current_room-G7_FIRST_ROOM;
 if(t>=TR_G7_SIGIL_FIRST&&t<=TR_G7_SIGIL_LAST){g7_sigil_interact(t-TR_G7_SIGIL_FIRST);return;}
 if(t>=TR_G7_ORB_FIRST&&t<=TR_G7_ORB_LAST){g7_orb_interact(t-TR_G7_ORB_FIRST);return;}
 if(t==TR_G7_PILLAR){g7_pillar_interact();return;}
 if(t==TR_G7_EXIT){arc_room_change((u8)(ARC_FIRST_ROOM+G7_PARENT[idx]),31,52,
  "YOUR OLD MAP AND FELLOWSHIP REMAIN HERE.");return;}
 if(t==TR_G7_NEXT){
   if(idx+1>=G7_COUNT){say("THIS IS THE END OF THE OPTIONAL STORY CHRONICLE.");return;}
   if(!(g7_done&(1u<<idx))){say("COMPLETE THE EASTERN PROOF FIRST.");return;}
   g7_warp(idx+1);return;
 }
 if(t==TR_G7_CACHE){
  if(g7_cache&(1u<<idx)){say("THE CHAPTER CACHE WAS ALREADY FOUND.");return;}
  g7_cache|=(u16)(1u<<idx);
  inv[ITEM_SHARD]=(u8)mini(99,inv[ITEM_SHARD]+2);
  say("A CONCEALED STAR SHARD CACHE. TWO SHARDS EARNED.");save_game();return;
 }
 if(t==TR_G7_OATH){
  if(g7_step[idx]){say(G7_OATH[idx]);return;}
  if(idx&&!(g7_done&(1u<<(idx-1)))){
   say("COMPLETE THE PREVIOUS LIVING BOOK CHAPTER FIRST.");return;}
  g7_step[idx]=1;say(G7_OATH[idx]);tone(1220);save_game();return;
 }
 if(t==TR_G7_CHOICE){
  if(g7_step[idx]==1){g7_pending=1;say(G7_CHOICES[idx]);}
  else say(g7_step[idx]==0?"READ THE WESTERN OATH FIRST.":
     "YOUR INDIVIDUAL CHOICE IS ALREADY PRESERVED.");
  return;
 }
 if(t==TR_G7_NODE_A||t==TR_G7_NODE_B){g7_node(idx,t-TR_G7_NODE_A);return;}
 if(t==TR_G7_PROOF){
  if(g7_done&(1u<<idx)){say("YOUR COMPLETED CHAPTER REMAINS IN THE STORY BOOK.");return;}
  if(g7_step[idx]!=2||g7_nodes[idx]!=3){
   say("CHOOSE AT THE MIRROR AND WALK BOTH REAL CLUE STATIONS.");return;}
  if(!g7_earned(idx)) {say(G7_HINT[idx]);return;}
  if(idx==9&&g7_sigils!=15){say("ALL FOUR PHYSICAL VOID SIGILS MUST BE RESTORED.");return;}
  if(idx==10&&g7_pillars!=3){say("EARN TWO REAL BATTLES TO STABILIZE THREE PILLARS.");return;}
  if(idx==11&&g7_orbs!=31){say("RESTORE ALL FIVE DISTINCT ORBS IN ORDER.");return;}
  g7_done|=(u16)(1u<<idx);g7_step[idx]=3;
  add_xp((u16)(40+idx*7));credits=(u8)mini(255,credits+4+(idx&3));
  if(g7_choice[idx]==1)cosmos.trust=(u8)mini(255,cosmos.trust+7);
  if(g7_choice[idx]==3)inv[ITEM_SHARD]=(u8)mini(99,inv[ITEM_SHARD]+1);
  if(idx==6)p4_material[2]=(u8)mini(99,p4_material[2]+1);
  if(idx==11)say(ending==1?"OPEN: YOUR FIVE ORBS LEAVE NEW ROADS.":
      ending==2?"PRESERVE: THE ORBS GUARD WHAT STILL GROWS.":
      "WANDER: THE ORBS LIGHT PATHS BEYOND THE MAP.");
  else say("YOUR EARNED STORY MEMORY HAS BEEN PRESERVED.");
  tone(1800);save_game();return;
 }
}
