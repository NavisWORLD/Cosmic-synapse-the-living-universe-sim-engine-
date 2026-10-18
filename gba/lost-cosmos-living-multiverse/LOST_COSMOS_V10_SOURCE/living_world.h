/* V12.0 LIVING WORLD. See living_world_state.h for the honest label and the
   save layout. Display: the whole VRAM, palettes, OAM, UI map and display
   registers are copied to EWRAM on entry and copied back on exit, so the
   top-down game resumes exactly as it was. */
#ifndef LIVING_WORLD_H
#define LIVING_WORLD_H
#ifndef HOST_QA
static u8 lw_vram_save[0x18000] __attribute__((section(".ewram"),aligned(4)));
static u16 lw_pal_save[512] __attribute__((section(".ewram"),aligned(4)));
static u16 lw_oam_save[512] __attribute__((section(".ewram"),aligned(4)));
static u16 lw_ui_save[1024] __attribute__((section(".ewram"),aligned(4)));
static u16 lw_io_save[14] __attribute__((section(".ewram"),aligned(4)));
#define LW_OBJ_TILES ((volatile u32*)0x06010000)
#define LW_REG16(a) (*(volatile u16*)(a))
#define LW_REG32(a) (*(volatile u32*)(a))
static const char*const LW_NAMES[LW_N]={"ZEREF","KAIRO","FROST","KITTEN","SHARDHOWL","VELVETCOIL"};
/* Zeref is bb-deada969. The other five are local cartridge identities for the
   website creature designs, not Beast Box guest IDs. */
static const u32 LW_IDS[LW_N]={0xDEADA969u,0x4B414952u,0x46524F53u,0x4B495454u,0x53484152u,0x56454C56u};
static const u32*const LW_CRE_TILES[LW_N]={v12_cre_zeref_tiles,v12_cre_kairo_tiles,v12_cre_frost_tiles,v12_cre_kitten_tiles,v12_cre_shardhowl_tiles,v12_cre_velvetcoil_tiles};
static const u16*const LW_CRE_PAL[LW_N]={v12_cre_zeref_pal,v12_cre_kairo_pal,v12_cre_frost_pal,v12_cre_kitten_pal,v12_cre_shardhowl_pal,v12_cre_velvetcoil_pal};
static const u32*const LW_COMP_TILES[LW_N]={v12_comp_zeref_tiles,v12_comp_kairo_tiles,v12_comp_frost_tiles,v12_comp_kitten_tiles,v12_comp_shardhowl_tiles,v12_comp_velvetcoil_tiles};
static const u16*const LW_COMP_PAL[LW_N]={v12_comp_zeref_pal,v12_comp_kairo_pal,v12_comp_frost_pal,v12_comp_kitten_pal,v12_comp_shardhowl_pal,v12_comp_velvetcoil_pal};
/* Cast gallery: same order as V12_CHARS (Zeref first; Zeref uses his creature art). */
static const u32*const LW_CHR_TILES[V12_CHAR_COUNT]={v12_cre_zeref_tiles,v12_chr_arin_tiles,v12_chr_mote_tiles,v12_chr_mote_linework_tiles,v12_chr_mote_wash_tiles,v12_chr_mote_still_here_tiles,v12_chr_traveler_tiles,v12_chr_hollis_tiles,v12_chr_edric_tiles,v12_chr_bryn_tiles,v12_chr_quillan_tiles,v12_chr_hesper_tiles,v12_chr_grumbleback_tiles,v12_chr_rime_tiles,v12_chr_cinderwake_tiles,v12_chr_thorne_tiles,v12_chr_sethra_tiles,v12_chr_malakar_tiles,v12_chr_counterfeit_tiles};
static const u16*const LW_CHR_PAL[V12_CHAR_COUNT]={v12_cre_zeref_pal,v12_chr_arin_pal,v12_chr_mote_pal,v12_chr_mote_linework_pal,v12_chr_mote_wash_pal,v12_chr_mote_still_here_pal,v12_chr_traveler_pal,v12_chr_hollis_pal,v12_chr_edric_pal,v12_chr_bryn_pal,v12_chr_quillan_pal,v12_chr_hesper_pal,v12_chr_grumbleback_pal,v12_chr_rime_pal,v12_chr_cinderwake_pal,v12_chr_thorne_pal,v12_chr_sethra_pal,v12_chr_malakar_pal,v12_chr_counterfeit_pal};
static const u8 LW_CHR_BIG[V12_CHAR_COUNT]={1,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0};
static int lw_streq(const char*a,const char*b){while(*a&&*a==*b){a++;b++;}return *a==*b;}
static int lw_item(const char*id){int i;for(i=0;i<V12_ITEM_COUNT;i++)if(lw_streq(V12_ITEMS[i].id,id))return i;return -1;}
static u32 lw_rand(LwBeast*b){u32 x=b->rng?b->rng:0x9E3779B9u;x^=x<<13;x^=x>>17;x^=x<<5;b->rng=x;return x;}
static void lw_copy32(volatile u32*d,const u32*s,int words){while(words--)*d++=*s++;}
static void lw_say(const char*a,const char*b){int n=0;while(a&&*a&&n<58)lw_msg[n++]=*a++;while(b&&*b&&n<58)lw_msg[n++]=*b++;lw_msg[n]=0;lw_msg_timer=180;}
/* ---------- DNA, stats ---------- */
static void lw_dna(LwBeast*b,u32 id){u32 off=(id*2654435761u)>>8;int i,h[32];
 off%= (QSEED_LEN-64);
 for(i=0;i<32;i++)h[i]=0;
 for(i=0;i<64;i++){b->dna[i]=(u8)(QSEED[off+i]&31u);h[b->dna[i]]++;}  /* 5-bit recorded values */
 /* Shannon entropy of the 64 recorded values over 32 bins, 0..5 bits -> 0..100,
    with an integer log2 table (x16). */
 {static const u8 L2[65]={0,0,16,25,32,37,41,45,48,51,53,55,57,59,61,63,64,65,67,68,69,70,71,72,73,74,75,76,77,78,79,79,80,81,81,82,83,83,84,85,85,86,86,87,87,88,88,89,89,90,90,91,91,92,92,93,93,93,94,94,95,95,95,96,96};
  int s=0;for(i=0;i<32;i++)if(h[i])s+=h[i]*(96-L2[h[i]]);  /* sum p*log(1/p)*64*16 */
  b->entropy=(u8)clampi((int)((u32)s*100u/(64u*80u)),0,100);}
 b->rng=(u32)b->dna[0]|((u32)b->dna[1]<<5)|((u32)b->dna[2]<<10)|((u32)b->dna[3]<<15)|((u32)b->dna[4]<<20)|((u32)b->dna[5]<<25)|1u;
 b->rng^=id;
 b->lx=((s32)b->dna[6]-16)*64+1;b->ly=((s32)b->dna[7]-16)*64+1;b->lz=((s32)b->dna[8])*96+256;
 b->base_hp=(u8)(40+b->dna[9]+b->dna[10]);b->base_atk=(u8)(4+(b->dna[11]>>1));b->base_def=(u8)(4+(b->dna[12]>>1));
 b->base_spd=(u8)(4+(b->dna[13]>>1));b->base_focus=(u8)(4+(b->dna[14]>>1));b->base_luck=(u8)(b->dna[15]>>1);}
