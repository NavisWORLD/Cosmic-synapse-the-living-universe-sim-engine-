/* V12.2b host test for ecosystem_bridge.h: LCQ1 apply/reject and LCE1 export. */
#include <stdio.h>
#include <string.h>
typedef unsigned char u8; typedef signed char s8; typedef unsigned short u16; typedef signed short s16; typedef unsigned int u32; typedef signed int s32;
static u8 HOST_SRAM[32768];
#define SRAM HOST_SRAM
#define CQ_COUNT 39
static u8 cq_state[CQ_COUNT];
static struct{u8 trust,energy,curiosity,avoid;}cosmos={100,80,60,20};
#include "../LOST_COSMOS_V10_SOURCE/qseed.h"
#include "../LOST_COSMOS_V10_SOURCE/cst12.h"
#include "../LOST_COSMOS_V10_SOURCE/ecosystem_bridge.h"
int main(int argc,char**argv){Cst12 a,b;s32 L[3];int k,f=0,i;FILE*fp;
 if(argc<2)return 2;fp=fopen(argv[1],"rb");if(!fp||fread(HOST_SRAM,1,32768,fp)!=32768)return 2;fclose(fp);
 cst_seed_id(&a,0xDEADA969u,L);b=a;
 if(!eb_apply_lcq(&b,0xDEADA969u)){puts("FAIL LCQ1 not applied");f++;}
 printf("LCQ1 offsets applied:");for(k=0;k<CST_N;k++)printf(" %d",b.ch[k]-a.ch[k]);puts("");
 b=a;if(eb_apply_lcq(&b,0x7F9C2A03u)){puts("FAIL applied to wrong identity");f++;}
 HOST_SRAM[LCQ_SRAM+5]=0;b=a;if(eb_apply_lcq(&b,0xDEADA969u)){puts("FAIL accepted without SIMULATED flag");f++;}
 HOST_SRAM[LCQ_SRAM+5]=1;HOST_SRAM[LCQ_SRAM+12]^=1;b=a;if(eb_apply_lcq(&b,0xDEADA969u)){puts("FAIL accepted bad checksum");f++;}
 cq_state[0]=2;cq_state[5]=1;
 for(i=0;i<3000;i++){cst_lorenz(&a,&L[0],&L[1],&L[2]);cst_step(&a,2600,2000,2000,300,2400,L[0],L[1]);if(cst_heartbeat(&a))eb_on_beat(&a,0xDEADA969u);}
 fp=fopen(argv[2],"wb");fwrite(HOST_SRAM,1,32768,fp);fclose(fp);
 printf(f?"FAILED %d\n":"PASS: ecosystem bridge host test\n",f);return f!=0;}
