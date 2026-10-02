#include "lc_creature.h"
static uint16_t r16(const uint8_t *p){return (uint16_t)(p[0]|((uint16_t)p[1]<<8));}
static uint32_t r32(const uint8_t *p){return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
static void w16(uint8_t*p,uint16_t v){p[0]=(uint8_t)v;p[1]=(uint8_t)(v>>8);}
static void w32(uint8_t*p,uint32_t v){for(unsigned i=0;i<4;i++)p[i]=(uint8_t)(v>>(8u*i));}
static void zero(void*p,size_t n){uint8_t*b=(uint8_t*)p;for(size_t i=0;i<n;i++)b[i]=0;}
uint32_t lc_crc32(const uint8_t*data,size_t n){
 uint32_t c=0xffffffffu;
 for(size_t i=0;i<n;i++){c^=data[i];for(unsigned j=0;j<8;j++)c=(c>>1)^((0u-(c&1u))&0xedb88320u);}
 return ~c;
}
uint32_t lc_prng_next(uint32_t *state){
 uint32_t x=*state ? *state : 0x6c637365u;
 x^=x<<13;x^=x>>17;x^=x<<5;*state=x;return x;
}
LcResult lc_parse_bcp1(const uint8_t *b,size_t n,LcProfile *p){
 if(!b||!p||n!=LC_BCP_BYTES)return LC_INVALID;
 if(b[0]!='B'||b[1]!='C'||b[2]!='P'||b[3]!='1'||b[4]!=1||b[5]>6||b[6]>2||b[7])return LC_INVALID;
 if(lc_crc32(b,60)!=r32(b+60))return LC_CORRUPT;
 unsigned sum=0;for(unsigned i=8;i<18;i++){if(b[i]<20||b[i]>80)return LC_INVALID;sum+=b[i];}
 if(sum!=500)return LC_INVALID;
 for(unsigned i=18;i<23;i++)if(b[i]<20||b[i]>80)return LC_INVALID;
 for(unsigned i=28;i<60;i++)if(b[i])return LC_INVALID;
 if(!r32(b+24))return LC_INVALID;
 zero(p,sizeof(*p));p->family=b[5];p->look=b[6];p->hue=(int8_t)b[23];p->public_id=r32(b+24);
 for(unsigned i=0;i<10;i++)p->stats[i]=b[8+i];
 for(unsigned i=0;i<5;i++)p->temperament[i]=b[18+i];
 return LC_OK;
}
/* Guest-only validator: refuse measured owner traces (even if otherwise numeric). */
LcResult lc_validate_bcg1_guest(const uint8_t *b,size_t n){
 if(!b||n!=LC_BCG_BYTES||b[0]!='B'||b[1]!='C'||b[2]!='G'||b[3]!='1'||b[4]!=1||b[5]>2||b[6]!=0||b[7])return LC_INVALID;
 for(unsigned i=8;i<60;i++)if(b[i])return LC_INVALID;
 return LC_OK;
}
void lc_roster_init(LcRoster*r){if(r)zero(r,sizeof(*r));}
static uint8_t uniq(const LcRoster*r,uint32_t id){for(unsigned i=0;i<r->count;i++)if(r->slots[i].identity==id)return 0;return 1;}
static uint8_t clamp_stat(uint16_t x){return (uint8_t)(x>255?255:x);}
LcResult lc_add_import(LcRoster*r,const LcProfile*p,uint32_t seed){
 if(!r||!p||p->family>6||!p->public_id)return LC_INVALID;
 if(r->count>=LC_ROSTER_CAP)return LC_FULL;
 if(!uniq(r,p->public_id))return LC_DUPLICATE;
 LcCreature*c=&r->slots[r->count];zero(c,sizeof(*c));
 c->species=LC_SPECIES_IMPORTED+p->family;c->level=1;c->identity=p->public_id;c->seed=seed;
 c->affinity=p->family;c->bond=10;c->hp=p->stats[0];
 c->attack=clamp_stat((uint16_t)(p->stats[2]+p->stats[5])/2);
 c->defense=clamp_stat((uint16_t)(p->stats[4]+p->stats[7])/2);
 c->flags=(uint8_t)((p->stats[9]>=50?1:0)|(p->look<<1));r->count++;return LC_OK;
}
/* Five genuine initial wild-species slots; detailed art/behaviors are separate assets. */
LcResult lc_add_wild(LcRoster*r,uint8_t species,uint32_t seed){
 if(!r||species<1||species>8)return LC_INVALID;
 if(r->count>=LC_ROSTER_CAP)return LC_FULL;
 uint32_t id=seed^((uint32_t)species*0x9e3779b9u);if(!id)id=1;
 if(!uniq(r,id))return LC_DUPLICATE;
 LcCreature*c=&r->slots[r->count];zero(c,sizeof(*c));c->species=species;c->level=1;
 c->identity=id;c->seed=seed;c->bond=5;c->hp=(uint16_t)(26+species*3);
 c->attack=(uint8_t)(18+species*4);c->defense=(uint8_t)(18+species*2);
 c->affinity=(uint8_t)((species-1)%5);r->count++;return LC_OK;
}
LcResult lc_reward_xp(LcRoster*r,uint8_t ix,uint16_t earned){
 if(!r||ix>=r->count)return LC_INVALID;
 LcCreature*c=&r->slots[ix];
 uint32_t x=(uint32_t)c->xp+earned;
 while(c->level<LC_MAX_LEVEL){uint32_t threshold=20u+3u*c->level*c->level;
 if(x<threshold)break;
 x-=threshold;c->level++;
 c->hp=(uint16_t)(c->hp+3u);c->attack=clamp_stat((uint16_t)c->attack+1u);c->defense=clamp_stat((uint16_t)c->defense+1u);}
 c->xp=(uint16_t)(x>65535u?65535u:x);return LC_OK;
}
/* Restoration=0, challenge=1, tribute=2. Actual interaction supplies proof 0..100.
   Species-specific response prevents arbitrary capture-by-dialogue. */
LcResult lc_bond(LcRoster*r,uint8_t ix,uint8_t approach,uint8_t proof){
 if(!r||ix>=r->count||approach>2||proof>100)return LC_INVALID;
 LcCreature*c=&r->slots[ix];
 uint8_t preferred=(uint8_t)((c->species>=128?c->species-128:c->species)%3);
 if(approach!=preferred||proof<55)return LC_NOT_READY;
 uint16_t bond=(uint16_t)c->bond+(proof>=85?25u:15u);
 c->bond=(uint8_t)(bond>100?100:bond);return LC_OK;
}
/* Catalyst 0 is regular, 1=Heartwood, 2=Crystal, 3=Void.
   Stage and catalyst are saved; no untestable freeform evolution. */
LcResult lc_evolve(LcRoster*r,uint8_t ix,uint8_t catalyst){
 if(!r||ix>=r->count||catalyst>3)return LC_INVALID;
 LcCreature*c=&r->slots[ix];if(c->stage>=2)return LC_NOT_READY;
 if(c->stage==0&&(c->level<12||c->bond<55))return LC_NOT_READY;
 if(c->stage==1&&(c->level<28||c->bond<80))return LC_NOT_READY;
 if(c->species>=128 && !(c->flags&1u) && !catalyst)return LC_NOT_READY;
 c->stage++;c->flags=(uint8_t)((c->flags&0x07u)|(catalyst<<3));
 c->hp=(uint16_t)(c->hp+18u);c->attack=clamp_stat((uint16_t)c->attack+8u+catalyst);
 c->defense=clamp_stat((uint16_t)c->defense+5u);
 return LC_OK;
}
uint16_t lc_damage(uint8_t atk,uint8_t defense,uint8_t a,uint8_t d){
 uint16_t power=(uint16_t)atk+6u;uint16_t guard=(uint16_t)defense/2u;
 uint16_t damage=power>guard?(uint16_t)(power-guard):(uint16_t)1u;
 /* Original cycle: Ember > Bloom > Tide > Ember. Other families neutral. */
 if((a==1&&d==3)||(a==3&&d==2)||(a==2&&d==1))damage=(uint16_t)(damage+damage/2u);
 return damage;
}
/* Noncritical region drops: 0 none, 1 material, 2 uncommon, 3 rare.
   Progression artifacts awarded by guaranteed story flags, never RNG. */
uint8_t lc_roll_drop(uint8_t biome,uint32_t*rng){if(!rng)return 0;
 uint32_t roll=lc_prng_next(rng)%10000u;
 uint16_t common=(uint16_t)(3000+(biome%5u)*250u);
 if(roll<common)return 1;
 if(roll<common+350u)return 2;
 if(roll<common+380u)return 3;
 return 0;
}
LcResult lc_roster_encode(const LcRoster*r,uint8_t*out,size_t n){
 if(!r||!out||n<LC_ROSTER_BYTES||r->count>LC_ROSTER_CAP||(r->count&&r->active>=r->count))return LC_INVALID;
 zero(out,LC_ROSTER_BYTES);out[0]='L';out[1]='C';out[2]='R';out[3]='1';out[4]=1;out[5]=r->count;out[6]=r->active;
 for(unsigned i=0;i<r->count;i++){const LcCreature*c=&r->slots[i];uint8_t*p=out+8u+20u*i;
 p[0]=c->species;p[1]=c->stage;p[2]=c->level;p[3]=c->bond;w16(p+4,c->hp);w16(p+6,c->xp);
 w32(p+8,c->identity);w32(p+12,c->seed);p[16]=c->attack;p[17]=c->defense;p[18]=c->affinity;p[19]=c->flags;
 }
 w32(out+248,lc_crc32(out,248));return LC_OK;
}
LcResult lc_roster_decode(const uint8_t*b,size_t n,LcRoster*out){
 if(!b||!out||n<LC_ROSTER_BYTES)return LC_INVALID;
 if(b[0]!='L'||b[1]!='C'||b[2]!='R'||b[3]!='1'||b[4]!=1||b[5]>LC_ROSTER_CAP||b[7])return LC_INVALID;
 if((b[5]&&b[6]>=b[5])||(!b[5]&&b[6]))return LC_INVALID;
 if(lc_crc32(b,248)!=r32(b+248))return LC_CORRUPT;
 LcRoster tmp;lc_roster_init(&tmp);tmp.count=b[5];tmp.active=b[6];
 for(unsigned i=0;i<tmp.count;i++){const uint8_t*p=b+8+20*i;LcCreature*c=&tmp.slots[i];
 c->species=p[0];c->stage=p[1];c->level=p[2];c->bond=p[3];c->hp=r16(p+4);c->xp=r16(p+6);
 c->identity=r32(p+8);c->seed=r32(p+12);c->attack=p[16];c->defense=p[17];c->affinity=p[18];c->flags=p[19];
 if(!(c->species>=1&&c->species<=8)&&!(c->species>=128&&c->species<=134))return LC_INVALID;
 if(!c->identity||!c->level||c->level>LC_MAX_LEVEL||c->stage>2||c->bond>100||c->affinity>6)return LC_INVALID;
 for(unsigned j=0;j<i;j++)if(tmp.slots[j].identity==c->identity)return LC_DUPLICATE;
 }
 {volatile uint8_t *d=(volatile uint8_t *)out;const uint8_t *src=(const uint8_t *)&tmp;
   for(size_t k=0;k<sizeof(tmp);k++)d[k]=src[k];}
 return LC_OK;
}

/* Remove a wild creature only at deliberate user request. Imported public-identity
 * companions are pinned; never silently discard unique external identities. */
LcResult lc_release_wild(LcRoster*r,uint8_t ix){
 if(!r||ix>=r->count)return LC_INVALID;
 if(r->slots[ix].species>=LC_SPECIES_IMPORTED)return LC_NOT_READY;
 for(unsigned i=ix+1;i<r->count;i++)r->slots[i-1]=r->slots[i];
 if(r->count){r->count--;
   for(unsigned j=0;j<sizeof(LcCreature);j++)((uint8_t*)&r->slots[r->count])[j]=0;}
 if(!r->count)r->active=0;
 else if(r->active>ix)r->active--;
 else if(r->active==ix&&r->active>=r->count)r->active=(uint8_t)(r->count-1);
 return LC_OK;
}
