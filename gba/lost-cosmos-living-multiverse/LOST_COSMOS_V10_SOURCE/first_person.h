/* V11.6 FIRST-PERSON / MODE-7 VIEW. See first_person_state.h for the
   design and the Beast Cage camera it follows. */
#ifndef FIRST_PERSON_H
#define FIRST_PERSON_H
#define FP_D 188                /* 80/tan(23 deg): the cage's 46 deg FOV */
#define FP_EYE_H 14             /* eye height in pixels */
#define FP_UNIT 8               /* one cage unit = one 8 px map tile */
#define FP_CB 2                 /* charblock 2 (cinema tiles) */
#define FP_SB 29                /* screenblocks 29-30 (space/cinema maps) */
/* Cage constants in 4096-per-turn units (651.9 per radian). */
#define FP_PHI_MIN 228          /* 0.35 rad */
#define FP_PHI_MAX 958          /* 1.47 rad */
#define FP_PHI_CAGE 685         /* 1.05 rad, the cage default */
#define FP_PHI_EYE 913          /* 1.40 rad: eye level, a little down */
#define FP_PHI_STEP 91          /* 0.14 rad per press */
#define FP_TURN 18              /* per frame while held */
#define FP_MAX_SPRITES 12
/* The HBlank DMA source keeps advancing if a frame's work runs past a
   vblank and the channel is not re-armed. Each buffer therefore holds the
   160 scanlines FP_RING times in a row: a late frame simply shows the same
   picture again instead of reading past the table. */
#define FP_RING 4
#define FP_LINES (FP_RING*160+1)
#ifdef HOST_QA
#define FP_EWRAM
#else
#define FP_EWRAM __attribute__((section(".ewram")))
#endif
typedef struct { s16 pa,pb,pc,pd; int x,y; } FpLine; /* = REG_BG2PA..BG2Y */
static FpLine fp_lines[2][FP_LINES] FP_EWRAM;
static u16 fp_sky[2][FP_LINES+1] FP_EWRAM __attribute__((aligned(4))); /* even rows: 32-bit copies */
static u16 fp_hkey[512] FP_EWRAM;
static u8 fp_hslot[512] FP_EWRAM;
static u8 fp_front=0,fp_ready=0;
static u16 fp_saved_disp=0,fp_saved_bg2=0,fp_saved_pal16=0;
static int fp_camx=0,fp_camy=0,fp_H=FP_EYE_H,fp_sinp=0,fp_cosp=0,fp_fx=0,fp_fy=0,fp_rx=0,fp_ry=0;
static const s16 FP_SIN[256]={0,402,804,1205,1606,2006,2404,2801,3196,3590,3981,4370,4756,5139,5520,5897,6270,6639,7005,7366,7723,8076,8423,8765,9102,9434,9760,10080,10394,10702,11003,11297,11585,11866,12140,12406,12665,12916,13160,13395,13623,13842,14053,14256,14449,14635,14811,14978,15137,15286,15426,15557,15679,15791,15893,15986,16069,16143,16207,16261,16305,16340,16364,16379,16384,16379,16364,16340,16305,16261,16207,16143,16069,15986,15893,15791,15679,15557,15426,15286,15137,14978,14811,14635,14449,14256,14053,13842,13623,13395,13160,12916,12665,12406,12140,11866,11585,11297,11003,10702,10394,10080,9760,9434,9102,8765,8423,8076,7723,7366,7005,6639,6270,5897,5520,5139,4756,4370,3981,3590,3196,2801,2404,2006,1606,1205,804,402,0,-402,-804,-1205,-1606,-2006,-2404,-2801,-3196,-3590,-3981,-4370,-4756,-5139,-5520,-5897,-6270,-6639,-7005,-7366,-7723,-8076,-8423,-8765,-9102,-9434,-9760,-10080,-10394,-10702,-11003,-11297,-11585,-11866,-12140,-12406,-12665,-12916,-13160,-13395,-13623,-13842,-14053,-14256,-14449,-14635,-14811,-14978,-15137,-15286,-15426,-15557,-15679,-15791,-15893,-15986,-16069,-16143,-16207,-16261,-16305,-16340,-16364,-16379,-16384,-16379,-16364,-16340,-16305,-16261,-16207,-16143,-16069,-15986,-15893,-15791,-15679,-15557,-15426,-15286,-15137,-14978,-14811,-14635,-14449,-14256,-14053,-13842,-13623,-13395,-13160,-12916,-12665,-12406,-12140,-11866,-11585,-11297,-11003,-10702,-10394,-10080,-9760,-9434,-9102,-8765,-8423,-8076,-7723,-7366,-7005,-6639,-6270,-5897,-5520,-5139,-4756,-4370,-3981,-3590,-3196,-2801,-2404,-2006,-1606,-1205,-804,-402};
static int fp_sin(int a){return FP_SIN[(a>>4)&255];}
static int fp_cos(int a){return FP_SIN[((a>>4)+64)&255];}
/* Signed quotient through the unsigned helper: the cartridge has no
   __aeabi_idiv. */
