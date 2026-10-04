typedef unsigned char  u8;
typedef signed char    s8;
typedef unsigned short u16;
typedef signed short   s16;
typedef unsigned int   u32;

#include "qseed.h"

/* ================================================================
   SIM EARTH // PIXEL UNIVERSE: THE LOST COSMOS V2
   Native Game Boy Advance tile/sprite exploration engine.
   No consciousness claim: COSMOS is an explicit simulated agent.
   ================================================================ */

#define REG_DISPCNT    (*(volatile u16*)0x04000000)
#define REG_BG0CNT     (*(volatile u16*)0x04000008)
#define REG_BG1CNT     (*(volatile u16*)0x0400000A)
#define REG_BG0HOFS    (*(volatile u16*)0x04000010)
#define REG_BG0VOFS    (*(volatile u16*)0x04000012)
#define REG_BG1HOFS    (*(volatile u16*)0x04000014)
#define REG_BG1VOFS    (*(volatile u16*)0x04000016)
#define REG_VCOUNT     (*(volatile u16*)0x04000006)
#define REG_KEYINPUT   (*(volatile u16*)0x04000130)
#define REG_SOUNDCNT_L (*(volatile u16*)0x04000080)
#define REG_SOUNDCNT_H (*(volatile u16*)0x04000082)
#define REG_SOUNDCNT_X (*(volatile u16*)0x04000084)
#define REG_SOUND1CNT_L (*(volatile u16*)0x04000060)
#define REG_SOUND1CNT_H (*(volatile u16*)0x04000062)
#define REG_SOUND1CNT_X (*(volatile u16*)0x04000064)

#define BG_PALETTE ((volatile u16*)0x05000000)
#define OBJ_PALETTE ((volatile u16*)0x05000200)
#define VRAM16      ((volatile u16*)0x06000000)
#define VRAM32      ((volatile u32*)0x06000000)
#define OBJ_VRAM32  ((volatile u32*)0x06010000)
#define OAM16       ((volatile u16*)0x07000000)
#define SRAM        ((volatile u8*)0x0E000000)

#define MODE0       0
#define BG0_ENABLE  (1u<<8)
#define BG1_ENABLE  (1u<<9)
#define OBJ_ENABLE  (1u<<12)
#define OBJ_1D_MAP  (1u<<6)
#define KEY_A       (1u<<0)
#define KEY_B       (1u<<1)
#define KEY_SELECT  (1u<<2)
#define KEY_START   (1u<<3)
#define KEY_RIGHT   (1u<<4)
#define KEY_LEFT    (1u<<5)
#define KEY_UP      (1u<<6)
#define KEY_DOWN    (1u<<7)
#define KEY_R       (1u<<8)
#define KEY_L       (1u<<9)
#define RGB5(r,g,b) ((u16)((r)|((g)<<5)|((b)<<10)))
#define BG_MAP_BASE 24
#define UI_MAP_BASE 28
#define BG_TILE_CB  0
#define UI_TILE_CB  1
#define MAP_W 64
#define MAP_H 64
#define MAP_PX 512
#define ARRAY_LEN(a) ((int)(sizeof(a)/sizeof((a)[0])))

/* Save type scanner used by Delta/mGBA. */
__attribute__((used)) static const char SAVE_TYPE[] = "SRAM_V113";

/* ---------- basic helpers ---------- */
static int iabs(int v){ return v<0?-v:v; }
static int clampi(int v,int a,int b){ return v<a?a:(v>b?b:v); }
static int mini(int a,int b){ return a<b?a:b; }
static int maxi(int a,int b){ return a>b?a:b; }
static int signi(int v){ return (v>0)-(v<0); }
static int wrapi(int v,int m){ while(v<0)v+=m; while(v>=m)v-=m; return v; }
static void copystr(char*d,const char*s,int n){ int i=0; while(i<n-1 && s[i]){d[i]=s[i];i++;}d[i]=0; }
static void appendstr(char*d,const char*s,int n){ int i=0,j=0; while(i<n-1 && d[i])i++; while(i<n-1 && s[j])d[i++]=s[j++]; d[i]=0; }
static void wait_vblank(void){ while(REG_VCOUNT>=160){} while(REG_VCOUNT<160){} }
static void vram_copy32(volatile u32* dst,const u32*src,int words){ int i; for(i=0;i<words;i++) dst[i]=src[i]; }

/* ---------- 5x7 font, A-Z 0-9 and punctuation ---------- */
static const u8 FONT[43][5]={
 {0x7E,0x11,0x11,0x11,0x7E},{0x7F,0x49,0x49,0x49,0x36},{0x3E,0x41,0x41,0x41,0x22},{0x7F,0x41,0x41,0x22,0x1C},
 {0x7F,0x49,0x49,0x49,0x41},{0x7F,0x09,0x09,0x09,0x01},{0x3E,0x41,0x49,0x49,0x7A},{0x7F,0x08,0x08,0x08,0x7F},
 {0x41,0x41,0x7F,0x41,0x41},{0x20,0x40,0x41,0x3F,0x01},{0x7F,0x08,0x14,0x22,0x41},{0x7F,0x40,0x40,0x40,0x40},
 {0x7F,0x02,0x0C,0x02,0x7F},{0x7F,0x04,0x08,0x10,0x7F},{0x3E,0x41,0x41,0x41,0x3E},{0x7F,0x09,0x09,0x09,0x06},
 {0x3E,0x41,0x51,0x21,0x5E},{0x7F,0x09,0x19,0x29,0x46},{0x26,0x49,0x49,0x49,0x32},{0x01,0x01,0x7F,0x01,0x01},
 {0x3F,0x40,0x40,0x40,0x3F},{0x1F,0x20,0x40,0x20,0x1F},{0x3F,0x40,0x38,0x40,0x3F},{0x63,0x14,0x08,0x14,0x63},
 {0x03,0x04,0x78,0x04,0x03},{0x61,0x51,0x49,0x45,0x43},
 {0x3E,0x51,0x49,0x45,0x3E},{0x00,0x42,0x7F,0x40,0x00},{0x42,0x61,0x51,0x49,0x46},{0x21,0x41,0x45,0x4B,0x31},
 {0x18,0x14,0x12,0x7F,0x10},{0x27,0x45,0x45,0x45,0x39},{0x3C,0x4A,0x49,0x49,0x30},{0x01,0x71,0x09,0x05,0x03},
 {0x36,0x49,0x49,0x49,0x36},{0x06,0x49,0x49,0x29,0x1E},
 {0x00,0x08,0x08,0x08,0x00}, /* - */
 {0x20,0x10,0x08,0x04,0x02}, /* / */
 {0x00,0x36,0x36,0x00,0x00}, /* : */
 {0x00,0x60,0x60,0x00,0x00}, /* . */
 {0x02,0x01,0x51,0x09,0x06}, /* ? */
 {0x00,0x06,0x09,0x09,0x06}, /* o */
 {0x00,0x00,0x5F,0x00,0x00}  /* ! */
};
static int font_index(char c){
 if(c>='A'&&c<='Z')return c-'A'; if(c>='0'&&c<='9')return 26+c-'0';
 if(c=='-')return 36; if(c=='/')return 37; if(c==':')return 38; if(c=='.')return 39;
 if(c=='?')return 40; if(c=='*')return 41; if(c=='!')return 42; return -1;
}

/* ---------- tile IDs ---------- */
enum {T_VOID=0,T_FLOOR=1,T_GRASS=2,T_WATER=3,T_WALL=4,T_PATH=5,T_LAVA=6,T_METAL=7,T_ARCHIVE=8,T_PLANT=9,T_BRIDGE=10,T_CROWN=11,T_DOOR=12,T_LIFT=13,T_HAZARD=14,T_STAR=15,T_PAD=16,T_RUIN=17,T_TREE=18,T_CRYSTAL=19,T_MAX=20};
enum {C_FREE=0,C_WALL=1,C_HAZARD=2};
enum {TR_NONE=0,TR_SHIP=1,TR_DOOR=2,TR_EXIT=3,TR_KEY_X=4,TR_KEY_Y=5,TR_KEY_Z=6,TR_LIFT=7,TR_TERMINAL=8,TR_SECRET=9,TR_CROWN_CORE=10,TR_ANOMALY=11};
enum {MODE_SURFACE=0,MODE_SPACE=1,MODE_PAUSE=2};
enum {GOAL_FOLLOW=0,GOAL_EXPLORE,GOAL_INSPECT,GOAL_WAIT,GOAL_RETURN,GOAL_WARN,GOAL_SEEK_KEY,GOAL_SEEK_MEMORY,GOAL_APPROACH,GOAL_AVOID,GOAL_BOARD,GOAL_REST,GOAL_WANDER,GOAL_COUNT};

typedef struct { u16 attr0,attr1,attr2,pad; } ObjAttr;
typedef struct { s16 x,y; s8 dx,dy; u8 face,anim,run,hp,hurt; } Actor;
typedef struct { s16 x,y; s8 vx,vy; u8 goal,mood,trust,curiosity,avoid,energy,focus,cooldown; u16 memory_flags; } Buddy;
typedef struct { u8 world,room,layer; s16 x,y; } Beacon;

typedef struct {
 const char*name; u16 base0,base1,base2,accent; u8 music;
} WorldDef;
static const WorldDef WORLDS[6]={
 {"ORIGIN EARTH",RGB5(3,8,13),RGB5(6,18,13),RGB5(7,22,28),RGB5(19,31,26),0},
 {"EMBER AXIS",RGB5(10,3,2),RGB5(20,6,3),RGB5(31,13,4),RGB5(31,25,8),1},
 {"TIDE MEMORY",RGB5(2,5,12),RGB5(3,14,20),RGB5(4,24,29),RGB5(18,31,31),2},
 {"BLOOM Z",RGB5(2,8,3),RGB5(5,18,5),RGB5(10,28,11),RGB5(24,31,14),3},
 {"BLACK GARDEN",RGB5(2,1,4),RGB5(6,2,9),RGB5(13,5,18),RGB5(28,8,31),4},
 {"SYNAPSE CROWN",RGB5(4,3,10),RGB5(10,7,20),RGB5(18,13,29),RGB5(8,31,29),5}
};