static int lw_stat(const LwBeast*b,int k){int v,i;
 v=k==0?b->base_hp+b->level*4:k==1?b->base_atk+b->level:k==2?b->base_def+b->level:k==3?b->base_spd+(b->level>>1):k==4?b->base_focus+(b->level>>1):b->base_luck;
 if(k<=4){static const u8 map[5]={0,1,2,3,4};for(i=0;i<4;i++)if(b->equip[i])v+=V12_ITEMS[b->equip[i]-1].st[map[k]];}
 return clampi(v,1,255);}
static void lw_defaults(void){int i;
 for(i=0;i<V12_ITEM_COUNT;i++)lw_inv[i]=0;for(i=0;i<5;i++)lw_claimed[i]=0;
 {static const char*const s[9]={"healing_herbs","moon_berry","sunseed_snack","warm_ale","forge_lantern","tiny_scarf","hammer_blade","star_candy","wet_sock"};
  static const u8 n[9]={3,4,2,1,1,1,1,2,1};for(i=0;i<9;i++){int j=lw_item(s[i]);if(j>=0)lw_inv[j]=n[i];}}
 for(i=0;i<LW_N;i++){LwBeast*b=&lw_b[i];int j;b->hunger=(u8)(30+b->dna[16]);b->energy=(u8)(60+b->dna[17]);b->mood=(u8)(50+b->dna[18]);b->bond=(u8)(20+b->dna[19]);b->level=1;b->xp=0;for(j=0;j<4;j++)b->equip[j]=0;b->hp=(u8)lw_stat(b,0);}}
static u32 lw_sum(void){u32 s=0x4C573132u;int i;for(i=0;i<252;i++)s=s*31u+SRAM[LW_SRAM+i];return s;}
static void lw_save(void){int i,o;
 for(i=0;i<256;i++)SRAM[LW_SRAM+i]=0;
 SRAM[LW_SRAM]='L';SRAM[LW_SRAM+1]='W';SRAM[LW_SRAM+2]=1;SRAM[LW_SRAM+3]=0;SRAM[LW_SRAM+4]=lw_world;
 for(i=0;i<V12_ITEM_COUNT;i++)SRAM[LW_SRAM+8+i]=lw_inv[i];
 for(i=0;i<LW_N;i++){LwBeast*b=&lw_b[i];o=LW_SRAM+76+i*12;
  SRAM[o]=b->hunger;SRAM[o+1]=b->energy;SRAM[o+2]=b->mood;SRAM[o+3]=b->bond;SRAM[o+4]=b->hp;SRAM[o+5]=b->level;
  SRAM[o+6]=(u8)b->xp;SRAM[o+7]=(u8)(b->xp>>8);SRAM[o+8]=b->equip[0];SRAM[o+9]=b->equip[1];SRAM[o+10]=b->equip[2];SRAM[o+11]=b->equip[3];}
 for(i=0;i<5;i++)SRAM[LW_SRAM+156+i]=lw_claimed[i];
 {u32 s=lw_sum();SRAM[LW_SRAM+252]=(u8)s;SRAM[LW_SRAM+253]=(u8)(s>>8);SRAM[LW_SRAM+254]=(u8)(s>>16);SRAM[LW_SRAM+255]=(u8)(s>>24);}}
static int lw_load(void){int i,o;u32 s;
 if(SRAM[LW_SRAM]!='L'||SRAM[LW_SRAM+1]!='W'||SRAM[LW_SRAM+2]!=1)return 0;
 s=(u32)SRAM[LW_SRAM+252]|((u32)SRAM[LW_SRAM+253]<<8)|((u32)SRAM[LW_SRAM+254]<<16)|((u32)SRAM[LW_SRAM+255]<<24);
 if(s!=lw_sum())return 0;
 lw_world=SRAM[LW_SRAM+4]&1;
 for(i=0;i<V12_ITEM_COUNT;i++)lw_inv[i]=(u8)mini(99,SRAM[LW_SRAM+8+i]);
 for(i=0;i<LW_N;i++){LwBeast*b=&lw_b[i];int j;o=LW_SRAM+76+i*12;
  b->hunger=(u8)mini(100,SRAM[o]);b->energy=(u8)mini(100,SRAM[o+1]);b->mood=(u8)mini(100,SRAM[o+2]);b->bond=(u8)mini(100,SRAM[o+3]);
  b->level=(u8)clampi(SRAM[o+5],1,99);b->xp=(u16)(SRAM[o+6]|(SRAM[o+7]<<8));
  for(j=0;j<4;j++){u8 e=SRAM[o+8+j];b->equip[j]=(u8)(e<=V12_ITEM_COUNT?e:0);}
  b->hp=(u8)mini(lw_stat(b,0),SRAM[o+4]);}
 for(i=0;i<5;i++)lw_claimed[i]=SRAM[LW_SRAM+156+i];
 return 1;}
