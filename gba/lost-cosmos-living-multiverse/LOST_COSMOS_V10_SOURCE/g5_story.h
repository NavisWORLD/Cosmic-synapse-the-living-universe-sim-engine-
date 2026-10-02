/* Field-operated, non-automatic independent guardian quests. Revisit older atlas
 * rooms using R from Fellowship or Guardian Journal. Only one active oath at
 * a time; SELECT from Journal cancels, spending NO ingredients or history. */
static int g5_here(void){if(ARC_IS_ROOM)return (int)current_room-ARC_FIRST_ROOM;
 if(current_world==0&&current_room==ARC_EPILOGUE_ROOM)return 16;return -1;}
static int g5_pop16(u16 value){int count=0;while(value){count+=value&1;value>>=1;}return count;}
static int g5_has_creature(u8 species,u8 trust){int i;
 for(i=0;i<lc_party.count;i++)if(lc_party.slots[i].species==species&&lc_party.slots[i].bond>=trust)return 1;
 return 0;}
/* Check before ANY material debit; no partial crafting or overflow grants. */
static int g5_ready(int idx){switch(idx){
 case 0:return (u16)(kill_count-g5_start_kills)>=2;
 case 1:return (arc_secret_mask&(1u<<1))&&p4_material[4]>=1;
 case 2:return player_mp>=3&&p4_material[1]>=1;
 case 3:return p4_material[2]>=1&&inv[ITEM_POTION]>=1;
 case 4:return (u16)(kill_count-g5_start_kills)>=3;
 case 5:return p4_material[0]>=1&&p4_material[1]>=1;
 case 6:return (arc_secret_mask&(1u<<6))&&p4_material[3]>=1;
 case 7:return arc_petals==3&&p4_material[2]>=1;
 case 8:return arc_anchors==3&&p4_material[1]>=1;
 case 9:return lc_party.count&&lc_party.slots[lc_party.active].bond>=70;
 case 10:return p4_material[4]>=1&&inv[ITEM_ETHER]>=1;
 case 11:return (u16)(kill_count-g5_start_kills)>=1&&p4_material[3]>=1;
 case 12:return (v10_relic&RF_FESTIVAL)&&p4_material[4]>=1;
 case 13:return g5_has_creature(3,55)&&p4_material[2]>=1;
 case 14:return keys_found==7&&p4_material[0]>=1&&p4_material[3]>=1;
 case 15:return p4_material[0]&&p4_material[1]&&p4_material[2]&&p4_material[3]&&p4_material[4];
 case 16:return postgame&&g5_pop16(arc_secret_mask)>=4&&inv[ITEM_SHARD]>=3;
 }return 0;
}
static void g5_debit(int idx){switch(idx){
 case 1:p4_material[4]--;break;
 case 2:p4_material[1]--;break;
 case 3:p4_material[2]--;inv[ITEM_POTION]--;break;
 case 5:p4_material[0]--;p4_material[1]--;break;
 case 6:p4_material[3]--;break;
 case 7:p4_material[2]--;break;
 case 8:p4_material[1]--;break;
 case 10:p4_material[4]--;inv[ITEM_ETHER]--;break;
 case 11:p4_material[3]--;break;
 case 12:p4_material[4]--;break;
 case 13:p4_material[2]--;break;
 case 14:p4_material[0]--;p4_material[3]--;break;
 case 15:for(int i=0;i<5;i++)p4_material[i]--;break;
 case 16:inv[ITEM_SHARD]-=3;break;
 }}
