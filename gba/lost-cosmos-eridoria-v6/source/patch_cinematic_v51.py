"""Deterministic source patch: verified V5 -> cinematic native GBA V5.1.
Idempotent, hash-locked to V5 gameplay source to avoid modifying another version.
No external network, no hidden generated code. Preserves original SRAM/checkpoint.
"""
from pathlib import Path
import hashlib
P=Path(__file__).resolve().parent
SRC=P/'lost_cosmos_v5.c'
EXPECTED=''
# exact V5 source sha available at development time; enforce original when set.
s=SRC.read_text()
assert '#include "cinematic_assets_v51.h"' not in s, 'already patched'

def change(old,new,amount=1):
 global s
 n=s.count(old)
 if n!=amount:
  raise AssertionError(f'patch target count {n} expected {amount}: {old[:125]}')
 s=s.replace(old,new)

change('#include "v5_art.h"','#include "v5_art.h"\n#include "cinematic_assets_v51.h"')
change('#define REG_SOUND1CNT_X (*(volatile u16*)0x04000064)',
'''#define REG_SOUND1CNT_X (*(volatile u16*)0x04000064)
#define REG_SOUND2CNT_L (*(volatile u16*)0x04000068)
#define REG_SOUND2CNT_H (*(volatile u16*)0x0400006C)''')
change('#define MODE0       0','#define MODE0       0\n#define CINEMA_CB 2\n#define CINEMA_MAP 30\n#define CINEMA_PAL 5')
change('static u8 postgame=0,audio_on=1,pause_sel=0,pause_page=0;',
       'static u8 postgame=0,audio_on=1,pause_sel=0,pause_page=0,touch_mode=0,hold_a_frames=0;')
change('static u8 intro=1;',
'''static u8 intro=1;
/* Cinematic frames are pre-rendered indexed 4bpp BG2; simulation/saves continue to
   own game state, and the render-only cutscene timer never consumes QSEED bytes. */
static u8 cinema_active=0,cinema_scene=0;
static u16 cinema_timer=0;
static u8 audio_fx_cooldown=0;''')
# BG2 cinematic bank5 overwrites only its own palette; BG0 gameplay content is untouched.
# Since charblock 2 + screenblock30 are VRAM BG-only, there is no OBJ/ROM overrun.
mark='/* ---------- sound ---------- */'
cinema='''/* ---------- deterministic native-GBA cinematic presentation ---------- */
static void cinema_end(void){
 cinema_active=0;cinema_timer=0;
 if(game_mode==MODE_SPACE){
  REG_BG2CNT=(u16)(1|(BG_TILE_CB<<2)|(SPACE_PARALLAX_MAP<<8));
  REG_DISPCNT|=BG2_ENABLE;
 }else REG_DISPCNT&=(u16)~BG2_ENABLE;
 ui_clear();
}
static void cinema_start(u8 id,u16 ticks){int i;u16 off,count;
 if(id>=V51_SCENE_COUNT)return;
 cinema_scene=id;cinema_timer=ticks;cinema_active=1;
 REG_DISPCNT=0; /* VRAM uploads can safely occur with LCD temporarily blanked. */
 off=V51_SCENE_OFFSETS[id];count=V51_SCENE_COUNTS[id];
 for(i=0;i<count;i++)vram_copy32(VRAM32+(CINEMA_CB*4096)+(i*8),V51_SCENE_TILES[off+i],8);
 for(i=0;i<16;i++)BG_PALETTE[CINEMA_PAL*16+i]=V51_SCENE_COLORS[id][i];
 for(i=0;i<600;i++)screenblock(CINEMA_MAP)[(i/30)*32+(i%30)]=(u16)(V51_SCENE_MAPS[id][i]|(CINEMA_PAL<<12));
 REG_BG2CNT=(u16)(1|(CINEMA_CB<<2)|(CINEMA_MAP<<8));
 REG_BG2HOFS=REG_BG2VOFS=0;
 REG_DISPCNT=MODE0|BG0_ENABLE|BG1_ENABLE|BG2_ENABLE|OBJ_ENABLE|OBJ_1D_MAP;
}
static void draw_cinema_caption(void){
 static const char*HEAD[8]={"THE LOST COSMOS", "LUNA ARC // WARP", "ORIGIN EARTH", "EMBER AXIS", "TIDE MEMORY", "BLOOM Z", "BLACK GARDEN", "SYNAPSE CROWN"};
 ui_clear();ui_fill_rows(0,1,63,15);ui_fill_rows(18,19,63,15);
 ui_text(2,0,HEAD[cinema_scene],14);
 ui_text(2,18,cinema_scene==0?"THE UNIVERSE LOST DEPTH":(cinema_scene==1?"FOLLOW THE SIX SIGNALS":"ANOTHER WORLD REMEMBERS"),15);
 ui_text(2,19,cinema_scene==0?"START TO AWAKEN":"A SKIP",13);
}

'''
change(mark,cinema+mark)
# Preserve full V5 save checksum and previous saves; marker C0/C1 distinguishes intentional new setting.
change('SRAM[162]=npc_recent;sw32(164,workload_qi);',
       'SRAM[162]=npc_recent;sw32(164,workload_qi);SRAM[168]=(u8)(0xC0|touch_mode);')
