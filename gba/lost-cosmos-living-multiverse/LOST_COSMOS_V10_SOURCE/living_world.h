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
/* V12.3: 5 Mote forms (Smudge, Linework, Shading, Wash, Ink) + 6 bible characters. The six have no
   Cosmo portrait yet: they show a stand-in sheet and the CAST page says so (LW_CHR_STANDIN). */
static const u32*const LW_CHR_TILES[V12_CHAR_COUNT]={v12_cre_zeref_tiles,v12_chr_arin_tiles,v12_chr_mote_tiles,v12_chr_mote_linework_tiles,v12_chr_mote_shading_tiles,v12_chr_mote_wash_tiles,v12_chr_mote_ink_tiles,v12_chr_traveler_tiles,v12_chr_hollis_tiles,v12_chr_edric_tiles,v12_chr_bryn_tiles,v12_chr_quillan_tiles,v12_chr_hesper_tiles,v12_chr_grumbleback_tiles,v12_chr_rime_tiles,v12_chr_cinderwake_tiles,v12_chr_thorne_tiles,v12_chr_sethra_tiles,v12_chr_malakar_tiles,v12_chr_counterfeit_tiles,v12_chr_edric_tiles,v12_chr_traveler_tiles,v12_chr_traveler_tiles,v12_chr_quillan_tiles,v12_chr_quillan_tiles,v12_chr_hesper_tiles};
static const u16*const LW_CHR_PAL[V12_CHAR_COUNT]={v12_cre_zeref_pal,v12_chr_arin_pal,v12_chr_mote_pal,v12_chr_mote_linework_pal,v12_chr_mote_shading_pal,v12_chr_mote_wash_pal,v12_chr_mote_ink_pal,v12_chr_traveler_pal,v12_chr_hollis_pal,v12_chr_edric_pal,v12_chr_bryn_pal,v12_chr_quillan_pal,v12_chr_hesper_pal,v12_chr_grumbleback_pal,v12_chr_rime_pal,v12_chr_cinderwake_pal,v12_chr_thorne_pal,v12_chr_sethra_pal,v12_chr_malakar_pal,v12_chr_counterfeit_pal,v12_chr_edric_pal,v12_chr_traveler_pal,v12_chr_traveler_pal,v12_chr_quillan_pal,v12_chr_quillan_pal,v12_chr_hesper_pal};
static const u8 LW_CHR_BIG[V12_CHAR_COUNT]={1,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0};
static const u8 LW_CHR_STANDIN[V12_CHAR_COUNT]={0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1};
typedef char lw_chr_count_check[(V12_CHAR_COUNT==26)?1:-1];
static int lw_streq(const char*a,const char*b){while(*a&&*a==*b){a++;b++;}return *a==*b;}
static int lw_item(const char*id){int i;for(i=0;i<V12_ITEM_COUNT;i++)if(lw_streq(V12_ITEMS[i].id,id))return i;return -1;}
static u32 lw_rand(LwBeast*b){u32 x=b->rng?b->rng:0x9E3779B9u;x^=x<<13;x^=x>>17;x^=x<<5;b->rng=x;return x;}
static void lw_copy32(volatile u32*d,const u32*s,int words){while(words--)*d++=*s++;}
static void lw_say(const char*a,const char*b){int n=0;while(a&&*a&&n<84)lw_msg[n++]=*a++;while(b&&*b&&n<84)lw_msg[n++]=*b++;lw_msg[n]=0;lw_msg_timer=180;}
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
 b->base_spd=(u8)(4+(b->dna[13]>>1));b->base_focus=(u8)(4+(b->dna[14]>>1));b->base_luck=(u8)(b->dna[15]>>1);
 cst_seed(&b->cst,b->dna,b->entropy);}  /* V12.2: 12-D CST state from the same recorded window */
static int lw_stat(const LwBeast*b,int k){int v,i;
 v=k==0?b->base_hp+b->level*4:k==1?b->base_atk+b->level:k==2?b->base_def+b->level:k==3?b->base_spd+(b->level>>1):k==4?b->base_focus+(b->level>>1):b->base_luck;
 if(k<=4){static const u8 map[5]={0,1,2,3,4};for(i=0;i<4;i++)if(b->equip[i])v+=V12_ITEMS[b->equip[i]-1].st[map[k]];}
 return clampi(v,1,255);}
static void lw_defaults(void){int i;
 for(i=0;i<V12_ITEM_COUNT;i++)lw_inv[i]=0;for(i=0;i<5;i++)lw_claimed[i]=0;
 {static const char*const s[9]={"healing_herbs","glowcap","sunseed_snack","warm_ale","forge_lantern","tiny_scarf","hammer_blade","star_shard","wet_sock"};
  static const u8 n[9]={3,4,2,1,1,1,1,2,1};for(i=0;i<9;i++){int j=lw_item(s[i]);if(j>=0)lw_inv[j]=n[i];}}
 for(i=0;i<LW_N;i++){LwBeast*b=&lw_b[i];int j;b->hunger=(u8)(30+b->dna[16]);b->energy=(u8)(60+b->dna[17]);b->mood=(u8)(50+b->dna[18]);b->bond=(u8)(20+b->dna[19]);b->level=1;b->xp=0;for(j=0;j<4;j++)b->equip[j]=0;b->hp=(u8)lw_stat(b,0);}}
/* V12.3 layout 1: items 0..67 at +8..+75 (unchanged), items 68.. at +168 (free tail before the
   checksum). Layout byte +3: 0 = V12.0-V12.2 ids, migrated once on load; 1 = V12.3 canon ids. */
#define LW_LAYOUT 1
static int lw_inv_at(int i){return i<68?LW_SRAM+8+i:LW_SRAM+168+(i-68);}
typedef char lw_inv_fits[(V12_ITEM_COUNT<=68+80)?1:-1];
static u32 lw_sum_at(int base){u32 s=0x4C573132u;int i;for(i=0;i<252;i++)s=s*31u+SRAM[base+i];return s;}
#define lw_sum() lw_sum_at(LW_SRAM)
/* V12.1: V12.0 kept this block at 16384, inside journal bank 1. One-time migration:
   if the new block is not valid and a valid V12.0 block survives there, copy it
   (same bytes, same checksum rule). 16384 is never written again. */
static int lw_valid_at(int base){u32 s;if(SRAM[base]!='L'||SRAM[base+1]!='W'||SRAM[base+2]!=1)return 0;
 s=(u32)SRAM[base+252]|((u32)SRAM[base+253]<<8)|((u32)SRAM[base+254]<<16)|((u32)SRAM[base+255]<<24);return s==lw_sum_at(base);}
static void lw_migrate(void){int i;if(lw_valid_at(LW_SRAM)||!lw_valid_at(LW_SRAM_V120))return;for(i=0;i<256;i++)SRAM[LW_SRAM+i]=SRAM[LW_SRAM_V120+i];lw_migrated=1;}
/* V12.3 fix: the LW block lives in the tail of the journaled 8 KiB page, but cold boot restores
   that page from the latest committed journal bank, which was snapshotted at the last game save:
   Living World progress made after that save was lost on every reboot (V12.1-V12.2). Now each LW
   save also patches its 256 bytes into the latest valid bank and re-seals that bank (commit byte
   cleared first, set last). Game state in the bank is untouched; no new bank is committed. */