/* ---------- quests: journal driven by the native campaign (cq_state) ---------- */
static const u8 LW_ACT_Q0[4]={10,15,22,32},LW_ACT_QN[4]={5,7,10,7};
static int lw_quest_state(int q){int a=V12_QUESTS[q].act-2,i,k=0,n=0,done=0,started=0;
 if(a<0||a>3)return 0;
 for(i=0;i<V12_QUEST_COUNT;i++)if(V12_QUESTS[i].act==V12_QUESTS[q].act){if(i<q)k++;n++;}
 for(i=0;i<LW_ACT_QN[a];i++){u8 s=cq_state[LW_ACT_Q0[a]+i];if(s==CQ_DONE)done++;if(s!=CQ_LOCKED)started=1;}
 if(done*n>=(k+1)*LW_ACT_QN[a])return 2;
 return started||done?1:0;}
static void lw_claim_quests(void){int q,j;
 for(q=0;q<V12_QUEST_COUNT;q++)if(lw_quest_state(q)==2&&!(lw_claimed[q>>3]&(1u<<(q&7)))){
  lw_claimed[q>>3]|=(u8)(1u<<(q&7));lw_quests_done++;
  for(j=0;j<3;j++){int it=V12_QUESTS[q].reward[j];if(it>=0&&lw_inv[it]<99)lw_inv[it]++;}
  lw_say("QUEST REWARD: ",V12_QUESTS[q].name);}}
/* ---------- art upload ---------- */
static void lw_upload_bg(void){int i;const u32*t=lw_world?v12_bg_cave_tiles:v12_bg_forest_tiles;const u16*m=lw_world?v12_bg_cave_map:v12_bg_forest_map;
 const u16*p=lw_world?v12_bg_cave_pal:v12_bg_forest_pal;int n=lw_world?V12_BG_CAVE_TILES:V12_BG_FOREST_TILES;
 lw_copy32((volatile u32*)0x06008000,t,n*8);
 for(i=0;i<2048;i++)VRAM16[29*1024+i]=(u16)(m[i]|(3u<<12));
 for(i=0;i<16;i++){u16 c=p[i];if(lw_night)c=(u16)(((c&0x1F)>>1)|((((c>>5)&0x1F)>>1)<<5)|((((u32)((c>>10)&0x1F)*3u)>>2)<<10));BG_PALETTE[48+i]=c;}
 REG_BG0CNT=(u16)(2|(2u<<2)|(29u<<8)|(1u<<14));}
static void lw_upload_obj_pals(void){int i,j;
 for(i=0;i<LW_N;i++)for(j=0;j<16;j++){OBJ_PALETTE[i*16+j]=LW_CRE_PAL[i][j];OBJ_PALETTE[(6+i)*16+j]=LW_COMP_PAL[i][j];}
 for(j=0;j<16;j++){OBJ_PALETTE[12*16+j]=v12_items_pal[j];OBJ_PALETTE[13*16+j]=v12_chr_arin_pal[j];}
 {static const u16 wp[16]={0,0x0000,0x0802,0x1004,0x1806,0x7C1F,0x2008,0x7FFF,0,0,0,0,0,0,0,0};for(j=0;j<16;j++)OBJ_PALETTE[14*16+j]=wp[j];}}
/* The darkness wisp: a procedural 16x16 shadow blob with two eyes (code art). */
static void lw_upload_wisp(int phase){int ty,tx,y,x;volatile u32*d=LW_OBJ_TILES+496*8;
 for(ty=0;ty<2;ty++)for(tx=0;tx<2;tx++)for(y=0;y<8;y++){u32 w=0;for(x=0;x<8;x++){int px=tx*8+x-8,py=ty*8+y-8,r=px*px+py*py,c=0;
  int rad=44+((phase&3)*6);if(r<rad)c=r<12?2:r<26?3:4;if(r<rad&&r>=rad-10&&((px+py+phase)&1))c=6;
  if((py==-2)&&(px==-3||px==2))c=7;w|=(u32)c<<(4*x);}*d++=w;}}
static void lw_upload_arin(void){lw_copy32(LW_OBJ_TILES+480*8,v12_chr_arin_tiles,16*8);}
static void lw_upload_icon(int it){const V12Item*v=&V12_ITEMS[it];volatile u32*d=LW_OBJ_TILES+500*8;int i;
 for(i=0;i<64;i++)d[i]=0;
 if(v->sheet==0)lw_copy32(d,v12_icons_a+v->icon*32,32);
 else if(v->sheet==1)lw_copy32(d,v12_weapons+v->icon*64,64);
 else lw_copy32(d,v12_lanterns+(v->icon*2+((lw_clock>>4)&1))*64,64);}
static int lw_frame_of(const LwBeast*b,int i){
 if(i==0&&b->trig==V12_TRIG_DARK_NEARBY)return 12+((lw_clock>>3)&3);   /* Zeref react_dark, 4 frames */
 return (b->moving?6:0)+(int)(((u32)lw_clock>>3)%6u);}
static void lw_upload_creatures(int force){int i;
 for(i=0;i<LW_N;i++){LwBeast*b=&lw_b[i];int f=lw_frame_of(b,i);
  if(force||f!=b->frame){b->frame=(u8)f;lw_copy32(LW_OBJ_TILES+i*64*8,LW_CRE_TILES[i]+f*64*8,64*8);
   lw_copy32(LW_OBJ_TILES+(384+i*16)*8,LW_COMP_TILES[i]+((b->moving?4:0)+((lw_clock>>3)&3))*16*8,16*8);}}}
/* ---------- OAM ---------- */
static void lw_obj(int i,int x,int y,int shape,int size,int tile,int pal,int hflip,int prio){
 if(x<-64||x>239||y<-64||y>159){OAM16[i*4]=0x0200;return;}
 OAM16[i*4]=(u16)((y&255)|(shape<<14));OAM16[i*4+1]=(u16)((x&511)|(size<<14)|(hflip?0x1000:0));OAM16[i*4+2]=(u16)(tile|(prio<<10)|(pal<<12));}
