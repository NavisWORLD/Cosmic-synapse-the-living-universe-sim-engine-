/* V12.2 host test for cst12.h: integer-only, deterministic, bounded, and
   seeded from the QSEED window (different identities -> different states). */
#include <stdio.h>
#include <string.h>
typedef unsigned char u8; typedef signed char s8; typedef unsigned short u16; typedef signed short s16; typedef unsigned int u32; typedef signed int s32;
#include "../LOST_COSMOS_V10_SOURCE/qseed.h"
#include "../LOST_COSMOS_V10_SOURCE/cst12.h"
static int fails=0;
#define CHECK(c,m) do{if(!(c)){printf("FAIL %s\n",m);fails++;}}while(0)
static void run(u32 id,Cst12*s,s32*L,int n,int fear){int i,k;cst_seed_id(s,id,L);
 for(i=0;i<n;i++){cst_lorenz(s,&L[0],&L[1],&L[2]);cst_step(s,2600,2000,2000,fear,2400,L[0],L[1]);cst_heartbeat(s);
  for(k=0;k<CST_N;k++)CHECK(s->ch[k]>=0&&s->ch[k]<=CST_ONE,"channel out of [0,1]");
  CHECK(s->coh>=0&&s->coh<=CST_ONE&&s->chaos>=0&&s->chaos<=CST_ONE,"derived out of range");}}
int main(void){Cst12 a,b,c;s32 La[3],Lb[3],Lc[3];
 run(0xDEADA969u,&a,La,20000,300);run(0xDEADA969u,&b,Lb,20000,300);
 CHECK(memcmp(&a,&b,sizeof a)==0&&memcmp(La,Lb,sizeof La)==0,"not deterministic");
 run(0x7F9C2A03u,&c,Lc,20000,300);
 CHECK(memcmp(&a,&c,sizeof a)!=0,"bb-deada969 and bb-7f9c2a03 seeded the same state");
 { Cst12 f;s32 Lf[3];run(0xDEADA969u,&f,Lf,3000,3800);CHECK(f.fear>a.fear,"fear input did not raise fear");CHECK(f.calm<=a.calm+200,"fear did not lower calm"); }
 printf("zeref: coh %d joy %d calm %d fear %d mischief %d qe %d beats %u\n",a.coh,a.joy,a.calm,a.fear,a.mischief,a.ch[CST_QENTROPY],(unsigned)cst_beats);
 printf(fails?"FAILED %d\n":"PASS: cst12 host test\n",fails);return fails!=0;}
