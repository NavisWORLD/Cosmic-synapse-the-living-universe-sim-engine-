#include "../native/lc_creature.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static void bcp(uint8_t*b){memset(b,0,64);memcpy(b,"BCP1",4);b[4]=1;b[5]=2;b[6]=1;
 for(int i=0;i<10;i++)b[8+i]=50;
 for(int i=0;i<5;i++)b[18+i]=50;
 b[23]=0xf8;b[24]=0x12;b[25]=0x34;b[26]=0x56;b[27]=0x78;
 uint32_t crc=lc_crc32(b,60);for(int i=0;i<4;i++)b[60+i]=(uint8_t)(crc>>(8*i));}
int main(void){
 uint8_t b[64];LcProfile p;bcp(b);assert(lc_parse_bcp1(b,64,&p)==LC_OK);assert(p.public_id==0x78563412u&&p.hue==-8);
 b[9]=90;assert(lc_parse_bcp1(b,64,&p)!=LC_OK);bcp(b);
 uint8_t guest[60]={0};memcpy(guest,"BCG1",4);guest[4]=1;assert(lc_validate_bcg1_guest(guest,60)==LC_OK);
 guest[6]=1;assert(lc_validate_bcg1_guest(guest,60)==LC_INVALID);
 LcRoster r;lc_roster_init(&r);assert(lc_add_import(&r,&p,0x98765432)==LC_OK);assert(r.count==1);
 assert(lc_add_import(&r,&p,0xabcdef12)==LC_DUPLICATE);
 assert(lc_evolve(&r,0,1)==LC_NOT_READY);
 assert(lc_bond(&r,0,1,85)==LC_NOT_READY);/* imported family2 prefers tribute */
 assert(lc_bond(&r,0,2,85)==LC_OK);assert(lc_bond(&r,0,2,85)==LC_OK);
 assert(lc_reward_xp(&r,0,4000)==LC_OK);assert(r.slots[0].level>=12);
 assert(lc_evolve(&r,0,1)==LC_OK);assert(r.slots[0].stage==1);
 uint16_t hit=lc_damage(60,20,1,3);assert(hit>lc_damage(60,20,1,2));
 for(unsigned i=1;i<12;i++)assert(lc_add_wild(&r,(uint8_t)(1+i%5),i*31337u)==LC_OK);
 assert(lc_add_wild(&r,1,987)==LC_FULL);
 uint8_t save[LC_ROSTER_BYTES];assert(lc_roster_encode(&r,save,sizeof(save))==LC_OK);
 LcRoster restored;lc_roster_init(&restored);assert(lc_roster_decode(save,sizeof(save),&restored)==LC_OK);
 assert(restored.count==12&&restored.slots[0].identity==0x78563412u&&restored.slots[0].stage==1);
 save[21]^=1;assert(lc_roster_decode(save,sizeof(save),&restored)==LC_CORRUPT);
 printf("PASS: BCP1+BCG1 guards, deterministic XP/bond/evolution/damage, bounded roster, save CRC and corruption\n");
 return 0;
}