static int fp_div(int a,int b){int neg=0;u32 q;if(!b)return 0;if(a<0){a=-a;neg=1;}if(b<0){b=-b;neg^=1;}q=(u32)a/(u32)b;return neg?-(int)q:(int)q;}
static int fp_mul14(int a,int b){return (int)(((long long)a*b)>>14);}

/* ---------- affine copy of the field map ---------- */
static u16 fp_map_entry(int x,int y){int block=(x>=32)+((y>=32)<<1);return screenblock(BG_MAP_BASE+block)[(y&31)*32+(x&31)];}
static u8 fp_px(u16 e,int x,int y){int t=e&1023,pal=(e>>12)&15,c;u16 h;
 if(e&0x400)x=7-x;if(e&0x800)y=7-y;
 h=VRAM16[t*16+y*2+(x>>2)];c=(h>>((x&3)*4))&15;
 /* Colour 0 is the field backdrop; slot 16 holds a copy of it so the
    affine layer stays opaque inside the map. */
 return (u8)(c?pal*16+c:16);}
static void fp_convert(u16 e,int slot){int x,y;volatile u16*d=VRAM16+(FP_CB*0x4000+slot*64)/2;
 for(y=0;y<8;y++)for(x=0;x<8;x+=2)d[y*4+(x>>1)]=(u16)(fp_px(e,x,y)|(fp_px(e,x+1,y)<<8));}
static int fp_find(u16 e){u32 h=((u32)e*40503u>>7)&511;
 while(fp_hslot[h]){if(fp_hkey[h]==e)return fp_hslot[h];h=(h+1)&511;}return -(int)h-1;}
static int fp_slot(u16 e){int f=fp_find(e),h;u16 alt;int p;
 if(f>0)return f;
 if(fp_unique<255){h=-f-1;fp_unique++;fp_hkey[h]=e;fp_hslot[h]=(u8)fp_unique;fp_convert(e,fp_unique);return fp_unique;}
 /* Out of the 255 affine tiles: drop the shade bank, then the flip. */
 fp_overflow++;p=(e>>12)&15;
 alt=(u16)((e&0x0FFF)|((p==8?0:p==9?1:p==10?3:p==11?4:p)<<12));f=fp_find(alt);if(f>0)return f;
 alt&=0xF3FF;f=fp_find(alt);return f>0?f:0;}
static void fp_build(void){int x,y,i,tx=player.x>>3,ty=player.y>>3,pass;volatile u16*map=screenblock(FP_SB);
 volatile u16*d=VRAM16+(FP_CB*0x4000)/2;
 for(i=0;i<512;i++)fp_hslot[i]=0;fp_unique=0;fp_overflow=0;
 for(i=0;i<32;i++)d[i]=0x1010; /* slot 0: backdrop */
 /* Near the player first, so the tiles in view win the 255 slots. */
 for(pass=0;pass<2;pass++)for(y=0;y<64;y++)for(x=0;x<64;x+=2){
  int near0=iabs(x-tx)<=18&&iabs(y-ty)<=18,near1=iabs(x+1-tx)<=18&&iabs(y-ty)<=18;
  if(pass==0&&!near0&&!near1)continue;
  if(pass==1&&near0&&near1)continue;
  map[(y*64+x)>>1]=(u16)(fp_slot(fp_map_entry(x,y))|(fp_slot(fp_map_entry(x+1,y))<<8));
 }}