/* Space positions in the 512x512 navigable star map. */
static const s16 PLANET_X[6]={256,405,105,365,72,452};
static const s16 PLANET_Y[6]={260,150,365,430,84,70};
static const u8 PLANET_COL[6]={1,2,3,4,5,6};

/* Runtime map state in IWRAM. */
static u8 collision[MAP_W*MAP_H];
static u8 trigger[MAP_W*MAP_H];
static Actor player;
static Buddy cosmos;
static Beacon beacons[8];
static u8 beacon_count=0;
static u8 current_world=0,current_room=0,current_layer=1,game_mode=MODE_SURFACE,return_mode=MODE_SURFACE;
static u8 keys_found=0,visited_mask=1,secrets_mask=0,chapter=0,ending=0,cosmos_preference=0,player_choice=0;
static u8 postgame=0,audio_on=1,pause_sel=0,pause_page=0;
static u16 frame=0,prev_keys=0;
static s16 cam_x=0,cam_y=0;
static u32 qi=0;
static u8 state12[12],state42[42],state54[54];
static char dialogue[90];
static u16 dialogue_timer=0;
static u8 pending_choice=0;
static s16 ship_x=256,ship_y=280;
static u8 ship_world=0;
static u16 music_tick=0;
static u16 anomaly_counter=0;
static u8 intro=1;

/* Memory bits. */
#define MEM_ORIGIN_ARCHIVE (1u<<0)
#define MEM_BLACK_GARDEN   (1u<<1)
#define MEM_PLAYER_HELPED  (1u<<2)
#define MEM_IGNORED        (1u<<3)
#define MEM_SECRET         (1u<<4)
#define MEM_ENDING         (1u<<5)
#define MEM_ANOMALY        (1u<<6)
#define MEM_SHIP           (1u<<7)

/* ---------- quantum tape ---------- */
static u8 next_q(void){ u8 v=QSEED[qi++]; if(qi>=QSEED_LEN)qi=0; return v; }
static u8 qpick(u8 n){ u8 v=next_q(); while(v>=n && n && v>=(u8)(n*8)) v=(u8)(v-n); return n?(u8)(v%n):0; }

/* ---------- VRAM map helpers ---------- */
static volatile u16* screenblock(int sb){ return VRAM16 + sb*1024; }
static void set_map_entry(int x,int y,u16 value){
 int block=(x>=32)+((y>=32)<<1); int idx=(y&31)*32+(x&31); screenblock(BG_MAP_BASE+block)[idx]=value;
}
static u16 map_attr(int tile,int pal){ return (u16)(tile | (pal<<12)); }
static void ui_clear(void){ int i; volatile u16*m=screenblock(UI_MAP_BASE); for(i=0;i<1024;i++)m[i]=0; }
static void ui_fill_rows(int y0,int y1,int tile,int pal){ int x,y; volatile u16*m=screenblock(UI_MAP_BASE); for(y=y0;y<=y1;y++)for(x=0;x<30;x++)m[y*32+x]=map_attr(tile,pal); }
static void ui_text(int x,int y,const char*s,int pal){ volatile u16*m=screenblock(UI_MAP_BASE); while(*s&&x<30){ int g=font_index(*s++); m[y*32+x]=(g<0)?0:map_attr(64+g,pal); x++; } }
static void ui_num(int x,int y,int v,int pal){ char b[8]; int i=0,n=v,d=1000,started=0;if(n<0){b[i++]='-';n=-n;}while(d){int q=0;while(n>=d){n-=d;q++;}if(q||started||d==1){b[i++]=(char)('0'+q);started=1;}d/=10;}b[i]=0;ui_text(x,y,b,pal);}

/* ---------- tile generation ---------- */
static void tile_pixel(u32*t,int x,int y,u8 c){ int w=y*1+(x>>3)*8; int lx=x&7; u32 mask=(u32)15<<(lx*4); t[w]=(t[w]&~mask)|((u32)(c&15)<<(lx*4)); }
static void upload_bg_tile(int id,const u32*t){ vram_copy32(VRAM32 + id*8,t,8); }
static void make_bg_tile(int id,int type){ u32 t[8];int x,y;for(y=0;y<8;y++)t[y]=0;for(y=0;y<8;y++)for(x=0;x<8;x++){
 u8 c=1;
 if(type==T_VOID)c=((x+y)&7)==0?2:0;
 else if(type==T_FLOOR)c=((x*3+y*5)&7)==0?2:1;
 else if(type==T_GRASS)c=((x+y)&3)==0?3:1;
 else if(type==T_WATER)c=((y+(frame>>3))&3)==0?3:2;
 else if(type==T_WALL)c=(x==0||y==0||x==7||y==7)?3:2;
 else if(type==T_PATH)c=((x+y)&1)?1:2;
 else if(type==T_LAVA)c=((y+(x>>1))&3)==0?3:2;
 else if(type==T_METAL)c=(x==0||y==0||x==7||y==7||x==y)?3:1;
 else if(type==T_ARCHIVE)c=((x==1||x==6||y==1||y==6)?3:1);
 else if(type==T_PLANT)c=(x==3||x==4||y==4)?3:1;
 else if(type==T_BRIDGE)c=(y==1||y==6)?3:1;
 else if(type==T_CROWN)c=((x+y)&3)==0?3:1;
 else if(type==T_DOOR)c=(x==1||x==6||y==1)?3:2;
 else if(type==T_LIFT)c=(x==y||x==7-y)?3:1;
 else if(type==T_HAZARD)c=((x+y+(frame>>2))&2)?3:2;
 else if(type==T_STAR)c=((x==3&&y==3)||(x==4&&y==3)||(x==3&&y==4))?3:0;
 else if(type==T_PAD)c=(x==0||x==7||y==0||y==7)?3:1;
 else if(type==T_RUIN)c=((x+y)&1)?2:3;
 else if(type==T_TREE)c=(x==3||x==4||y<3)?3:1;
 else if(type==T_CRYSTAL)c=(x==3||x==4||((x==2||x==5)&&y>2))?3:0;
 tile_pixel(t,x,y,c);
 }upload_bg_tile(id,t);}
static void make_ui_tiles(void){ int g,x,y;u32 t[8]; /* tile 63 opaque panel */
 for(y=0;y<8;y++)t[y]=0x22222222u; vram_copy32(VRAM32 + (0x4000/4) + 63*8,t,8);
 for(g=0;g<43;g++){for(y=0;y<8;y++)t[y]=0;for(x=0;x<5;x++)for(y=0;y<7;y++)if(FONT[g][x]&(1u<<y))tile_pixel(t,x+1,y,1);vram_copy32(VRAM32 + (0x4000/4) + (64+g)*8,t,8);}
}
static void make_all_tiles(void){ int i; for(i=0;i<T_MAX;i++)make_bg_tile(i,i); make_ui_tiles(); }

/* ---------- object sprite generation ---------- */
static void objpix(u32*b,int x,int y,u8 c){ int tile=(x>>3)+((y>>3)<<1),ly=y&7,lx=x&7,idx=tile*8+ly;u32 mask=(u32)15<<(lx*4);b[idx]=(b[idx]&~mask)|((u32)(c&15)<<(lx*4)); }
static void upload_obj16(int base,const u32*b){ vram_copy32(OBJ_VRAM32+base*8,b,32); }
static void gen_player_frame(int base,int face,int step){ u32 b[32];int i,x,y;for(i=0;i<32;i++)b[i]=0; /* head */
 for(y=2;y<7;y++)for(x=5;x<11;x++)objpix(b,x,y,1);objpix(b,6,4,3);objpix(b,9,4,3);
 for(y=7;y<12;y++)for(x=4;x<12;x++)objpix(b,x,y,2); /* pack / chest */
 if(face==2){for(y=7;y<12;y++)for(x=4;x<7;x++)objpix(b,x,y,4);} if(face==3){for(y=7;y<12;y++)for(x=9;x<12;x++)objpix(b,x,y,4);}
 for(y=12;y<15;y++){objpix(b,5+(step?1:0),y,2);objpix(b,6+(step?1:0),y,2);objpix(b,9-(step?1:0),y,2);objpix(b,10-(step?1:0),y,2);} upload_obj16(base,b);}
static void gen_buddy_frame(int base,int mood){u32 b[32];int i,x,y;for(i=0;i<32;i++)b[i]=0;for(y=4;y<12;y++)for(x=4;x<12;x++)if((x-8)*(x-8)+(y-8)*(y-8)<20)objpix(b,x,y,(u8)(5+mood));objpix(b,6,7,1);objpix(b,9,7,1);objpix(b,7,10,3);objpix(b,8,10,3);upload_obj16(base,b);}
static void gen_ship_frame(int base){u32 b[32];int i,x,y;for(i=0;i<32;i++)b[i]=0;for(y=5;y<11;y++)for(x=2+y/2;x<14-y/3;x++)objpix(b,x,y,2);for(x=6;x<10;x++)objpix(b,x,5,3);objpix(b,3,11,4);objpix(b,12,11,4);upload_obj16(base,b);}
static void gen_planet_frame(int base){u32 b[32];int i,x,y;for(i=0;i<32;i++)b[i]=0;for(y=2;y<14;y++)for(x=2;x<14;x++){int dx=x-8,dy=y-8;if(dx*dx+dy*dy<36)objpix(b,x,y,(x+y<13)?2:1);}upload_obj16(base,b);}
static void gen_marker_frame(int base){u32 b[32];int i,x,y;for(i=0;i<32;i++)b[i]=0;for(y=2;y<14;y++){objpix(b,7,y,3);objpix(b,8,y,3);}for(x=4;x<12;x++)objpix(b,x,2,2);upload_obj16(base,b);}
static void make_obj_tiles(void){int f;for(f=0;f<8;f++)gen_player_frame(f*4,f>>1,f&1);for(f=0;f<4;f++)gen_buddy_frame(32+f*4,f);gen_ship_frame(48);gen_planet_frame(52);gen_marker_frame(56);}
static void oam_hide_all(void){int i;for(i=0;i<128;i++){OAM16[i*4]=0x0200;OAM16[i*4+1]=0;OAM16[i*4+2]=0;OAM16[i*4+3]=0;}}
static void oam_set(int i,int x,int y,int tile,int pal,int hflip){ if(x<-16||x>239||y<-16||y>159){OAM16[i*4]=0x0200;return;} OAM16[i*4]=(u16)(y&255);OAM16[i*4+1]=(u16)((x&511)|(1u<<14)|(hflip?0x1000:0));OAM16[i*4+2]=(u16)(tile|(pal<<12)); }

