/* V12.3 boss battle core (pure logic, no hardware: host-testable). The cartridge glue in
   living_world.h streams the chosen frame (one 2 KB 64x64 4bpp block) per tick with DMA3 and
   gives every boss its own OBJ palette slot.
   Sprite bosses (Cosmo's sheets): IDLE -> ATTACK (windup frames 0-1 telegraph, strike on frame 2,
   last frame held as the open window) -> ... ; each phase takes BB_PHASE_HP hits, then the GROW
   animation plays and the boss enters its next phase (bigger, faster attacks).
     Grumbleback v2.1: 3 phases, ends calm (hum_calm -> defeat_attuned: the kitten-crown moment).
     Forest Guardian:  2 phases, ends with defeat.
   Guardian Statues (Ruined Citadels hazard, CHANGES_canon.md; Cosmo's 58-frame sheet + lane art):
   no HP to hit. Three 32 px lanes. Each sweep follows Cosmo's timing hints (60 fps): warning dim 12f,
   warn 36f (24f in phase 3), statue windup 12f, imminent 8f, swing 12f (hitbox live on its last 9f),
   afterimage 8f, recovery 12f = 100f (1.67 s). Warning before the first live frame: 71f (59f in
   phase 3), always >= 40f. Phase 1 sweeps one lane, phase 2 sweeps two non-adjacent lanes, phase 3
   any two lanes; one lane is always safe. 3 phases x 5 sweeps, grow animations between, then defeat.
   Controls: LEFT/RIGHT dodge (sprite bosses) or change lane (statues), A strike in the open window. */
#ifndef BOSS_BATTLE_H
#define BOSS_BATTLE_H
enum{BB_GRUMBLEBACK=0,BB_GUARDIAN=1,BB_STATUES=2,BB_KINDS=3};
enum{BBS_IDLE=0,BBS_ATTACK,BBS_GROW,BBS_FINALE,BBS_LANES,BBS_WIN,BBS_LOSE};
#define BB_PHASE_HP 3
#define BB_ZHP 6
typedef struct{u8 kind,state,phase,nphases,hp,zhp,anim,afr,finale,dodge,struck,hit_ok,lane,swing,sweeps,lanes_mask;
 u16 tick,timer,frame,prev_frame;u32 rng;
 u16 hits_landed,hits_taken,dodges,grows,anims_played,frame_changes,sweeps_done;u8 pad_[2];}BossBattle;
typedef struct{u8 first,count,div,loop;}BBAnim;
/* phase tables, indices into the V12_BOSS_*_ANIM lists (v12_boss.h) */
static const u8 BB_IDLE[3][3]={{0,4,8},{0,4,0},{0,3,8}};
static const u8 BB_ATK[2][3][2]={{{1,2},{5,6},{9,10}},{{1,2},{5,6},{0,0}}};
static const u8 BB_GROW[3][2]={{3,7},{3,0},{2,7}};
static const u8 BB_FIN[3][2]={{11,12},{7,7},{10,10}};
#define BB_ST_SWEEP 6
static const u8 BB_ST_LEN[7]={12,36,12,8,12,8,12}; /* dim warn windup imminent swing after recovery */
static const u8 BB_NPH[3]={3,2,3};
static u32 bb_rand(BossBattle*b){u32 x=b->rng?b->rng:0x2545F491u;x^=x<<13;x^=x>>17;x^=x<<5;b->rng=x;return x;}
static const BBAnim*bb_anims(int kind);
static void bb_play(BossBattle*b,int a){b->anim=(u8)a;b->afr=0;b->tick=0;b->anims_played++;b->struck=0;b->hit_ok=0;}
static int bb_anim_done(BossBattle*b){const BBAnim*A=bb_anims(b->kind)+b->anim;return !A->loop&&b->afr>=A->count-1&&b->tick>=A->div;}
static int bb_stage_len(BossBattle*b){return b->swing==1&&b->phase==2?24:BB_ST_LEN[b->swing];}
static void bb_lane_next(BossBattle*b){u32 r=bb_rand(b);int l=(int)(r%3u);
 b->swing=0;b->struck=0;b->timer=(u16)bb_stage_len(b);
 if(b->phase==0)b->lanes_mask=(u8)(1u<<l);
 else if(b->phase==1)b->lanes_mask=(u8)((r>>4)&1?5:(1u<<l));          /* two lanes only as 0+2 */
 else b->lanes_mask=(u8)(7u&~(1u<<l));                                 /* any two, lane l safe */}
static void bb_start(BossBattle*b,int kind,u32 seed){int i;u8*p=(u8*)b;for(i=0;i<(int)sizeof *b;i++)p[i]=0;
 b->kind=(u8)kind;b->rng=seed|1u;b->nphases=BB_NPH[kind];b->hp=BB_PHASE_HP;b->zhp=BB_ZHP;b->prev_frame=0xFFFF;b->lane=1;
 if(kind==BB_STATUES){b->state=BBS_LANES;b->sweeps=5;bb_play(b,BB_IDLE[2][0]);bb_lane_next(b);}
 else{b->state=BBS_IDLE;bb_play(b,BB_IDLE[kind][0]);b->timer=90;}}
