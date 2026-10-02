/* Appended campaign state; legacy regions and all original room IDs are stable. */
#ifndef LC_COMPLETION_STATE_H
#define LC_COMPLETION_STATE_H
#include "story_completion_data.h"
#define COMP_SRAM 7168
#define COMP_BYTES 128
#define COMP_IS_ROOM (current_world==0 && current_room>=COMPLETION_FIRST_ROOM && current_room<COMPLETION_FIRST_ROOM+COMPLETION_SCENE_COUNT)
#define TR_COMP_ENTER 96
#define TR_COMP_EXIT 97
#define TR_COMP_NEXT 98
#define TR_COMP_OBJECTIVE 99
#define TR_COMP_SEQUENCE 103
#define TR_COMP_CACHE 106
static u32 completion_done=0,completion_seen=0,completion_cache=0;
static u8 completion_step[24],completion_choice[24],completion_sub[24];
static u8 completion_guard=0,completion_attack=0,completion_sel=0;
/* Transient input/dialogue state is deliberately never a saved battle proof. */
static u8 completion_pending=0,completion_page=0,completion_setting=0;
static u8 completion_scene=0,completion_objective=0,completion_sequence_active=0;
static u8 completion_enemy_scene=255,completion_enemy_objective=255;
static int completion_count(void){int i,n=0;for(i=0;i<24;i++)if(completion_done&(1u<<i))n++;return n;}
static int completion_attack_bonus(void){return completion_attack;}
static int completion_guard_bonus(void){return completion_guard;}
static void completion_reset(void){int i;completion_done=completion_seen=completion_cache=0;
 for(i=0;i<24;i++)completion_step[i]=completion_choice[i]=completion_sub[i]=0;
 completion_guard=completion_attack=completion_sel=0;
 completion_pending=completion_page=completion_setting=completion_sequence_active=0;
 completion_enemy_scene=completion_enemy_objective=255;
}
static int completion_available(int i);
static const char* completion_requirement(int i);
static void completion_generate_map(void);
static void completion_patch_portal(void);
static void completion_spawn(void);
static int completion_enemy_defeated(Enemy *e);
static void completion_interact(u8 t);
static void completion_input(u16 keys);
static void completion_draw_ui(void);
static void completion_warp(int i);
#endif