/* ---------- hardware ---------- */
#ifndef HOST_QA
#define FP_IO16(a) (*(volatile u16*)(a))
#define FP_IO32(a) (*(volatile u32*)(a))
static void fp_dma_stop(void){FP_IO16(0x040000BA)=0;FP_IO16(0x040000C6)=0;}
static void fp_vblank(void){const FpLine*l;
 if(!fp_active||!fp_ready)return;
 fp_dma_stop();l=&fp_lines[fp_front][0];
 FP_IO16(0x04000020)=(u16)l->pa;FP_IO16(0x04000022)=0;FP_IO16(0x04000024)=(u16)l->pc;FP_IO16(0x04000026)=0;
 FP_IO32(0x04000028)=(u32)l->x;FP_IO32(0x0400002C)=(u32)l->y;
 FP_IO16(0x05000000)=fp_sky[fp_front][0];
 /* HBlank DMA: one line of affine parameters and one backdrop colour per
    scanline. No interrupts are needed. */
 FP_IO32(0x040000B0)=(u32)&fp_lines[fp_front][1];FP_IO32(0x040000B4)=0x04000020u;FP_IO16(0x040000B8)=4;
 FP_IO16(0x040000BA)=0x8000|0x2000|0x0400|0x0200|0x0060;
 FP_IO32(0x040000BC)=(u32)&fp_sky[fp_front][1];FP_IO32(0x040000C0)=0x05000000u;FP_IO16(0x040000C4)=1;
 FP_IO16(0x040000C6)=0x8000|0x2000|0x0200|0x0040;}
#else
static void fp_dma_stop(void){}
static void fp_vblank(void){}
#endif

/* ---------- camera ---------- */
static u16 fp_mix(int t){ /* t 0..32: night zenith to horizon haze */
 int r=2+((12*t)>>5),g=3+((17*t)>>5),b=10+((17*t)>>5);return RGB5(r,g,b);}
/* Per-scanline ground distance depends only on the camera height and
   pitch, so the divisions run when those change; turning and walking only
   rotate and move the cached lines. */
static int fp_lam[160],fp_fwd[160];
static u16 fp_skyc[160] __attribute__((aligned(4)));
static int fp_cache_key=-1;
static void fp_lines_for_pitch(void){int y,hz=-1;
 for(y=0;y<160;y++){int yc=y-80,den=FP_D*fp_sinp+yc*fp_cosp;fp_lam[y]=0;fp_fwd[y]=0;
  if(den>(1<<13)){u32 lam=((u32)fp_H<<22)/(u32)den;
   if(lam<6000){int fwd=fp_mul14((int)lam,FP_D*fp_cosp-yc*fp_sinp);
    if(fwd<1100*256){fp_lam[y]=(int)lam;fp_fwd[y]=fwd;if(hz<0)hz=y;}}}}
 fp_horizon=(s16)(hz<0?160:hz);
 for(y=0;y<160;y++)fp_skyc[y]=y>=fp_horizon?fp_mix(32):fp_mix((int)((u32)(y*32)/(u32)(fp_horizon>0?fp_horizon:1)));}