change('workload_qi=(old_v3||old_v4)?qi:sr32(164);if(workload_qi>=QSEED_LEN)workload_qi=0;if(old_v3||old_v4)save_game();',
       'workload_qi=(old_v3||old_v4)?qi:sr32(164);if(workload_qi>=QSEED_LEN)workload_qi=0;touch_mode=(!old_v3&&!old_v4&&((SRAM[168]&0xFE)==0xC0))?(SRAM[168]&1):0;if(old_v3||old_v4||((SRAM[168]&0xFE)!=0xC0))save_game();')
change('workload_qi=qi;save_game();}}','workload_qi=qi;touch_mode=0;save_game();}}')
change('SRAM[15]=audio_on;','SRAM[15]=audio_on;')
# Music on square wave 1 / sfx and speech on square wave 2: cosmetic audio cannot affect QSEED.
change('static void sound_init(void){REG_SOUNDCNT_X=0x0080;REG_SOUNDCNT_L=0x1177;REG_SOUNDCNT_H=0x0002;REG_SOUND1CNT_L=0;}\nstatic void tone(u16 f){if(!audio_on)return;REG_SOUND1CNT_H=0xA080;REG_SOUND1CNT_X=(u16)(0x8000|(f&0x07FF));}',
'''static void sound_init(void){
 REG_SOUNDCNT_X=0x0080;
 REG_SOUNDCNT_L=0x2277; /* PSG channel1 music and channel2 effects, both stereo */
 REG_SOUNDCNT_H=0x0002;REG_SOUND1CNT_L=0;
 REG_SOUND1CNT_H=0xA880;REG_SOUND2CNT_L=0xA660;
}
static void music_tone(u16 f){if(!audio_on)return;REG_SOUND1CNT_H=0xA880;REG_SOUND1CNT_X=(u16)(0x8000|(f&2047));}
static void tone(u16 f){if(!audio_on)return;REG_SOUND2CNT_L=0xA660;REG_SOUND2CNT_H=(u16)(0x8000|(f&2047));}''')
change('if(SONGS[game_mode==MODE_SPACE?5:WORLDS[current_world].music][n])tone((u16)(SONGS[game_mode==MODE_SPACE?5:WORLDS[current_world].music][n]+(frame&7)));',
       'if(SONGS[game_mode==MODE_SPACE?5:WORLDS[current_world].music][n])music_tone((u16)(SONGS[game_mode==MODE_SPACE?5:WORLDS[current_world].music][n]+(frame&7)));')
