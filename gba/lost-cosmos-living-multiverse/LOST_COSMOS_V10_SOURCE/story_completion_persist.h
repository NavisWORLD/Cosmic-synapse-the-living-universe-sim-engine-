#ifndef LC_COMPLETION_PERSIST_H
#define LC_COMPLETION_PERSIST_H
static void completion_save(void){u8 b[COMP_BYTES];int i;u32 crc;
 for(i=0;i<COMP_BYTES;i++)b[i]=0;
 b[0]='L';b[1]='C';b[2]='B';b[3]='8';b[4]=1;
 for(i=0;i<4;i++){b[8+i]=(u8)(completion_done>>(8*i));b[12+i]=(u8)(completion_seen>>(8*i));b[16+i]=(u8)(completion_cache>>(8*i));}
 for(i=0;i<24;i++){b[20+i]=completion_step[i];b[44+i]=completion_choice[i];b[68+i]=completion_sub[i];}
 b[92]=completion_guard;b[93]=completion_attack;
 crc=lc_crc32(b,124);for(i=0;i<4;i++)b[124+i]=(u8)(crc>>(8*i));
 for(i=0;i<COMP_BYTES;i++)SRAM[COMP_SRAM+i]=b[i];
}
static void completion_restore(void){u8 b[COMP_BYTES];int i,valid=1,ga=0,at=0;u32 got=0,done=0,seen=0,cache=0;
 for(i=0;i<COMP_BYTES;i++)b[i]=SRAM[COMP_SRAM+i];
 for(i=0;i<4;i++){got|=(u32)b[124+i]<<(8*i);done|=(u32)b[8+i]<<(8*i);seen|=(u32)b[12+i]<<(8*i);cache|=(u32)b[16+i]<<(8*i);}
 if(b[0]!='L'||b[1]!='C'||b[2]!='B'||b[3]!='8'||b[4]!=1||got!=lc_crc32(b,124)||done>0xffffffu||seen>0xffffffu||cache>0xffffffu)valid=0;
 for(i=5;i<8;i++)if(b[i])valid=0;
 for(i=94;i<124;i++)if(b[i])valid=0;
 for(i=0;i<24;i++){
  int st=b[20+i],choice=b[44+i];
  if(st>4||choice>3||b[68+i]>3||((done&(1u<<i)) && (st!=4||!choice))||(!(done&(1u<<i))&&choice)||
     (st&&i&&!(done&(1u<<(i-1))))||(i&& (done&(1u<<i))&&!(done&(1u<<(i-1)))))valid=0;
  if(choice){if(COMPLETION_CHOICES[i].reward[choice-1]==COMP_REWARD_GUARD)ga+=COMPLETION_CHOICES[i].amount[choice-1];
   if(COMPLETION_CHOICES[i].reward[choice-1]==COMP_REWARD_ATTACK)at+=COMPLETION_CHOICES[i].amount[choice-1];}
 }
 if(b[92]!=mini(4,ga)||b[93]!=mini(4,at))valid=0;
 completion_reset();
 if(valid){completion_done=done;completion_seen=seen;completion_cache=cache;
  for(i=0;i<24;i++){completion_step[i]=b[20+i];completion_choice[i]=b[44+i];completion_sub[i]=b[68+i];}
  completion_guard=b[92];completion_attack=b[93];
 }
 if(COMP_IS_ROOM && (!valid||!completion_available(current_room-COMPLETION_FIRST_ROOM))){
  current_world=0;current_room=2;current_layer=1;player.x=31*8;player.y=50*8;
 }
}
#endif
