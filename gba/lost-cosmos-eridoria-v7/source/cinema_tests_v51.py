"""Host tests supplement, but do not replace, native mGBA visual/audio evidence."""
from pathlib import Path
import subprocess
R=Path(__file__).resolve().parent
src=(R/'host_qa_v5.c').read_text().split('\n#ifdef HOST_QA\nint main(',1)[0]
assert 'V51_SCENE_TILES' in src
src += r'''
#include <assert.h>
#include <stdio.h>
int main(void){
 int i;
 init_new_game();init_graphics();generate_surface();
 assert(!cinema_active);
 cinema_start(0,0);
 assert(cinema_active && cinema_scene==0);
 assert(REG_BG2CNT==(1|(CINEMA_CB<<2)|(CINEMA_MAP<<8)));
 assert(REG_DISPCNT & BG2_ENABLE);
 assert(BG_PALETTE[CINEMA_PAL*16+11]==V51_SCENE_COLORS[0][11]);
 assert(V51_SCENE_COUNTS[0]<=512 && V51_SCENE_COUNTS[0]>150);
 assert(V51_SCENE_COUNT==11);
 for(i=0;i<V51_SCENE_COUNT;i++)assert(V51_SCENE_COUNTS[i]<=512);
 assert(V51_SCENE_MAPS[0][0]<V51_SCENE_COUNTS[0]);
 assert(screenblock(CINEMA_MAP)[0]==(V51_SCENE_MAPS[0][0]|(CINEMA_PAL<<12)));
 assert(VRAM32[CINEMA_CB*4096]==V51_SCENE_TILES[V51_SCENE_OFFSETS[0]][0]);
 cinema_end();assert(!(REG_DISPCNT&BG2_ENABLE));
 game_mode=MODE_SPACE;cinema_start(1,75);assert(REG_DISPCNT&BG2_ENABLE);
 cinema_end();assert(REG_BG2CNT==(1|(BG_TILE_CB<<2)|(SPACE_PARALLAX_MAP<<8)));
 /* Audio on PSG square 1 and 2 must coexist rather than truncate one another. */
 audio_on=1;frame=36;music_tick=35;game_mode=MODE_SURFACE;current_world=0;
 sound_init();music_step();assert(REG_SOUND1CNT_X&0x8000);
 {u16 bg=REG_SOUND1CNT_X;
  tone(1550);assert(REG_SOUND1CNT_X==bg && (REG_SOUND2CNT_H&0x8000));}
 {u16 efx=REG_SOUND2CNT_H,bg=REG_SOUND1CNT_X;
  audio_on=0;tone(1700);music_step();assert(REG_SOUND2CNT_H==efx&&REG_SOUND1CNT_X==bg);}
 /* v5.1 touch preference persists in the existing LCV5 checksum format. */
 audio_on=1;game_mode=MODE_SURFACE;touch_mode=1;save_game();
 assert((SRAM[168]&0xFE)==0xC0 && save_valid());
 touch_mode=0;load_game();assert(touch_mode==1);
 /* A real V5 mGBA save's unused 168=FF must default to normal button chords. */
 {FILE*f=fopen("qa_fixtures/v5_mgba_boot1.sav","rb");assert(f);
  assert(fread((void*)HOST_SRAM,1,32768,f)==32768);fclose(f);}
 assert(SRAM[168]==0xFF && save_valid());
 init_new_game();load_game();assert(touch_mode==0&&save_valid());
 assert(SRAM[168]==0xC0 && (keys_found&1));
 /* Exercise real gameplay button router and prevent select from double-beacon. */
 init_new_game();current_world=0;game_mode=MODE_SURFACE;generate_surface();
 npc_count=0;clear_combat();intro=0;touch_mode=1;dodge_cooldown=0;beacon_count=0;
 player.x=80;player.y=400;
 update_surface(KEY_SELECT,KEY_SELECT);
 assert(dodge_timer>0&&dodge_cooldown>0&&beacon_count==0);
 touch_mode=0;dodge_cooldown=0;dodge_timer=0;
 update_surface(KEY_SELECT,KEY_SELECT);
 assert(beacon_count==1&&dodge_timer==0);
 update_surface(KEY_SELECT|KEY_B,KEY_SELECT);
 assert(dodge_timer>0&&beacon_count==1);
 /* Touch mode long-hold A triggers a heavy strike without touching Q replay. */
 clear_combat();npc_count=0;touch_mode=1;dodge_timer=0;heavy_cooldown=0;
 player.x=184;player.y=368;for(i=0;i<4096;i++)trigger[i]=TR_NONE;
 {u32 old=workload_qi;
  for(i=0;i<23;i++)update_surface(KEY_A,0);
  assert(heavy_cooldown>0 && workload_qi==old);}
 puts("PASS: 11 authentic 4bpp cinema scenes, VRAM-safe BG2 overlay, separate PSG audio, 1-button touch dodge, V5 save migration, touch-heavy, replay isolation");
 return 0;
}
'''
(R/'cinema_qa.c').write_text(src)
subprocess.run(['clang','-DQA_AUTORUN','-DHOST_QA','-O2','-Wno-unused-function','cinema_qa.c','-o','cinema_qa'],cwd=R,check=True)
subprocess.run([str(R/'cinema_qa')],cwd=R,check=True)
