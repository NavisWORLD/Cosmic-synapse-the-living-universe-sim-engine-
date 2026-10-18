/* V12.2 CST-12: Cory Davis's 12-Dimensional Cosmic Synapse Theory core, in
   fixed point for the GBA.

   Port of the Beast Box site engine (NavisWORLD/The-beast-box-,
   apps/beastbox-cloud/lib/physics/cst-integrator.mjs: CST12 channels,
   lorenzStep with arousal-modulated rho and quantum_entropy forcing,
   coherenceFeedback, the Hebbian strength, stepCSTState, creatureMood and
   motionParams; lib/creatures3d/life-brain.mjs: modeWeights; and
   lib/companion/zeref-heart.mjs: the 830 ms heartbeat and moodBeatMs).

   HONEST LABEL: this is a CLASSICAL simulation. Each creature's 12 channels
   are SEEDED from its own window of the cartridge's recorded IBM quantum
   values (QSEED, frozen measured data) and its quantum_entropy channel is
   the Shannon entropy of that window. Nothing quantum runs on the GBA.

   Units: Q12 (4096 = 1.0) for every channel, one step per 60 Hz frame
   (dt = 1/60 s, folded into the integer gains below). Integer only: no
   floats, no divides in the per-frame step. Not saved: the whole state is
   re-derived from the creature's identity and QSEED window on entry, so the
   save format does not change.

   The JS step names 12 channels but only integrates valence, arousal,
   curiosity, avoid, quantum_entropy and phi_harmonics. The other six are
   seeded traits here (same as the site): frequency_mass slows needs and
   steps, geometric_phase is the starting phase, phase_velocity scales the
   phase rate, entanglement couples a creature's coherence to the group,
   dominance biases toward bold actions, spectral_flatness / audio_psi /
   av_coherence feed curiosity. Those trait mappings are this port's
   design choice, not something the site engine defines. */
#ifndef CST12_H
#define CST12_H
#define CST_ONE 4096
enum{CST_FREQ_MASS,CST_GEO_PHASE,CST_SPEC_FLAT,CST_PHASE_VEL,CST_ENTANGLE,CST_VALENCE,CST_AROUSAL,CST_DOMINANCE,CST_AUDIO_PSI,CST_PHI_HARM,CST_AV_COH,CST_QENTROPY,CST_N};
typedef struct{
 s16 ch[CST_N];                     /* the 12 CST channels, Q12 */
 s16 coh,chaos,instab,cur,reson,avoid; /* derived state, Q12 */
 s32 hebb;                          /* Hebbian strength, Q16 */
 u16 phase;                         /* 65536 = one turn */
 s16 joy,curio,fear,calm,mischief;  /* creatureMood(), Q12 */
 u16 beat_timer;                    /* heartbeat countdown, frames */
}Cst12;
static volatile u32 cst_steps=0;    /* read by the emulator test */
static volatile u16 cst_beats=0;
static int cst_c(int v){return v<0?0:v>CST_ONE?CST_ONE:v;}
static int cst_abs(int v){return v<0?-v:v;}
/* Seed from a 64-value QSEED window (5-bit values) and its entropy 0..100.
   Channel k = 0.25 + 0.5 * (10-bit value from window bytes 20+2k, 21+2k). */
static void cst_seed(Cst12*s,const u8*dna,int entropy100){int k;
 for(k=0;k<CST_N;k++){int v=((int)(dna[(20+2*k)&63]&31)<<5)|(dna[(21+2*k)&63]&31); /* 0..1023 */
  s->ch[k]=(s16)(1024+(v<<1));}
 s->ch[CST_QENTROPY]=(s16)cst_c(entropy100*41);
 s->coh=(s16)2458;s->chaos=(s16)819;s->instab=(s16)819;s->reson=2048;  /* site defaults .6 .2 .2 .5 */
 s->cur=(s16)((s->ch[CST_SPEC_FLAT]+s->ch[CST_AUDIO_PSI]+s->ch[CST_AV_COH]+2048)>>2);
 s->avoid=410;                                                      /* .1 */
 s->hebb=(s32)(((1024+(dna[60]&31)*26))<<4);                       /* .25 + up to .2 */
 s->phase=(u16)(s->ch[CST_GEO_PHASE]<<4);
 s->beat_timer=50;}
/* Seed from an identity alone: the same QSEED window and entropy rule as the
   Living World's lw_dna() (used by the first-person companion). L gets the
   Lorenz Q8 start values from window bytes 6..8. */
static void cst_seed_id(Cst12*s,u32 id,s32*L){u8 dna[64];int i,h[32],e=0;u32 off=((id*2654435761u)>>8)%(u32)(QSEED_LEN-64);
 static const u8 L2[65]={0,0,16,25,32,37,41,45,48,51,53,55,57,59,61,63,64,65,67,68,69,70,71,72,73,74,75,76,77,78,79,79,80,81,81,82,83,83,84,85,85,86,86,87,87,88,88,89,89,90,90,91,91,92,92,93,93,93,94,94,95,95,95,96,96};
 for(i=0;i<32;i++)h[i]=0;for(i=0;i<64;i++){dna[i]=(u8)(QSEED[off+i]&31u);h[dna[i]]++;}
 for(i=0;i<32;i++)if(h[i])e+=h[i]*(96-L2[h[i]]);e=(int)(((u32)e*100u)/(64u*80u));if(e>100)e=100;
 cst_seed(s,dna,e);L[0]=((s32)dna[6]-16)*64+1;L[1]=((s32)dna[7]-16)*64+1;L[2]=((s32)dna[8])*96+256;}
/* Lorenz with the CST couplings, on the existing Q8 state used by the ROM
   (sigma 10, rho 28*(1+0.3*(arousal-.5)), beta 8/3, x forced by
   2.0*(quantum_entropy-.5), dt 1/256). */
