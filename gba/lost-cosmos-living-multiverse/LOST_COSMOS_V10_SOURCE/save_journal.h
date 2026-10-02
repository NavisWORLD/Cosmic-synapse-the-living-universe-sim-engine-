/* Original V10.8 cartridge save journal. All historical offsets stay intact.
 * The primary 8 KiB page is snapshotted into alternating banks. A bank's
 * commit byte is written last, so cold boot can recover a complete save.
 * No allocation; no imported private data; 32 KiB SRAM only. */
#ifndef LC_SAVE_JOURNAL_H
#define LC_SAVE_JOURNAL_H
#define JOURNAL_BYTES 8192u
#define JOURNAL_META 24576u
static u32 journal_read32(unsigned o){
 return (u32)SRAM[o]|((u32)SRAM[o+1]<<8)|((u32)SRAM[o+2]<<16)|((u32)SRAM[o+3]<<24);
}
static void journal_write32(unsigned o,u32 v){
 for(unsigned i=0;i<4;i++)SRAM[o+i]=(u8)(v>>(8*i));
}
static u32 journal_crc(unsigned o){
 u32 c=0xffffffffu;
 for(unsigned i=0;i<JOURNAL_BYTES;i++){
  c^=SRAM[o+i];
  for(unsigned j=0;j<8;j++)c=(c>>1)^((0u-(c&1u))&0xedb88320u);
 }
 return c^0xffffffffu;
}
static int journal_bank_valid(unsigned b){
 unsigned m=JOURNAL_META+b*64;
 return SRAM[m]=='L'&&SRAM[m+1]=='C'&&SRAM[m+2]=='J'&&SRAM[m+3]=='8'&&
  SRAM[m+12]==1&&SRAM[m+13]==32&&SRAM[m+14]==0&&SRAM[m+15]==0xa8&&
  journal_read32(m+8)==journal_crc((b+1)*JOURNAL_BYTES);
}
static int journal_latest(void){
 int a=journal_bank_valid(0),b=journal_bank_valid(1);
 if(!a)return b?1:-1;if(!b)return 0;
 u32 d=journal_read32(JOURNAL_META+64+4)-journal_read32(JOURNAL_META+4);
 return (d&&d<0x80000000u)?1:0;
}
static int journal_recover(void){
 int b=journal_latest();if(b<0)return 0;
 unsigned src=(unsigned)(b+1)*JOURNAL_BYTES;
 for(unsigned i=0;i<JOURNAL_BYTES;i++)SRAM[i]=SRAM[src+i];
 return 1;
}
static void journal_commit(void){
 int latest=journal_latest();unsigned b=latest<0?0:((unsigned)latest^1u);
 unsigned m=JOURNAL_META+b*64,dst=(b+1)*JOURNAL_BYTES;
 u32 seq=latest<0?1:journal_read32(JOURNAL_META+(unsigned)latest*64+4)+1;
 SRAM[m+15]=0;
 for(unsigned i=0;i<JOURNAL_BYTES;i++)SRAM[dst+i]=SRAM[i];
 SRAM[m]='L';SRAM[m+1]='C';SRAM[m+2]='J';SRAM[m+3]='8';
 journal_write32(m+4,seq);journal_write32(m+8,journal_crc(dst));
 SRAM[m+12]=1;SRAM[m+13]=32;SRAM[m+14]=0;
 SRAM[m+15]=0xa8;
}
#endif
