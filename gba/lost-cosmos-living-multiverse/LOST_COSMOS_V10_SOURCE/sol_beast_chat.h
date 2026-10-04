/* Controller chat: local game dialogue, not model inference or medical advice.
 * No SRAM writes, XP grants, bond grants or private memory. */
static char sol_chat_input[32];
static const char*sol_chat_reply="HI ARIN. WHAT SHALL WE EXPLORE?";
static u8 sol_chat_pos,sol_chat_letter;
static int sol_chat_word(const char*s,const char*word){int i,j;for(i=0;s[i];i++){if(i&&s[i-1]!=' ')continue;for(j=0;word[j]&&s[i+j]==word[j];j++){}if(!word[j]&&(!s[i+j]||s[i+j]==' '))return 1;}return 0;}
static const char*sol_chat_answer(const char*s,const LcCreature*c){
 if(sol_chat_word(s,"HELP")||sol_chat_word(s,"WHERE")||sol_chat_word(s,"MAP"))return v11_signal_goal(v11_world());
 if(sol_chat_word(s,"EVOLVE")||sol_chat_word(s,"GROW")){if(c&&c->stage==2)return "WE REACHED MY FINAL FORM. OUR JOURNEY CONTINUES.";
 return c&&c->stage==1?"NEXT: LEVEL 28 AND BOND 80. A LOW EVOLUTION STAT NEEDS A HEARTWOOD SIGIL.":"FIRST: LEVEL 12 AND BOND 55. A LOW EVOLUTION STAT NEEDS A HEARTWOOD SIGIL.";}
 if(sol_chat_word(s,"TRAIN"))return "TRAIN IN PARTY WITH THREE SCRAP OR TWO CAMPAIGN SHARDS. WALK AND FIGHT TO GROW.";
 if(sol_chat_word(s,"REST")||sol_chat_word(s,"TIRED"))return "WE CAN TAKE A BREATHER. FIND THE CAMPFIRE ON YOUR LOCAL MAP.";
 if(sol_chat_word(s,"QUANTUM")||sol_chat_word(s,"SEED"))return "MY SPARK REPLAYS A RECORDED SEED. OUR ADVENTURE MAKES THE NEW MEMORIES.";
 if(sol_chat_word(s,"SAVE"))return "SYSTEM HAS THREE BATTERY SLOTS. KEEP YOUR SAVE AND COMPANION RECEIPT TOGETHER.";
 if(sol_chat_word(s,"LOVE")||sol_chat_word(s,"FRIEND"))return c&&c->bond>=55?"WE HAVE WALKED A LONG WAY TOGETHER. I AM READY FOR THE NEXT ISLAND.":"LET US GET TO KNOW EACH OTHER ON THE ROAD. ONE LITTLE STEP AT A TIME.";
 if(sol_chat_word(s,"PLAY"))return "RACE YOU TO THE NEXT BEACON. THEN WE CAN LOOK FOR A HIDDEN ECHO.";
 if(!s[0])return "TRY HI, HELP, EVOLVE, TRAIN, REST, SAVE OR QUANTUM.";
 if(sol_chat_word(s,"HI")||sol_chat_word(s,"HELLO"))return "HELLO ARIN. MY PAWS ARE READY. WHERE SHALL WE GO?";
 switch(c?c->seed%4:0){case 0:return "I HEARD YOU. LET US FIND SOMETHING SHINY TOGETHER.";case 1:return "A LITTLE WONDER. A LITTLE COURAGE. I WILL WALK WITH YOU.";case 2:return "THE NEXT ISLAND HAS A STORY. SHALL WE FOLLOW ITS SIGNAL?";default:return "I AM LISTENING. TRY HELP IF YOU WANT OUR NEXT ROAD GOAL.";}
}
static void sol_chat_open(void){sol_chat_input[0]=0;sol_chat_pos=sol_chat_letter=0;sol_chat_reply="HI ARIN. TRY HELP OR EVOLVE.";}
static void sol_chat_draw(void){int i;v11_header("CHAT // COMPANION");v11_short(2,3,v11_assign?v11_creature_name(v11_assign-1):v11_cosmos_label(),26,13);
 v11_lines(2,5,sol_chat_reply,26,4,15);v11_short(2,10,sol_chat_input,26,14);if(sol_chat_pos>26)v11_short(2,11,sol_chat_input+26,5,14);
 for(i=0;i<27;i++){char b[2]={i==26?' ':'A'+i,0};ui_text(3+(i%9)*3,12+i/9,b,i==sol_chat_letter?13:15);if(i==sol_chat_letter)ui_text(2+(i%9)*3,12+i/9,">",13);}
 ui_text(2,16,"A LETTER  L ERASE  B BACK",14);ui_text(2,17,"SELECT SEND // GAME DIALOGUE",13);
}
static void sol_chat_input_step(u16 k){
 if(k&KEY_LEFT)sol_chat_letter=(u8)wrapi(sol_chat_letter-1,27);if(k&KEY_RIGHT)sol_chat_letter=(u8)wrapi(sol_chat_letter+1,27);
 if(k&KEY_UP)sol_chat_letter=(u8)wrapi(sol_chat_letter-9,27);if(k&KEY_DOWN)sol_chat_letter=(u8)wrapi(sol_chat_letter+9,27);
 if(k&KEY_A&&sol_chat_pos<31){sol_chat_input[sol_chat_pos++]=sol_chat_letter==26?' ':'A'+sol_chat_letter;sol_chat_input[sol_chat_pos]=0;}
 if(k&KEY_L&&sol_chat_pos)sol_chat_input[--sol_chat_pos]=0;
 if(k&KEY_SELECT){LcCreature*c=v11_assign?&lc_party.slots[v11_assign-1]:0;sol_chat_reply=sol_chat_answer(sol_chat_input,c);sol_spark_chirp(c?c->identity:0x43534d53u);sol_chat_input[0]=0;sol_chat_pos=0;}
}