/* ---------- palettes ---------- */
static void set_world_palette(int w){int i;u16 a=WORLDS[w].base0,b=WORLDS[w].base1,c=WORLDS[w].base2,d=WORLDS[w].accent;BG_PALETTE[0]=RGB5(0,0,0);for(i=0;i<16;i++){BG_PALETTE[i]=RGB5(0,0,0);}BG_PALETTE[1]=a;BG_PALETTE[2]=b;BG_PALETTE[3]=c;
 /* banks 1-7 give biome accents */
 for(i=1;i<8;i++){BG_PALETTE[i*16]=RGB5(0,0,0);BG_PALETTE[i*16+1]=a;BG_PALETTE[i*16+2]=b;BG_PALETTE[i*16+3]=(i&1)?d:c;}
 /* UI palette banks 13-15 */
 BG_PALETTE[13*16+1]=RGB5(31,25,8);BG_PALETTE[13*16+2]=RGB5(2,2,5);BG_PALETTE[14*16+1]=RGB5(8,31,29);BG_PALETTE[14*16+2]=RGB5(2,2,5);BG_PALETTE[15*16+1]=RGB5(31,31,31);BG_PALETTE[15*16+2]=RGB5(2,2,5);
 /* OBJ palettes */
 for(i=0;i<128;i++)OBJ_PALETTE[i]=0;OBJ_PALETTE[1]=RGB5(31,31,31);OBJ_PALETTE[2]=RGB5(22,22,25);OBJ_PALETTE[3]=RGB5(6,26,31);OBJ_PALETTE[4]=RGB5(31,10,18);
 for(i=0;i<4;i++){OBJ_PALETTE[(1+i)*16+1]=RGB5(31,31,31);OBJ_PALETTE[(1+i)*16+2]=RGB5(4+i*5,20+i*2,31-i*5);OBJ_PALETTE[(1+i)*16+3]=RGB5(31,18+i*3,8+i*5);OBJ_PALETTE[(1+i)*16+5+i]=WORLDS[w].accent;}
 for(i=0;i<6;i++){int p=8+i;OBJ_PALETTE[p*16+1]=WORLDS[i].base1;OBJ_PALETTE[p*16+2]=WORLDS[i].base2;OBJ_PALETTE[p*16+3]=WORLDS[i].accent;}
}

/* ---------- map painting ---------- */
static int mi(int x,int y){return y*MAP_W+x;}
static void map_put(int x,int y,int tile,int pal,int col,int trig){ if((unsigned)x>=MAP_W||(unsigned)y>=MAP_H)return;set_map_entry(x,y,map_attr(tile,pal));collision[mi(x,y)]=(u8)col;trigger[mi(x,y)]=(u8)trig; }
static void map_fill(int tile,int pal){int x,y;for(y=0;y<MAP_H;y++)for(x=0;x<MAP_W;x++)map_put(x,y,tile,pal,C_FREE,TR_NONE);}
static void map_border(void){int i;for(i=0;i<MAP_W;i++){map_put(i,0,T_WALL,0,C_WALL,0);map_put(i,MAP_H-1,T_WALL,0,C_WALL,0);}for(i=0;i<MAP_H;i++){map_put(0,i,T_WALL,0,C_WALL,0);map_put(MAP_W-1,i,T_WALL,0,C_WALL,0);}}
static void map_rect(int x0,int y0,int w,int h,int tile,int pal,int col){int x,y;for(y=y0;y<y0+h;y++)for(x=x0;x<x0+w;x++)map_put(x,y,tile,pal,col,TR_NONE);}
static void map_wall_box(int x0,int y0,int w,int h,int pal){int x,y;for(x=x0;x<x0+w;x++){map_put(x,y0,T_WALL,pal,C_WALL,0);map_put(x,y0+h-1,T_WALL,pal,C_WALL,0);}for(y=y0;y<y0+h;y++){map_put(x0,y,T_WALL,pal,C_WALL,0);map_put(x0+w-1,y,T_WALL,pal,C_WALL,0);}}
static void map_door(int x,int y,int trig){map_put(x,y,T_DOOR,2,C_FREE,trig);}
static void add_noise_decor(int seed,int tile,int pal,int count,int solid){int i;for(i=0;i<count;i++){int x=2+((seed+i*17+i*i*3)%60),y=2+((seed*3+i*29+i*i)%60);if(collision[mi(x,y)]==C_FREE && trigger[mi(x,y)]==TR_NONE)map_put(x,y,tile,pal,solid?C_WALL:C_FREE,0);}}

