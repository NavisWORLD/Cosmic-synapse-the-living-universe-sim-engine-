#include <assert.h>
#include <stdio.h>
#include <string.h>
typedef unsigned char u8;
typedef unsigned int u32;
static volatile u8 memory[32768];
#define SRAM memory
#if __has_include("../LOST_COSMOS_V10_SOURCE/save_journal.h")
#include "../LOST_COSMOS_V10_SOURCE/save_journal.h"
#else
static void journal_commit(void) {}
static int journal_recover(void) {return 0;}
#endif
static u8 snapshot[32768];
int main(void) {
 memset((void*)memory,255,sizeof memory);
 for(int i=0;i<8192;i++) memory[i]=(u8)(i*7);
 journal_commit();
 memcpy(snapshot,(const void*)memory,sizeof memory);
 memory[12]=99; memory[1024]=11; memory[6144]=0;
 assert(journal_recover()==1);
 for(int i=0;i<8192;i++) assert(memory[i]==(u8)(i*7));
 /* A half-written active page restores the most recent complete snapshot. */
 memory[12]=77; memory[1024]=42; journal_commit();
 memory[12]=255; memory[1024]=1;
 assert(journal_recover()==1 && memory[12]==77 && memory[1024]==42);
 /* Corrupt newest bank: last older completed save survives. */
 memory[16384+123]^=1;
 assert(journal_recover()==1 && memory[12]==(u8)(12*7));
 /* Torn payload and every torn metadata prefix cannot advertise a commit. */
 for(int n=0;n<16;n++){
  memcpy((void*)memory,snapshot,sizeof memory);
  memory[12]=201;
  memory[24576+64+15]=0;
  for(int i=0;i<n;i++)memory[24576+64+i]=(u8)i;
  assert(journal_recover()==1 && memory[12]==(u8)(12*7));
 }
 memset((void*)memory,255,sizeof memory);
 memory[12]=7; assert(!journal_recover() && memory[12]==7);
 puts("PASS dual-bank save recovery: newest commit, corruption, torn metadata, legacy no-journal");
}