static void lw_journal_patch(void){int b=journal_latest();unsigned i,m,dst;if(b<0)return;
 m=JOURNAL_META+(unsigned)b*64;dst=(unsigned)(b+1)*JOURNAL_BYTES;SRAM[m+15]=0;
 for(i=0;i<256;i++)SRAM[dst+LW_SRAM+i]=SRAM[LW_SRAM+i];
 journal_write32(m+8,journal_crc(dst));SRAM[m+15]=0xa8;lw_journal_patches++;}
static void lw_save(void){int i,o;
 for(i=0;i<256;i++)SRAM[LW_SRAM+i]=0;
 SRAM[LW_SRAM]='L';SRAM[LW_SRAM+1]='W';SRAM[LW_SRAM+2]=1;SRAM[LW_SRAM+3]=LW_LAYOUT;SRAM[LW_SRAM+4]=lw_world;
 for(i=0;i<V12_ITEM_COUNT;i++)SRAM[lw_inv_at(i)]=lw_inv[i];
 for(i=0;i<LW_N;i++){LwBeast*b=&lw_b[i];o=LW_SRAM+76+i*12;
  SRAM[o]=b->hunger;SRAM[o+1]=b->energy;SRAM[o+2]=b->mood;SRAM[o+3]=b->bond;SRAM[o+4]=b->hp;SRAM[o+5]=b->level;
  SRAM[o+6]=(u8)b->xp;SRAM[o+7]=(u8)(b->xp>>8);SRAM[o+8]=b->equip[0];SRAM[o+9]=b->equip[1];SRAM[o+10]=b->equip[2];SRAM[o+11]=b->equip[3];}
 for(i=0;i<5;i++)SRAM[LW_SRAM+156+i]=lw_claimed[i];
 SRAM[LW_SRAM+164]=lw_end_d_flag;
 {u32 s=lw_sum();SRAM[LW_SRAM+252]=(u8)s;SRAM[LW_SRAM+253]=(u8)(s>>8);SRAM[LW_SRAM+254]=(u8)(s>>16);SRAM[LW_SRAM+255]=(u8)(s>>24);}
 lw_journal_patch();}
static int lw_load(void){int i,o;u32 s;
 lw_items_migrated=0;lw_migrate();
 if(SRAM[LW_SRAM]!='L'||SRAM[LW_SRAM+1]!='W'||SRAM[LW_SRAM+2]!=1)return 0;
 s=(u32)SRAM[LW_SRAM+252]|((u32)SRAM[LW_SRAM+253]<<8)|((u32)SRAM[LW_SRAM+254]<<16)|((u32)SRAM[LW_SRAM+255]<<24);
 if(s!=lw_sum())return 0;
 lw_world=SRAM[LW_SRAM+4]&1;
 if(SRAM[LW_SRAM+3]==0){ /* V12.3: V12.2 save, item ids remapped (CHANGES_canon.md) */
  for(i=0;i<V12_ITEM_COUNT;i++)lw_inv[i]=0;
  for(i=0;i<V12_OLD_ITEM_COUNT;i++){int n=V12_ITEM_MIGRATE[i];lw_inv[n]=(u8)mini(99,lw_inv[n]+SRAM[LW_SRAM+8+i]);}
  lw_items_migrated=1;}
 else for(i=0;i<V12_ITEM_COUNT;i++)lw_inv[i]=(u8)mini(99,SRAM[lw_inv_at(i)]);
 for(i=0;i<LW_N;i++){LwBeast*b=&lw_b[i];int j;o=LW_SRAM+76+i*12;
  b->hunger=(u8)mini(100,SRAM[o]);b->energy=(u8)mini(100,SRAM[o+1]);b->mood=(u8)mini(100,SRAM[o+2]);b->bond=(u8)mini(100,SRAM[o+3]);
  b->level=(u8)clampi(SRAM[o+5],1,99);b->xp=(u16)(SRAM[o+6]|(SRAM[o+7]<<8));
  for(j=0;j<4;j++){u8 e=SRAM[o+8+j];if(lw_items_migrated)e=(u8)(e&&e<=V12_OLD_ITEM_COUNT?V12_ITEM_MIGRATE[e-1]+1:0);b->equip[j]=(u8)(e<=V12_ITEM_COUNT?e:0);}
  b->hp=(u8)mini(lw_stat(b,0),SRAM[o+4]);}
 for(i=0;i<5;i++)lw_claimed[i]=SRAM[LW_SRAM+156+i];
 lw_end_d_flag=(u8)(SRAM[LW_SRAM+164]&1);
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
static int lw_dist(const LwBeast*b,s32 x,s32 y);
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
 for(j=0;j<16;j++)OBJ_PALETTE[14*16+j]=v12_wisp_pal[j];
 lw_npc_pal_dirty=1;}
/* The darkness wisp: a procedural 16x16 shadow blob with two eyes (code art). */
/* V12.1: Cosmo's wisp_dark sheet (32x32): drift 0-3, lunge 4-5 when close to Zeref. */
static int lw_wisp_frame(int phase){if(lw_dist(&lw_b[0],lw_wx,lw_wy)<72)return 4+(phase&1);return phase&3;}
static void lw_upload_wisp(int phase){int f=lw_wisp_frame(phase);if(f==lw_wisp_f)return;lw_wisp_f=(u8)f;if(f>=4)lw_wisp_lunges++;
 lw_copy32(LW_OBJ_TILES+LW_WISP_TILE*8,v12_wisp_tiles+f*16*8,16*8);}
/* V12.1: Arin idles on frames 0-5 and walks on 6-9 while the player moves. */
static void lw_upload_arin(void){int f=lw_pmoving?6+(int)(((u32)lw_clock>>3)&3u):(int)(((u32)lw_clock>>4)%6u);
 if(f==lw_arin_f)return;lw_arin_f=(u8)f;lw_copy32(LW_OBJ_TILES+480*8,v12_chr_arin_tiles+f*16*8,16*8);}
/* V12.1: one cast member lives in each world: Mote (64x64) in the forest, Rime (32x32)
   in the cave. Mote: idle 0-3, sneeze 4, yawn 5, walk 6-9. Humans: idle 0-5, walk 6-9. */
/* V12.2: Cosmo's shared character palettes (v12_assets/art/sprites/char_palette_map.json).
   Every char_<id>.pal is an exact copy of its group, so one member's table is the
   group's table. Field OBJ slots: 13 = warm (Arin + warm walker), 12 = cool (cool
   walker, Rime in the cave; slot 12 holds the item bank only on the ITEMS page),
   15 = Mote in the forest / dusk in the cave. */