/* ---------- life ---------- */
static int lw_dist(const LwBeast*b,s32 x,s32 y){int dx=(b->x-x)>>8,dy=(b->y-y)>>8;return iabs(dx)+iabs(dy);}
static void lw_target(LwBeast*b,int x,int y){b->tx=clampi(x,24,LW_W-24);b->ty=clampi(y,40,LW_H-8);}
static void lw_pick(int i){LwBeast*b=&lw_b[i];int t=-1,j,near_other=9999;
 int dark=lw_dist(b,lw_wx,lw_wy)<72,pl=lw_dist(b,lw_px,lw_py);
 for(j=0;j<LW_N;j++)if(j!=i)near_other=mini(near_other,lw_dist(b,lw_b[j].x,lw_b[j].y));
 if(dark)t=V12_TRIG_DARK_NEARBY;
 else if(b->found)t=V12_TRIG_ITEM_FOUND;
 else if(b->trig==V12_TRIG_DRANK_ALE&&b->timer)t=V12_TRIG_DRANK_ALE;
 else if(b->energy<8)t=V12_TRIG_EXHAUSTED;
 else if(b->hunger>88)t=V12_TRIG_VERY_HUNGRY;
 else if(b->hunger>65)t=V12_TRIG_HUNGRY;
 else if(b->energy<28)t=V12_TRIG_TIRED;
 else if(b->bond<15)t=V12_TRIG_BOND_LOW;
 else if(b->equip[3])t=(lw_rand(b)&3)==0?V12_TRIG_LIGHT_NEAR:-1;
 if(t<0&&lw_dist(b,lw_wx,lw_wy)<130&&(lw_rand(b)&3)==0)t=V12_TRIG_ENEMY_NEAR;
 if(t<0&&pl>200&&b->bond>50)t=V12_TRIG_LONELY;
 if(t<0&&near_other>220)t=V12_TRIG_FRIEND_LOST;
 if(t<0&&lw_night&&(lw_rand(b)%3)==0)t=V12_TRIG_NIGHT;
 if(t<0&&b->hunger<25&&b->energy>75)t=V12_TRIG_FED_AND_RESTED;
 if(t<0&&b->since>6)t=V12_TRIG_IDLE_LONG;
 if(t<0){u32 r=lw_rand(b)%100;
  /* Entropy-weighted wandering choice: restless DNA investigates more. */
  if(r<(u32)(20u+(u32)b->entropy/3u))t=V12_TRIG_CURIOUS;else if(r<70)t=V12_TRIG_TOY_NEAR;else if(r<80)t=V12_TRIG_STILLING_NEAR;else if(r<88)t=V12_TRIG_LEANING_ROLL;else t=V12_TRIG_CURIOUS;}
 b->since=(u16)(b->trig==t?b->since+1:0);
 b->trig=(u8)t;b->action=V12_MOODS[t].action;lw_decisions++;
 b->timer=(u16)(120+(lw_rand(b)%120));
 switch(b->action){
  case V12_ACT_SEEK_FOOD:lw_target(b,(int)(lw_rand(b)%LW_W),(int)(lw_rand(b)%LW_H));break;
  case V12_ACT_FOLLOW_PLAYER:case V12_ACT_PRESENT_ITEM:case V12_ACT_NUZZLE:lw_target(b,(lw_px>>8)+16,(lw_py>>8));break;
  case V12_ACT_HIDE_BEHIND:{int bx=(b->x>>8)*2-(lw_wx>>8),by=(b->y>>8)*2-(lw_wy>>8);lw_target(b,bx,by);}break;
  case V12_ACT_INVESTIGATE:case V12_ACT_DIG:case V12_ACT_CHASE_TOY:case V12_ACT_ZOOMIES:lw_target(b,(int)(lw_rand(b)%LW_W),(int)(lw_rand(b)%LW_H));break;
  case V12_ACT_SIT_CHAIR:case V12_ACT_SIT_ALONE:{int j2=(int)(lw_rand(b)%(u32)LW_N);lw_target(b,(lw_b[j2].x>>8)+24,(lw_b[j2].y>>8));}break;
  default:b->tx=b->x>>8;b->ty=b->y>>8;break;}
 if(i==lw_focus)lw_say(LW_NAMES[i],": ");
 if(i==lw_focus){int n=0;const char*s=V12_MOODS[t].line;while(lw_msg[n])n++;while(*s&&n<58)lw_msg[n++]=*s++;lw_msg[n]=0;}
 if(i==0&&t==V12_TRIG_DARK_NEARBY)lw_dark_reacts++;}
static void lw_lorenz(LwBeast*b,int speed){s32 x=b->lx,y=b->ly,z=b->lz,dx,dy,dz;
 /* sigma 10, rho 28, beta 8/3, dt 1/256, Q8 */
 dx=10*(y-x);dy=((x*((28<<8)-z))>>8)-y;dz=((x*y)>>8)-((z*683)>>8);
 x+=dx>>8;y+=dy>>8;z+=dz>>8;(void)speed;
 b->lx=clampi(x,-(60<<8),60<<8);b->ly=clampi(y,-(60<<8),60<<8);b->lz=clampi(z,0,90<<8);}
