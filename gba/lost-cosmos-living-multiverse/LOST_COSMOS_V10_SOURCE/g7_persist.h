/* Exactly disjoint versioned SRAM[6144..6207] page for 12 optional chapters.
 * Older game files 0..237, 1024..1275, 2048..2079, 3072..3103,
 * 4096..4127 and 5120..5151 remain byte-for-byte untouched on restore. */
static void g7_save(void){u8 b[G7_SRAM_BYTES];unsigned i;u32 crc;
 for(i=0;i<G7_SRAM_BYTES;i++)b[i]=0;
 b[0]='G';b[1]='S';b[2]='C';b[3]='7';b[4]=1;
 b[5]=(u8)g7_done;b[6]=(u8)(g7_done>>8);
 b[7]=(u8)g7_cache;b[8]=(u8)(g7_cache>>8);
 for(i=0;i<G7_COUNT;i++){b[9+i]=g7_step[i];b[21+i]=g7_choice[i];b[33+i]=g7_nodes[i];}
 b[45]=g7_sigils;b[46]=g7_orbs;b[47]=g7_pillars;
 b[48]=(u8)g7_pillar_kills;b[49]=(u8)(g7_pillar_kills>>8);
 crc=lc_crc32(b,60);for(i=0;i<4;i++)b[60+i]=(u8)(crc>>(i*8));
 for(i=0;i<G7_SRAM_BYTES;i++)SRAM[G7_SRAM+i]=b[i];
}
static void g7_restore(void){u8 b[G7_SRAM_BYTES];unsigned i;int valid=1;
 u32 got,crc;u16 done,cache;
 for(i=0;i<G7_SRAM_BYTES;i++)b[i]=SRAM[G7_SRAM+i];
 done=(u16)b[5]|((u16)b[6]<<8);cache=(u16)b[7]|((u16)b[8]<<8);
 got=(u32)b[60]|((u32)b[61]<<8)|((u32)b[62]<<16)|((u32)b[63]<<24);
 crc=lc_crc32(b,60);
 if(b[0]!='G'||b[1]!='S'||b[2]!='C'||b[3]!='7'||b[4]!=1||
     crc!=got||done>4095||cache>4095||b[45]>15||b[46]>31||b[47]>3)valid=0;
 for(i=0;i<G7_COUNT;i++){int step=b[9+i],choice=b[21+i],nodes=b[33+i];
  int allowed=(i&1)?(nodes==0||nodes==2||nodes==3):(nodes==0||nodes==1||nodes==3);
  if(step>3||choice>3||!allowed||(step<2 && (nodes||choice))||
    (step>=2&&!choice)||(step==3&&nodes!=3)||
    (!!(done&(1u<<i))!=(step==3))||
    (step && arc_progress<=G7_PARENT[i])||
    (step && i && !(done&(1u<<(i-1)))))valid=0;
 }
 /* Unique appendix nodes must form strictly ordered prefixes, not spoofed bits. */
 if(!(b[45]==0||b[45]==1||b[45]==3||b[45]==7||b[45]==15)||
    !(b[46]==0||b[46]==1||b[46]==3||b[46]==7||b[46]==15||b[46]==31)||
    (b[45]&&!b[9+9])||(b[46]&&!b[9+11])||
    (b[47]&&!b[9+10])||
    (b[9+9]==3&&b[45]!=15)||
    (b[9+10]==3&&b[47]!=3)||
    (b[9+11]==3&&b[46]!=31))valid=0;
 for(i=50;i<60;i++)if(b[i])valid=0;
 g7_reset();
 if(valid){g7_done=done;g7_cache=cache;
  for(i=0;i<G7_COUNT;i++){g7_step[i]=b[9+i];g7_choice[i]=b[21+i];g7_nodes[i]=b[33+i];}
  g7_sigils=b[45];g7_orbs=b[46];g7_pillars=b[47];
  g7_pillar_kills=(u16)b[48]|((u16)b[49]<<8);
 }
 /* A legacy .sav has no GSC7: do not spawn into an accidental generic 64x64 room. */
 if(G7_IS_ROOM){int idx=(int)current_room-G7_FIRST_ROOM;
  if(!valid||arc_progress<=G7_PARENT[idx]||(idx&&! (g7_done&(1u<<(idx-1))))) {
   current_world=0;current_room=2;current_layer=1;
   player.x=39*8;player.y=52*8;
  }
 }
}