static void generate_origin(void){int y;map_fill(T_GRASS,0);map_border();for(y=3;y<61;y++)map_put(31,y,T_WATER,2,C_WALL,0);for(y=28;y<35;y++)map_put(31,y,T_BRIDGE,1,C_FREE,0);map_rect(8,46,9,7,T_PAD,1,C_FREE);map_put(12,49,T_PAD,2,C_FREE,TR_SHIP);map_wall_box(19,16,16,13,2);map_door(26,28,TR_DOOR);map_rect(22,19,10,5,T_RUIN,2,C_WALL);map_put(27,22,T_ARCHIVE,3,C_FREE,TR_TERMINAL);map_wall_box(47,5,12,10,3);map_door(52,14,TR_SECRET);add_noise_decor(7,T_TREE,1,90,1);{int x;for(x=10;x<31;x++)map_put(x,51,T_PATH,1,C_FREE,0);for(y=28;y<52;y++)map_put(26,y,T_PATH,1,C_FREE,(y==28)?TR_DOOR:0);}for(y=0;y<64;y+=8)map_put(30,y,T_WATER,2,C_WALL,0);for(y=28;y<35;y++){map_put(30,y,T_BRIDGE,1,C_FREE,0);map_put(31,y,T_BRIDGE,1,C_FREE,0);} }
static void generate_ember(void){int x,y;map_fill(T_FLOOR,0);map_border();for(y=8;y<58;y+=12)for(x=2;x<62;x++)if((x<16||x>22)&&(x<42||x>48))map_put(x,y,T_LAVA,2,C_HAZARD,0);for(x=5;x<60;x++)map_put(x,34,T_METAL,1,C_FREE,0);map_rect(5,48,9,7,T_PAD,1,C_FREE);map_put(9,51,T_PAD,2,C_FREE,TR_SHIP);map_wall_box(42,38,17,18,2);map_door(49,55,TR_DOOR);map_put(20,20,T_LIFT,3,C_FREE,TR_LIFT);add_noise_decor(17,T_CRYSTAL,3,38,1);for(x=9;x<50;x++)map_put(x,51,T_METAL,1,C_FREE,(x==9)?TR_SHIP:0);for(y=20;y<52;y++)map_put(20,y,T_METAL,1,C_FREE,(y==20)?TR_LIFT:0);}
static void generate_tide(void){int x,y;map_fill(T_WATER,2);for(y=2;y<62;y++)for(x=2;x<62;x++)if(((x*5+y*3+11)&15)<6)map_put(x,y,T_FLOOR,0,C_FREE,0);map_border();for(x=5;x<58;x++)map_put(x,31,T_BRIDGE,1,C_FREE,0);map_rect(6,49,9,7,T_PAD,1,C_FREE);map_put(10,52,T_PAD,2,C_FREE,TR_SHIP);map_wall_box(41,9,16,15,3);map_door(48,23,TR_DOOR);map_put(22,45,T_LIFT,3,C_FREE,TR_LIFT);add_noise_decor(23,T_ARCHIVE,3,25,0);for(x=10;x<=48;x++)map_put(x,52,T_BRIDGE,1,C_FREE,(x==10)?TR_SHIP:0);for(y=23;y<=52;y++)map_put(48,y,T_BRIDGE,1,C_FREE,(y==23)?TR_DOOR:0);for(y=45;y<=52;y++)map_put(22,y,T_BRIDGE,1,C_FREE,(y==45)?TR_LIFT:0);map_put(22,45,T_LIFT,3,C_FREE,TR_LIFT);}
static void generate_bloom(void){int x,y;map_fill(T_GRASS,0);map_border();for(x=2;x<62;x+=7)for(y=3;y<60;y+=9)map_put(x,y,T_PLANT,2,C_WALL,0);map_rect(6,48,9,7,T_PAD,1,C_FREE);map_put(10,51,T_PAD,2,C_FREE,TR_SHIP);map_put(31,31,T_LIFT,3,C_FREE,TR_LIFT);map_wall_box(44,8,14,12,3);map_door(50,19,TR_DOOR);add_noise_decor(31,T_TREE,1,70,1);for(x=10;x<=50;x++)map_put(x,51,T_PATH,1,C_FREE,(x==10)?TR_SHIP:0);for(y=19;y<=51;y++)map_put(31,y,T_PATH,1,C_FREE,(y==31)?TR_LIFT:0);map_put(50,19,T_DOOR,2,C_FREE,TR_DOOR);}
static void generate_black(void){int x,y;map_fill(T_VOID,0);map_border();for(y=3;y<61;y++)for(x=3;x<61;x++)if(((x*13+y*7+x*y)&31)<5)map_put(x,y,T_HAZARD,2,C_HAZARD,0);for(x=6;x<56;x++)map_put(x,32,T_PATH,3,C_FREE,0);map_rect(7,49,9,7,T_PAD,1,C_FREE);map_put(11,52,T_PAD,2,C_FREE,TR_SHIP);map_wall_box(43,8,15,15,3);map_door(50,22,TR_DOOR);map_put(24,14,T_CRYSTAL,3,C_FREE,TR_SECRET);}
static void generate_crown(void){int x,y;map_fill(T_CROWN,0);map_border(); /* six connected chambers */
 for(x=8;x<57;x+=16)for(y=5;y<58;y++)if(y!=15&&y!=31&&y!=47)map_put(x,y,T_WALL,2,C_WALL,0);
 for(y=16;y<49;y+=16)for(x=3;x<61;x++)if(x!=16&&x!=32&&x!=48)map_put(x,y,T_WALL,2,C_WALL,0);
 map_rect(4,51,9,7,T_PAD,1,C_FREE);map_put(8,54,T_PAD,2,C_FREE,TR_SHIP);map_put(55,8,T_CRYSTAL,3,C_FREE,TR_CROWN_CORE);map_put(16,15,T_ARCHIVE,3,C_FREE,TR_TERMINAL);map_put(32,31,T_ARCHIVE,3,C_FREE,TR_TERMINAL);map_put(48,47,T_ARCHIVE,3,C_FREE,TR_TERMINAL);
}
static void generate_layer_overlay(void){int x,y;if(current_layer==0){for(y=2;y<62;y++)for(x=2;x<62;x++)if(((x*11+y*7+current_world*13)&31)==0 && collision[mi(x,y)]==C_FREE && trigger[mi(x,y)]==TR_NONE)map_put(x,y,T_RUIN,2,C_WALL,0);}
 else if(current_layer==2){for(y=3;y<61;y++)for(x=3;x<61;x++)if(((x*3+y*11+current_world*17)&31)==1 && collision[mi(x,y)]==C_FREE && trigger[mi(x,y)]==TR_NONE)map_put(x,y,T_PLANT,3,C_WALL,0);}
 /* layer-specific axis keys */
 if(current_world==1 && current_layer==0){for(x=20;x<=53;x++)map_put(x,20,T_METAL,1,C_FREE,0);for(y=10;y<=20;y++)map_put(53,y,T_METAL,1,C_FREE,0);map_put(53,10,T_CRYSTAL,3,C_FREE,TR_KEY_X);}
 if(current_world==2 && current_layer==0){for(x=22;x<=50;x++)map_put(x,45,T_BRIDGE,1,C_FREE,0);for(y=12;y<=45;y++)map_put(50,y,T_BRIDGE,1,C_FREE,0);map_put(50,12,T_CRYSTAL,3,C_FREE,TR_KEY_Y);}
 if(current_world==3 && current_layer==2){for(x=31;x<=52;x++)map_put(x,31,T_PATH,1,C_FREE,0);for(y=11;y<=31;y++)map_put(52,y,T_PATH,1,C_FREE,0);map_put(52,11,T_CRYSTAL,3,C_FREE,TR_KEY_Z);}
}
static void generate_room(void){int x,y;map_fill(T_FLOOR,0);for(y=0;y<32;y++)for(x=0;x<32;x++)if(x==0||y==0||x==31||y==31)map_put(x,y,T_WALL,2,C_WALL,0);for(y=32;y<64;y++)for(x=0;x<64;x++)map_put(x,y,T_VOID,0,C_WALL,0);for(y=0;y<32;y++)for(x=32;x<64;x++)map_put(x,y,T_VOID,0,C_WALL,0);map_door(15,30,TR_EXIT);
 if(current_world==0){map_rect(5,5,22,3,T_ARCHIVE,3,C_WALL);map_put(16,10,T_ARCHIVE,3,C_FREE,TR_TERMINAL);map_put(26,5,T_CRYSTAL,3,C_FREE,TR_SECRET);}
 else if(current_world==1){for(x=4;x<28;x++)map_put(x,12,T_LAVA,2,C_HAZARD,0);for(x=12;x<20;x++)map_put(x,12,T_BRIDGE,1,C_FREE,0);map_put(24,6,T_LIFT,3,C_FREE,TR_LIFT);}
 else if(current_world==2){for(y=4;y<26;y+=6)for(x=4;x<28;x++)map_put(x,y,T_ARCHIVE,3,C_WALL,0);map_put(26,25,T_LIFT,3,C_FREE,TR_LIFT);map_put(8,8,T_ARCHIVE,3,C_FREE,TR_TERMINAL);}
 else if(current_world==3){for(y=4;y<25;y+=5)for(x=5;x<27;x+=5)map_put(x,y,T_PLANT,2,C_WALL,0);map_put(16,8,T_LIFT,3,C_FREE,TR_LIFT);}
 else if(current_world==4){for(y=3;y<29;y++)for(x=3;x<29;x++)if(((x*y+7)&15)==0)map_put(x,y,T_HAZARD,2,C_HAZARD,0);map_put(16,8,T_CRYSTAL,3,C_FREE,TR_SECRET);}
 else { /* Crown interior chamber used as memory vault */ map_wall_box(5,5,22,18,3);map_door(16,22,TR_EXIT);map_put(16,10,T_ARCHIVE,3,C_FREE,TR_TERMINAL);}
}
static void generate_surface(void){int i;REG_DISPCNT=0;for(i=0;i<MAP_W*MAP_H;i++){collision[i]=C_FREE;trigger[i]=TR_NONE;}set_world_palette(current_world);if(current_room){generate_room();}else{if(current_world==0)generate_origin();else if(current_world==1)generate_ember();else if(current_world==2)generate_tide();else if(current_world==3)generate_bloom();else if(current_world==4)generate_black();else generate_crown();generate_layer_overlay();}
 REG_BG0CNT=(u16)(2|(BG_TILE_CB<<2)|(BG_MAP_BASE<<8)|(3u<<14));REG_BG1CNT=(u16)((UI_TILE_CB<<2)|(UI_MAP_BASE<<8));ui_clear();REG_DISPCNT=MODE0|BG0_ENABLE|BG1_ENABLE|OBJ_ENABLE|OBJ_1D_MAP;}
static void generate_space(void){int x,y;REG_DISPCNT=0;set_world_palette(ship_world);for(y=0;y<MAP_H;y++)for(x=0;x<MAP_W;x++){int h=(x*37+y*53+x*y*3)&127;map_put(x,y,h<6?T_STAR:T_VOID,(h&1)?3:0,C_FREE,TR_NONE);}REG_BG0CNT=(u16)(2|(BG_TILE_CB<<2)|(BG_MAP_BASE<<8)|(3u<<14));REG_BG1CNT=(u16)((UI_TILE_CB<<2)|(UI_MAP_BASE<<8));ui_clear();REG_DISPCNT=MODE0|BG0_ENABLE|BG1_ENABLE|OBJ_ENABLE|OBJ_1D_MAP;}

/* ---------- sound ---------- */
static void sound_init(void){REG_SOUNDCNT_X=0x0080;REG_SOUNDCNT_L=0x1177;REG_SOUNDCNT_H=0x0002;REG_SOUND1CNT_L=0;}
static void tone(u16 f){if(!audio_on)return;REG_SOUND1CNT_H=0xA080;REG_SOUND1CNT_X=(u16)(0x8000|(f&0x07FF));}
static const u16 SONGS[6][8]={
 {1350,1420,1510,1420,1600,1510,1420,0},{1210,1290,1210,1380,1210,1460,1290,0},{1510,1580,1660,1580,1740,1660,1580,0},
 {1390,1510,1630,1760,1630,1510,1810,0},{1100,1160,1090,1240,1130,1300,1040,0},{1350,1510,1660,1810,1660,1510,1900,0}
};
static void music_step(void){if(!audio_on)return;music_tick++;if(music_tick>=36){u8 n=(u8)((frame/36)&7);music_tick=0;if(SONGS[game_mode==MODE_SPACE?5:WORLDS[current_world].music][n])tone((u16)(SONGS[game_mode==MODE_SPACE?5:WORLDS[current_world].music][n]+(next_q()&7)));}}

/* ---------- dialogue & UI ---------- */
static void say(const char*s){copystr(dialogue,s,90);dialogue_timer=210;tone((u16)(1500+(next_q()<<1)));}
static const char* goal_name(u8 g){static const char*G[GOAL_COUNT]={"FOLLOW","EXPLORE","INSPECT","WAIT","RETURN","WARN","SEEK KEY","SEEK MEMORY","APPROACH","AVOID","BOARD SHIP","REST","WANDER"};return G[g<GOAL_COUNT?g:0];}
static const char* mood_name(void){if(cosmos.avoid>190)return "CAUTIOUS";if(cosmos.curiosity>195)return "CURIOUS";if(cosmos.trust>190)return "LINKED";if(cosmos.energy<60)return "TIRED";return "CALM";}
static const char* layer_name(void){return current_layer==0?"UNDER":(current_layer==2?"UPPER":"SURFACE");}

