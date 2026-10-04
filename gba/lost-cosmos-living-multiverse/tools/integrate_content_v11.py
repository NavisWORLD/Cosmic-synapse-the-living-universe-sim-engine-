#!/usr/bin/env python3
"""Small audited hooks into the original TU; all new implementation is modular."""
from pathlib import Path
path=Path(__file__).resolve().parents[1]/'LOST_COSMOS_V10_SOURCE/lost_cosmos_v5.c'
s=path.read_text()
if '#include "content_v11_state.h"' in s:
    raise SystemExit('Content hooks already installed')
def replace(old,new):
    global s
    if s.count(old)!=1:raise ValueError(f'Expected one hook: {old[:90]} ({s.count(old)})')
    s=s.replace(old,new)
replace('#define MEM_SHIP           (1u<<7)', '#define MEM_SHIP           (1u<<7)\n#include "content_v11_state.h"')
replace('static void generate_surface(void){int i;location_banner=150;',
        'static void generate_surface(void){int i;if(V11_IS_ROOM){world_build_cover("FOLLOWING THE NEW SIGNAL");v11_generate();return;}location_banner=150;')
replace('completion_patch_portal();spawn_monsters();spawn_npcs();v108_paint_world();',
        'completion_patch_portal();spawn_monsters();spawn_npcs();v108_paint_world();\n if(current_world==0&&current_room==2){map_put(34,44,T_RUNE,3,C_FREE,TR_V11_ENTER);map_put(34,43,T_PATH,1,C_FREE,0);}')
replace('static void draw_battle(void){Enemy*e=&enemies[battle_index];',
        'static void draw_battle(void){if(V11_IS_ROOM){v11_draw_battle();return;}Enemy*e=&enemies[battle_index];')
replace('lc_draw_import_field(3,108,59,0,1);','v11_draw_import_battle(3,91,40);')
replace('REG_DISPCNT|=BG1_ENABLE;ui_pause_canvas();','REG_DISPCNT|=BG1_ENABLE;ui_pause_canvas();if(v11_draw_pause())return;')
replace('g7_save();completion_save();journal_commit();','g7_save();completion_save();v11_save();journal_commit();')
replace('g7_restore();completion_restore();','g7_restore();completion_restore();v11_restore();')
replace('static void update_battle(u16 newk){Enemy*e=&enemies[battle_index];',
        'static void update_battle(u16 newk){if(V11_IS_ROOM){v11_update_battle(newk);return;}Enemy*e=&enemies[battle_index];')
replace('static void interact(void){u8 t=trigger_near();if(t>=TR_GATE)',
        'static void interact(void){u8 t=trigger_near();if(t==TR_V11_ENTER){v11_enter(0);return;}if(t>=TR_GATE)')
replace('static void render(void){if((frame&15)',
        'static void render(void){if(!intro&&!cinema_active&&game_mode==MODE_SURFACE&&V11_IS_ROOM){refresh_camera();v11_draw_field();return;}if((frame&15)')
replace('static void update_surface(u16 k,u16 newk){int speed=',
        'static void update_surface(u16 k,u16 newk){if(V11_IS_ROOM){v11_update_field(k,newk);return;}int speed=')
replace('static void enter_pause(void){return_mode=game_mode;',
        'static void enter_pause(void){v11_menu_reset();return_mode=game_mode;')
replace('static void update_pause(u16 newk){\n',
        'static void update_pause(u16 newk){\n if(v11_update_pause(newk))return;\n')
replace('static void init_new_game(void){int i;arc_reset();',
        'static void init_new_game(void){int i;keys_found=secrets_mask=chapter=ending=postgame=cosmos_preference=player_choice=beacon_count=0;visited_mask=1;arc_reset();')
replace('copystr(dialogue,"I REMEMBER A SKY MADE OF SQUARES.",90);}',
        'copystr(dialogue,"I REMEMBER A SKY MADE OF SQUARES.",90);v11_reset();}')
replace('void gba_main(void){u16 k,newk;',
        '#include "content_v11_core.h"\n#include "content_v11_world.h"\n#include "content_v11_combat.h"\n#include "content_v11_menus.h"\nvoid gba_main(void){u16 k,newk;')
replace('if(game_mode!=MODE_PAUSE&&(newk&KEY_START))enter_pause();',
        'if(game_mode!=MODE_PAUSE&&!v11_gameover&&(newk&KEY_START))enter_pause();')
replace('music_step();v108_credits_tick();wait_vblank();frame++;render();',
        'v11_clock();music_step();v108_credits_tick();wait_vblank();frame++;render();')
replace('ui_text(6,17,"A OPEN",14);ui_text(19,17,"B CLOSE",13);',
        'ui_text(4,3,"SELECT ARIN STATUS",13);ui_text(6,17,"A OPEN",14);ui_text(19,17,"B CLOSE",13);')
replace('static void draw_intro(void){\n', 'static void draw_intro(void){\n v11_title_beast();\n')
path.write_text(s)
print('Installed additive content hooks; original native campaign functions retained.')