static void lw_tick_beast(int i){LwBeast*b=&lw_b[i];s32 vx,vy,ox=b->x,oy=b->y;int spd=lw_stat(b,3),act=b->action,still=0;
 lw_lorenz(b,spd);
 /* needs drift */
 if((lw_clock&127)==(u16)(i*16)){if(b->hunger<100)b->hunger++;if(b->moving&&b->energy)b->energy--;
  if(b->hunger>70&&b->mood)b->mood--;if(b->energy<20&&b->mood)b->mood--;if(b->hunger<30&&b->energy>60&&b->mood<100)b->mood++;}
 if(b->timer)b->timer--;else lw_pick(i);
 switch(act){
  case V12_ACT_NAP:case V12_ACT_COLLAPSE_SLEEP:still=1;if((lw_clock&15)==0&&b->energy<100)b->energy++;if(b->energy>=95)b->timer=0;break;
  case V12_ACT_STARGAZE:case V12_ACT_FREEZE_STARE:case V12_ACT_GLARE:case V12_ACT_GROWL:case V12_ACT_BASK_LIGHT:case V12_ACT_FLICKER:still=1;if((lw_clock&63)==0&&b->mood<100)b->mood++;break;
  case V12_ACT_RAID_PACK:still=1;if(b->timer==1){int j;for(j=0;j<V12_ITEM_COUNT;j++)if(lw_inv[j]&&V12_ITEMS[j].cat==1)break;
   if(j<V12_ITEM_COUNT){lw_inv[j]--;b->hunger=(u8)clampi(b->hunger-V12_ITEMS[j].st[6]*2,0,100);if(i==lw_focus)lw_say(LW_NAMES[i]," RAIDED THE PACK AND ATE.");}
   else{b->action=V12_ACT_SEEK_FOOD;lw_target(b,(int)(lw_rand(b)%LW_W),(int)(lw_rand(b)%LW_H));b->timer=160;}}break;
  default:break;}
 if(!still){s32 gx=(b->tx<<8)-b->x,gy=(b->ty<<8)-b->y;int boost=act==V12_ACT_ZOOMIES?3:act==V12_ACT_HIDE_BEHIND?3:1;
  /* classical Lorenz wobble (DNA-seeded) + steering toward the action goal */
  vx=(b->lx*(20+b->entropy))>>12;vy=(b->ly*(20+b->entropy))>>12;
  if(iabs(gx)>512||iabs(gy)>512){vx+=signi(gx)*(64+spd*4)*boost;vy+=signi(gy)*(48+spd*3)*boost;}
  else if(act==V12_ACT_SEEK_FOOD){b->hunger=(u8)(b->hunger>30?b->hunger-30:0);b->timer=0;if(i==lw_focus)lw_say(LW_NAMES[i]," FOUND BERRIES AND ATE.");}
  else if(act==V12_ACT_DIG&&!b->found&&(lw_rand(b)%100)<(u32)(25+b->base_luck)){b->found=1;b->timer=0;}
  else if(act==V12_ACT_PRESENT_ITEM&&b->found){int it=(int)(lw_rand(b)%V12_ITEM_COUNT),tries=0;
   while((V12_ITEMS[it].cat>2&&V12_ITEMS[it].cat!=7)&&tries++<40)it=(int)(lw_rand(b)%V12_ITEM_COUNT);
   if(V12_ITEMS[it].cat<=2||V12_ITEMS[it].cat==7){if(lw_inv[it]<99)lw_inv[it]++;lw_say("A GIFT: ",V12_ITEMS[it].name);}
   b->found=0;b->timer=0;if(b->bond<100)b->bond++;}
  if(act==V12_ACT_STUMBLE)vx+=((lw_clock>>4)&1)?96:-96;
  b->x=clampi(b->x+vx,24<<8,(LW_W-24)<<8);b->y=clampi(b->y+vy,40<<8,(LW_H-8)<<8);}
 b->moving=(u8)(iabs((b->x>>8)-(ox>>8))+iabs((b->y>>8)-(oy>>8))>0);
 if(b->moving){lw_moved_px+=1;if(b->x!=ox)b->face=(u8)(b->x<ox);}
 if((lw_clock&511)==(u16)(i*32)&&b->moving){b->xp++;if(b->xp>=(u16)(b->level*20)){b->xp=0;if(b->level<99)b->level++;if(i==lw_focus)lw_say(LW_NAMES[i]," GREW A LEVEL.");}}}
static void lw_tick_wisp(void){s32 x=lw_wl[0],y=lw_wl[1],z=lw_wl[2];
 x+=(10*(y-x))>>8;y+=(((x*((28<<8)-z))>>8)-y)>>8;z+=(((x*y)>>8)-((z*683)>>8))>>8;lw_wl[0]=x;lw_wl[1]=y;lw_wl[2]=z;
 /* the darkness drifts slowly toward Zeref, pushed around by its own attractor */
 lw_wx+=(x>>3)+signi((lw_b[0].x-lw_wx)>>8)*40;lw_wy+=(y>>3)+signi((lw_b[0].y-lw_wy)>>8)*30;
 if(lw_b[0].trig==V12_TRIG_DARK_NEARBY&&lw_dist(&lw_b[0],lw_wx,lw_wy)<40){lw_wx+=(lw_wx>lw_b[0].x?1:-1)*(160<<8);lw_wy=(s32)(40u+((u32)lw_clock%180u))<<8;}
 lw_wx=clampi(lw_wx,16<<8,(LW_W-16)<<8);lw_wy=clampi(lw_wy,40<<8,(LW_H-16)<<8);}
/* ---------- enter / exit ---------- */
static void lw_mode0(void){int i;
 lw_copy32((volatile u32*)0x06000000,(const u32*)lw_vram_save,0xA000/4);   /* repair what the mode-4 card overwrote */
 for(i=0;i<256;i++)BG_PALETTE[i]=lw_pal_save[i];
 lw_upload_bg();lw_upload_obj_pals();lw_upload_arin();lw_upload_wisp(0);lw_upload_creatures(1);
 for(i=0;i<128;i++)OAM16[i*4]=0x0200;ui_clear();
 REG_DISPCNT=MODE0|BG0_ENABLE|BG1_ENABLE|OBJ_ENABLE|OBJ_1D_MAP;lw_card=0;}
static void lw_card_show(void){int i;const u8*px=lw_world?v12_scene_cave_px:v12_scene_forest_px;const u16*p=lw_world?v12_scene_cave_pal:v12_scene_forest_pal;
 for(i=0;i<128;i++)OAM16[i*4]=0x0200;
 lw_copy32((volatile u32*)0x06000000,(const u32*)px,240*160/4);
 for(i=0;i<256;i++)BG_PALETTE[i]=p[i];
 LW_REG16(0x04000020)=0x100;LW_REG16(0x04000022)=0;LW_REG16(0x04000024)=0;LW_REG16(0x04000026)=0x100;LW_REG32(0x04000028)=0;LW_REG32(0x0400002C)=0;
 REG_BG2CNT=0;REG_DISPCNT=4|BG2_ENABLE;lw_card=1;lw_card_timer=150;}
