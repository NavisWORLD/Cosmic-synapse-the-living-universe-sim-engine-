/* LOST COSMOS / Cory Davis / NavisWORLD
   Native GBA creature subsystem; V10.1 integration wires roster into a disjoint save extension.
   Pure C99, no allocation, no I/O, no live network, fixed 252-byte roster image. */
#ifndef LOST_COSMOS_CREATURE_H
#define LOST_COSMOS_CREATURE_H
#include <stddef.h>
#include <stdint.h>
#define LC_ROSTER_CAP 12u
#define LC_ROSTER_BYTES 252u
#define LC_BCP_BYTES 64u
#define LC_BCG_BYTES 60u
#define LC_SPECIES_IMPORTED 128u
#define LC_MAX_LEVEL 60u

typedef enum {LC_OK=0,LC_INVALID=1,LC_FULL=2,LC_DUPLICATE=3,
              LC_NOT_READY=4,LC_CORRUPT=5} LcResult;
typedef struct {
 uint8_t family, look, stats[10], temperament[5];
 int8_t hue; uint32_t public_id;
} LcProfile;
typedef struct {
 uint8_t species,stage,level,bond;
 uint16_t hp,xp;
 uint32_t identity,seed;
 uint8_t attack,defense,affinity,flags;
} LcCreature;
typedef struct {uint8_t count,active;LcCreature slots[LC_ROSTER_CAP];} LcRoster;
uint32_t lc_crc32(const uint8_t *data,size_t size);
uint32_t lc_prng_next(uint32_t *state);
LcResult lc_parse_bcp1(const uint8_t *blob,size_t size,LcProfile *out);
LcResult lc_validate_bcg1_guest(const uint8_t *blob,size_t size);
void lc_roster_init(LcRoster *r);
LcResult lc_add_import(LcRoster *r,const LcProfile *profile,uint32_t seed);
LcResult lc_add_wild(LcRoster *r,uint8_t species,uint32_t unique_seed);
LcResult lc_release_wild(LcRoster *r,uint8_t index);
LcResult lc_reward_xp(LcRoster *r,uint8_t index,uint16_t xp);
LcResult lc_bond(LcRoster *r,uint8_t index,uint8_t approach,uint8_t proof);
LcResult lc_evolve(LcRoster *r,uint8_t index,uint8_t catalyst);
uint16_t lc_damage(uint8_t attack,uint8_t defense,uint8_t attack_affinity,uint8_t defend_affinity);
uint8_t lc_roll_drop(uint8_t biome,uint32_t *rng);
LcResult lc_roster_encode(const LcRoster *r,uint8_t *out,size_t len);
LcResult lc_roster_decode(const uint8_t *data,size_t len,LcRoster *out);
#endif
