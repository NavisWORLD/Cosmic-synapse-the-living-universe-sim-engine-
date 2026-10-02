/* Disjoint private state extension; original GBA SRAM regions unchanged. */
static void g5_save(void){u8 b[G5_BYTES];u32 sum;unsigned i;
 for(i=0;i<G5_BYTES;i++)b[i]=0;
 b[0]='G';b[1]='Q';b[2]='S';b[3]='5';b[4]=1;b[5]=g5_active;
 b[6]=(u8)g5_start_kills;b[7]=(u8)(g5_start_kills>>8);
 for(i=0;i<4;i++)b[8+i]=(u8)(g5_complete>>(8*i));
 b[12]=g5_book_step;
 sum=lc_crc32(b,28);for(i=0;i<4;i++)b[28+i]=(u8)(sum>>(8*i));
 for(i=0;i<G5_BYTES;i++)SRAM[G5_SRAM+i]=b[i];
}
static void g5_restore(void){u8 b[G5_BYTES];u32 done,crc;unsigned i;
 g5_reset();for(i=0;i<G5_BYTES;i++)b[i]=SRAM[G5_SRAM+i];
 crc=(u32)b[28]|((u32)b[29]<<8)|((u32)b[30]<<16)|((u32)b[31]<<24);
 if(b[0]!='G'||b[1]!='Q'||b[2]!='S'||b[3]!='5'||b[4]!=1||b[5]>G5_NONE||
    lc_crc32(b,28)!=crc)return;
 done=(u32)b[8]|((u32)b[9]<<8)|((u32)b[10]<<16)|((u32)b[11]<<24);
 if((done&~0x1ffffu)||(done&~arc_guardians_mask)||b[12]>3||
    (b[5]<G5_NONE && (!(arc_guardians_mask&(1u<<b[5])) || (done&(1u<<b[5])))))return;
 for(i=13;i<28;i++)if(b[i])return;
 g5_active=b[5];g5_start_kills=(u16)b[6]|((u16)b[7]<<8);
 g5_complete=done;g5_book_step=b[12];
}