static void fp_copy32(void*dst,const void*src,int bytes){
#ifdef HOST_QA
 int i;for(i=0;i<bytes/4;i++)((u32*)dst)[i]=((const u32*)src)[i];
#else
 lc_blit32(src,(u32)dst,(u32)(bytes/32));
#endif
}
static void fp_compute(void){int b=fp_front^1,y,ph=fp_phi[fp_cam],p=1024-ph,B,key,r;FpLine*L=fp_lines[b];u16*sky=fp_sky[b];
 fp_sinp=fp_sin(p);fp_cosp=fp_cos(p);
 if(fp_cam==FP_CAM_EYE){fp_H=FP_EYE_H;B=0;}
 else{int R=(int)((u32)(fp_zoom10*FP_UNIT)/10u);fp_H=(R*fp_cos(ph))>>14;B=(R*fp_sin(ph))>>14;if(fp_H<4)fp_H=4;}
 key=(fp_cam<<12)|ph;if(key!=fp_cache_key){fp_cache_key=key;fp_lines_for_pitch();}
 fp_fx=fp_sin(fp_heading);fp_fy=-fp_cos(fp_heading);fp_rx=fp_cos(fp_heading);fp_ry=fp_sin(fp_heading);
 /* Orbit position: the camera sits B pixels behind the focus. */
 fp_camx=player.x*256-((B*fp_fx)>>6);fp_camy=player.y*256-((B*fp_fy)>>6);
 {int fx=fp_fx>>4,fy=fp_fy>>4;
  for(y=0;y<160;y++){int lam=fp_lam[y];
   if(lam){int pa=(lam*fp_rx)>>14,pc=(lam*fp_ry)>>14,f=fp_fwd[y]>>2;
    L[y].pa=(s16)pa;L[y].pc=(s16)pc;L[y].pb=L[y].pd=0;
    L[y].x=fp_camx+((f*fx)>>8)-120*pa;L[y].y=fp_camy+((f*fy)>>8)-120*pc;}
   else{L[y].pa=L[y].pb=L[y].pc=L[y].pd=0;L[y].x=-(2048*256);L[y].y=0;}}}
 fp_copy32(sky,fp_skyc,160*2);
 for(r=1;r<FP_RING;r++){fp_copy32(&L[r*160],L,160*16);fp_copy32(&sky[r*160],sky,160*2);}
 L[FP_RING*160]=L[0];sky[FP_RING*160]=sky[0];
 fp_front=(u8)b;fp_ready=1;}
/* World point on the ground -> screen point and sprite scale (8.8). */
static int fp_project(int wx,int wy,int*sx,int*sy,int*scale){
 int rx=wx-(fp_camx>>8),ry=wy-(fp_camy>>8),zf=rx*fp_fx+ry*fp_fy,xr=rx*fp_rx+ry*fp_ry,zc,yd,zpx;
 zc=fp_mul14(zf,fp_cosp)+fp_H*fp_sinp;yd=fp_H*fp_cosp-fp_mul14(zf,fp_sinp);
 if(zc<(6<<14))return 0;
 *sx=120+fp_div(FP_D*(xr>>6),zc>>6);*sy=80+fp_div(FP_D*(yd>>6),zc>>6);
 zpx=zc>>14;*scale=clampi(fp_div(FP_D*128,zpx),48,512);return 1;}

/* ---------- sprites ---------- */
typedef struct { int z,sx,sy,scale; u16 tile; u8 pal,size,kind; u32 identity; } FpSprite;
static void fp_put(int oi,const FpSprite*s){int S=s->size?32:16,h=(S*s->scale)>>8,cx=s->sx,cy=s->sy-(h>>1),inv=(int)(65536u/(u32)s->scale);
 if(cx<-2*S||cx>240+2*S||cy<-2*S||cy>160+2*S){OAM16[oi*4]=0x0200;return;}
 if(s->kind==2){lc_draw_import_field(oi,8,8,0,0,s->identity);}
 else{OAM16[oi*4+2]=(u16)(s->tile|(1u<<10)|(s->pal<<12));}
 OAM16[oi*4]=(u16)(((cy-S)&255)|0x0100|0x0200);
 OAM16[oi*4+1]=(u16)(((cx-S)&511)|(oi<<9)|((s->size?2u:1u)<<14));
 OAM16[(oi*4+0)*4+3]=(u16)inv;OAM16[(oi*4+1)*4+3]=0;OAM16[(oi*4+2)*4+3]=0;OAM16[(oi*4+3)*4+3]=(u16)inv;}
static int fp_add(FpSprite*list,int n,int wx,int wy,u16 tile,u8 pal,u8 size,u8 kind,u32 id){FpSprite s;
 if(n>=FP_MAX_SPRITES||!fp_project(wx,wy,&s.sx,&s.sy,&s.scale))return n;
 s.z=(wx-(fp_camx>>8))*fp_fx+(wy-(fp_camy>>8))*fp_fy;s.tile=tile;s.pal=pal;s.size=size;s.kind=kind;s.identity=id;list[n]=s;return n+1;}