/* one tick; dir = -1/0/+1 (new LEFT/RIGHT press), a = new A press */
static void bb_step(BossBattle*b,int dir,int a){int i;
 if(b->state==BBS_WIN||b->state==BBS_LOSE)return;
 if(b->kind==BB_STATUES&&b->state==BBS_LANES){const BBAnim*A;
  if(dir<0&&b->lane>0)b->lane--;if(dir>0&&b->lane<2)b->lane++;
  A=bb_anims(b->kind)+b->anim;if(++b->tick>=A->div){b->tick=0;if(b->afr+1<A->count)b->afr++;else if(A->loop)b->afr=0;else b->tick=A->div;}
  if(b->timer)b->timer--;
  if(b->swing==4&&b->timer<9&&!b->struck&&(b->lanes_mask&(1u<<b->lane))){b->struck=1;if(b->zhp)b->zhp--;b->hits_taken++;if(!b->zhp){b->state=BBS_LOSE;return;}}
  if(!b->timer){
   if(b->swing==4&&!b->struck)b->dodges++;
   if(b->swing<6){b->swing++;b->timer=(u16)bb_stage_len(b);
    if(b->swing==2){bb_play(b,BB_ST_SWEEP);}                          /* telegraph eyes + windup */
    if(b->swing==6){bb_play(b,BB_IDLE[2][b->phase]);}}
   else{b->sweeps_done++;
    if(--b->sweeps==0){b->grows++;b->lanes_mask=0;
     if(b->phase+1<b->nphases){b->state=BBS_GROW;bb_play(b,BB_GROW[2][b->phase]);}
     else{b->state=BBS_FINALE;b->finale=0;bb_play(b,BB_FIN[2][0]);}}
    else bb_lane_next(b);}}
  b->frame=(u16)((bb_anims(b->kind)+b->anim)->first+b->afr);return;}
 {const BBAnim*A=bb_anims(b->kind)+b->anim;
  if(dir)b->dodge=20;else if(b->dodge)b->dodge--;
  if(++b->tick>=A->div){b->tick=0;if(b->afr+1<A->count)b->afr++;else if(A->loop)b->afr=0;else b->tick=A->div;}
  b->frame=(u16)(A->first+b->afr);
  switch(b->state){
   case BBS_IDLE:if(b->timer)b->timer--;else{b->state=BBS_ATTACK;bb_play(b,BB_ATK[b->kind][b->phase][bb_rand(b)&1]);b->timer=0;}break;
   case BBS_ATTACK:
    if(b->afr>=2&&!b->struck){b->struck=1;if(b->dodge){b->dodges++;}else{if(b->zhp)b->zhp--;b->hits_taken++;}if(!b->zhp){b->state=BBS_LOSE;return;}}
    if(bb_anim_done(b)){if(!b->hit_ok){b->hit_ok=1;b->timer=36;}   /* open window: last frame held */
     if(a&&b->hit_ok==1){b->hit_ok=2;b->hits_landed++;if(--b->hp==0){
       if(b->phase+1<b->nphases){b->state=BBS_GROW;bb_play(b,BB_GROW[b->kind][b->phase]);b->grows++;}
       else{b->state=BBS_FINALE;b->finale=0;bb_play(b,BB_FIN[b->kind][0]);}break;}}
     if(b->timer)b->timer--;else{b->state=BBS_IDLE;bb_play(b,BB_IDLE[b->kind][b->phase]);b->timer=(u16)(90-b->phase*20);}}
    break;
   case BBS_GROW:if(bb_anim_done(b)){b->phase++;b->hp=BB_PHASE_HP;bb_play(b,BB_IDLE[b->kind][b->phase]);
     if(b->kind==BB_STATUES){b->state=BBS_LANES;b->sweeps=5;bb_lane_next(b);}else{b->state=BBS_IDLE;b->timer=60;}}break;
   case BBS_FINALE:if(bb_anim_done(b)){if(!b->finale&&BB_FIN[b->kind][1]!=BB_FIN[b->kind][0]){b->finale=1;bb_play(b,BB_FIN[b->kind][1]);}
     else{b->timer++;if(b->timer>60)b->state=BBS_WIN;}}break;}
  b->frame=(u16)((bb_anims(b->kind)+b->anim)->first+b->afr);}}
/* returns 1 when the shown frame changed since the last call (the caller streams it) */
static int bb_take_frame(BossBattle*b){if(b->frame==b->prev_frame)return 0;b->prev_frame=b->frame;b->frame_changes++;return 1;}
#endif