static const char* crown_zone(void){int x=player.x>>3,y=player.y>>3;if(y>=49)return "ENTRY";if(y<16)return x<32?"X CHAMBER":"Y CHAMBER";if(y<32)return x<32?"Z CHAMBER":"MEMORY";if(y<48)return x<32?"STATE":"CHOICE";return "CORE";}
static const char* location_name(void){return (current_world==5&&game_mode==MODE_SURFACE&&!current_room)?crown_zone():WORLDS[current_world].name;}
static void ui_wrap_text(int row,const char*s,int pal,int maxrows){int col=0,r=0;char word[28];int wi=0;while(*s&&r<maxrows){while(*s==' ')s++;wi=0;while(*s&&*s!=' '&&wi<27)word[wi++]=*s++;word[wi]=0;if(!wi)break;if(col&&col+wi+1>29){r++;col=0;if(r>=maxrows)break;}if(col){ui_text(col,row+r," ",pal);col++;}ui_text(col,row+r,word,pal);col+=wi;}}
static void draw_hud(void){char k[8];ui_clear();ui_fill_rows(0,1,63,15);ui_fill_rows(18,19,63,15);ui_text(1,0,game_mode==MODE_SPACE?"SPACE":location_name(),14);if(game_mode==MODE_SURFACE){ui_text(19,0,layer_name(),13);}
 k[0]='X';k[1]=(keys_found&1)?'*':'-';k[2]='Y';k[3]=(keys_found&2)?'*':'-';k[4]='Z';k[5]=(keys_found&4)?'*':'-';k[6]=0;ui_text(1,1,k,13);ui_text(9,1,"COSMOS",14);ui_text(16,1,mood_name(),15);
 if(dialogue_timer){ui_fill_rows(15,17,63,15);ui_text(1,15,"COSMOS:",14);ui_wrap_text(16,dialogue,15,2);}else{ui_text(1,18,"A ACT",14);ui_text(8,18,"START MENU",15);ui_text(20,18,"SELECT BEACON",13);ui_text(1,19,"GOAL",14);ui_text(6,19,goal_name(cosmos.goal),15);ui_text(20,19,"HP",14);ui_num(23,19,player.hp,15);}
}
static void draw_intro(void){ui_clear();ui_fill_rows(2,17,63,15);ui_text(9,4,"SIM EARTH",14);ui_text(6,6,"PIXEL UNIVERSE",15);ui_text(7,8,"THE LOST COSMOS",13);ui_text(4,11,"THE UNIVERSE DID NOT DIE",15);ui_text(8,12,"IT LOST DEPTH",14);ui_text(4,15,"PRESS START TO WAKE",13);}
static const char* story_line(void){if(postgame)return "EPILOGUE // THE UNIVERSE REMEMBERS. THE FINAL CHAPTER IS EXPLORATION.";if(chapter==0)return "CHAPTER I // THE WORLD THAT LOST DEPTH. FIND THE SHIP AND LISTEN TO COSMOS.";if(chapter==1)return "CHAPTER II // EMBER / X. THE FIRST AXIS IS BURIED BELOW THE FURNACES.";if(chapter==2)return "CHAPTER III // TIDE / Y. A DROWNED ARCHIVE REMEMBERS DISTANCE.";if(chapter==3)return "CHAPTER IV // BLOOM / Z. THE FOREST GREW TOWARD A MISSING DIRECTION.";if(chapter==4)return "CHAPTER V // BLACK GARDEN. DELETED FUTURES STILL CAST SHADOWS.";return "CHAPTER VI // THE SYNAPSE CROWN. COSMOS WILL SPEAK FIRST. YOU DECIDE.";}
static void draw_pause(void){ui_clear();ui_fill_rows(0,19,63,15);ui_text(2,1,"PAUSED // SYNAPSE ARCHIVE",14);if(pause_page==0){static const char*items[8]={"MAP","COSMOS","MEMORIES","AXIS KEYS","BEACONS","STORY","SETTINGS","SAVE"};int i;for(i=0;i<8;i++){ui_text(2,3+i,(i==pause_sel)?">":" ",13);ui_text(4,3+i,items[i],(i==pause_sel)?14:15);}ui_text(2,17,"A OPEN   B RESUME",13);}else if(pause_page==1){ui_text(2,3,"MAP // KNOWN WORLDS",14);{int i;for(i=0;i<6;i++){ui_text(2,5+i,(visited_mask&(1u<<i))?"*":"-",13);ui_text(4,5+i,WORLDS[i].name,15);}}ui_text(2,17,"B BACK",13);}else if(pause_page==2){ui_text(2,3,"COSMOS // SYNAPSE BUDDY",14);ui_text(2,5,"MOOD",13);ui_text(10,5,mood_name(),15);ui_text(2,6,"GOAL",13);ui_text(10,6,goal_name(cosmos.goal),15);ui_text(2,7,"TRUST",13);ui_num(10,7,cosmos.trust,15);ui_text(2,8,"CURIOSITY",13);ui_num(13,8,cosmos.curiosity,15);ui_text(2,9,"AVOID",13);ui_num(10,9,cosmos.avoid,15);ui_text(2,11,"MODEL != MEMORY",14);ui_text(2,12,"MODEL != STATE",14);ui_text(2,13,"MODEL != AUTHORITY",14);ui_text(2,17,"B BACK",13);}else if(pause_page==3){ui_text(2,3,"MEMORIES",14);ui_text(2,5,(cosmos.memory_flags&MEM_ORIGIN_ARCHIVE)?"* ORIGIN ARCHIVE":"- ORIGIN ARCHIVE",15);ui_text(2,6,(cosmos.memory_flags&MEM_BLACK_GARDEN)?"* BLACK GARDEN":"- BLACK GARDEN",15);ui_text(2,7,(cosmos.memory_flags&MEM_SECRET)?"* SECRET SIGNAL":"- SECRET SIGNAL",15);ui_text(2,8,(cosmos.memory_flags&MEM_SHIP)?"* FIRST FLIGHT":"- FIRST FLIGHT",15);ui_text(2,9,(cosmos.memory_flags&MEM_ENDING)?"* CROWN CHOICE":"- CROWN CHOICE",15);ui_text(2,17,"B BACK",13);}else if(pause_page==4){ui_text(2,3,"AXIS KEYS",14);ui_text(2,5,(keys_found&1)?"X // RESTORED":"X // MISSING",15);ui_text(2,6,(keys_found&2)?"Y // RESTORED":"Y // MISSING",15);ui_text(2,7,(keys_found&4)?"Z // RESTORED":"Z // MISSING",15);ui_text(2,10,"L/R SHIFT DEPTH AT LIFTS",13);ui_text(2,17,"B BACK",13);}else if(pause_page==5){ui_text(2,3,"BEACONS",14);ui_text(2,5,"SAVED",13);ui_num(9,5,beacon_count,15);ui_text(2,7,"SELECT DROPS A WORLD BEACON",15);ui_text(2,17,"B BACK",13);}else if(pause_page==6){ui_text(2,3,"STORY",14);ui_wrap_text(5,story_line(),15,8);ui_text(2,17,"B BACK",13);}else if(pause_page==7){ui_text(2,3,"SETTINGS",14);ui_text(2,5,"AUDIO",13);ui_text(10,5,audio_on?"ON":"OFF",15);ui_text(2,7,"A TOGGLE",15);ui_text(2,17,"B BACK",13);}else if(pause_page==8){ui_text(2,5,"SAVE COMPLETE",14);ui_text(2,7,"SRAM_V113",15);ui_text(2,9,"COSMOS MEMORY PERSISTED",13);ui_text(2,17,"B BACK",13);}}

/* ---------- SRAM persistence ---------- */
static void sw16(int o,s16 v){SRAM[o]=(u8)v;SRAM[o+1]=(u8)(((u16)v)>>8);}static s16 sr16(int o){return(s16)((u16)SRAM[o]|((u16)SRAM[o+1]<<8));}
static void sw32(int o,u32 v){SRAM[o]=(u8)v;SRAM[o+1]=(u8)(v>>8);SRAM[o+2]=(u8)(v>>16);SRAM[o+3]=(u8)(v>>24);}static u32 sr32(int o){return(u32)SRAM[o]|((u32)SRAM[o+1]<<8)|((u32)SRAM[o+2]<<16)|((u32)SRAM[o+3]<<24);}
static u8 save_checksum(void){int i;u8 s=0xA7;for(i=0;i<120;i++)s=(u8)(s+SRAM[i]+(i*3));return s;}
static void save_game(void){int i,o=40;SRAM[0]='L';SRAM[1]='C';SRAM[2]='V';SRAM[3]='2';SRAM[4]=2;SRAM[5]=keys_found;SRAM[6]=visited_mask;SRAM[7]=secrets_mask;SRAM[8]=chapter;SRAM[9]=ending;SRAM[10]=postgame;SRAM[11]=current_world;SRAM[12]=current_room;SRAM[13]=current_layer;SRAM[14]=game_mode==MODE_PAUSE?return_mode:game_mode;SRAM[15]=audio_on;sw16(16,player.x);sw16(18,player.y);sw16(20,ship_x);sw16(22,ship_y);SRAM[24]=ship_world;SRAM[25]=player.hp;SRAM[26]=cosmos.goal;SRAM[27]=cosmos.mood;SRAM[28]=cosmos.trust;SRAM[29]=cosmos.curiosity;SRAM[30]=cosmos.avoid;SRAM[31]=cosmos.energy;SRAM[32]=(u8)cosmos.memory_flags;SRAM[33]=(u8)(cosmos.memory_flags>>8);SRAM[34]=cosmos_preference;SRAM[35]=player_choice;SRAM[36]=beacon_count;sw32(120,qi);for(i=0;i<8;i++){SRAM[o++]=beacons[i].world;SRAM[o++]=beacons[i].room;SRAM[o++]=beacons[i].layer;sw16(o,beacons[i].x);o+=2;sw16(o,beacons[i].y);o+=2;}SRAM[124]=save_checksum();}
static int save_valid(void){return SRAM[0]=='L'&&SRAM[1]=='C'&&SRAM[2]=='V'&&SRAM[3]=='2'&&SRAM[4]==2&&SRAM[124]==save_checksum();}
static void load_game(void){int i,o=40;if(!save_valid())return;keys_found=SRAM[5]&7;visited_mask=SRAM[6];secrets_mask=SRAM[7];chapter=SRAM[8];ending=SRAM[9];postgame=SRAM[10];current_world=SRAM[11]%6;current_room=SRAM[12];current_layer=SRAM[13]%3;game_mode=SRAM[14]%2;audio_on=SRAM[15];player.x=sr16(16);player.y=sr16(18);ship_x=sr16(20);ship_y=sr16(22);ship_world=SRAM[24]%6;player.hp=SRAM[25];cosmos.goal=SRAM[26]%GOAL_COUNT;cosmos.mood=SRAM[27]&3;cosmos.trust=SRAM[28];cosmos.curiosity=SRAM[29];cosmos.avoid=SRAM[30];cosmos.energy=SRAM[31];cosmos.memory_flags=(u16)SRAM[32]|((u16)SRAM[33]<<8);cosmos_preference=SRAM[34];player_choice=SRAM[35];beacon_count=SRAM[36];if(beacon_count>8)beacon_count=0;for(i=0;i<8;i++){beacons[i].world=SRAM[o++];beacons[i].room=SRAM[o++];beacons[i].layer=SRAM[o++];beacons[i].x=sr16(o);o+=2;beacons[i].y=sr16(o);o+=2;}qi=sr32(120);if(qi>=QSEED_LEN)qi=0;}

