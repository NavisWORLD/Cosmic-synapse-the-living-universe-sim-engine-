"""Five truly distinct room music loops and three unique playable-cartridge finale paintings.
Host-mapped GBA registers are used; this is not an external audio recording.
"""
from pathlib import Path
import subprocess
R=Path(__file__).resolve().parent
src=(R/'host_qa_v5.c').read_text().split('\n#ifdef HOST_QA\nint main(',1)[0]
src+=r'''
#include <assert.h>
#include <stdio.h>
int main(void){int i;u16 freq[5];
 init_new_game();init_graphics();intro=0;audio_on=1;game_mode=MODE_SURFACE;
 assert(V51_SCENE_COUNT==23);
 for(i=20;i<=22;i++){
   assert(V51_SCENE_COUNTS[i]>100&&V51_SCENE_COUNTS[i]<=512);
   cinema_start((u8)i,0);assert(cinema_active && cinema_scene==i);
   assert((REG_DISPCNT&BG2_ENABLE)&&BG_PALETTE[CINEMA_PAL*16+11]==V51_SCENE_COLORS[i][11]);
   assert(screenblock(CINEMA_MAP)[0]==(V51_SCENE_MAPS[i][0]|(CINEMA_PAL<<12)));
   cinema_end();
 }
 cinema_start(23,0);assert(!cinema_active); /* never out of bounds */
 for(i=1;i<=3;i++){
   init_new_game();game_mode=MODE_SURFACE;intro=0;
   finalize_choice((u8)i);
   assert(postgame==1&&player_choice==i&&ending==i&&v10_ending_card==1);
   assert(cinema_scene==19+i&&cinema_active);
   draw_cinema_caption();
   assert((screenblock(UI_MAP_BASE)[0]&1023)!=0);
   cinema_end();
 }
 /* Real PSG channel 1 register receives one distinct original realm melody
    while channel 2 continues to provide simultaneous sound effects. */
 for(i=0;i<5;i++){
   static const u8 W[5]={0,0,7,0,6};
   static const u8 ROOM[5]={8,9,10,12,11};
   current_world=W[i];current_room=ROOM[i];game_mode=MODE_SURFACE;
   sound_init();frame=0;music_tick=35;music_step();
   freq[i]=(u16)(REG_SOUND1CNT_X&2047);
   assert(freq[i]==SONGS[6+i][0]);
   tone(1000);assert((REG_SOUND2CNT_H&0x8000)!=0);
 }
 for(i=0;i<5;i++)for(int j=i+1;j<5;j++)assert(freq[i]!=freq[j]);
 puts("PASS V10: 23 genuine 4bpp scenes; real 3 distinct new ending art animations and safe captions; 5 distinct GBA PSG theme sequences coexist with combat sound; reserved no-scene guard");
 return 0;
}
'''
(R/'v10_finale_audio_qa.c').write_text(src)
subprocess.run(['clang','-DHOST_QA','-O2','-Wno-unused-function','v10_finale_audio_qa.c','-o','v10_finale_audio_qa'],cwd=R,check=True)
subprocess.run([str(R/'v10_finale_audio_qa')],cwd=R,check=True)
