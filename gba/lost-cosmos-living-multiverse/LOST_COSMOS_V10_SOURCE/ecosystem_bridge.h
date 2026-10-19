/* V12.2b Beast Box ecosystem bridge. The GBA has no network: both directions
   ride in free SRAM bytes of the normal 32 KiB save. Additive only; old ROMs
   ignore both records, and an absent/invalid record is a no-op.

   site -> game  LCQ1 at SRAM 25540..25599 (60 bytes), written by the site
   into the save next to LCX1/LCG1. Carries the beast's latest Rigetti growth
   state. The site's Rigetti loop runs on a QVM: it is SIMULATED, and the
   record must say so (flags bit0 = 1) or the cartridge rejects it.
     0  'LCQ1'   4  ver=1   5  flags (bit0 SIMULATED, required; others 0)
     6  u16 0    8  u32 public_id (must match the creature identity)
     12 s8[12]   per-channel offset, Q12 = value*16 (clamped to +-1024 = .25)
     24 u32 cycle (site loop cycle)   28 u16[4] counts 00/01/10/11
     36..55 zero   56 u32 FNV-1a-32 of bytes 0..55
   game -> site  LCE1 at SRAM 24704..24831 (128 bytes, previously empty),
   refreshed by the cartridge every 8 companion heartbeats.
     0  'LCE1'   4  ver=1   5  flags (bit0 LCQ1 applied)  6 u16 heartbeats
     8  u32 identity   12 u8[12] channels (Q12>>4)   24 u8 coh,joy,curio,fear,calm,mischief (>>4)
     30 u8 trust,energy,curiosity,avoid (game needs)   34 u8 quests touched   35 u8 mood ring head
     36 u8[32] mood history ring (0 empty, 1..5 = top mood+1, one per 8 heartbeats)
     68 u32 cst steps   72..123 zero   124 u32 FNV-1a-32 of bytes 0..123
   Nothing is printed or saved beyond these bytes. */
#ifndef ECOSYSTEM_BRIDGE_H
#define ECOSYSTEM_BRIDGE_H
#define LCQ_SRAM 25540u
#define LCE_SRAM 24704u
static u32 eb_fnv(volatile const u8*p,unsigned n){u32 h=2166136261u;unsigned i;for(i=0;i<n;i++){h^=p[i];h*=16777619u;}return h;}
static u32 eb_rd32(unsigned o){return (u32)SRAM[o]|((u32)SRAM[o+1]<<8)|((u32)SRAM[o+2]<<16)|((u32)SRAM[o+3]<<24);}
static void eb_wr32(unsigned o,u32 v){SRAM[o]=(u8)v;SRAM[o+1]=(u8)(v>>8);SRAM[o+2]=(u8)(v>>16);SRAM[o+3]=(u8)(v>>24);}
static volatile u8 eb_q_applied=0;
/* Adds the SIMULATED Rigetti growth offset to a freshly seeded state. */
static int eb_apply_lcq(Cst12*s,u32 id){unsigned g=LCQ_SRAM,i;
 if(SRAM[g]!='L'||SRAM[g+1]!='C'||SRAM[g+2]!='Q'||SRAM[g+3]!='1'||SRAM[g+4]!=1)return 0;
 if(SRAM[g+5]!=1||SRAM[g+6]||SRAM[g+7])return 0;
 for(i=36;i<56;i++)if(SRAM[g+i])return 0;
 if(eb_rd32(g+8)!=id||eb_fnv(SRAM+g,56)!=eb_rd32(g+56))return 0;
 for(i=0;i<CST_N;i++){int o=((int)(s8)SRAM[g+12+i])*16;o=o<-1024?-1024:o>1024?1024:o;s->ch[i]=(s16)cst_c(s->ch[i]+o);}
 eb_q_applied=1;return 1;}
static u8 eb_ring[32];static u8 eb_head=0;static u16 eb_beats=0;
static void eb_export(const Cst12*s,u32 id){unsigned e=LCE_SRAM,i;int q=0;
 for(i=0;i<CQ_COUNT;i++)if(cq_state[i])q++;
 SRAM[e]='L';SRAM[e+1]='C';SRAM[e+2]='E';SRAM[e+3]='1';SRAM[e+4]=1;SRAM[e+5]=eb_q_applied;SRAM[e+6]=(u8)eb_beats;SRAM[e+7]=(u8)(eb_beats>>8);
 eb_wr32(e+8,id);for(i=0;i<CST_N;i++)SRAM[e+12+i]=(u8)(cst_c(s->ch[i])>>4>255?255:cst_c(s->ch[i])>>4);
 SRAM[e+24]=(u8)(cst_c(s->coh)>>4>255?255:cst_c(s->coh)>>4);SRAM[e+25]=(u8)(s->joy>>4>255?255:s->joy>>4);SRAM[e+26]=(u8)(s->curio>>4>255?255:s->curio>>4);
 SRAM[e+27]=(u8)(s->fear>>4>255?255:s->fear>>4);SRAM[e+28]=(u8)(s->calm>>4>255?255:s->calm>>4);SRAM[e+29]=(u8)(s->mischief>>4>255?255:s->mischief>>4);
 SRAM[e+30]=(u8)cosmos.trust;SRAM[e+31]=(u8)cosmos.energy;SRAM[e+32]=(u8)cosmos.curiosity;SRAM[e+33]=(u8)cosmos.avoid;
 SRAM[e+34]=(u8)q;SRAM[e+35]=eb_head;for(i=0;i<32;i++)SRAM[e+36+i]=eb_ring[i];
 eb_wr32(e+68,(u32)cst_steps);for(i=72;i<124;i++)SRAM[e+i]=0;eb_wr32(e+124,eb_fnv(SRAM+e,124));}
static void eb_on_beat(const Cst12*s,u32 id){eb_beats++;if(eb_beats&7)return;eb_ring[eb_head&31]=(u8)(cst_top_mood(s)+1);eb_head=(u8)((eb_head+1)&31);eb_export(s,id);}
#endif
