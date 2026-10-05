/* Sol's SPK1 extension uses only the free 128-byte metadata gap and 1024-byte
 * SRAM tail. The roster, journal banks, LCG1 and all manual slots are untouched.
 * Actual Spark sprites come from Grok's unchanged renderer; native stage wins. */
#define SOL_SPK_META 24704u
#define SOL_SPK_TILES 31744u
static u16 sol_spark_clock;
static u32 sol_spark_checked_id,sol_spark_checked_crc;
static u8 sol_spark_checked,sol_spark_ok,sol_spark_stage=255,sol_spark_blink=255;
static u32 sol_spark_u32(unsigned o){return (u32)SRAM[o]|((u32)SRAM[o+1]<<8)|((u32)SRAM[o+2]<<16)|((u32)SRAM[o+3]<<24);}
static u32 sol_spark_crc(void){u32 c=0xffffffffu;unsigned i,j,o;u8 b;
 for(i=0;i<1696;i++){o=i<128?SOL_SPK_META+i:i<1152?SOL_SPK_TILES+i-128:24832u+96+i-1152;b=i>=20&&i<24?0:SRAM[o];
 c^=b;for(j=0;j<8;j++)c=(c>>1)^((0u-(c&1u))&0xedb88320u);}return ~c;}
static void sol_spark_restore(unsigned stage){unsigned i,p=stage?SOL_SPK_META+64+(stage-1)*32:24832u+96,t=stage?SOL_SPK_TILES+(stage-1)*512:24832u+128;
 for(i=0;i<32;i++)lc_mail_pal[i]=SRAM[p+i];for(i=0;i<512;i++)lc_mail_tiles[i]=SRAM[t+i];}
static int sol_spark_valid(void){unsigned m=SOL_SPK_META,i;u32 crc=sol_spark_u32(m+20);
 if(!lc_mail_live)return 0;
 if(sol_spark_checked&&sol_spark_checked_id==lc_mail_identity&&sol_spark_checked_crc==crc)return sol_spark_ok;
 if(sol_spark_ok)sol_spark_restore(0);
 sol_spark_checked=1;sol_spark_checked_id=lc_mail_identity;sol_spark_checked_crc=crc;sol_spark_ok=0;sol_spark_stage=sol_spark_blink=255;
 if(SRAM[m]!='S'||SRAM[m+1]!='P'||SRAM[m+2]!='K'||SRAM[m+3]!='1'||SRAM[m+4]!=1||SRAM[m+5]!=2||SRAM[m+6]||SRAM[m+7])return 0;
 if(sol_spark_u32(m+8)!=lc_mail_identity||sol_spark_u32(m+12)!=sol_spark_u32(24842)||sol_spark_u32(m+16)!=sol_spark_u32(24924))return 0;
 if(!(SRAM[24837]&2)||sol_spark_crc()!=crc)return 0;
 for(i=32;i<56;i+=4)if((unsigned)SRAM[m+i]+SRAM[m+i+2]>32||(unsigned)SRAM[m+i+1]+SRAM[m+i+3]>32)return 0;
 if(SRAM[m+56]>6||!SRAM[m+57]||SRAM[m+58]>7||SRAM[m+59]>3||SRAM[m+62]>3||SRAM[m+63]>15||sol_spark_u32(m+60)%65536u>2047)return 0;
 for(i=1;i<32;i+=2)if(SRAM[24832+96+i]&128)return 0;for(i=65;i<128;i+=2)if(SRAM[m+i]&128)return 0;
 sol_spark_ok=1;return 1;
}
static unsigned sol_spark_pixel(int x,int y){unsigned a=((y/8)*4+x/8)*32+(y&7)*4+(x&7)/2;return (lc_mail_tiles[a]>>((x&1)*4))&15;}
static void sol_spark_set_pixel(int x,int y,unsigned p){unsigned a=((y/8)*4+x/8)*32+(y&7)*4+(x&7)/2,s=(x&1)*4;lc_mail_tiles[a]=(u8)((lc_mail_tiles[a]&~(15u<<s))|(p<<s));}
static int sol_spark_refresh(void){unsigned i,stage=0,blink,period;int found=0;
 if(!sol_spark_valid())return 0;
 for(i=0;i<lc_party.count;i++)if(lc_party.slots[i].identity==lc_mail_identity&&lc_party.slots[i].seed==sol_spark_u32(SOL_SPK_META+12)){stage=lc_party.slots[i].stage;found=1;break;}
 if(!found||stage>2)return 0;
 period=120+(lc_mail_identity%181);blink=sol_spark_clock%period<8;
 if(stage==sol_spark_stage&&blink==sol_spark_blink)return 1;
 sol_spark_restore(stage);sol_spark_stage=(u8)stage;sol_spark_blink=(u8)blink;
 if(blink)for(i=0;i<2;i++){unsigned o=SOL_SPK_META+32+stage*8+i*4;int x=SRAM[o],y=SRAM[o+1],w=SRAM[o+2],h=SRAM[o+3],xx,yy;unsigned face;
 if(!w||!h)continue;face=sol_spark_pixel(x+w/2,y?y-1:0);if(!face)face=sol_spark_pixel(x?x-1:0,y+h/2);
 for(yy=y;yy<y+h;yy++)for(xx=x;xx<x+w;xx++)if(sol_spark_pixel(xx,yy))sol_spark_set_pixel(xx,yy,face);
 for(xx=x;xx<x+w;xx++)sol_spark_set_pixel(xx,y+h/2,1);}
 return 1;
}
static int sol_spark_offset(u32 identity,int horizontal){unsigned tempo,phase,gait,amp;
 if(identity!=lc_mail_identity||!sol_spark_valid())return 0;tempo=SRAM[SOL_SPK_META+57];phase=((u32)sol_spark_clock*tempo/480u)&3u;gait=SRAM[SOL_SPK_META+56];amp=SRAM[SOL_SPK_META+59];
 if(horizontal)return gait==2||gait==4||gait==5?(phase==0?-(int)amp:phase==2?(int)amp:0):0;
 return phase==1||phase==2?-(int)(gait==1?amp:1):0;
}
