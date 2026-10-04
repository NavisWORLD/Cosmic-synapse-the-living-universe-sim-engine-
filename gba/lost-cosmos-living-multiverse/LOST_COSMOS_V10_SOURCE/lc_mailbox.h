/* LCX1 living-link mailbox. Additive SRAM only.
 *
 * V11.1 map this must not touch:
 *   main page 0..8191, including roster at 1024 and the journal snapshot
 *   journal banks 8192 and 16384
 *   journal metadata 24576..24703
 * Content Bible regions remain owned by V11.1:
 *   LCEX 6208..6399, LC11 6400..7167
 *   LCM1 slots at 25600, 27648 and 29696 (2048 bytes each)
 *
 * This mailbox is 644 bytes at 24832 (0x6100), ending at 25475.
 * 24704..24831 stays empty after the journal metadata.
 * 25476..25539 is the optional LCG1 cage record. The cartridge only reads it.
 * 25540..25599 stays empty before the first LCM1 slot.
 *
 * The cartridge parses BCP1 and calls lc_add_import. The host must not write
 * the LCR1 roster image. Raw sensor samples are not part of this record.
 */
#ifndef LOST_COSMOS_MAILBOX_H
#define LOST_COSMOS_MAILBOX_H
#define LC_MAILBOX_SRAM 24832u
#define LC_MAILBOX_BYTES 644u
#define LC_MAIL_BODY 640u
#define LC_GROWTH_SRAM 25476u
#define LC_GROWTH_BYTES 64u
typedef char lc_mailbox_fits_before_lcm1[(LC_MAILBOX_SRAM + LC_MAILBOX_BYTES <= LC_GROWTH_SRAM) ? 1 : -1];
typedef char lc_growth_fits_before_lcm1[(LC_GROWTH_SRAM + LC_GROWTH_BYTES <= 25600u) ? 1 : -1];

static u32 lc_mail_read32(unsigned o){
 return (u32)SRAM[o]|((u32)SRAM[o+1]<<8)|((u32)SRAM[o+2]<<16)|((u32)SRAM[o+3]<<24);
}
static void lc_mail_write32(unsigned o,u32 v){
 unsigned i;for(i=0;i<4;i++)SRAM[o+i]=(u8)(v>>(8*i));
}
static u32 lc_sram_crc(unsigned o,unsigned n){
 u32 c=0xffffffffu;unsigned i,j;
 for(i=0;i<n;i++){
  c^=SRAM[o+i];
  for(j=0;j<8;j++)c=(c>>1)^((0u-(c&1u))&0xedb88320u);
 }
 return ~c;
}
static u32 lc_mail_crc(void){return lc_sram_crc(LC_MAILBOX_SRAM,LC_MAIL_BODY);}
/* Missing or mismatched LCG1 is a no-op. Epoch stays in a u32 so the save cannot overflow. */
static void lc_growth_publish(u32 public_id){
 unsigned g=LC_GROWTH_SRAM,i;u8 flags;u16 layer,points;
 lc_mail_epoch=0;lc_mail_trade=0;lc_mail_grown=0;
 if(SRAM[g]!='L'||SRAM[g+1]!='C'||SRAM[g+2]!='G'||SRAM[g+3]!='1'||SRAM[g+4]!=1)return;
 flags=SRAM[g+5];
 if(flags&~3u)return;
 if(SRAM[g+6]||SRAM[g+7])return;
 for(i=28;i<60;i++)if(SRAM[g+i])return;
 if(lc_mail_read32(g+24)!=public_id)return;
 if(lc_sram_crc(g,60)!=lc_mail_read32(g+60))return;
 layer=(u16)SRAM[g+12]|((u16)SRAM[g+13]<<8);
 points=(u16)SRAM[g+14]|((u16)SRAM[g+15]<<8);
 if(layer>999u||points>999u)return;
 lc_mail_epoch=lc_mail_read32(g+8);
 lc_mail_trade=(u8)((flags&1u)?1:0);
 lc_mail_grown=(u8)((flags&2u)?1:0);
}
static int lc_mail_body(int x,int y,int family){
 int dx=x-15,dy=y-16,ax=dx<0?-dx:dx,ay=dy<0?-dy:dy;
 if(x<6||x>25||y<6||y>25)return 0;
 switch(family%7){
  case 0: return dx*dx+dy*dy<=36;
  case 1: return (dx*dx)/2+dy*dy<=40;
  case 2: return dx*dx+(dy*dy)/2<=40;
  case 3: return ax+ay<=8;
  case 4: return dx*dx+dy*dy<=34 && dx*dx+dy*dy>=10;
  case 5: return dx*dx<=36 && ay<=6;
  default: return dx*dx+dy*dy<=32 && !(dx>1 && ay<2);
 }
}
static u8 lc_mail_color_at(int x,int y,int family,int hue){
 int body=lc_mail_body(x,y,family);
 if(!body)return 0;
 if(!lc_mail_body(x-1,y,family)||!lc_mail_body(x+1,y,family)||
    !lc_mail_body(x,y-1,family)||!lc_mail_body(x,y+1,family))return 1;
 if((y>=14&&y<=16)&&((x>=11&&x<=12)||(x>=18&&x<=19)))return 4;
 if(((x+hue)&2)!=0)return 3;
 return 2;
}
static u16 lc_mail_rgb(int r,int g,int b){
 if(r<0)r=0;if(r>31)r=31;if(g<0)g=0;if(g>31)g=31;if(b<0)b=0;if(b>31)b=31;
 return (u16)RGB5(r,g,b);
}
static void lc_mail_paint(int family,int hue){
 int ty,tx,y,x,i,h=hue;
 int r=14+((h+family*3)&15),g=10+((family*4)&15),b=20-((h>>2)&12);
 u16 outline=lc_mail_rgb(2,2,4),body=lc_mail_rgb(r,g,b),lite=lc_mail_rgb(r+8,g+10,b+6),eye=lc_mail_rgb(31,31,28);
 lc_mail_pal[0]=0;lc_mail_pal[1]=0;
 lc_mail_pal[2]=(u8)outline;lc_mail_pal[3]=(u8)(outline>>8);
 lc_mail_pal[4]=(u8)body;lc_mail_pal[5]=(u8)(body>>8);
 lc_mail_pal[6]=(u8)lite;lc_mail_pal[7]=(u8)(lite>>8);
 lc_mail_pal[8]=(u8)eye;lc_mail_pal[9]=(u8)(eye>>8);
 for(i=10;i<32;i++)lc_mail_pal[i]=0;
 for(ty=0;ty<4;ty++)for(tx=0;tx<4;tx++)for(y=0;y<8;y++)for(x=0;x<8;x+=2){
  u8 lo=lc_mail_color_at(tx*8+x,ty*8+y,family,hue);
  u8 hi=lc_mail_color_at(tx*8+x+1,ty*8+y,family,hue);
  lc_mail_tiles[(ty*4+tx)*32+y*4+x/2]=(u8)(lo|(hi<<4));
 }
}
static void lc_mail_read_name(unsigned o){
 int i,ok=1;lc_mail_name[0]=0;
 for(i=0;i<12;i++){
  u8 ch=SRAM[o+14+i];
  if(!ch){lc_mail_name[i]=0;break;}
  if(!((ch>='A'&&ch<='Z')||(ch>='0'&&ch<='9')||ch==' ')){ok=0;break;}
  lc_mail_name[i]=(char)ch;lc_mail_name[i+1]=0;
 }
 if(!ok)lc_mail_name[0]=0;
}
/* commit=1 writes the consumed flag only after the identity is in the party.
   The roster image itself is still written by the existing save path. */
