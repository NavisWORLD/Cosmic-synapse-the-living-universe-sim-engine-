/* V11.1 additive content. Historical structs and SRAM offsets stay frozen. */
#ifndef V11_STATE_H
#define V11_STATE_H
#include "content_v11_data.h"
#include "content_v11_art.h"
#if defined(LC_IMPORT_HAS_BCP1)
#include "content_v11_import_receipt.h"
#endif
#define V11_SRAM 6400
#define V11_BYTES 768
#define V11_FIRST_ROOM 70
#define V11_IS_ROOM (current_world==0&&current_room>=70&&current_room<=77)
#define TR_V11_ENTER 110
#define TR_V11_EXIT 111
#define TR_V11_NEXT 112
#define TR_V11_CAMP 113
#define TR_V11_BEACON 114
#define TR_V11_CACHE 115
#define TR_V11_CORE 116
#define TR_V11_ECHO 117
#define TR_V11_FORGE 118
#define TR_V11_TRIAL 119
static u8 v11_pending[100];
static u8 v11_qty[100],v11_encounters[100],v11_learned[13];
static u8 v11_equipment[3],v11_shortcuts[4],v11_passives[4],v11_ultimate=255;
static u8 v11_visited=0,v11_beacons=0,v11_last_beacon=255,v11_track=255;
static u8 v11_quest[15],v11_world_kills[8];static u16 v11_elite_day[20];
static u16 v11_quest_started=0,v11_quest_done=0,v11_boss_done=0,v11_cores_found=0;
static u32 v11_npc_seen=0,v11_caches=0,v11_ticks=0;
static u16 v11_credits=0,v11_hp=24,v11_mp=24,v11_buddy_hp=22,v11_crafted=0;
static u8 v11_echo_found=0,v11_perm_hp=0,v11_ult_charge=0,v11_xp_boost=0;
static u8 v11_durability[3]={100,100,100},v11_corvus_trust=0;
static u8 v11_text_speed=1,v11_brightness=3,v11_best_reward=0,v11_forges=0;
static u16 v11_ninth_day=65535,v11_stay_day=65535;
static u16 v11_days=0,v11_day_ticks=0,v11_scrap=0,v11_notice_timer=0;
static u8 v11_herbs=0;
static u8 v11_active_cosmos=0,v11_battle_pose=255,v11_export_ready=0,v11_cosmos_stage=0;
static char v11_cosmos_name[12];
static u8 v11_dialogue_scroll=0,v11_dialogue_reveal=0,v11_fetch_used=0;
static char v11_names[12][12]; /* Display labels only; identities never change. */
static u8 v11_enemy_id[10],v11_npc_id[6],v11_npc_count=0;
static u16 v11_enemy_hp[10],v11_enemy_max[10];
static s16 v11_npc_x[6],v11_npc_y[6];
static volatile u8 v11_ui_dirty=1;static u8 v11_list_kind=255;
static int v11_menu_handled(int page);
static u8 v11_sel=0,v11_sub=0,v11_menu_mode=0,v11_sort=0,v11_cat=0;
static u8 v11_list[100],v11_list_count=0,v11_detail=0,v11_slot=0;
static u8 v11_dialogue=0,v11_dialogue_page=0,v11_speaker=255,v11_choice=0;
static u8 v11_shop=0,v11_shop_sell=0,v11_shop_sel=0,v11_craft_sel=0;
static u8 v11_evolution=0,v11_evo_timer=0,v11_evo_old=0,v11_rename=0,v11_rename_col=0;
static u8 v11_battle_sub=0,v11_battle_sel=0,v11_turn=0,v11_gameover=0;
static u8 v11_status=0,v11_status_turn=0,v11_enemy_status=0,v11_enemy_status_turn=0;
static u8 v11_guard=0,v11_ward=0,v11_haste=0,v11_focus=0,v11_free_cast=0;
static u8 v11_decoy=0,v11_regen=0,v11_revived=0,v11_second_wind=0;
static u8 v11_invincible=0,v11_stand=0,v11_echo_turns=0,v11_enemy_buff=0,v11_phase=0;
static u8 v11_last_spell=255,v11_last_power=0,v11_judgment_used=0,v11_flare=0;
static u8 v11_add_count=0,v11_add_id[3];static u16 v11_add_hp[3];
static u8 v11_field_light=0,v11_field_track=0,v11_field_scout=0,v11_forage_day=255;
static char v11_notice[90];
static int v11_world(void);
static int v11_passive(int id);
static void v11_reset(void);
static void v11_save(void);
static void v11_restore(void);
static void v11_generate(void);
static void v11_enter(int world);
static void v11_leave(void);
static void v11_draw_field(void);
static void v11_update_field(u16 k,u16 newk);
static int v11_draw_pause(void);
static int v11_update_pause(u16 newk);
static void v11_draw_battle(void);
static void v11_update_battle(u16 newk);
static void v11_draw_import_battle(int oi,int x,int y);
static void v11_clock(void);
static int v11_inventory_add(int id,int quantity);
static int v11_skill_known(int id);
static void v11_unlock(void);
static void v11_menu_reset(void);
static void v11_title_beast(void);
static void v11_resume_art(void);
static void v11_dialogue_advance(void);
static void v11_dialogue_draw(void);
#endif