static void cst_lorenz(const Cst12*s,s32*px,s32*py,s32*pz){s32 x=*px,y=*py,z=*pz,dx,dy,dz,rho;
 rho=7168+((7168*((1229*(s->ch[CST_AROUSAL]-2048))>>12))>>12);
 dx=10*(y-x)+((s->ch[CST_QENTROPY]-2048)>>3);dy=((x*(rho-z))>>8)-y;dz=((x*y)>>8)-((z*683)>>8);
 x+=dx>>8;y+=dy>>8;z+=dz>>8;
 *px=x<-(60<<8)?-(60<<8):x>(60<<8)?(60<<8):x;*py=y<-(60<<8)?-(60<<8):y>(60<<8)?(60<<8):y;*pz=z<0?0:z>(90<<8)?(90<<8):z;}
/* One 60 Hz step of stepCSTState. Targets (Q12) come from the game world:
   valence, arousal, curiosity, fear. group_coh is the mean coherence of the
   other creatures (entanglement coupling). lx,ly are the Lorenz Q8 state. */
#define CST_K1 68   /* dt     */
#define CST_K2 137  /* dt*2   */
#define CST_K3 205  /* dt*3   */
static void cst_step(Cst12*s,int val_t,int aro_t,int cur_t,int fear_t,int group_coh,s32 lx,s32 ly){
 int lx01,ly01,t,coh;
 s->ch[CST_VALENCE]+=(s16)(((cst_c(val_t)-s->ch[CST_VALENCE])*CST_K3)>>12);
 s->ch[CST_AROUSAL]+=(s16)(((cst_c(aro_t)-s->ch[CST_AROUSAL])*CST_K3)>>12);
 s->cur+=(s16)(((cst_c(cur_t)-s->cur)*CST_K3)>>12);
 s->avoid+=(s16)(((cst_c(fear_t)-s->avoid)*CST_K3)>>12);
 lx01=cst_c(2048+((lx*1638)>>12));ly01=cst_c(2048+((ly*1311)>>12)); /* L.x/40, L.y/50 */
 t=cst_c((cst_abs(lx01-2048)*1434+cst_abs(ly01-2048)*614)>>10);
 s->chaos+=(s16)(((t-s->chaos)*CST_K2)>>12);
 t=cst_c((s->chaos*2048+s->avoid*1638+s->ch[CST_AROUSAL]*819)>>12);
 s->instab+=(s16)(((t-s->instab)*CST_K2)>>12);
 coh=cst_c(((CST_ONE-s->instab)*2048+s->ch[CST_VALENCE]*1229+s->ch[CST_PHI_HARM]*819)>>12);
 coh=cst_c(coh+((819*(cst_c((int)(s->hebb>>4))-1024))>>12));          /* coherenceFeedback */
 coh+=(int)(((group_coh-coh)*(s->ch[CST_ENTANGLE]>>2))>>12);          /* entanglement */
 s->coh+=(s16)(((cst_c(coh)-s->coh)*CST_K2)>>12);
 t=cst_c((s->coh*2458+s->ch[CST_VALENCE]*819)>>12);
 s->hebb+=(((s32)(t<<4)-s->hebb)*55)>>16;                               /* dt*.05 */
 t=cst_c((s->coh*2867+s->ch[CST_VALENCE]*1229)>>12);
 s->reson+=(s16)(((t-s->reson)*CST_K1)>>12);
 /* phi_harmonics breathes with resonance (site keeps it at .6) */
 s->ch[CST_PHI_HARM]+=(s16)((((2048+(s->reson>>1))-s->ch[CST_PHI_HARM])*CST_K1)>>14);
 s->phase=(u16)(s->phase+(((174*(CST_ONE+s->ch[CST_AROUSAL]))>>12)*(2048+s->ch[CST_PHASE_VEL])>>12));
 /* creatureMood */
 s->joy=(s16)cst_c((s->reson*2458+s->coh*1638)>>12);s->curio=(s16)cst_c(s->cur);s->fear=(s16)cst_c(s->avoid);
 s->calm=(s16)(CST_ONE-cst_c(s->instab));s->mischief=(s16)cst_c((s->chaos*2458+s->cur*1638)>>12);
 cst_steps++;}
/* motionParams: speed multiplier (.75 + mischief*.5) slowed by frequency_mass,
   turbulence (chaos*.9 + instability*.3) and smoothing from coherence. Q12. */
static int cst_speed(const Cst12*s){return ((3072+(s->mischief>>1))*(5120-(s->ch[CST_FREQ_MASS]>>1)))>>12;}
static int cst_turb(const Cst12*s){return cst_c((s->chaos*3686+s->instab*1229)>>12);}
static int cst_damp(const Cst12*s){return 2253+((s->coh*3686)>>12);} /* .55 + coh*.9 */
static const char*const CST_MOOD_NAMES[5]={"JOY","CURIOUS","FEAR","CALM","MISCHIEF"};
static int cst_top_mood(const Cst12*s){int v[5],i,b=0;v[0]=s->joy;v[1]=s->curio;v[2]=s->fear;v[3]=s->calm;v[4]=s->mischief;for(i=1;i<5;i++)if(v[i]>v[b])b=i;return b;}
/* zeref-heart.mjs: 72.29 bpm (830 ms = 50 frames) nudged by mood
   (joy .9, curiosity .95, fear .8, calm 1.1, mischief .85). Returns 1 on a beat. */
static int cst_heartbeat(Cst12*s){static const u8 f[5]={45,48,40,55,43};
 if(s->beat_timer>1){s->beat_timer--;return 0;}
 s->beat_timer=f[cst_top_mood(s)];cst_beats++;return 1;}
#endif