/* ---------- CST / Synapse state ---------- */
static void state_tick(void){int i;u8 q=next_q(),near=0;state12[0]=(u8)clampi(iabs(player.dx)*40+iabs(player.dy)*40,0,255);state12[1]=(u8)(frame&255);state12[2]=(u8)(current_world*42);state12[3]=(u8)(current_layer*96);state12[4]=q;state12[5]=(u8)(80+keys_found*45);state12[6]=cosmos.curiosity;state12[7]=cosmos.trust;state12[8]=audio_on?180:0;state12[9]=(u8)(frame*3);state12[10]=(u8)(255-iabs((int)q-(int)cosmos.curiosity));state12[11]=next_q();for(i=0;i<12;i++)state42[i]=state12[i];for(i=12;i<42;i++)state42[i]=(u8)(state12[(i-12)%12]+next_q()+i*5);state42[31]=(u8)(current_world*50);state42[32]=(u8)(current_layer*110);state42[38]=(u8)(cosmos.memory_flags&255);state42[39]=cosmos.curiosity;state42[40]=cosmos.avoid;state42[41]=(u8)(255-iabs((int)q-128));for(i=0;i<42;i++)state54[i]=state42[i];for(i=42;i<54;i++)state54[i]=(u8)(state42[i-42]+next_q()+i*7);state54[42]=cosmos.trust;state54[43]=(u8)(96+(next_q()>>1));state54[44]=cosmos.focus;state54[45]=cosmos.curiosity;state54[46]=cosmos.avoid;state54[49]=(u8)((cosmos.memory_flags?180:40)+keys_found*20);state54[50]=(u8)iabs((int)q-(int)state12[5]);state54[51]=(u8)(25+(next_q()&31));state54[52]=(u8)(255-iabs((int)state12[10]-(int)cosmos.trust));state54[53]=(u8)(current_world==5?255:near);}

/* ---------- COSMOS autonomous agent ---------- */
static void buddy_speak_context(void){u8 q=qpick(5);if(current_world==2&&(visited_mask&(1u<<2)))say("I REMEMBER THIS WATER. THE ARCHIVE SOUNDS DIFFERENT NOW.");else if(current_world==4)say("I DO NOT LIKE THE BLACK GARDEN. I STILL WANT TO REMEMBER IT.");else if(cosmos.memory_flags&MEM_PLAYER_HELPED){if(q&1)say("YOU LISTENED TO ME BEFORE. I KEPT THAT MEMORY.");else say("WE CAME THROUGH HERE BEFORE. THE MAP FEELS SMALLER NOW.");}else if(q==0)say("I CHOSE THIS PATH BEFORE. WOULD I CHOOSE IT AGAIN?");else if(q==1)say("THERE IS ENOUGH SIGNAL HERE TO BECOME A MEMORY.");else if(q==2)say("THE AXES FEEL THIN. STAY CLOSE IF YOU WANT TO.");else if(q==3)say("I AM FOLLOWING A PATTERN IN THE OLD TAPE.");else say("I WONDER WHAT THE MAP FORGOT ON PURPOSE.");}
static int nearest_interest(s16*x,s16*y,u8*goal){int best=9999,bx=player.x,by=player.y,g=GOAL_EXPLORE;int tx,ty,d;if(current_room){tx=16*8;ty=10*8;d=iabs(player.x-tx)+iabs(player.y-ty);if(d<best){best=d;bx=tx;by=ty;g=GOAL_INSPECT;}}else{ /* key targets by world/layer */
 if(current_world==1&&!(keys_found&1)){tx=53*8;ty=10*8;d=iabs(player.x-tx)+iabs(player.y-ty);if(d<best){best=d;bx=tx;by=ty;g=GOAL_SEEK_KEY;}}
 if(current_world==2&&!(keys_found&2)){tx=50*8;ty=12*8;d=iabs(player.x-tx)+iabs(player.y-ty);if(d<best){best=d;bx=tx;by=ty;g=GOAL_SEEK_KEY;}}
 if(current_world==3&&!(keys_found&4)){tx=52*8;ty=11*8;d=iabs(player.x-tx)+iabs(player.y-ty);if(d<best){best=d;bx=tx;by=ty;g=GOAL_SEEK_KEY;}}
 if(current_world==5&&keys_found==7){tx=55*8;ty=8*8;d=iabs(player.x-tx)+iabs(player.y-ty);if(d<best){best=d;bx=tx;by=ty;g=GOAL_APPROACH;}}
 }
 *x=(s16)bx;*y=(s16)by;*goal=g;return best;}
static void choose_buddy_goal(void){int scores[GOAL_COUNT],i,best=-999,bestg=0;u8 q=next_q();s16 ix,iy;u8 ig;int pd=iabs(cosmos.x-player.x)+iabs(cosmos.y-player.y);nearest_interest(&ix,&iy,&ig);for(i=0;i<GOAL_COUNT;i++)scores[i]=0;scores[GOAL_FOLLOW]=120+(pd>80?90:0)+cosmos.trust/3;scores[GOAL_EXPLORE]=60+cosmos.curiosity/2+(q&31);scores[GOAL_INSPECT]=ig==GOAL_INSPECT?170:20;scores[GOAL_WAIT]=cosmos.energy<80?130:20;scores[GOAL_RETURN]=pd>150?240:10;scores[GOAL_WARN]=(current_world==4||collision[mi(clampi(player.x>>3,0,63),clampi(player.y>>3,0,63))]==C_HAZARD)?160+cosmos.avoid/2:15;scores[GOAL_SEEK_KEY]=ig==GOAL_SEEK_KEY?190+cosmos.curiosity/3:5;scores[GOAL_SEEK_MEMORY]=(current_world==2||current_world==0)?100+(cosmos.curiosity>>2):20;scores[GOAL_APPROACH]=ig==GOAL_APPROACH?220:30;scores[GOAL_AVOID]=current_world==4?120+cosmos.avoid/2:10;scores[GOAL_BOARD]=(game_mode==MODE_SPACE)?150:10;scores[GOAL_REST]=cosmos.energy<55?220:15;scores[GOAL_WANDER]=50+(q>>1);for(i=0;i<GOAL_COUNT;i++){scores[i]+=(next_q()&15);if(i==cosmos.goal)scores[i]+=28; /* hysteresis */if(scores[i]>best){best=scores[i];bestg=i;}}cosmos.goal=(u8)bestg;cosmos.cooldown=(u8)(50+(next_q()&63));if((q&7)==0)buddy_speak_context();}
static int buddy_tile_blocked(int x,int y){int tx=x>>3,ty=y>>3;if((unsigned)tx>=64u||(unsigned)ty>=64u)return 1;return collision[mi(tx,ty)]==C_WALL;}
static void buddy_tick(void){s16 tx=player.x+18,ty=player.y-10,ix,iy;u8 ig;int dx,dy;if(game_mode!=MODE_SURFACE)return;if(cosmos.cooldown)cosmos.cooldown--;else choose_buddy_goal();nearest_interest(&ix,&iy,&ig);if(cosmos.goal==GOAL_SEEK_KEY||cosmos.goal==GOAL_INSPECT||cosmos.goal==GOAL_APPROACH||cosmos.goal==GOAL_SEEK_MEMORY){tx=ix;ty=iy;}else if(cosmos.goal==GOAL_EXPLORE||cosmos.goal==GOAL_WANDER){tx=(s16)clampi(player.x+((int)next_q()-128),16,496);ty=(s16)clampi(player.y+((int)next_q()-128),16,496);}else if(cosmos.goal==GOAL_WAIT||cosmos.goal==GOAL_REST){tx=cosmos.x;ty=cosmos.y;}else if(cosmos.goal==GOAL_AVOID||cosmos.goal==GOAL_WARN){tx=(s16)clampi(player.x+signi(player.x-256)*50,16,496);ty=(s16)clampi(player.y+signi(player.y-256)*50,16,496);}dx=signi(tx-cosmos.x);dy=signi(ty-cosmos.y);if(!buddy_tile_blocked(cosmos.x+dx,cosmos.y))cosmos.x+=(s16)dx;if(!buddy_tile_blocked(cosmos.x,cosmos.y+dy))cosmos.y+=(s16)dy;cosmos.energy=(u8)clampi(cosmos.energy+((cosmos.goal==GOAL_REST)?1:-((frame&15)==0)),0,255);cosmos.mood=(u8)((cosmos.avoid>190)?3:(cosmos.curiosity>190?2:(cosmos.trust>190?1:0)));}

/* ---------- movement / collisions ---------- */
static int blocked_px(int x,int y){int tx=x>>3,ty=y>>3;if((unsigned)tx>=64u||(unsigned)ty>=64u)return 1;return collision[mi(tx,ty)]==C_WALL;}
static u8 tile_collision_at(int x,int y){int tx=clampi(x>>3,0,63),ty=clampi(y>>3,0,63);return collision[mi(tx,ty)];}
static void hurt_player(int dx,int dy){if(player.hurt)return;player.hurt=40;if(player.hp)player.hp--;player.x=(s16)clampi(player.x-dx*10,10,502);player.y=(s16)clampi(player.y-dy*10,10,502);tone(1000);say("HAZARD. I AM MARKING THE SAFE EDGE.");cosmos.avoid=(u8)clampi(cosmos.avoid+10,0,255);if(player.hp==0){player.hp=3;player.x=80;player.y=400;say("I PULLED YOUR LAST STABLE POSITION FROM MEMORY.");}}
static int can_stand(int x,int y){return !blocked_px(x-5,y-5)&&!blocked_px(x+5,y-5)&&!blocked_px(x-5,y+5)&&!blocked_px(x+5,y+5);}
static void move_player(int dx,int dy,int running){int nx=player.x+dx,ny=player.y+dy;player.dx=(s8)dx;player.dy=(s8)dy;if(dx<0)player.face=2;else if(dx>0)player.face=3;else if(dy<0)player.face=0;else if(dy>0)player.face=1;if(can_stand(nx,player.y))player.x=(s16)nx;if(can_stand(player.x,ny))player.y=(s16)ny;player.x=(s16)clampi(player.x,8,MAP_PX-9);player.y=(s16)clampi(player.y,8,MAP_PX-9);if(dx||dy){player.anim=(u8)((frame>>(running?2:3))&1);player.run=(u8)running;}else player.anim=0;if(tile_collision_at(player.x,player.y)==C_HAZARD)hurt_player(dx,dy);}
static u8 trigger_near(void){int tx=player.x>>3,ty=player.y>>3,x,y;for(y=ty-1;y<=ty+1;y++)for(x=tx-1;x<=tx+1;x++)if((unsigned)x<64u&&(unsigned)y<64u&&trigger[mi(x,y)])return trigger[mi(x,y)];return TR_NONE;}
static void refresh_camera(void){int maxx=current_room?16:272,maxy=current_room?96:352;cam_x=(s16)clampi(player.x-120,0,maxx);cam_y=(s16)clampi(player.y-80,0,maxy);REG_BG0HOFS=(u16)cam_x;REG_BG0VOFS=(u16)cam_y;REG_BG1HOFS=0;REG_BG1VOFS=0;}

