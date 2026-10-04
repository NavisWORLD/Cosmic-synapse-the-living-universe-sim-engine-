/* Independent 32-byte CRC32 SRAM page: old 0..237 and LCR1 1024..1275 untouched. */
static void arc_reset(void){
 arc_progress=arc_solved=arc_boss_done=arc_pending=arc_route=arc_ally=0;
 arc_secret_mask=arc_mercy_mask=0;arc_guardians_mask=0;arc_petals=arc_anchors=0;lc_sanctuary_mask=0;
}
static void arc_save(void){u8 b[ARC_SRAM_BYTES];unsigned i;u32 sum;
 for(i=0;i<ARC_SRAM_BYTES;i++)b[i]=0;
 b[0]='A';b[1]='R';b[2]='C';b[3]='2';
 b[4]=arc_progress;b[5]=arc_solved;b[6]=arc_boss_done;b[7]=arc_route;
 b[8]=(u8)arc_secret_mask;b[9]=(u8)(arc_secret_mask>>8);
 b[10]=(u8)arc_mercy_mask;b[11]=(u8)(arc_mercy_mask>>8);
 b[12]=(u8)arc_guardians_mask;b[13]=(u8)(arc_guardians_mask>>8);
 b[14]=(u8)(arc_guardians_mask>>16);b[15]=(u8)(arc_guardians_mask>>24);
 b[16]=arc_ally;b[17]=arc_petals;b[18]=arc_anchors;
 b[19]=lc_sanctuary_mask; /* NEW V10.3, old ARC2 stored 0 here */
 sum=lc_crc32(b,28);
 b[28]=(u8)sum;b[29]=(u8)(sum>>8);b[30]=(u8)(sum>>16);b[31]=(u8)(sum>>24);
 for(i=0;i<ARC_SRAM_BYTES;i++)SRAM[ARC_SRAM+i]=b[i];
}
static void arc_restore(void){u8 b[ARC_SRAM_BYTES];unsigned i;u32 got;
 for(i=0;i<ARC_SRAM_BYTES;i++)b[i]=SRAM[ARC_SRAM+i];
 got=(u32)b[28]|((u32)b[29]<<8)|((u32)b[30]<<16)|((u32)b[31]<<24);
 arc_reset();
 if(b[0]=='A'&&b[1]=='R'&&b[2]=='C'&&b[3]=='2'&&
  lc_crc32(b,28)==got && b[4]<=ARC_STAGES && b[5]<=1 && b[6]<=1 &&
  b[7]<=3 && b[16]<17 && b[17]<=3 && b[18]<=3 && b[19]<=31 && !(b[15]&0xFE)){
  arc_progress=b[4];arc_solved=b[5];arc_boss_done=b[6];arc_route=b[7];
  arc_secret_mask=(u16)b[8]|((u16)b[9]<<8);
  arc_mercy_mask=(u16)b[10]|((u16)b[11]<<8);
  arc_guardians_mask=(u32)b[12]|((u32)b[13]<<8)|((u32)b[14]<<16)|((u32)b[15]<<24);
  arc_ally=b[16];arc_petals=b[17];arc_anchors=b[18];lc_sanctuary_mask=b[19];
  if(arc_ally && !(arc_guardians_mask&(1u<<arc_ally)))arc_ally=0;
  /* Reject an impossible future-region save without invalidating legacy state. */
  if(ARC_IS_ROOM && current_room-ARC_FIRST_ROOM>arc_progress){
   current_room=(u8)(ARC_FIRST_ROOM+(arc_progress?arc_progress-1:0));
   player.x=31*8;player.y=52*8;
  }
 }else if(ARC_IS_ROOM || (current_world==0&&current_room==ARC_EPILOGUE_ROOM)){
  current_room=2;player.x=39*8;player.y=52*8;
 }
}