static void lw_enter(void){int i;
 if(lw_active||game_mode!=MODE_SURFACE||cinema_active||intro||v108_credits_active||fp_active)return;
 for(i=0;i<0x18000/4;i++)((u32*)lw_vram_save)[i]=((volatile u32*)0x06000000)[i];
 for(i=0;i<512;i++){lw_pal_save[i]=lc_pal_shadow[i];lw_oam_save[i]=lc_oam_shadow[i];}
 for(i=0;i<1024;i++)lw_ui_save[i]=lc_ui_shadow[i];
 for(i=0;i<14;i++)lw_io_save[i]=lc_io_shadow[i];
 for(i=0;i<LW_N;i++){LwBeast*b=&lw_b[i];b->id=LW_IDS[i];lw_dna(b,b->id);
  b->x=(s32)(60+i*72)<<8;b->y=(s32)(80+(b->dna[20]<<2))<<8;b->tx=b->x>>8;b->ty=b->y>>8;b->timer=(u16)(20+i*15);b->trig=V12_TRIG_CURIOUS;b->action=V12_ACT_INVESTIGATE;b->found=0;b->since=0;b->frame=255;}
 lw_wl[0]=QSEED[100]*64+1;lw_wl[1]=QSEED[101]*64+1;lw_wl[2]=QSEED[102]*96+256;lw_wx=440<<8;lw_wy=200<<8;
 if(!lw_load())lw_defaults();
 lw_claim_quests();
 lw_active=1;lw_entries++;lw_page=0;lw_sel=0;lw_focus=0;lw_px=240<<8;lw_py=150<<8;
 lw_card_show();lc_sfx(SFX_CONFIRM);
 if(!lw_msg_timer)lw_say("LIVING WORLD. CLASSICAL LIFE SEEDED BY RECORDED IBM DATA.",0);}
static void lw_exit(void){int i;
 if(!lw_active)return;
 lw_save();lw_active=0;lw_exits++;
 for(i=0;i<0x18000/4;i++)((volatile u32*)0x06000000)[i]=((u32*)lw_vram_save)[i];
 for(i=0;i<512;i++){lc_pal_shadow[i]=lw_pal_save[i];lc_oam_shadow[i]=lw_oam_save[i];}
 for(i=0;i<1024;i++)lc_ui_shadow[i]=lw_ui_save[i];
 for(i=0;i<14;i++)lc_io_shadow[i]=lw_io_save[i];
 lc_sfx(SFX_CANCEL);}
/* ---------- input ---------- */
static void lw_use(int it){LwBeast*b=&lw_b[lw_focus];const V12Item*v=&V12_ITEMS[it];int slot=-1;
 if(!lw_inv[it]){lw_say("NONE LEFT.",0);return;}
 if(v->cat==0||v->cat==1){lw_inv[it]--;lw_items_used++;
  b->hp=(u8)clampi(b->hp+v->st[0],0,lw_stat(b,0));b->hunger=(u8)clampi(b->hunger-v->st[6]*2,0,100);
  b->energy=(u8)clampi(b->energy+v->st[7]*2,0,100);b->mood=(u8)clampi(b->mood+v->st[5],0,100);if(b->bond<100)b->bond++;
  if(lw_streq(v->id,"warm_ale")){b->trig=V12_TRIG_DRANK_ALE;b->action=V12_ACT_STUMBLE;b->timer=240;}
  lc_sfx(SFX_POTION);lw_say(LW_NAMES[lw_focus]," ENJOYED IT.");lw_save();return;}
 slot=v->cat==2?0:v->cat==3?1:v->cat==4?2:v->cat==5?3:-1;
 if(slot<0){lw_say(v->cat==6?"A KEY ITEM. KEEP IT SAFE.":"A MATERIAL FOR CRAFTING.",0);return;}
 if(b->equip[slot]==it+1){b->equip[slot]=0;lw_inv[it]++;lw_say(LW_NAMES[lw_focus]," TOOK IT OFF.");}
 else{if(b->equip[slot]&&lw_inv[b->equip[slot]-1]<99)lw_inv[b->equip[slot]-1]++;b->equip[slot]=(u8)(it+1);lw_inv[it]--;lw_items_used++;lw_say(LW_NAMES[lw_focus]," EQUIPPED IT.");}
 b->hp=(u8)mini(b->hp,lw_stat(b,0));lc_sfx(SFX_CONFIRM);lw_save();}