#define LW_PAL_WARM v12_chr_arin_pal      /* arin hollis thorne sethra quillan cinderwake */
#define LW_PAL_COOL v12_chr_edric_pal     /* edric bryn hesper rime */
#define LW_PAL_DUSK v12_chr_traveler_pal  /* traveler malakar grumbleback counterfeit */
/* walkers per world: forest Hollis (warm) + Edric (cool); cave Thorne (warm) + Traveler (dusk) */
static const u32*const LW_WALK_TILES[2][LW_WALK_N]={{v12_chr_hollis_tiles,v12_chr_edric_tiles},{v12_chr_thorne_tiles,v12_chr_traveler_tiles}};
static const u8 LW_WALK_PAL[2][LW_WALK_N]={{13,12},{13,15}};
static void lw_upload_npc(int force){int big=lw_world==0,f,i;const u32*t=big?v12_chr_mote_tiles:v12_chr_rime_tiles;const u16*p=big?v12_chr_mote_pal:LW_PAL_DUSK;
 if(lw_npc_pal_dirty||force||lw_npc_w!=lw_world){for(i=0;i<16;i++){OBJ_PALETTE[15*16+i]=p[i];OBJ_PALETTE[12*16+i]=LW_PAL_COOL[i];OBJ_PALETTE[13*16+i]=LW_PAL_WARM[i];}lw_npc_pal_dirty=0;
  for(i=0;i<LW_WALK_N;i++)lw_walk_f[i]=255;}
 if(lw_npc.moving)f=6+(int)(((u32)lw_clock>>3)&3u);
 else if(big)f=lw_npc_beat==1?4:lw_npc_beat==2?5:(int)(((u32)lw_clock>>4)&3u);
 else f=(int)(((u32)lw_clock>>4)%6u);
 if(!force&&f==lw_npc_f&&lw_npc_w==lw_world)return;
 if(f!=lw_npc_f){if(f==4&&big)lw_sneezes++;if(f==5&&big)lw_yawns++;if(f>=6)lw_npc_walk_frames++;}
 lw_npc_f=(u8)f;lw_npc_w=lw_world;
 lw_copy32(LW_OBJ_TILES+LW_NPC_TILE*8,t+f*(big?64:16)*8,(big?64:16)*8);}
static void lw_upload_walkers(void){int k,f;
 for(k=0;k<LW_WALK_N;k++){LwBeast*n=&lw_walk[k];f=n->moving?6+(int)(((u32)(lw_clock+k*5)>>3)&3u):(int)(((u32)(lw_clock+k*9)>>4)%6u);
  if(f==lw_walk_f[k])continue;if(f>=6)lw_walk_frames++;lw_walk_f[k]=(u8)f;
  lw_copy32(LW_OBJ_TILES+(LW_WALK_TILE+k*16)*8,LW_WALK_TILES[lw_world][k]+f*16*8,16*8);}}
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
/* V12.3: creature_moods synapse_mood. The trigger still sets the action; the spoken line comes from
   a mood entry whose synapse_mood matches the creature's live CST-12 top mood (creatureMood), so
   Zeref says what he actually feels. Prefer the trigger's own line when it already matches; else
   the first matching entry among the CST-weighted triggers, rotating by the creature's RNG. */
static int lw_synapse_line(LwBeast*b,int t){int top=cst_top_mood(&b->cst),k,n=0,c[V12_MOOD_COUNT];
 if(V12_MOODS[t].synapse==top){lw_synapse_hits++;return t;}
 for(k=0;k<V12_MOOD_COUNT;k++)if(V12_MOODS[k].synapse==top)c[n++]=k;
 if(!n)return t;lw_synapse_swaps++;return c[lw_rand(b)%(u32)n];}
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
 if(t<0){/* V12.2: life-brain.mjs modeWeights from the CST mood (Q12 weights). */
  const Cst12*c=&b->cst;int en=b->energy*41,ng=lw_night?CST_ONE:0,k;u32 w[7],sum=0,r;
  static const u8 trig[7]={V12_TRIG_CURIOUS,V12_TRIG_TIRED,V12_TRIG_TOY_NEAR,V12_TRIG_FED_AND_RESTED,V12_TRIG_STILLING_NEAR,V12_TRIG_LONELY,V12_TRIG_LEANING_ROLL};
  w[0]=(u32)(2458+((c->curio*3686)>>12));                                     /* wander .6+cur*.9 */
  w[1]=(u32)(((cst_c(CST_ONE-en)*6554)>>12)+((ng*2867)>>12)+((c->calm*1638)>>12)); /* nap */
  w[2]=(u32)((c->joy*3686)>>12);                                              /* play joy*.9 */
  w[3]=(u32)(((c->mischief*4915)>>12)*(lw_night?4:1)>>2);                     /* chase mischief*1.2*night */
  w[4]=(u32)(205+((c->curio*328)>>12)+((c->fear*2048)>>12));                  /* glance/shelter */
  w[5]=(u32)(82+((((c->joy*c->curio)>>12)*328)>>12)+((c->ch[CST_DOMINANCE]*410)>>12)); /* approach */
  w[6]=(u32)(614);                                                            /* undecided */
  for(k=0;k<7;k++)sum+=w[k];r=lw_rand(b)%sum;
  for(k=0;k<6&&r>=w[k];k++)r-=w[k];t=trig[k];lw_cst_picks++;}
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
 if(i==lw_focus){int n=0;const char*s=V12_MOODS[lw_synapse_line(b,t)].line;while(lw_msg[n])n++;while(*s&&n<84)lw_msg[n++]=*s++;lw_msg[n]=0;}
 if(i==0&&t==V12_TRIG_DARK_NEARBY)lw_dark_reacts++;}
/* V12.2: CST Lorenz (rho modulated by arousal, x forced by quantum_entropy). */
static void lw_lorenz(LwBeast*b,int speed){(void)speed;cst_lorenz(&b->cst,&b->lx,&b->ly,&b->lz);}
/* V12.2: one CST-12 step per frame. World -> emotion targets (Q12). */
static void lw_cst(int i){LwBeast*b=&lw_b[i];int j,g=0,dd=lw_dist(b,lw_wx,lw_wy),val,aro,cur,fear;
 for(j=0;j<LW_N;j++)if(j!=i)g+=lw_b[j].cst.coh;g=(g*819)>>12;                       /* mean of 5 */
 val=b->mood*41;if(b->hunger>70)val-=(b->hunger-70)*40;
 aro=b->energy*20+(dd<130?1600:0)+(b->action==V12_ACT_ZOOMIES?1200:0)-(lw_night?600:0);
 cur=((b->entropy*41+b->cst.ch[CST_SPEC_FLAT]+b->cst.ch[CST_DOMINANCE])*1365)>>12;
 fear=dd<72?3600:dd<130?2000:300;if(b->bond>60)fear-=200;
 cst_step(&b->cst,val,aro,cur,fear,g,b->lx,b->ly);
 if(i==0&&cst_heartbeat(&b->cst)){lw_heartbeats++;                                      /* Zeref's heart */
  if(b->cst.reson>2700&&b->mood<100)b->mood++;else if(b->cst.fear>2900&&b->mood>0)b->mood--;}
 else if(i&&(lw_clock&63)==(u16)(i*8)){if(b->cst.reson>2700&&b->mood<100)b->mood++;else if(b->cst.fear>2900&&b->mood>0)b->mood--;}}