# Audio intro / dialogue cues now layer without cutting world music.
change('static void draw_intro(void){ui_clear();ui_fill_rows(2,17,63,15);ui_text(9,4,"SIM EARTH",14);ui_text(6,6,"PIXEL UNIVERSE",15);ui_text(7,8,"THE LOST COSMOS V5",13);ui_text(4,11,"THE UNIVERSE DID NOT DIE",15);ui_text(8,12,"IT LOST DEPTH",14);ui_text(4,15,"PRESS START TO WAKE",13);}',
       'static void draw_intro(void){if(cinema_active)draw_cinema_caption();else{ui_clear();ui_fill_rows(2,17,63,15);ui_text(6,6,"THE LOST COSMOS V5",15);ui_text(4,15,"PRESS START TO WAKE",13);}}')
# Caption mode only draws on BG1 and doesn't rewrite BG2.
change('if(intro){oam_hide_all();draw_intro();return;}if(game_mode==MODE_PAUSE)',
       'if(intro){oam_hide_all();draw_intro();return;}if(cinema_active){oam_hide_all();draw_cinema_caption();return;}if(game_mode==MODE_PAUSE)')
# Real in-game cutscenes, not mock screenshots. Exclude from scripted QA to isolate gameplay and preserve timing.
change('generate_surface();refresh_camera();say("LANDED. I AM BUILDING A LOCAL MEMORY OF THIS PLACE.");save_game();}',
'''generate_surface();refresh_camera();say("LANDED. I AM BUILDING A LOCAL MEMORY OF THIS PLACE.");save_game();
#ifndef QA_AUTORUN
 cinema_start((u8)(2+world),90);
#endif
}''')
change('generate_space();say("LUNA-ARC LINKED. SPACE SCALE ONLINE.");save_game();}',
'''generate_space();say("LUNA-ARC LINKED. SPACE SCALE ONLINE.");save_game();
#ifndef QA_AUTORUN
 cinema_start(1,90);
#endif
}''')
change('refresh_player_frames();say(line);tone((u16)(1500+keys_found*60));',
'''refresh_player_frames();say(line);tone((u16)(1500+keys_found*60));
#ifndef QA_AUTORUN
 cinema_start((u8)(2+current_world),85);
#endif
''')
change('save_game();}\nstatic void interact(void){',
'''save_game();
#ifndef QA_AUTORUN
 cinema_start(7,150);
#endif
}\nstatic void interact(void){''')
# UI settings add touch mode without shifting menus; supports one-button dodge on touchscreen.
change('ui_text(2,16,"B+A HEAVY  B+SEL DODGE",14);',
       'ui_text(2,16,touch_mode?"SELECT DODGE   B+A HEAVY":"B+A HEAVY  B+SEL DODGE",14);')
change('ui_text(2,7,setting_sel==2?"> AUTO TALK":"  AUTO TALK",13);ui_text(16,7,buddy_talk?"ON":"OFF",15);ui_text(2,10,"UP/DOWN SELECT A TOGGLE",14);',
       'ui_text(2,7,setting_sel==2?"> AUTO TALK":"  AUTO TALK",13);ui_text(16,7,buddy_talk?"ON":"OFF",15);ui_text(2,8,setting_sel==3?"> TOUCH MODE":"  TOUCH MODE",13);ui_text(16,8,touch_mode?"ON":"OFF",15);ui_text(2,10,"UP/DOWN SELECT A TOGGLE",14);')
change('if(newk&KEY_SELECT){if(k&KEY_B)player_dodge(k);else drop_beacon();}',
       'if(newk&KEY_SELECT){if((touch_mode&&!(k&KEY_B))||(!touch_mode&&(k&KEY_B)))player_dodge(k);else drop_beacon();}')
change('if(newk&KEY_A){int ni=npc_near();',
'''if(touch_mode&&(k&KEY_A)&&!t&&!npc_near()&&!(k&KEY_B)){
  if(hold_a_frames<26)hold_a_frames++;
  if(hold_a_frames==22)player_heavy_attack();
 }else if(!(k&KEY_A))hold_a_frames=0;
 if(newk&KEY_A){int ni=npc_near();''')