static int lw_owned(int n){int i,c=0;for(i=0;i<V12_ITEM_COUNT;i++)if(lw_inv[i]||(lw_b[lw_focus].equip[0]==i+1||lw_b[lw_focus].equip[1]==i+1||lw_b[lw_focus].equip[2]==i+1||lw_b[lw_focus].equip[3]==i+1)){if(c==n)return i;c++;}return n<0?c:-1;}
static int lw_owned_count(void){int i,c=0;for(i=0;i<V12_ITEM_COUNT;i++)if(lw_inv[i]||lw_b[lw_focus].equip[0]==i+1||lw_b[lw_focus].equip[1]==i+1||lw_b[lw_focus].equip[2]==i+1||lw_b[lw_focus].equip[3]==i+1)c++;return c;}
static void lw_update(u16 k,u16 newk){int i;
 lw_clock++;
 if(lw_card){if(lw_card_timer)lw_card_timer--;if((newk&(KEY_A|KEY_START|KEY_B))||!lw_card_timer)lw_mode0();return;}
 {u8 night=(u8)((((u32)lw_clock/1800u)&1u));if(night!=lw_night){lw_night=night;lw_upload_bg();}}
 for(i=0;i<LW_N;i++)lw_tick_beast(i);
 lw_tick_wisp();
 if((lw_clock&1023)==0)lw_save();
 if(lw_page){int max=lw_page==1?lw_owned_count():lw_page==3?V12_QUEST_COUNT:lw_page==4?V12_CHAR_COUNT:1;
  if(newk&KEY_B){lw_page=0;ui_clear();lw_dirty_art=1;lc_sfx(SFX_CANCEL);return;}
  if(newk&KEY_START){lw_page=(u8)(lw_page>=4?1:lw_page+1);lw_sel=0;ui_clear();lw_dirty_art=1;lc_sfx(SFX_MOVE);return;}
  if(newk&KEY_UP){lw_sel=(u8)(lw_sel?lw_sel-1:(max?max-1:0));ui_clear();}
  if(newk&KEY_DOWN){lw_sel=(u8)(max&&lw_sel+1<max?lw_sel+1:0);ui_clear();}
  if(newk&(KEY_L|KEY_R)){lw_focus=(u8)((u32)(lw_focus+((newk&KEY_R)?1:LW_N-1))%(u32)LW_N);ui_clear();}
  if((newk&KEY_A)&&lw_page==1){int it=lw_owned(lw_sel);if(it>=0)lw_use(it);ui_clear();}
  return;}
 if(newk&KEY_B){lw_exit();return;}
 if(newk&KEY_START){lw_page=1;lw_sel=0;ui_clear();lc_sfx(SFX_CONFIRM);return;}
 if(newk&KEY_SELECT){lw_world^=1;lw_upload_bg();lw_say(lw_world?"THE CRYSTAL CAVE.":"THE VIOLET FOREST.",0);lw_save();}
 if(newk&(KEY_L|KEY_R)){lw_focus=(u8)((u32)(lw_focus+((newk&KEY_R)?1:LW_N-1))%(u32)LW_N);lw_say("WATCHING ",LW_NAMES[lw_focus]);}
 {int run=(k&KEY_A)?0:1;s32 sp=(s32)(run?384:384);
  if(k&KEY_LEFT)lw_px-=sp;if(k&KEY_RIGHT)lw_px+=sp;if(k&KEY_UP)lw_py-=sp;if(k&KEY_DOWN)lw_py+=sp;
  lw_px=clampi(lw_px,16<<8,(LW_W-16)<<8);lw_py=clampi(lw_py,40<<8,(LW_H-4)<<8);}
 if(newk&KEY_A){for(i=0;i<LW_N;i++)if(lw_dist(&lw_b[i],lw_px,lw_py)<40){LwBeast*b=&lw_b[i];
   int asleep=b->action==V12_ACT_NAP||b->action==V12_ACT_COLLAPSE_SLEEP;
   b->trig=asleep?V12_TRIG_WOKEN_UP:V12_TRIG_PETTED;b->action=V12_MOODS[b->trig].action;b->timer=120;
   if(!asleep){if(b->mood<100)b->mood=(u8)mini(100,b->mood+8);if(b->bond<100)b->bond++;}
   lw_focus=(u8)i;lw_say(LW_NAMES[i],": ");{int n=0;const char*s=V12_MOODS[b->trig].line;while(lw_msg[n])n++;while(*s&&n<58)lw_msg[n++]=*s++;lw_msg[n]=0;}
   lc_sfx(SFX_BEFRIEND);break;}}
 lw_camx=(s16)clampi((lw_px>>8)-120,0,LW_W-240);lw_camy=(s16)clampi((lw_py>>8)-80,0,LW_H-160);}
/* ---------- render ---------- */
static void lw_line(int y,const char*s,int pal){char t[29];int n=0;while(s&&*s&&n<28)t[n++]=*s++;t[n]=0;ui_text(1,y,t,pal);}
static void lw_wrap(int y,const char*s,int pal,int lines){char t[29];int l,n,len,cut;
 for(l=0;l<lines&&*s;l++){for(len=0;s[len];)len++;cut=len<=28?len:28;
  if(len>28){for(n=28;n>0&&s[n]!=' ';)n--;if(n>0)cut=n;}
  for(n=0;n<cut;n++)t[n]=s[n];t[n]=0;ui_text(1,y+l,t,pal);s+=cut;while(*s==' ')s++;}}
static void lw_hud(void){LwBeast*b=&lw_b[lw_focus];
 ui_fill_rows(0,0,62,15);ui_fill_rows(16,19,62,15);
 ui_text(1,0,"LIVING WORLD",14);ui_text(14,0,lw_world?"CAVE":"FOREST",13);ui_text(21,0,lw_night?"NIGHT":"DAY",13);
 ui_text(1,16,LW_NAMES[lw_focus],14);ui_text(12,16,V12_ACT_NAMES[b->action],13);
 ui_text(1,17,"HU",13);ui_num(4,17,b->hunger,15);ui_text(8,17,"EN",13);ui_num(11,17,b->energy,15);
 ui_text(15,17,"MO",13);ui_num(18,17,b->mood,15);ui_text(22,17,"LV",13);ui_num(25,17,b->level,15);
 if(lw_msg_timer){lw_msg_timer--;lw_wrap(18,lw_msg,15,2);}
 else lw_line(18,V12_MOODS[b->trig].name,14);}
static void lw_draw_field(void){int i,o=0;
 REG_BG0HOFS=(u16)lw_camx;REG_BG0VOFS=(u16)lw_camy;
 lw_upload_creatures(lw_dirty_art);lw_dirty_art=0;
 if((lw_clock&7)==0)lw_upload_wisp(lw_clock>>3);
 lw_obj(o++,(lw_px>>8)-lw_camx-16,(lw_py>>8)-lw_camy-30,0,2,480,13,0,1);
 lw_obj(o++,(lw_wx>>8)-lw_camx-8,(lw_wy>>8)-lw_camy-8+((lw_clock>>4)&1),0,1,496,14,0,1);
 for(i=0;i<LW_N;i++){LwBeast*b=&lw_b[i];int sx=(b->x>>8)-lw_camx,sy=(b->y>>8)-lw_camy;
  int blink=b->action==V12_ACT_FLICKER&&((lw_clock>>2)&1);
  lw_obj(o++,b->face?sx+24:sx-56,sy-34,0,2,384+i*16,6+i,b->face,1);
  if(blink)OAM16[o*4]=0x0200,o++;else lw_obj(o++,sx-32,sy-60,0,3,i*64,i,b->face,1);}
 for(;o<128;o++)OAM16[o*4]=0x0200;
 lw_hud();}