static void fp_sprites(void){FpSprite list[FP_MAX_SPRITES];int n=0,i,j;LcCreature*c=lc_party.count?&lc_party.slots[lc_party.active]:0;
 int bx=fp_beast_x>>8,by=fp_beast_y>>8;fp_beast_sx=fp_beast_sy=-99;fp_beast_scale=0;
 oam_hide_all();
 if(c){u8 sp=c->species;
  if(sp>=1&&sp<=8)n=fp_add(list,n,bx,by,(u16)(384+(sp-1)*24+mini(2,c->stage)*8+((frame>>4)&1)*4),(u8)(4+sp),0,1,c->identity);
  else if(lc_has_import_art(c))n=fp_add(list,n,bx,by,0,0,1,2,c->identity);
  else{u8 typ=(u8)(sp%EN_COUNT);n=fp_add(list,n,bx,by,(u16)(60+typ*4),(u8)(5+typ),0,1,c->identity);}
  if(n){fp_beast_sx=(s16)list[n-1].sx;fp_beast_sy=(s16)list[n-1].sy;fp_beast_scale=(s16)list[n-1].scale;}}
 if(fp_cam==FP_CAM_CAGE)n=fp_add(list,n,player.x,player.y,(u16)(576+(0*4+(player.anim&3))*4),0,0,0,0);
 if(V11_IS_ROOM){for(i=0;i<v11_npc_count;i++)n=fp_add(list,n,v11_npc_x[i],v11_npc_y[i],(u16)(128+i*16),14,1,0,0);}
 else for(i=0;i<npc_count;i++){NPC*q=&npc_runtime[i];n=fp_add(list,n,q->x,q->y,(u16)(92+q->kind*8+((frame>>4)&1)*4),(u8)(13+(q->kind&1)),0,0,0);}
 /* Nearest first: lower OAM numbers draw on top. */
 for(i=1;i<n;i++){FpSprite t=list[i];j=i;while(j>0&&list[j-1].z>t.z){list[j]=list[j-1];j--;}list[j]=t;}
 for(i=0;i<n;i++)fp_put(i,&list[i]);}

/* ---------- mode ---------- */
static void fp_beast_target(int*tx,int*ty){
 if(fp_cam==FP_CAM_EYE){*tx=player.x+((fp_fx*40+fp_rx*14)>>14);*ty=player.y+((fp_fy*40+fp_ry*14)>>14);}
 else{*tx=player.x+((fp_rx*16)>>14);*ty=player.y+((fp_ry*16)>>14);}}
static void fp_enter(void){static const u16 face_heading[4]={0,2048,3072,1024};int tx,ty;
 if(fp_active||game_mode!=MODE_SURFACE||cinema_active||intro||v108_credits_active)return;
 if(V11_IS_ROOM&&(v11_wild||v11_shop||v11_dialogue||v11_lore||v11_gameover))return;
 if(npc_dialogue_active||shop_open)return;
 fp_saved_disp=REG_DISPCNT;fp_saved_bg2=REG_BG2CNT;fp_saved_pal16=BG_PALETTE[16];
 fp_heading=face_heading[player.face&3];fp_cam=FP_CAM_EYE;
 fp_phi[FP_CAM_EYE]=FP_PHI_EYE;fp_phi[FP_CAM_CAGE]=FP_PHI_CAGE;fp_zoom10=106;
 fp_sub_x=fp_sub_y=0;fp_walked=fp_turned=0;
 fp_fx=fp_sin(fp_heading);fp_fy=-fp_cos(fp_heading);fp_rx=fp_cos(fp_heading);fp_ry=fp_sin(fp_heading);
 fp_beast_target(&tx,&ty);fp_beast_x=tx*256;fp_beast_y=ty*256;
 fp_build();fp_cache_key=-1;
 BG_PALETTE[16]=BG_PALETTE[0];
 REG_BG2CNT=(u16)(1|(FP_CB<<2)|(FP_SB<<8)|(2u<<14));
 REG_DISPCNT=(u16)(1|BG1_ENABLE|BG2_ENABLE|OBJ_ENABLE|OBJ_1D_MAP);
 fp_active=1;fp_ready=0;fp_entries++;
 oam_hide_all();ui_clear();fp_compute();lc_sfx(SFX_CONFIRM);}