/* ---------- gameplay transitions ---------- */
static void spawn_surface(int world){current_world=(u8)world;current_room=0;current_layer=1;game_mode=MODE_SURFACE;player.x=80;player.y=408;player.dx=player.dy=0;cosmos.x=100;cosmos.y=396;visited_mask|=(u8)(1u<<world);generate_surface();refresh_camera();say("LANDED. I AM BUILDING A LOCAL MEMORY OF THIS PLACE.");save_game();}
static void enter_room(void){current_room=1;player.x=16*8;player.y=28*8;cosmos.x=player.x+14;cosmos.y=player.y-10;generate_surface();refresh_camera();say("INTERIOR LAYER FOUND. THE WALLS STILL HAVE STATE.");}
static void exit_room(void){current_room=0;player.x=26*8;player.y=31*8;cosmos.x=player.x+14;cosmos.y=player.y-10;generate_surface();refresh_camera();say("BACK OUTSIDE. I KEPT THE ROOM IN MEMORY.");}
static void shift_layer(int dir){u8 old=current_layer;if(dir<0&&current_layer>0)current_layer--;if(dir>0&&current_layer<2)current_layer++;if(old!=current_layer){generate_surface();say(current_layer==0?"DEPTH SHIFT // UNDER LAYER":"DEPTH SHIFT // UPPER LAYER");tone((u16)(1300+current_layer*180));}}
static void board_ship(void){game_mode=MODE_SPACE;ship_world=current_world;ship_x=PLANET_X[current_world];ship_y=(s16)(PLANET_Y[current_world]+26);cosmos.memory_flags|=MEM_SHIP;generate_space();say("LUNA-ARC LINKED. SPACE SCALE ONLINE.");save_game();}
static int nearest_planet(void){int i,b=0,d=9999;for(i=0;i<6;i++){int q=iabs(ship_x-PLANET_X[i])+iabs(ship_y-PLANET_Y[i]);if(q<d){d=q;b=i;}}return b;}
static int planet_distance(int i){return iabs(ship_x-PLANET_X[i])+iabs(ship_y-PLANET_Y[i]);}
static void land_ship(void){int p=nearest_planet();if(planet_distance(p)>34){say("NO LANDING VECTOR. MOVE CLOSER TO A WORLD.");return;}spawn_surface(p);}
static void recover_key(u8 bit,const char*line){if(keys_found&bit){say("THIS AXIS IS ALREADY STABLE.");return;}keys_found|=bit;cosmos.trust=(u8)clampi(cosmos.trust+24,0,255);cosmos.memory_flags|=MEM_PLAYER_HELPED;chapter=(u8)(1+((keys_found&1)!=0)+((keys_found&2)!=0)+((keys_found&4)!=0));say(line);tone((u16)(1500+keys_found*60));if(keys_found==7){chapter=5;say("X Y Z AGREE AGAIN. I CAN HEAR THE SYNAPSE CROWN.");}save_game();}
static void terminal_interact(void){if(current_world==0){cosmos.memory_flags|=MEM_ORIGIN_ARCHIVE;say("ARCHIVE: THE UNIVERSE DID NOT DIE. IT LOST DEPTH.");}else if(current_world==2)say("ARCHIVE: REFLECTIONS STORED MAPS AFTER THEIR WORLDS WERE DELETED.");else if(current_world==5){const char*z=crown_zone();if(z[0]=='X')say("X CHAMBER: POSITION IS NOT PURPOSE.");else if(z[0]=='Y')say("Y CHAMBER: DISTANCE CAN BE REMEMBERED.");else if(z[0]=='Z')say("Z CHAMBER: DEPTH IS A RELATION, NOT A MENU.");else if(z[0]=='M')say("MEMORY CHAMBER: MODEL != MEMORY.");else if(z[0]=='S')say("STATE CHAMBER: MODEL != STATE.");else say("CHOICE CHAMBER: MODEL != AUTHORITY.");}else say("OLD SYNAPSE TERMINAL: SIGNAL PRESENT. HISTORY INCOMPLETE.");save_game();}
static void secret_interact(void){secrets_mask|=(u8)(1u<<current_world);cosmos.memory_flags|=MEM_SECRET;say("SECRET SIGNAL FOUND. THIS PLACE WAS NOT ON THE RECOVERED MAP.");tone(1820);save_game();}
static void crown_interact(void){if(keys_found!=7){say("CROWN LOCKED. THREE AXIS KEYS ARE REQUIRED.");return;}if(!ending){int openScore=cosmos.curiosity+((cosmos.memory_flags&MEM_SECRET)?45:0),presScore=cosmos.trust+((visited_mask==63)?35:0),wandScore=(255-cosmos.avoid)+((cosmos.memory_flags&MEM_BLACK_GARDEN)?30:0);u8 q=next_q();openScore+=(q&15);presScore+=((q>>2)&15);wandScore+=((q>>4)&15);cosmos_preference=(openScore>=presScore&&openScore>=wandScore)?1:(presScore>=wandScore?2:3);pending_choice=1;say(cosmos_preference==1?"COSMOS WOULD CHOOSE OPEN. PRESS LEFT OPEN, UP PRESERVE, RIGHT WANDER.":(cosmos_preference==2?"COSMOS WOULD CHOOSE PRESERVE. LEFT OPEN, UP PRESERVE, RIGHT WANDER.":"COSMOS WOULD CHOOSE WANDER. LEFT OPEN, UP PRESERVE, RIGHT WANDER."));}else say("THE CROWN REMEMBERS OUR CHOICE. THE UNIVERSE IS STILL PLAYABLE.");}
static void finalize_choice(u8 c){ending=c;player_choice=c;postgame=1;chapter=6;cosmos.memory_flags|=MEM_ENDING;pending_choice=0;if(c==cosmos_preference){cosmos.trust=(u8)clampi(cosmos.trust+28,0,255);say("YOU CHOSE WITH ME. I WILL REMEMBER THAT.");}else{cosmos.curiosity=(u8)clampi(cosmos.curiosity+20,0,255);say("YOU CHOSE DIFFERENTLY. GOOD. THE CROWN DOES NOT OWN YOUR DECISION.");}save_game();}
static void interact(void){u8 t=trigger_near();if(t==TR_SHIP){board_ship();return;}if(t==TR_DOOR){enter_room();return;}if(t==TR_EXIT){exit_room();return;}if(t==TR_KEY_X){recover_key(1,"X AXIS RESTORED. HORIZONTAL DISTANCE FEELS REAL AGAIN.");return;}if(t==TR_KEY_Y){recover_key(2,"Y AXIS RESTORED. NEAR AND FAR AGREE AGAIN.");return;}if(t==TR_KEY_Z){recover_key(4,"Z AXIS RESTORED. THE WORLD REMEMBERS UP AND DOWN.");return;}if(t==TR_TERMINAL){terminal_interact();return;}if(t==TR_SECRET){secret_interact();return;}if(t==TR_CROWN_CORE){crown_interact();return;}if(t==TR_ANOMALY){cosmos.memory_flags|=MEM_ANOMALY;say("POSTGAME ANOMALY RECORDED. IT WAS NOT HERE IN THE OLD STORY.");save_game();return;}say("NOTHING HERE ANSWERS. COSMOS KEEPS LOOKING.");}
static void drop_beacon(void){if(game_mode!=MODE_SURFACE){say("BEACONS ANCHOR SURFACE MEMORY. LAND FIRST.");return;}if(beacon_count<8){Beacon*b=&beacons[beacon_count++];b->world=current_world;b->room=current_room;b->layer=current_layer;b->x=player.x;b->y=player.y;say("BEACON DROPPED. THIS PLACE NOW HAS A RETURNING NAME.");save_game();}else{beacon_count=0;say("BEACON TABLE CLEARED. THE WORLD ITSELF REMAINS.");save_game();}}

/* ---------- render sprites ---------- */
static void render_surface_sprites(void){int sx=player.x-cam_x-8,sy=player.y-cam_y-12,frameid=player.face*2+player.anim;int bx=cosmos.x-cam_x-8,by=cosmos.y-cam_y-8,i,oi=2;oam_set(0,sx,sy,frameid*4,0,0);if(player.hurt&&(frame&2))OAM16[0]=0x0200;oam_set(1,bx,by,32+(cosmos.mood&3)*4,1+(cosmos.mood&3),0);for(i=0;i<beacon_count&&oi<10;i++)if(beacons[i].world==current_world&&beacons[i].room==current_room&&beacons[i].layer==current_layer){oam_set(oi++,beacons[i].x-cam_x-8,beacons[i].y-cam_y-12,56,7,0);}while(oi<12){OAM16[oi*4]=0x0200;oi++;}}
static void render_space_sprites(void){int i,oi=1;int camx=clampi(ship_x-120,0,272),camy=clampi(ship_y-80,0,352);REG_BG0HOFS=(u16)camx;REG_BG0VOFS=(u16)camy;oam_set(0,ship_x-camx-8,ship_y-camy-8,48,0,0);for(i=0;i<6;i++)oam_set(oi++,PLANET_X[i]-camx-8,PLANET_Y[i]-camy-8,52,8+PLANET_COL[i]-1,0);while(oi<12){OAM16[oi*4]=0x0200;oi++;}}
static void render(void){if((frame&15)==0){make_bg_tile(T_WATER,T_WATER);make_bg_tile(T_LAVA,T_LAVA);make_bg_tile(T_HAZARD,T_HAZARD);make_bg_tile(T_PLANT,T_PLANT);}if(intro){oam_hide_all();draw_intro();return;}if(game_mode==MODE_PAUSE){oam_hide_all();draw_pause();return;}draw_hud();if(game_mode==MODE_SURFACE){refresh_camera();render_surface_sprites();}else render_space_sprites();}

