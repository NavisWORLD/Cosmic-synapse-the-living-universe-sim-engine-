/* V10.3 native wildlife design / 5 NEW OPTIONAL HABITAT SANCTUARY QUESTS.
 * Game-only additions inspired by ecosystem motifs; not verbatim manuscript.
 * Shrine entry always optional; original campaign and legacy world IDs unchanged. */
static const char* const ECO_NAMES[8]={
 "FORGELING","TIDEWISP","ROOTKIN","VOIDMOTH","SKYSPARK",
 "FROST WOLF","EMBER PHOENIX","HOLLOW WRAITH"};
static const char* const ECO_STAGE1[8]={
 "HEARTHCUB","RILLWISP","THORNBARK","NIGHTMOTH","STORMWING",
 "FROSTFANG","SUNPLUME","DUSKSPIRIT"};
static const char* const ECO_STAGE2[8]={
 "SOLFORGE","DEEPTIDE","WORLDROOT","ECLIPSEMOTH","SKYFORGE",
 "GLACIAL KING","ASHEN PHOENIX","VEILKEEPER"};
static const char* const ECO_HABITAT[8]={
 "EMBER AXIS","TIDE MEMORY","BLOOM Z","BLACK GARDEN","SYNAPSE CROWN",
 "GLACIAL GROTTO","EMBER CAVERNS","HOLLOW GROVE"};
static const char* const ECO_ABILITY[8]={
 "FORGE STRIKE","TIDAL SHIELD","ROOT GUARD","VOID STEP","ARC LIGHT",
 "FROST WARD","PHOENIX FIRE","CURSE CLEANSE"};
/* Five sanctuary villages have standalone region mechanics; do not gate main quest. */
static const char* const ECO_SHRINES[5]={
 "FORGE VOW: BRING 2 SHARDS","TIDE OATH: FIND CHRONOHEART",
 "ROOT RITE: BRING 1 CORE","VOID MIRROR: FIND VOID SIGIL",
 "SKY PACT: RECOVER X Y Z"};
static const int ECO_SHRINE_X[5]={24,28,35,27,20};
static const int ECO_SHRINE_Y[5]={51,52,51,32,53};
/* Map enemy classes to the correctly named game species. Glitch is a sky signal. */
static u8 eco_species_for_enemy(u8 type){
 switch(type){case EN_EMBER:return 1;case EN_TIDE:return 2;
 case EN_BLOOM:return 3;case EN_VOID:return 4;
 case EN_CROWN:return 5;default:return 5;}
}
static int eco_capture_count(int species){int n=0;
 for(int i=0;i<lc_party.count;i++)if(lc_party.slots[i].species==species)n++;
 return n;
}
static int eco_unlocked(int species){
 if(species>=1&&species<=5)return !!(lc_sanctuary_mask&(1u<<(species-1)));
 return eco_capture_count(species)>0;
}