static void fp_exit(void){
 if(!fp_active)return;
 fp_dma_stop();fp_active=0;fp_ready=0;fp_exits++;
 REG_DISPCNT=fp_saved_disp;REG_BG2CNT=fp_saved_bg2;BG_PALETTE[16]=fp_saved_pal16;
 player.anim=0;oam_hide_all();ui_clear();refresh_camera();lc_sfx(SFX_CANCEL);}
static void fp_update(u16 k,u16 newk){int sp=0,run=(k&KEY_B)!=0,speed=run?3:2,dx,dy,tx,ty;
 if(newk&(KEY_SELECT|KEY_START)){fp_exit();return;}
 if(newk&KEY_A){fp_cam^=1;lc_sfx(SFX_MOVE);}
 if(newk&KEY_L)fp_phi[fp_cam]=(s16)clampi(fp_phi[fp_cam]-FP_PHI_STEP,FP_PHI_MIN,FP_PHI_MAX);
 if(newk&KEY_R)fp_phi[fp_cam]=(s16)clampi(fp_phi[fp_cam]+FP_PHI_STEP,FP_PHI_MIN,FP_PHI_MAX);
 if(k&KEY_LEFT){fp_heading=(u16)((fp_heading-FP_TURN)&4095);fp_turned++;}
 if(k&KEY_RIGHT){fp_heading=(u16)((fp_heading+FP_TURN)&4095);fp_turned++;}
 fp_fx=fp_sin(fp_heading);fp_fy=-fp_cos(fp_heading);fp_rx=fp_cos(fp_heading);fp_ry=fp_sin(fp_heading);
 if(k&KEY_UP)sp=1;else if(k&KEY_DOWN)sp=-1;
 fp_sub_x=(s16)(fp_sub_x+((sp*speed*fp_fx)>>6));fp_sub_y=(s16)(fp_sub_y+((sp*speed*fp_fy)>>6));
 dx=fp_sub_x>>8;dy=fp_sub_y>>8;fp_sub_x=(s16)(fp_sub_x-dx*256);fp_sub_y=(s16)(fp_sub_y-dy*256);
 if(dx||dy){int ox=player.x,oy=player.y;move_player(dx,dy,run);fp_walked=(u16)(fp_walked+iabs(player.x-ox)+iabs(player.y-oy));}
 else if(!sp)player.anim=0;
 if(player.hurt)player.hurt--;
 /* The beast keeps pace beside the player and never walks into a wall. */
 fp_beast_target(&tx,&ty);
 {int nx=fp_beast_x+((tx*256-fp_beast_x)>>2),ny=fp_beast_y+((ty*256-fp_beast_y)>>2);
  if(!blocked_px(nx>>8,fp_beast_y>>8))fp_beast_x=nx;if(!blocked_px(fp_beast_x>>8,ny>>8))fp_beast_y=ny;
  if(iabs((fp_beast_x>>8)-player.x)+iabs((fp_beast_y>>8)-player.y)>64){fp_beast_x=tx*256;fp_beast_y=ty*256;}}}
static void fp_render(void){static const char*dir[4]={"N","E","S","W"};
 fp_compute();fp_sprites();
 ui_clear();ui_fill_rows(0,0,62,15);
 ui_text(1,0,fp_cam==FP_CAM_EYE?"EYE VIEW":"CAGE VIEW",14);
 ui_text(11,0,V11_IS_ROOM?v11_short_world():location_name(),13);
 ui_text(28,0,dir[((fp_heading+512)>>10)&3],15);
 ui_fill_rows(19,19,62,15);ui_text(1,19,"A CAM  L R TILT  SELECT MAP",15);}
#endif
