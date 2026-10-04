/* Optional V10.6 disjoint SRAM[5120..5151] CRC32; reject impossible progress.
 * Missing/bad new page does not overwrite older story/party/atlas/material/quests. */
static void g6_save(void){u8 b[G6_BYTES];unsigned i;u32 crc;
 for(i=0;i<G6_BYTES;i++)b[i]=0;
 b[0]='G';b[1]='A';b[2]='C';b[3]='6';b[4]=1;
 b[5]=g6_done;b[6]=g6_cache;
 for(i=0;i<G6_COUNT;i++){b[8+i]=g6_step[i];b[12+i]=g6_choice[i];b[16+i]=g6_nodes[i];}
 crc=lc_crc32(b,28);for(i=0;i<4;i++)b[28+i]=(u8)(crc>>(8*i));
 for(i=0;i<G6_BYTES;i++)SRAM[G6_SRAM+i]=b[i];
}
static void g6_restore(void){u8 b[G6_BYTES];unsigned i;u32 crc,got;int valid=1;
 for(i=0;i<G6_BYTES;i++)b[i]=SRAM[G6_SRAM+i];
 got=(u32)b[28]|((u32)b[29]<<8)|((u32)b[30]<<16)|((u32)b[31]<<24);
 g6_reset();crc=lc_crc32(b,28);
 if(b[0]!='G'||b[1]!='A'||b[2]!='C'||b[3]!='6'||b[4]!=1||
    b[5]>15||b[6]>15||b[7]!=0||crc!=got)valid=0;
 for(i=0;i<G6_COUNT;i++){
  u8 st=b[8+i],ch=b[12+i],done=(u8)((b[5]>>i)&1),nodes=b[16+i];
  u8 prefix=0,allowed=nodes<=7;int j,n=0;
  for(j=0;j<3;j++)if(nodes&(1u<<j))n++;
  for(j=0;j<n&&j<3;j++)prefix|=(u8)(1u<<G6_ORDER[i][j]);
  if(!allowed||nodes!=prefix||(st<2&&nodes!=0)||(st==3&&nodes!=7))valid=0;
  if(st>3||ch>3||(st<2&&ch!=0)||(st>=2&&ch==0)||
    (done!=(st==3))||(st && arc_progress<=G6_PARENT[i]))valid=0;
 }
 for(i=20;i<28;i++)if(b[i])valid=0;
 if(valid){g6_done=b[5];g6_cache=b[6];
  for(i=0;i<G6_COUNT;i++){g6_step[i]=b[8+i];g6_choice[i]=b[12+i];g6_nodes[i]=b[16+i];}
 }
 /* A newly loaded old save has no GAC6: return from otherwise unsupported
  * room 30..33 rather than allowing movement in a mismatched generic room. */
 if(G6_IS_ROOM){u8 idx=(u8)(current_room-G6_FIRST_ROOM);
  if(!valid||arc_progress<=G6_PARENT[idx]){
   current_world=0;current_room=2;current_layer=1;
   player.x=39*8;player.y=52*8;
  }
 }
}
