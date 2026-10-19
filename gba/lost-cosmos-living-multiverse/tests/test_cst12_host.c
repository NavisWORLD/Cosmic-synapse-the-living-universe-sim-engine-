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
 { /* V12.2b: emergent traits vary across creatures, drift, stay bounded, warm up gently */
  static const int T[8]={CST_FREQ_MASS,CST_GEO_PHASE,CST_SPEC_FLAT,CST_PHASE_VEL,CST_ENTANGLE,CST_DOMINANCE,CST_AUDIO_PSI,CST_AV_COH};
  static const char*N[8]={"freq_mass","geo_phase","spec_flat","phase_vel","entangle","dominance","audio_psi","av_coh"};
  u32 ids[8]={0xDEADA969u,0x7F9C2A03u,1,2,3,0x1234u,0xBEEFu,0xC0FFEEu};int k,j,i,nd=0;
  for(k=0;k<8;k++){int s0[8],mn=4096,mx=0,mnf=4096,mxf=0,maxjump=0,lo=4096,hi=0;
   for(j=0;j<8;j++){Cst12 q;s32 L[3];int prev;cst_seed_id(&q,ids[j],L);s0[j]=q.ch[T[k]];prev=s0[j];
    for(i=0;i<60000;i++){cst_lorenz(&q,&L[0],&L[1],&L[2]);cst_step(&q,2600-(i/7000)*200,2000+((i/5000)&1)*900,2000,(i>30000)?2500:300,2400,L[0],L[1]);
     if(i<60){int d=cst_abs(q.ch[T[k]]-prev);if(d>maxjump)maxjump=d;}prev=q.ch[T[k]];
     if(i>=1000){if(q.ch[T[k]]<lo)lo=q.ch[T[k]];if(q.ch[T[k]]>hi)hi=q.ch[T[k]];}}
    if(s0[j]<mn)mn=s0[j];if(s0[j]>mx)mx=s0[j];if(q.ch[T[k]]<mnf)mnf=q.ch[T[k]];if(q.ch[T[k]]>mxf)mxf=q.ch[T[k]];
    if(cst_abs(q.ch[T[k]]-s0[j])>40)nd++;
    CHECK(lo>=205&&hi<=3891,"trait left .05..95");}
   printf("%-9s seed spread %4d..%4d  after 60k frames %4d..%4d  range(after warmup) %4d..%4d  max 1st-sec step %d\n",N[k],mn,mx,mnf,mxf,lo,hi,maxjump);
   CHECK(maxjump<=8,"trait swung on boot");CHECK(mx>mn,"trait identical across creatures at seed");}
  printf("drifted >1%% from seed: %d of 64 creature-traits\n",nd);CHECK(nd>=40,"traits did not drift");}
 printf("zeref: coh %d joy %d calm %d fear %d mischief %d qe %d beats %u\n",a.coh,a.joy,a.calm,a.fear,a.mischief,a.ch[CST_QENTROPY],(unsigned)cst_beats);
 printf(fails?"FAILED %d\n":"PASS: cst12 host test\n",fails);return fails!=0;}