static void g5_interact(u8 t){int idx=g5_here();u32 bit;
 if(idx<0||idx>=17)return;bit=1u<<idx;
 if(!(arc_guardians_mask&bit)){say("RESTORE THIS GUARDIANS ATLAS CHAPTER FIRST.");return;}
 if(idx==16&&!postgame){say("ALTAIR AWAITS YOUR OWN ENDING.");return;}
 if(g5_complete&bit){say(GUARDIAN_CHARACTERS[idx].after);return;}
 if(t==TR_G5_OATH){
  if(g5_active==idx){say(GUARDIAN_CHARACTERS[idx].preparation);return;}
  if(g5_active!=G5_NONE){say("FINISH OR CANCEL YOUR PREVIOUS GUARDIAN OATH.");return;}
  g5_active=(u8)idx;g5_start_kills=kill_count;
  say(GUARDIAN_CHARACTERS[idx].oath);save_game();return;
 }
 if(t==TR_G5_PROOF){
  if(g5_active!=idx){say("FIND THIS GUARDIANS WESTERN OATH STONE FIRST.");return;}
  if(!g5_ready(idx)){say(G5_HINT[idx]);return;}
  g5_debit(idx);g5_complete|=bit;g5_active=G5_NONE;g5_start_kills=0;
  add_xp((u16)(18+idx*3));credits=(u8)mini(255,credits+4+(idx%5));
  cosmos.trust=(u8)mini(255,cosmos.trust+2);
  say(GUARDIAN_CHARACTERS[idx].after);tone(1455);save_game();return;
 }
}
/* First-act novel-adapted optional three-place replay quest:
 * Oakwood archaeologist clues -> actual Cragstone rune approach ->
 * post-Heart Brindlemark return. These dialogues are newly authored GAME
 * paraphrases, no manuscript quotes, no false claim of full chapter closure. */
static void g5_book_interact(u8 t){
 if(t==TR_G5_BOOK_OAK){
  if(g5_book_step){say("RAVENSWOODS BROTHER LEFT HIS CLUES WITH THE TEMPLE.");return;}
  if(current_world!=0||current_room!=3)return;
  g5_book_step=1;say("AN ARCHAEOLOGISTS NOTES MARK FOUR TEMPLE RUNES. FOLLOW HIS CRAGSTONE TRAIL.");
  tone(1250);save_game();return;
 }
 if(t==TR_G5_BOOK_TEMPLE){
  if(current_world!=0||current_room!=4)return;
  if(!g5_book_step){say("THE RUNES ARE OLD. ASK RAVENSWOOD ABOUT HIS BROTHERS CLUES.");return;}
  if(g5_book_step>=2){say("THE FOUR RUNES STILL ANSWER SKY ROOT HEART STAR.");return;}
  g5_book_step=2;say("THE ARCHAEOLOGISTS CLUES MATCH THESE RUNES. SOLVE THE REAL FOUR-SEAL DOOR.");
  tone(1390);save_game();return;
 }
 if(t==TR_G5_BOOK_HOME){
  if(current_world!=0||current_room!=2)return;
  if(g5_book_step==3){say("BRINDLEMARK REMEMBERS THE HEART AND YOUR RETURN.");return;}
  if(g5_book_step!=2){say("BRINDLEMARK AWAITS NEWS OF RAVENSWOODS TEMPLE TRAIL.");return;}
  if(!(story_flags&ST_HEART)){say("RETURN AFTER THE FOUR RUNES AND MALAKARS HEART CHAMBER.");return;}
  g5_book_step=3;inv[ITEM_SHARD]=(u8)mini(99,inv[ITEM_SHARD]+3);
  cosmos.trust=(u8)mini(255,cosmos.trust+6);
  say("THE HEART RETURNS TO BRINDLEMARK. THE FELLOWSHIP HAS A HOME TO DEFEND.");
  tone(1670);save_game();return;
 }
}
static void g5_warp(u8 idx){if(idx>=17)return;
 if(!(arc_guardians_mask&(1u<<idx))||(idx==16&&!postgame)){
  say("RECRUIT THIS GUARDIAN BEFORE VISITING THEIR TRIAL.");return;
 }
 if(idx==16)arc_room_change(ARC_EPILOGUE_ROOM,31,52,"ALTAIRS RECORD IS IN THE EPILOGUE.");
 else arc_room_change((u8)(ARC_FIRST_ROOM+idx),31,52,"THE GUARDIANS PERSONAL TRIAL AWAITS.");
}