static void lw_draw_page(void){int i,r;LwBeast*b=&lw_b[lw_focus];static const char*const tab[5]={"","ITEMS","STATS","QUESTS","CAST"};
 for(i=0;i<128;i++)OAM16[i*4]=0x0200;
 ui_fill_rows(0,19,62,15);ui_text(1,0,tab[lw_page],14);ui_text(9,0,LW_NAMES[lw_focus],13);ui_text(20,0,"START>TAB",13);
 if(lw_page==1){int n=lw_owned_count(),start=lw_sel&~7;
  if(!n){ui_text(1,3,"THE PACK IS EMPTY.",15);return;}
  for(r=0;r<8&&start+r<n;r++){int it=lw_owned(start+r),eq=0,j;for(j=0;j<4;j++)if(b->equip[j]==it+1)eq=1;
   ui_text(1,2+r,start+r==lw_sel?">":" ",14);ui_text(2,2+r,V12_ITEMS[it].name,start+r==lw_sel?14:15);
   if(eq)ui_text(18,2+r,"E",9);ui_text(20,2+r,"X",13);ui_num(21,2+r,lw_inv[it],15);}
  {int it=lw_owned(lw_sel);if(it>=0){const V12Item*v=&V12_ITEMS[it];static const char*const cat[8]={"USE","FOOD","WEAPON","ARMOR","ACCESSORY","LANTERN","KEY","MATERIAL"};
   lw_wrap(11,v->desc,15,2);ui_text(1,14,cat[v->cat],13);
   {static const char*const sn[8]={"HP","AT","DF","SP","FO","MO","HU","EN"};int c=8,j;for(j=0;j<8;j++)if(v->st[j]){ui_text(c,14,sn[j],13);if(v->st[j]<0){ui_text(c+2,14,"-",7);ui_num(c+3,14,-v->st[j],7);}else ui_num(c+2,14,v->st[j],9);c+=6;if(c>26)break;}}
   ui_text(1,16,"A USE  L/R BEAST  B BACK",13);
   lw_upload_icon(it);
   if(v->sheet==0)lw_obj(0,200,24,0,1,500,12,0,0);else if(v->sheet==1)lw_obj(0,192,24,1,2,500,12,0,0);else lw_obj(0,200,20,2,2,500,12,0,0);}}}
 else if(lw_page==2){static const char*const sn[6]={"HP","ATK","DEF","SPD","FOCUS","LUCK"};static const char*const slot[4]={"WEAPON","ARMOR","ACCESS","LIGHT"};char id[12];int j;u32 v=b->id;
  for(j=0;j<6;j++){ui_text(1,2+j,sn[j],13);ui_num(8,2+j,lw_stat(b,j),15);}
  ui_text(1,8,"HP NOW",13);ui_num(8,8,b->hp,15);ui_text(14,2,"HUNGER",13);ui_num(22,2,b->hunger,15);ui_text(14,3,"ENERGY",13);ui_num(22,3,b->energy,15);
  ui_text(14,4,"MOOD",13);ui_num(22,4,b->mood,15);ui_text(14,5,"BOND",13);ui_num(22,5,b->bond,15);ui_text(14,6,"LEVEL",13);ui_num(22,6,b->level,15);ui_text(14,7,"ENTROPY",13);ui_num(22,7,b->entropy,15);
  for(j=0;j<4;j++){ui_text(1,10+j,slot[j],13);ui_text(8,10+j,b->equip[j]?V12_ITEMS[b->equip[j]-1].name:"-",15);}
  id[0]='I';id[1]='D';id[2]=' ';for(j=0;j<8;j++){u32 d=(v>>(28-4*j))&15;id[3+j]=(char)(d<10?'0'+d:'A'+d-10);}id[11]=0;ui_text(1,15,id,13);
  ui_text(1,16,"DNA: RECORDED IBM QSEED WINDOW",13);ui_text(1,17,"LIFE: CLASSICAL LORENZ SIM",13);}
 else if(lw_page==3){int start=(int)((u32)lw_sel/7u)*7;const V12Quest*q=&V12_QUESTS[lw_sel];static const char*const st[3]={"LOCKED","OPEN","DONE"};
  for(r=0;r<7&&start+r<V12_QUEST_COUNT;r++){int s=lw_quest_state(start+r);ui_text(1,2+r,start+r==lw_sel?">":" ",14);ui_text(2,2+r,"A",13);ui_num(3,2+r,V12_QUESTS[start+r].act,13);ui_text(5,2+r,V12_QUESTS[start+r].name,start+r==lw_sel?14:15);ui_text(23,2+r,st[s],s==2?9:s==1?14:13);}
  lw_wrap(10,q->summary,15,3);ui_text(1,13,"FROM",13);ui_text(6,13,q->giver,15);
  ui_text(1,14,"REWARD",13);{int j,c=8;for(j=0;j<3;j++)if(q->reward[j]>=0){ui_text(c,14+(c>20),V12_ITEMS[q->reward[j]].name,15);c+=11;}}
  ui_text(1,16,"TRACKS THE NATIVE CAMPAIGN",13);}
 else if(lw_page==4){const V12Char*c=&V12_CHARS[lw_sel];int big=LW_CHR_BIG[lw_sel];
  ui_text(1,2,c->name,14);lw_wrap(4,c->look,15,3);lw_wrap(8,c->pose,13,3);ui_num(24,2,lw_sel+1,13);
  lw_copy32(LW_OBJ_TILES,LW_CHR_TILES[lw_sel],big?512:128);for(i=0;i<16;i++)OBJ_PALETTE[15*16+i]=LW_CHR_PAL[lw_sel][i];
  lw_obj(0,big?168:184,96,0,big?3:2,0,15,0,0);lw_dirty_art=1;
  ui_text(1,17,"UP/DOWN CAST  B BACK",13);}}
static void lw_render(void){if(lw_card)return;if(lw_page)lw_draw_page();else lw_draw_field();}
#endif /* HOST_QA */
#endif