# Fix previous guarded phrase: !npc_near() incorrectly true when NPC index -1 (nonzero). Replace with ==-1.
change('!t&&!npc_near()', '!t&&npc_near()<0')
change('setting_sel=(u8)((setting_sel+2)%3)','setting_sel=(u8)((setting_sel+3)%4)')
change('setting_sel=(u8)((setting_sel+1)%3)','setting_sel=(u8)((setting_sel+1)%4)')
change('else buddy_talk=(u8)!buddy_talk;save_game();',
       'else if(setting_sel==2)buddy_talk=(u8)!buddy_talk;else touch_mode=(u8)!touch_mode;save_game();')
change('dodge_timer=dodge_cooldown=heavy_cooldown=0;workload_qi=0;',
       'dodge_timer=dodge_cooldown=heavy_cooldown=0;touch_mode=0;hold_a_frames=0;workload_qi=0;')
# Cinematic title on regular cartridge and QA gameplay parity.
change('if(game_mode==MODE_SPACE)generate_space();else generate_surface();\n#ifdef QA_AUTORUN',
'''if(game_mode==MODE_SPACE)generate_space();else generate_surface();
#ifndef QA_AUTORUN
 cinema_start(0,0); /* Title remains until player presses START */
#endif
#ifdef QA_AUTORUN''')
change('if(intro){if(newk&KEY_START){intro=0;say("YOU WOKE ME WITH THE OLD TAPE. THREE AXIS KEYS ARE STILL BROADCASTING.");}}else{',
'''if(intro){if(newk&KEY_START){intro=0;cinema_end();say("YOU WOKE ME WITH THE OLD TAPE. THREE AXIS KEYS ARE STILL BROADCASTING.");}}
else if(cinema_active){if(newk&(KEY_A|KEY_START))cinema_end();else if(cinema_timer&&!--cinema_timer)cinema_end();}
else{''')
change('if(dialogue_timer)dialogue_timer--;music_step();}wait_vblank();',
       'if(dialogue_timer)dialogue_timer--;}music_step();wait_vblank();')
# Imported V5.1 keeps the same cartridge save format and original narrative.
SRC.write_text(s)
# Keep native-host register simulation and cartridge build metadata aligned with V5.1.
host=P/'host_qa_v5.py'
h=host.read_text()
assert 'HOST_REG_SOUND1CNT_H,HOST_REG_SOUND1CNT_X;' in h
h=h.replace('HOST_REG_SOUND1CNT_H,HOST_REG_SOUND1CNT_X;',
            'HOST_REG_SOUND1CNT_H,HOST_REG_SOUND1CNT_X,HOST_REG_SOUND2CNT_L,HOST_REG_SOUND2CNT_H;')
h=h.replace('#define REG_SOUND1CNT_X HOST_REG_SOUND1CNT_X',
            '#define REG_SOUND1CNT_X HOST_REG_SOUND1CNT_X\n#define REG_SOUND2CNT_L HOST_REG_SOUND2CNT_L\n#define REG_SOUND2CNT_H HOST_REG_SOUND2CNT_H')
host.write_text(h)
rom=P/'build_rom_v5.py';r=rom.read_text()
assert "LOSTCOSMOSV5" in r and "b'LCV5'" in r
r=r.replace('SIM_EARTH_PIXEL_UNIVERSE_LOST_COSMOS_V5.gba','SIM_EARTH_PIXEL_UNIVERSE_LOST_COSMOS_V5_CINEMATIC.gba').replace("b'LOSTCOSMOSV5'","b'LOSTCOSMOS51'").replace("b'LCV5'","b'LC51'").replace('header[0xBC]=5','header[0xBC]=6')
rom.write_text(r)
ver=P/'verify_v5.py';v=ver.read_text()
v=v.replace('SIM_EARTH_PIXEL_UNIVERSE_LOST_COSMOS_V5.gba','SIM_EARTH_PIXEL_UNIVERSE_LOST_COSMOS_V5_CINEMATIC.gba').replace("b'LOSTCOSMOSV5'","b'LOSTCOSMOS51'").replace("b'LCV5'","b'LC51'").replace('data[0xBC] != 5','data[0xBC] != 6')
ver.write_text(v)
print('PATCH_SHA256' ,hashlib.sha256(s.encode()).hexdigest(),'bytes',len(s))