static void lw_tick_beast(int i){LwBeast*b=&lw_b[i];s32 vx,vy,ox=b->x,oy=b->y;int spd=lw_stat(b,3),act=b->action,still=0;
 lw_lorenz(b,spd);lw_cst(i);
 /* needs drift; V12.2: heavy frequency_mass ticks hunger slower, mischief burns energy */
 if((lw_clock&127)==(u16)(i*16)){if(b->hunger<100&&(b->cst.ch[CST_FREQ_MASS]<2800||(lw_clock&128)))b->hunger++;if(b->moving&&b->energy){b->energy--;if(b->cst.mischief>3000&&b->energy)b->energy--;}
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
  /* V12.2 motionParams: CST turbulence scales the wobble, speed = .75+mischief*.5
     slowed by frequency_mass, coherence smooths the steering. */
  int tb=cst_turb(&b->cst),sm=cst_speed(&b->cst),dm=cst_damp(&b->cst);
  vx=(b->lx*(20+b->entropy))>>12;vy=(b->ly*(20+b->entropy))>>12;
  vx=(vx*(2048+tb))>>12;vy=(vy*(2048+tb))>>12;
  if(iabs(gx)>512||iabs(gy)>512){vx+=((signi(gx)*(64+spd*4)*boost)*sm)>>12;vy+=((signi(gy)*(48+spd*3)*boost)*sm)>>12;
   vx=(vx*(6144-(dm>>1)))>>12;vy=(vy*(6144-(dm>>1)))>>12;}
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
static void lw_tick_npc(void){LwBeast*n=&lw_npc;s32 ox=n->x,oy=n->y,gx,gy;
 if(n->timer)n->timer--;else{u32 r=lw_rand(n);
  if((r&3)==0){n->tx=n->x>>8;n->ty=n->y>>8;lw_npc_beat=(u8)(lw_world==0?1+((r>>3)&1):0);n->timer=(u16)(48+(r>>8)%40u);}
  else{lw_npc_beat=0;lw_target(n,(int)((r>>4)%LW_W),(int)((r>>12)%LW_H));n->timer=(u16)(160+(r>>20)%120u);}}
 gx=(n->tx<<8)-n->x;gy=(n->ty<<8)-n->y;
 if(iabs(gx)>384)n->x+=signi(gx)*160;if(iabs(gy)>384)n->y+=signi(gy)*120;
 n->moving=(u8)(n->x!=ox||n->y!=oy);if(n->x!=ox)n->face=(u8)(n->x<ox);}
/* V12.2: cast walkers. Each has its own QSEED window and CST-12 state; calm
   walkers stroll, curious ones go further, frightened ones keep away from the wisp. */
static void lw_tick_walk(int k){LwBeast*n=&lw_walk[k];s32 ox=n->x,oy=n->y,gx,gy;int dd=lw_dist(n,lw_wx,lw_wy),sp;
 cst_lorenz(&n->cst,&n->lx,&n->ly,&n->lz);
 cst_step(&n->cst,2600,dd<130?3000:1600,(n->entropy*41),dd<90?3600:300,lw_b[0].cst.coh,n->lx,n->ly);
 if(n->timer)n->timer--;else{u32 r=lw_rand(n);int reach=64+((n->cst.curio*160)>>12);
  if(n->cst.fear>2600){lw_target(n,(n->x>>8)*2-(lw_wx>>8),(n->y>>8)*2-(lw_wy>>8));n->timer=90;}
  else if((r&3)==0||((u32)n->cst.calm>(r>>20))){n->tx=n->x>>8;n->ty=n->y>>8;n->timer=(u16)(60+(r>>8)%60u);}
  else{lw_target(n,(n->x>>8)+(int)((r>>4)%(u32)(2*reach))-reach,(n->y>>8)+(int)((r>>12)%(u32)reach)-(reach>>1));n->timer=(u16)(140+(r>>20)%120u);}}
 gx=(n->tx<<8)-n->x;gy=(n->ty<<8)-n->y;sp=(128*cst_speed(&n->cst))>>12;
 if(iabs(gx)>384)n->x+=signi(gx)*sp;if(iabs(gy)>384)n->y+=signi(gy)*((sp*3)>>2);
 n->x+=(n->lx*cst_turb(&n->cst))>>18;
 n->x=clampi(n->x,24<<8,(LW_W-24)<<8);n->y=clampi(n->y,40<<8,(LW_H-8)<<8);
 n->moving=(u8)((n->x>>8)!=(ox>>8)||(n->y>>8)!=(oy>>8));if((n->x>>8)!=(ox>>8))n->face=(u8)(n->x<ox);}
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
 lw_upload_bg();lw_upload_obj_pals();lw_arin_f=lw_wisp_f=255;lw_upload_arin();lw_upload_wisp(0);lw_upload_creatures(1);lw_upload_npc(1);
 for(i=0;i<128;i++)OAM16[i*4]=0x0200;ui_clear();
 REG_DISPCNT=MODE0|BG0_ENABLE|BG1_ENABLE|OBJ_ENABLE|OBJ_1D_MAP;lw_card=0;}
static void lw_card_show(void){int i;const u8*px=lw_world?v12_scene_cave_px:v12_scene_forest_px;const u16*p=lw_world?v12_scene_cave_pal:v12_scene_forest_pal;
 for(i=0;i<128;i++)OAM16[i*4]=0x0200;
 lw_copy32((volatile u32*)0x06000000,(const u32*)px,240*160/4);
 for(i=0;i<256;i++)BG_PALETTE[i]=p[i];
 LW_REG16(0x04000020)=0x100;LW_REG16(0x04000022)=0;LW_REG16(0x04000024)=0;LW_REG16(0x04000026)=0x100;LW_REG32(0x04000028)=0;LW_REG32(0x0400002C)=0;
 REG_BG2CNT=0;REG_DISPCNT=4|BG2_ENABLE;lw_card=1;lw_card_timer=150;}
/* V12.3 secret ending D 'The Passenger Seat' (bible 10). Requirement: Ending A + Bond 150 + all 12
   Corner Sketches. The cartridge's crown ending (MEM_ENDING) stands for Ending A and bond tops out at
   100 here, so: crown ending reached, Zeref bond 100, 12 corner_sketch. Unlocks once, grants last_map,
   remembered at LW+164 bit0. */
static volatile u8 lw_end_d=0;
static int lw_end_d_ready(void){int cs=lw_item("corner_sketch");
 return (cosmos.memory_flags&MEM_ENDING)&&lw_b[0].bond>=100&&cs>=0&&lw_inv[cs]>=12;}
static void lw_check_end_d(void){if(lw_end_d||!lw_end_d_ready())return;lw_end_d=1;lw_end_d_flag=1;
 {int lm=lw_item("last_map");if(lm>=0&&lw_inv[lm]<99)lw_inv[lm]++;}
 lw_say("SECRET ENDING D: ",V12_ENDINGS[V12_END_D][1]);lw_save();}
static void lw_seed_walkers(void){int i;static const u32 wid[2][LW_WALK_N]={{0x484F4C4Cu,0x45445249u},{0x54484F52u,0x54524156u}}; /* HOLL EDRI / THOR TRAV */
 for(i=0;i<LW_WALK_N;i++){LwBeast*n=&lw_walk[i];n->id=wid[lw_world&1][i];lw_dna(n,n->id);n->x=(s32)(120+i*200)<<8;n->y=(s32)(110+i*40)<<8;n->tx=n->x>>8;n->ty=n->y>>8;n->timer=(u16)(10+i*20);n->moving=0;lw_walk_f[i]=255;}}
static void lw_enter(void){int i;
 if(lw_active||game_mode!=MODE_SURFACE||cinema_active||intro||v108_credits_active||fp_active)return;
 for(i=0;i<0x18000/4;i++)((u32*)lw_vram_save)[i]=((volatile u32*)0x06000000)[i];
 for(i=0;i<512;i++){lw_pal_save[i]=lc_pal_shadow[i];lw_oam_save[i]=lc_oam_shadow[i];}
 for(i=0;i<1024;i++)lw_ui_save[i]=lc_ui_shadow[i];
 for(i=0;i<14;i++)lw_io_save[i]=lc_io_shadow[i];
 for(i=0;i<LW_N;i++){LwBeast*b=&lw_b[i];b->id=LW_IDS[i];lw_dna(b,b->id);
  b->x=(s32)(60+i*72)<<8;b->y=(s32)(80+(b->dna[20]<<2))<<8;b->tx=b->x>>8;b->ty=b->y>>8;b->timer=(u16)(20+i*15);b->trig=V12_TRIG_CURIOUS;b->action=V12_ACT_INVESTIGATE;b->found=0;b->since=0;b->frame=255;}
 lw_npc.rng=0x4D4F5445u^QSEED[103];lw_npc.x=200<<8;lw_npc.y=120<<8;lw_npc.tx=200;lw_npc.ty=120;lw_npc.timer=30;lw_npc_beat=0;
 lw_wl[0]=QSEED[100]*64+1;lw_wl[1]=QSEED[101]*64+1;lw_wl[2]=QSEED[102]*96+256;lw_wx=440<<8;lw_wy=200<<8;
 if(!lw_load())lw_defaults();
 lw_seed_walkers();
 lw_claim_quests();
 lw_end_d=lw_end_d_flag;lw_check_end_d();lw_end_d_flag=lw_end_d;
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
/* ---------- V12.3 boss battles (boss_battle.h logic + cartridge glue) ----------
   Each tick at most one frame is streamed: one 2 KB block (64 tiles) by DMA3 into OBJ tiles 0..63.
   Palette slot per boss: Grumbleback 9, Forest Guardian 10, Guardian Statues 11 (placeholder art).
   Later phases are also drawn bigger with the affine double-size OBJ (1.0x, 1.25x, 1.5x). */
#include "v12_boss.h"
#include "boss_battle.h"
static BossBattle lw_bt;
static volatile u8 lw_bt_active=0,lw_bt_kind=0,lw_bt_result=0,lw_bt_lastdir=0;
static volatile u16 lw_bt_dma_frames=0,lw_bt_wins=0,lw_bt_losses=0,lw_bt_starts=0;
static volatile u32 lw_bt_dma_bytes=0;
static const BBAnim*bb_anims(int k){return (const BBAnim*)(k==BB_GUARDIAN?V12_BOSS_GUARDIAN_ANIM:k==BB_STATUES?V12_BOSS_STATUE_ANIM:k==BB_MOTH?V12_BOSS_MOTH_ANIM:V12_BOSS_GRUMBLEBACK_ANIM);}
static int lw_boss_of(int q){return q==2?BB_GUARDIAN:q==3?BB_GRUMBLEBACK:q==4?BB_MOTH:q==5?BB_STATUES:-1;}
static void lw_dma3(volatile u32*dst,const u32*src,u32 words){LW_REG32(0x040000D4)=(u32)src;LW_REG32(0x040000D8)=(u32)dst;LW_REG32(0x040000DC)=words|0x84000000u;
 lw_bt_dma_frames++;lw_bt_dma_bytes+=words*4u;}
static const char*const LW_BT_NAME[BB_KINDS]={"GRUMBLEBACK","FOREST GUARDIAN","GUARDIAN STATUES","MOTH SWARM"};
static u8 lw_lane_up=0,lw_lane_arc=255,lw_lane_obj=0;
static void lw_bt_start(int kind){int i;const u16*p=kind==BB_GRUMBLEBACK?v12_boss_grumbleback_pal:kind==BB_GUARDIAN?v12_boss_guardian_pal:kind==BB_MOTH?v12_boss_moth_pal:v12_boss_statue_pal;
 bb_start(&lw_bt,kind,LW_IDS[0]^((u32)QSEED[110+kind]<<8)^lw_clock);lw_bt_kind=(u8)kind;lw_bt_active=1;lw_bt_result=0;lw_bt_starts++;
 for(i=0;i<16;i++)OBJ_PALETTE[(9+kind)*16+i]=p[i];
 lw_lane_up=0;lw_lane_arc=255;
 lw_copy32(LW_OBJ_TILES+384*8,LW_COMP_TILES[0],16*8);
 for(i=0;i<128;i++)OAM16[i*4]=0x0200;ui_clear();lc_sfx(SFX_CONFIRM);}
static void lw_bt_end(void){int i_unused_bt;lw_bt_active=0;lw_upload_obj_pals();lw_dirty_art=1;lw_page=3;ui_clear();
 for(i_unused_bt=0;i_unused_bt<128;i_unused_bt++)OAM16[i_unused_bt*4]=0x0200;}
static void lw_bt_update(u16 newk){int dir=(newk&KEY_LEFT)?-1:(newk&KEY_RIGHT)?1:0;
 if(dir)lw_bt_lastdir=(u8)(dir<0);
 if(lw_bt.state==BBS_WIN||lw_bt.state==BBS_LOSE){
  if(!lw_bt_result){lw_bt_result=(u8)(lw_bt.state==BBS_WIN?1:2);if(lw_bt_result==1){lw_bt_wins++;lc_sfx(SFX_BEFRIEND);}else lw_bt_losses++;ui_clear();}
  if(newk&(KEY_A|KEY_B))lw_bt_end();return;}
 if(newk&KEY_B){lw_bt_end();return;}
 bb_step(&lw_bt,dir,(newk&KEY_A)?1:0);}
static void lw_bt_render(void){int i,o=0;BossBattle*b=&lw_bt;
 {const u32*fr=b->kind==BB_GRUMBLEBACK?v12_boss_grumbleback_frames:b->kind==BB_GUARDIAN?v12_boss_guardian_frames:b->kind==BB_MOTH?v12_boss_moth_frames:v12_boss_statue_frames;
  if(bb_take_frame(b))lw_dma3(LW_OBJ_TILES,fr+(u32)b->frame*512u,512);}
 if(b->kind!=BB_STATUES){
  {int sc=256+b->phase*64,inv=(256*256)/sc;   /* affine group 0 */
   OAM16[0*4+3]=(u16)inv;OAM16[1*4+3]=0;OAM16[2*4+3]=0;OAM16[3*4+3]=(u16)inv;
   OAM16[0]=(u16)(((24-32)&255)|0x0300);OAM16[1]=(u16)(((120-64)&511)|(3u<<14));OAM16[2]=(u16)(0|(1u<<10)|((9+b->kind)<<12));}
  lw_obj(1,104+(b->dodge?(lw_bt_lastdir?-28:28):0),118,0,2,384,6,0,0);o=2;}
 else{ /* Cosmo lane art: warning tiles at OBJ 64..79 (4 frames x 4 tiles), arcs at 80..95 (one 64x32 frame) */
  int st=b->swing,wf=st==0?0:st==1?1+((b->timer/6)&1):st==2?2:3,l,r;
  if(!lw_lane_up){lw_copy32(LW_OBJ_TILES+64*8,v12_lane_warn,16*8);lw_lane_up=1;}
  if(st>=1&&st<=4&&b->state==BBS_LANES){int af=st==4?2+(((12-b->timer)/3)&3):st>=2?2+((b->timer/6)&1):((b->timer/8)&1);
   const u32*src=st==4?v12_lane_swing+(af-2)*256:v12_lane_tele+(af&3)*256;if(af!=lw_lane_arc){lw_copy32(LW_OBJ_TILES+80*8,src,256);lw_lane_arc=(u8)af;}}
  lw_obj(0,88,0,0,3,0,11,0,0);o=1;
  if(b->state==BBS_LANES)for(l=0;l<3;l++)if(b->lanes_mask&(1u<<l)){int x=72+l*32;
   for(r=0;r<4;r++){lw_obj(o++,x,64+r*16,0,1,64+wf*4,11,0,0);lw_obj(o++,x+16,64+r*16,0,1,64+wf*4,11,1,0);}
   if(st>=1&&st<=4)lw_obj(o++,x-16,st==4?88:72,1,3,80,11,0,0);}
  lw_obj(o++,72+b->lane*32,124,0,2,384,6,0,0);lw_lane_obj=(u8)o;}
 for(i=o;i<128;i++)OAM16[i*4]=0x0200;
 ui_fill_rows(0,1,62,15);ui_fill_rows(16,19,62,15);
 ui_text(1,0,LW_BT_NAME[b->kind],14);ui_text(20,0,"PHASE",13);ui_num(26,0,b->phase+1>b->nphases?b->nphases:b->phase+1,15);
 ui_text(1,1,"ZEREF",13);for(i=0;i<BB_ZHP;i++)ui_text(7+i,1,i<b->zhp?"*":"-",i<b->zhp?9:13);
 if(b->kind!=BB_STATUES){ui_text(15,1,"BOSS",13);for(i=0;i<BB_PHASE_HP;i++)ui_text(20+i,1,i<b->hp?"#":"-",14);}
 else{ui_text(15,1,"SWEEPS",13);ui_num(22,1,b->sweeps,15);}
 if(lw_bt_result){ui_text(1,16,lw_bt_result==1?(b->kind==BB_GRUMBLEBACK?"CALM NOW. A KITTEN CROWN!":b->kind==BB_GUARDIAN?"THE GUARDIAN BOWS.":b->kind==BB_MOTH?"MOTHS REST ON THE LANTERN.":"THE STATUES REST."):"ZEREF NEEDS A REST.",14);ui_text(1,18,"A/B BACK",13);}
 else{ui_text(1,17,b->kind==BB_STATUES?"L/R LANE. WATCH THE EYES.":b->state==BBS_ATTACK&&b->hit_ok==1?"NOW! PRESS A":"L/R DODGE. A WHEN OPEN",b->hit_ok==1?14:13);
  ui_text(1,18,"B FLEE",13);}}
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
 if(lw_bt_active){lw_bt_update(newk);return;}
 {u8 night=(u8)((((u32)lw_clock/1800u)&1u));if(night!=lw_night){lw_night=night;lw_upload_bg();}}
 for(i=0;i<LW_N;i++)lw_tick_beast(i);
 lw_tick_wisp();
 lw_tick_npc();
 for(i=0;i<LW_WALK_N;i++)lw_tick_walk(i);
 if((lw_clock&1023)==0)lw_save();
 if(lw_page){int max=lw_page==1?lw_owned_count():lw_page==3?V12_QUEST_COUNT:lw_page==4?V12_CHAR_COUNT:1;
  if(lw_page!=5&&(newk&KEY_B)){lw_page=0;ui_clear();lw_dirty_art=1;lc_sfx(SFX_CANCEL);return;}
  if(lw_page!=5&&(newk&KEY_START)){lw_page=(u8)(lw_page>=4?1:lw_page+1);lw_sel=0;ui_clear();lw_dirty_art=1;lc_sfx(SFX_MOVE);return;}
  if(newk&KEY_UP){lw_sel=(u8)(lw_sel?lw_sel-1:(max?max-1:0));ui_clear();}
  if(newk&KEY_DOWN){lw_sel=(u8)(max&&lw_sel+1<max?lw_sel+1:0);ui_clear();}
  if(newk&(KEY_L|KEY_R)){lw_focus=(u8)((u32)(lw_focus+((newk&KEY_R)?1:LW_N-1))%(u32)LW_N);ui_clear();}
  if(lw_page==5){if(newk&KEY_B){lw_page=3;lw_sel=lw_scene_q;ui_clear();return;}
   if(newk&(KEY_A|KEY_DOWN)){if(lw_scene_k+1<V12_QUEST_BOXN[lw_scene_q])lw_scene_k++;else{lw_page=3;lw_sel=lw_scene_q;}ui_clear();lw_scene_reads++;}
   if((newk&KEY_UP)&&lw_scene_k)lw_scene_k--,ui_clear();return;}
  if((newk&KEY_SELECT)&&lw_page==3&&V12_QUEST_BOXN[lw_sel]){lw_scene_q=lw_sel;lw_scene_k=0;lw_page=5;ui_clear();return;}
  if((newk&KEY_A)&&lw_page==3&&lw_boss_of(lw_sel)>=0){lw_bt_start(lw_boss_of(lw_sel));return;}
  if((newk&KEY_A)&&lw_page==1){int it=lw_owned(lw_sel);if(it>=0)lw_use(it);ui_clear();}
  return;}
 if(newk&KEY_B){lw_exit();return;}
 if(newk&KEY_START){lw_page=1;lw_sel=0;ui_clear();lc_sfx(SFX_CONFIRM);return;}
 if(newk&KEY_SELECT){lw_world^=1;lw_upload_bg();lw_seed_walkers();lw_say(lw_world?"THE CRYSTAL CAVE.":"THE VIOLET FOREST.",0);lw_save();}
 if(newk&(KEY_L|KEY_R)){lw_focus=(u8)((u32)(lw_focus+((newk&KEY_R)?1:LW_N-1))%(u32)LW_N);lw_say("WATCHING ",LW_NAMES[lw_focus]);}
 {int run=(k&KEY_A)?0:1;s32 sp=(s32)(run?384:384);
  {s32 opx=lw_px,opy=lw_py;
  if(k&KEY_LEFT){lw_px-=sp;lw_pface=1;}if(k&KEY_RIGHT){lw_px+=sp;lw_pface=0;}if(k&KEY_UP)lw_py-=sp;if(k&KEY_DOWN)lw_py+=sp;
  lw_px=clampi(lw_px,16<<8,(LW_W-16)<<8);lw_py=clampi(lw_py,40<<8,(LW_H-4)<<8);lw_pmoving=(u8)(opx!=lw_px||opy!=lw_py);}}
 if(newk&KEY_A){for(i=0;i<LW_N;i++)if(lw_dist(&lw_b[i],lw_px,lw_py)<40){LwBeast*b=&lw_b[i];
   int asleep=b->action==V12_ACT_NAP||b->action==V12_ACT_COLLAPSE_SLEEP;
   b->trig=asleep?V12_TRIG_WOKEN_UP:V12_TRIG_PETTED;b->action=V12_MOODS[b->trig].action;b->timer=120;
   if(!asleep){if(b->mood<100)b->mood=(u8)mini(100,b->mood+8);if(b->bond<100)b->bond++;}
   lw_focus=(u8)i;lw_say(LW_NAMES[i],": ");{int n=0;const char*s=V12_MOODS[b->trig].line;while(lw_msg[n])n++;while(*s&&n<84)lw_msg[n++]=*s++;lw_msg[n]=0;}
   lc_sfx(SFX_BEFRIEND);break;}}
 lw_camx=(s16)clampi((lw_px>>8)-120,0,LW_W-240);lw_camy=(s16)clampi((lw_py>>8)-80,0,LW_H-160);}
/* ---------- render ---------- */
static void lw_line(int y,const char*s,int pal){char t[29];int n=0;while(s&&*s&&n<28)t[n++]=*s++;t[n]=0;ui_text(1,y,t,pal);}
/* Word wrap. V12.2: a width (max LW_TEXT_W = 28 characters, the Living World
   line width), a number of lines to skip first (HUD scroll), and the number of
   lines the whole text needs (lw_wrap_lines) so nothing is silently dropped. */
#define LW_TEXT_W 28
static const char*lw_wrap_next(const char*s,int w,int*cut){int n,len;for(len=0;s[len]&&len<=w;)len++;*cut=len<=w?len:w;
 if(len>w){for(n=w;n>0&&s[n]!=' ';)n--;if(n>0)*cut=n;}return s;}
static int lw_wrap_lines(const char*s,int w){int l=0,cut;while(s&&*s){lw_wrap_next(s,w,&cut);s+=cut;while(*s==' ')s++;l++;}return l;}
static void lw_wrapw(int y,const char*s,int pal,int lines,int w,int skip){char t[LW_TEXT_W+1];int l,n,cut;
 if(w>LW_TEXT_W)w=LW_TEXT_W;
 for(l=-skip;l<lines&&s&&*s;l++){lw_wrap_next(s,w,&cut);
  if(l>=0){for(n=0;n<cut;n++)t[n]=s[n];t[n]=0;ui_text(1,y+l,t,pal);}s+=cut;while(*s==' ')s++;}}
static void lw_wrap(int y,const char*s,int pal,int lines){lw_wrapw(y,s,pal,lines,LW_TEXT_W,0);}
static void lw_hud(void){LwBeast*b=&lw_b[lw_focus];
 ui_fill_rows(0,0,62,15);ui_fill_rows(16,19,62,15);
 ui_text(1,0,"LIVING WORLD",14);ui_text(14,0,lw_world?"CAVE":"FOREST",13);ui_text(21,0,lw_night?"NIGHT":"DAY",13);
 ui_text(1,16,LW_NAMES[lw_focus],14);ui_text(12,16,V12_ACT_NAMES[b->action],13);
 ui_text(1,17,"HU",13);ui_num(4,17,b->hunger,15);ui_text(8,17,"EN",13);ui_num(11,17,b->energy,15);
 ui_text(15,17,"MO",13);ui_num(18,17,b->mood,15);ui_text(22,17,"LV",13);ui_num(25,17,b->level,15);
 if(lw_msg_timer){int nl=lw_wrap_lines(lw_msg,LW_TEXT_W);lw_msg_timer--;
  /* V12.2: a message that needs a third line scrolls up one line halfway through */
  if(nl>2&&lw_msg_timer<90){ui_fill_rows(18,19,62,15);lw_wrapw(18,lw_msg,15,2,LW_TEXT_W,nl-2);lw_hud_scrolls++;}else lw_wrap(18,lw_msg,15,2);}
 else lw_line(18,V12_MOODS[b->trig].name,14);}
static void lw_draw_field(void){int i,o=0;
 REG_BG0HOFS=(u16)lw_camx;REG_BG0VOFS=(u16)lw_camy;
 lw_upload_creatures(lw_dirty_art);
 if(lw_dirty_art){lw_arin_f=255;lw_wisp_f=255;lw_npc_pal_dirty=1;}
 if((lw_clock&7)==0||lw_wisp_f==255)lw_upload_wisp(lw_clock>>3);
 lw_upload_arin();lw_upload_npc(lw_dirty_art);lw_dirty_art=0;
 lw_obj(o++,(lw_px>>8)-lw_camx-16,(lw_py>>8)-lw_camy-30,0,2,480,13,lw_pface,1);
 lw_obj(o++,(lw_wx>>8)-lw_camx-16,(lw_wy>>8)-lw_camy-16+((lw_clock>>4)&1),0,2,LW_WISP_TILE,14,0,1);
 {int nx=(lw_npc.x>>8)-lw_camx,ny=(lw_npc.y>>8)-lw_camy;if(lw_world==0)lw_obj(o++,nx-32,ny-60,0,3,LW_NPC_TILE,15,lw_npc.face,1);else lw_obj(o++,nx-16,ny-30,0,2,LW_NPC_TILE,12,lw_npc.face,1);}
 lw_upload_walkers();
 for(i=0;i<LW_WALK_N;i++){LwBeast*n=&lw_walk[i];lw_obj(o++,(n->x>>8)-lw_camx-16,(n->y>>8)-lw_camy-30,0,2,LW_WALK_TILE+i*16,LW_WALK_PAL[lw_world][i],n->face,1);}
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
   {static const char*const sn[8]={"HP","AT","DF","SP","FO","MO","HU","EN"};int c=11,j;for(j=0;j<8;j++)if(v->st[j]){ui_text(c,14,sn[j],13);if(v->st[j]<0){ui_text(c+2,14,"-",7);ui_num(c+3,14,-v->st[j],7);}else ui_num(c+2,14,v->st[j],9);c+=6;if(c>26)break;}}
   ui_text(1,16,"A USE  L/R BEAST  B BACK",13);
   lw_upload_icon(it);
   {int ip=V12_ITEM_BANK[it]?15:12;for(i=0;i<16;i++){OBJ_PALETTE[15*16+i]=v12_items_b_pal[i];OBJ_PALETTE[12*16+i]=v12_items_pal[i];}lw_npc_pal_dirty=1;
   if(v->sheet==0)lw_obj(0,200,24,0,1,500,ip,0,0);else if(v->sheet==1)lw_obj(0,192,24,1,2,500,ip,0,0);else lw_obj(0,200,20,2,2,500,ip,0,0);}}}}
 else if(lw_page==2){static const char*const sn[6]={"HP","ATK","DEF","SPD","FOCUS","LUCK"};static const char*const slot[4]={"WEAPON","ARMOR","ACCESS","LIGHT"};char id[12];int j;u32 v=b->id;
  for(j=0;j<6;j++){ui_text(1,2+j,sn[j],13);ui_num(8,2+j,lw_stat(b,j),15);}
  ui_text(1,8,"HP NOW",13);ui_num(8,8,b->hp,15);ui_text(14,2,"HUNGER",13);ui_num(22,2,b->hunger,15);ui_text(14,3,"ENERGY",13);ui_num(22,3,b->energy,15);
  ui_text(14,4,"MOOD",13);ui_num(22,4,b->mood,15);ui_text(14,5,"BOND",13);ui_num(22,5,b->bond,15);ui_text(14,6,"LEVEL",13);ui_num(22,6,b->level,15);ui_text(14,7,"ENTROPY",13);ui_num(22,7,b->entropy,15);
  for(j=0;j<4;j++){ui_text(1,10+j,slot[j],13);ui_text(8,10+j,b->equip[j]?V12_ITEMS[b->equip[j]-1].name:"-",15);}
  id[0]='I';id[1]='D';id[2]=' ';for(j=0;j<8;j++){u32 d=(v>>(28-4*j))&15;id[3+j]=(char)(d<10?'0'+d:'A'+d-10);}id[11]=0;ui_text(1,15,id,13);
  ui_text(1,16,"DNA: RECORDED IBM QSEED DATA",13);ui_text(1,17,"LIFE: CLASSICAL CST-12 SIM",13);
  /* V12.2: the CST-12 mood (creatureMood) and coherence */
  ui_text(14,8,"CST",13);ui_text(18,8,CST_MOOD_NAMES[cst_top_mood(&b->cst)],15);ui_text(14,9,"COHERE",13);ui_num(22,9,(b->cst.coh*100)>>12,15);
  ui_text(1,14,"JOY",13);ui_num(5,14,(b->cst.joy*100)>>12,15);ui_text(9,14,"CALM",13);ui_num(14,14,(b->cst.calm*100)>>12,15);ui_text(18,14,"FEAR",13);ui_num(23,14,(b->cst.fear*100)>>12,15);}
 else if(lw_page==3){int start=(int)((u32)lw_sel/7u)*7;const V12Quest*q=&V12_QUESTS[lw_sel];static const char*const st[3]={"LOCKED","OPEN","DONE"};
  for(r=0;r<7&&start+r<V12_QUEST_COUNT;r++){int s=lw_quest_state(start+r);ui_text(1,2+r,start+r==lw_sel?">":" ",14);ui_text(2,2+r,"A",13);ui_num(3,2+r,V12_QUESTS[start+r].act,13);ui_text(5,2+r,V12_QUESTS[start+r].name,start+r==lw_sel?14:15);ui_text(23,2+r,st[s],s==2?9:s==1?14:13);}
  lw_wrap(10,q->summary,15,3);ui_text(1,13,"FROM",13);ui_text(6,13,q->giver,15);
  ui_text(1,14,"REWARD",13);{int j,c=8;for(j=0;j<3;j++)if(q->reward[j]>=0){ui_text(c,14+(c>20),V12_ITEMS[q->reward[j]].name,15);c+=11;}}
  ui_text(1,16,q->biome,9);lw_wrapw(17,q->place,13,1,LW_TEXT_W,0);
  if(V12_QUEST_BOXN[lw_sel])ui_text(17,18,"SEL SCENES",13);
  if(lw_boss_of(lw_sel)>=0)ui_text(1,18,lw_quest_state(lw_sel)?"A FIGHT BOSS":"A PRACTICE BOSS",14);}
 else if(lw_page==4){const V12Char*c=&V12_CHARS[lw_sel];int big=LW_CHR_BIG[lw_sel];
  /* V12.2: bios are no longer cut at 3 lines; the pose wraps at 20 columns so it
     never runs under the portrait. */
  ui_text(1,2,c->name,14);lw_wrapw(3,c->look,15,8,LW_TEXT_W,0);lw_wrapw(11,c->pose,13,5,20,0);ui_num(24,2,lw_sel+1,13);
  if(lw_sel>=2&&lw_sel<2+V12_MOTE_FORMS){static const char*const form[V12_MOTE_FORMS]={"FORM 1 OF 5","FORM 2 OF 5","FORM 3 OF 5","FORM 4 OF 5","FORM 5 OF 5"};ui_text(1,16,form[lw_sel-2],14);lw_cast_form=(u8)(lw_sel-1);}
  if(LW_CHR_STANDIN[lw_sel])ui_text(1,16,"STAND-IN ART",13);
  {int f,cyc=(int)(((u32)lw_clock>>4)%16u);
   if(lw_sel==0)f=cyc<12?cyc:12+(cyc&3);                    /* Zeref: idle 0-5, 4-leg walk 6-11, react_dark 12-15 */
   else if(big)f=cyc<10?cyc:(cyc&3);                         /* Mote: idle 0-3, sneeze 4, yawn 5, walk 6-9 */
   else f=cyc<10?cyc:(cyc%6);                                /* humans: idle 0-5, walk 6-9 */
   lw_cast_f=(u8)f;lw_copy32(LW_OBJ_TILES,LW_CHR_TILES[lw_sel]+f*(big?512:128),big?512:128);}for(i=0;i<16;i++)OBJ_PALETTE[15*16+i]=LW_CHR_PAL[lw_sel][i];
  lw_obj(0,big?168:184,96,0,big?3:2,0,15,0,0);lw_dirty_art=1;
  ui_text(1,17,"UP/DOWN CAST  B BACK",13);}}
static void lw_draw_scene(void){const V12Box*x=&V12_SCENE_BOX[V12_QUEST_BOX0[lw_scene_q]+lw_scene_k];int i;
 for(i=0;i<128;i++)OAM16[i*4]=0x0200;ui_fill_rows(0,19,62,15);
 ui_text(1,0,V12_QUESTS[lw_scene_q].name,14);ui_num(25,0,lw_scene_k+1,13);
 ui_text(1,4,x->who,9);for(i=0;i<3;i++)ui_text(1,6+i,x->l[i],15);
 if(V12_QUEST_BOSS[lw_scene_q][0]){ui_text(1,12,"BOSS",13);lw_wrapw(13,V12_QUEST_BOSS[lw_scene_q],15,2,LW_TEXT_W,0);
  if(lw_boss_of(lw_scene_q)<0)ui_text(1,15,"BOSS ART PENDING: NOT FOUGHT YET",13);}
 ui_text(1,18,"A NEXT  UP BACK  B QUESTS",13);}
static void lw_render(void){if(lw_card)return;if(lw_bt_active){lw_bt_render();return;}if(lw_page==5)lw_draw_scene();else if(lw_page)lw_draw_page();else lw_draw_field();}
#endif /* HOST_QA */
#endif