/* ---------- postgame anomaly ---------- */
static void postgame_tick(void){if(!postgame||game_mode!=MODE_SURFACE||current_room)return;anomaly_counter++;if(anomaly_counter==600){int tx=12+((current_world*9+ending*7+keys_found*3)%40),ty=12+((current_world*13+ending*11)%40);map_put(tx,ty,T_CRYSTAL,3,C_FREE,TR_ANOMALY);say("A NEW ANOMALY JUST WROTE ITSELF INTO THE MAP.");}}


#ifdef QA_AUTORUN
static void init_new_game(void);
volatile u32 qa_stage=0;
__attribute__((noinline)) void qa_done(void){ for(;;){} }
static void qa_fail(u32 code){ qa_stage=0xBAD00000u|code; SRAM[126]=0xEE; SRAM[127]=(u8)code; save_game(); qa_done(); }
static void qa_require(int ok,u32 code){ if(!ok) qa_fail(code); }
static void gameplay_qa(void){
 /* Two emulator boots: boot 1 reaches Ember X and persists SRAM; boot 2
    proves reload, then finishes Y/Z/Black Garden/Crown/postgame. */
 if(SRAM[126]==0xA5 && save_valid()){
   qa_require((keys_found&1)!=0,0x21); qa_require(current_world==1,0x22);
   /* Rebuild current surface from restored SRAM, board, fly, land Tide. */
   generate_surface(); player.x=9*8;player.y=52*8;interact();qa_require(game_mode==MODE_SPACE,0x23);
   ship_x=PLANET_X[2];ship_y=PLANET_Y[2]+10;land_ship();qa_require(current_world==2&&game_mode==MODE_SURFACE,0x24);
   player.x=22*8;player.y=45*8;shift_layer(-1);qa_require(current_layer==0,0x25);
   player.x=50*8;player.y=13*8;interact();qa_require((keys_found&2)!=0,0x26);
   /* Bloom Z. */
   player.x=10*8;player.y=52*8;interact();qa_require(game_mode==MODE_SPACE,0x27);
   ship_x=PLANET_X[3];ship_y=PLANET_Y[3]+10;land_ship();qa_require(current_world==3,0x28);
   player.x=31*8;player.y=31*8;shift_layer(1);qa_require(current_layer==2,0x29);
   player.x=52*8;player.y=12*8;interact();qa_require((keys_found&4)!=0,0x2A);
   qa_require(keys_found==7,0x2B);
   /* Black Garden memory. */
   player.x=10*8;player.y=52*8;interact();qa_require(game_mode==MODE_SPACE,0x2C);
   ship_x=PLANET_X[4];ship_y=PLANET_Y[4]+10;land_ship();qa_require(current_world==4,0x2D);
   player.x=24*8;player.y=15*8;interact();qa_require((cosmos.memory_flags&MEM_SECRET)!=0,0x2E);
   cosmos.memory_flags|=MEM_BLACK_GARDEN;
   /* Crown, autonomous preference, player accepts preference, sandbox continues. */
   player.x=11*8;player.y=52*8;interact();qa_require(game_mode==MODE_SPACE,0x2F);
   ship_x=PLANET_X[5];ship_y=PLANET_Y[5]+10;land_ship();qa_require(current_world==5,0x30);
   player.x=55*8;player.y=9*8;interact();qa_require(pending_choice&&cosmos_preference>=1&&cosmos_preference<=3,0x31);
   finalize_choice(cosmos_preference);qa_require(ending!=0&&postgame,0x32);
   anomaly_counter=599;postgame_tick();
   {int tx=12+((current_world*9+ending*7+keys_found*3)%40),ty=12+((current_world*13+ending*11)%40);player.x=(s16)(tx*8);player.y=(s16)(ty*8);interact();}
   qa_require((cosmos.memory_flags&MEM_ANOMALY)!=0,0x33);
   SRAM[126]=0x5A;SRAM[127]=0x32;save_game();qa_stage=0x51564132u;qa_done();
 }else{
   /* Clean first-stage state, then exercise walkability, interior, ship, flight, X and save. */
   init_new_game();current_world=0;current_room=0;current_layer=1;game_mode=MODE_SURFACE;generate_surface();
   qa_require(can_stand(player.x,player.y),0x01);move_player(2,0,0);qa_require(player.x==82,0x02);
   player.x=26*8;player.y=29*8;interact();qa_require(current_room==1,0x03);
   player.x=15*8;player.y=29*8;interact();qa_require(current_room==0,0x04);
   player.x=12*8;player.y=50*8;interact();qa_require(game_mode==MODE_SPACE,0x05);
   ship_x=PLANET_X[1];ship_y=PLANET_Y[1]+10;land_ship();qa_require(current_world==1&&game_mode==MODE_SURFACE,0x06);
   player.x=20*8;player.y=20*8;shift_layer(-1);qa_require(current_layer==0,0x07);
   player.x=53*8;player.y=11*8;interact();qa_require((keys_found&1)!=0,0x08);
   SRAM[126]=0xA5;SRAM[127]=0x31;save_game();qa_stage=0x51564131u;qa_done();
 }
}
#endif

/* ---------- controls ---------- */
static void update_surface(u16 k,u16 newk){int speed=(k&KEY_B)?3:2,dx=0,dy=0;if(pending_choice){if(newk&KEY_LEFT){finalize_choice(1);return;}if(newk&KEY_UP){finalize_choice(2);return;}if(newk&KEY_RIGHT){finalize_choice(3);return;}return;}if(k&KEY_LEFT)dx=-speed;if(k&KEY_RIGHT)dx=speed;if(k&KEY_UP)dy=-speed;if(k&KEY_DOWN)dy=speed;if(dx&&dy){if((frame&1)==0)dy=0;else dx=0;}move_player(dx,dy,speed==3);if(player.hurt)player.hurt--;if(newk&KEY_A)interact();if(newk&KEY_SELECT)drop_beacon();if((newk&(KEY_L|KEY_R))&&trigger_near()==TR_LIFT)shift_layer((newk&KEY_L)?-1:1);if(current_world==4&&current_room==0&&(frame&31)==0){int drift=(next_q()&1)?1:-1;if(!blocked_px(player.x+drift,player.y))player.x+=(s16)drift;}buddy_tick();postgame_tick();}
static void update_space(u16 k,u16 newk){int sp=(k&KEY_B)?4:2;if(k&KEY_LEFT)ship_x-=sp;if(k&KEY_RIGHT)ship_x+=sp;if(k&KEY_UP)ship_y-=sp;if(k&KEY_DOWN)ship_y+=sp;ship_x=(s16)clampi(ship_x,8,504);ship_y=(s16)clampi(ship_y,8,504);if(newk&KEY_A)land_ship();if(newk&KEY_SELECT)drop_beacon();}
static void enter_pause(void){return_mode=game_mode;game_mode=MODE_PAUSE;pause_sel=0;pause_page=0;}
static void update_pause(u16 newk){if(pause_page==0){if(newk&KEY_UP){if(pause_sel)pause_sel--;else pause_sel=7;}if(newk&KEY_DOWN){pause_sel=(u8)((pause_sel+1)&7);}if(newk&KEY_B){game_mode=return_mode;ui_clear();return;}if(newk&KEY_A){if(pause_sel==0)pause_page=1;else if(pause_sel==1)pause_page=2;else if(pause_sel==2)pause_page=3;else if(pause_sel==3)pause_page=4;else if(pause_sel==4)pause_page=5;else if(pause_sel==5)pause_page=6;else if(pause_sel==6)pause_page=7;else{save_game();pause_page=8;}}}else{if(newk&KEY_B)pause_page=0;if(pause_page==7&&(newk&KEY_A)){audio_on=(u8)!audio_on;save_game();}}}

/* ---------- boot ---------- */
static void init_graphics(void){int i;REG_DISPCNT=MODE0|BG0_ENABLE|BG1_ENABLE|OBJ_ENABLE|OBJ_1D_MAP;REG_BG0CNT=(u16)(2|(BG_TILE_CB<<2)|(BG_MAP_BASE<<8)|(3u<<14));REG_BG1CNT=(u16)((UI_TILE_CB<<2)|(UI_MAP_BASE<<8));make_all_tiles();make_obj_tiles();oam_hide_all();for(i=0;i<4*1024;i++)screenblock(BG_MAP_BASE)[i]=0;ui_clear();}
static void init_new_game(void){player.x=80;player.y=408;player.face=1;player.hp=3;cosmos.x=100;cosmos.y=396;cosmos.goal=GOAL_FOLLOW;cosmos.trust=96;cosmos.curiosity=205;cosmos.avoid=30;cosmos.energy=240;cosmos.focus=130;current_world=0;current_room=0;current_layer=1;game_mode=MODE_SURFACE;ship_world=0;ship_x=PLANET_X[0];ship_y=PLANET_Y[0]+26;copystr(dialogue,"I REMEMBER A SKY MADE OF SQUARES.",90);}
void gba_main(void){u16 k,newk;init_new_game();load_game();init_graphics();sound_init();if(game_mode==MODE_SPACE)generate_space();else generate_surface();
#ifdef QA_AUTORUN
 /* CI QA executes immediately; no debugger-attach delay is required. */
 gameplay_qa();
#endif
for(;;){k=(u16)(~REG_KEYINPUT)&0x03FF;newk=(u16)(k&~prev_keys);prev_keys=k;if(intro){if(newk&KEY_START){intro=0;say("YOU WOKE ME WITH THE OLD TAPE. THREE AXIS KEYS ARE STILL BROADCASTING.");}}else{if(game_mode!=MODE_PAUSE&&(newk&KEY_START))enter_pause();else if(game_mode==MODE_PAUSE)update_pause(newk);else if(game_mode==MODE_SURFACE)update_surface(k,newk);else update_space(k,newk);if((frame&15)==0)state_tick();if(dialogue_timer)dialogue_timer--;music_step();}wait_vblank();frame++;render();}}