static void lc_mailbox_refresh(int commit){
 unsigned o=LC_MAILBOX_SRAM,i;
 u8 bcp[64],flags;
 LcProfile prof;
 u32 seed;
 int result;
 lc_mail_epoch=0;lc_mail_trade=0;lc_mail_grown=0;
 if(SRAM[o]!='L'||SRAM[o+1]!='C'||SRAM[o+2]!='X'||SRAM[o+3]!='1'||SRAM[o+4]!=1)return;
 if(SRAM[o+9])return;
 flags=SRAM[o+5];
 if(flags&~7u)return;
 for(i=0;i<6;i++)if(SRAM[o+26+i])return;
 if(lc_mail_crc()!=lc_mail_read32(o+LC_MAIL_BODY))return;
 for(i=0;i<64;i++)bcp[i]=SRAM[o+32+i];
 if(lc_parse_bcp1(bcp,64,&prof)!=LC_OK)return;
 seed=lc_mail_read32(o+10);if(!seed)seed=1;
 if((flags&1u)){
  int present=0;
  for(i=0;i<lc_party.count;i++)if(lc_party.slots[i].identity==prof.public_id)present=1;
  if(!present){
   result=lc_add_import(&lc_party,&prof,seed);
   if(result==LC_OK){
    LcCreature*c=&lc_party.slots[lc_party.count-1];
    unsigned bond=10;u8 focus=SRAM[o+6],calm=SRAM[o+7];
    if(focus<=100)bond+=focus/20u;
    if(calm<=100)bond+=calm/25u;
    if(bond>40)bond=40;
    c->bond=(u8)bond;
    lc_party.active=(u8)(lc_party.count-1);
    lc_party_sel=lc_party.active;
   }else if(result!=LC_DUPLICATE){
    lc_mail_live=0;return;
   }
  }
 }
 {int present=0;
  for(i=0;i<lc_party.count;i++)if(lc_party.slots[i].identity==prof.public_id)present=1;
  if(!present){lc_mail_live=0;return;}}
 lc_mail_read_name(o);
 if(flags&2u){
  for(i=0;i<32;i++)lc_mail_pal[i]=SRAM[o+96+i];
  for(i=0;i<512;i++)lc_mail_tiles[i]=SRAM[o+128+i];
 }else lc_mail_paint((int)prof.family,(int)prof.hue);
 lc_mail_live=1;
 lc_mail_identity=prof.public_id;
 lc_mail_species=(u8)(LC_SPECIES_IMPORTED+prof.family);
 lc_mail_ready=1;
 lc_growth_publish(prof.public_id);
 if(commit && (flags&1u)){
  SRAM[o+5]=(u8)((flags|4u)&~1u);
  lc_mail_write32(o+LC_MAIL_BODY,lc_mail_crc());
 }
}
#endif
