/* Baked Spark Beast art. Field frames are 32x32. Portraits are 64x64.
 * world 255 is a companion evolution line and is not a map spawn.
 * OBJ palette 15 and tiles 640 / 896 stay reserved for the imported beast. */
#ifndef SPARK_ART_H
#define SPARK_ART_H
#include "spark_field_beasts.h"
static int spark_name_eq(const char*a,const char*b){
 int i;if(!a||!b)return 0;
 for(i=0;i<12;i++){
  unsigned char ca=(unsigned char)a[i],cb=(unsigned char)b[i];
  if(ca>='a'&&ca<='z')ca=(unsigned char)(ca-32);
  if(cb>='a'&&cb<='z')cb=(unsigned char)(cb-32);
  if(ca!=cb)return 0;
  if(!ca)return 1;
 }
 return 1;
}
/* A callsign matches the first form of its line. Later stages of that line
 * follow the party stage. Any other name uses the field roster. */
static int spark_form_index(const char*name,int stage){
 int i,named=-1;
 if(!name||!name[0])return -1;
 if(stage<0)stage=0;
 if(stage>2)stage=2;
 for(i=0;i<SPARK_FIELD_COUNT;i++){
  if(SPARK_FIELD[i].world==255&&SPARK_FIELD[i].stage==0&&spark_name_eq(SPARK_FIELD[i].name,name)){
   int at=i+stage;
   if(at<SPARK_FIELD_COUNT&&SPARK_FIELD[at].world==255)return at;
  }
 }
 for(i=0;i<SPARK_FIELD_COUNT;i++){
  if(SPARK_FIELD[i].world==255)continue;
  if(!spark_name_eq(SPARK_FIELD[i].name,name))continue;
  if(SPARK_FIELD[i].stage==(u8)stage)return i;
  if(named<0)named=i;
 }
 if(named>=0)return named;
 for(i=0;i<SPARK_FIELD_COUNT;i++){
  if(!spark_name_eq(SPARK_FIELD[i].name,name))continue;
  if(SPARK_FIELD[i].stage==(u8)stage)return i;
  if(named<0)named=i;
 }
 return named;
}
static void spark_upload_portrait(int id){
 int i;volatile u16*dst=(volatile u16*)OBJ_VRAM32;const u8*src;
 if(id<0||id>=SPARK_FIELD_COUNT)return;
 src=SPARK_PORTRAIT_TILES[id];
 for(i=0;i<16;i++)OBJ_PALETTE[LC_IMPORT_OBJ_PAL*16+i]=SPARK_PORTRAIT_PAL[id][i];
 for(i=0;i<1024;i++)dst[LC_IMPORT_OBJ_TILE*16+i]=(u16)src[i*2]|((u16)src[i*2+1]<<8);
}
static void spark_upload_field(int id,int pose){
 int i;volatile u16*dst=(volatile u16*)OBJ_VRAM32;const u8*src;
 if(id<0||id>=SPARK_FIELD_COUNT)return;
 src=SPARK_FIELD_TILES[id][pose&1];
 for(i=0;i<16;i++)OBJ_PALETTE[LC_IMPORT_OBJ_PAL*16+i]=SPARK_FIELD_PAL[id][i];
 for(i=0;i<256;i++)dst[LC_IMPORT_FIELD_OBJ_TILE*16+i]=(u16)src[i*2]|((u16)src[i*2+1]<<8);
}
#endif
