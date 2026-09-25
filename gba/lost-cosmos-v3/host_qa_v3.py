from pathlib import Path
import subprocess, sys
root=Path(__file__).resolve().parent
src=(root/'lost_cosmos_v3.c').read_text()
src=src.replace('#include "qseed.h"', '#include "qseed.h"\n#ifdef HOST_QA\n#include <stdio.h>\n#include <stdlib.h>\n#include <string.h>\n#endif')
start=src.index('#define REG_DISPCNT')
end=src.index('#define MODE0', start)
orig=src[start:end]
host=r'''#ifdef HOST_QA
static volatile u16 HOST_REG_DISPCNT,HOST_REG_BG0CNT,HOST_REG_BG1CNT,HOST_REG_BG0HOFS,HOST_REG_BG0VOFS,HOST_REG_BG1HOFS,HOST_REG_BG1VOFS,HOST_REG_VCOUNT,HOST_REG_KEYINPUT;
static volatile u16 HOST_REG_SOUNDCNT_L,HOST_REG_SOUNDCNT_H,HOST_REG_SOUNDCNT_X,HOST_REG_SOUND1CNT_L,HOST_REG_SOUND1CNT_H,HOST_REG_SOUND1CNT_X;
static volatile u16 HOST_BG_PALETTE[256],HOST_OBJ_PALETTE[256];
static volatile u8 HOST_VRAM[0x18000];
static volatile u16 HOST_OAM16[512];
static volatile u8 HOST_SRAM[32768];
#define REG_DISPCNT HOST_REG_DISPCNT
#define REG_BG0CNT HOST_REG_BG0CNT
#define REG_BG1CNT HOST_REG_BG1CNT
#define REG_BG0HOFS HOST_REG_BG0HOFS
#define REG_BG0VOFS HOST_REG_BG0VOFS
#define REG_BG1HOFS HOST_REG_BG1HOFS
#define REG_BG1VOFS HOST_REG_BG1VOFS
#define REG_VCOUNT HOST_REG_VCOUNT
#define REG_KEYINPUT HOST_REG_KEYINPUT
#define REG_SOUNDCNT_L HOST_REG_SOUNDCNT_L
#define REG_SOUNDCNT_H HOST_REG_SOUNDCNT_H
#define REG_SOUNDCNT_X HOST_REG_SOUNDCNT_X
#define REG_SOUND1CNT_L HOST_REG_SOUND1CNT_L
#define REG_SOUND1CNT_H HOST_REG_SOUND1CNT_H
#define REG_SOUND1CNT_X HOST_REG_SOUND1CNT_X
#define BG_PALETTE HOST_BG_PALETTE
#define OBJ_PALETTE HOST_OBJ_PALETTE
#define VRAM16 ((volatile u16*)HOST_VRAM)
#define VRAM32 ((volatile u32*)HOST_VRAM)
#define OBJ_VRAM32 ((volatile u32*)(HOST_VRAM+0x10000))
#define OAM16 HOST_OAM16
#define SRAM HOST_SRAM
#else
'''+orig+'#endif\n\n'
src=src[:start]+host+src[end:]
src=src.replace('static void wait_vblank(void){ while(REG_VCOUNT>=160){} while(REG_VCOUNT<160){} }', '''static void wait_vblank(void){
#ifdef HOST_QA
 return;
#else
 while(REG_VCOUNT>=160){} while(REG_VCOUNT<160){}
#endif
}''')
src=src.replace('__attribute__((noinline)) void qa_done(void){ for(;;){} }', '''__attribute__((noinline)) void qa_done(void){
#ifdef HOST_QA
 return;
#else
 for(;;){}
#endif
}''')
old='static void qa_fail(u32 code){ qa_stage=0xBAD00000u|code; SRAM[126]=0xEE; SRAM[127]=(u8)code; save_game(); qa_done(); }'
new='''static void qa_fail(u32 code){ qa_stage=0xBAD00000u|code; SRAM[126]=0xEE; SRAM[127]=(u8)code; save_game();
#ifdef HOST_QA
 fprintf(stderr,"QA_FAIL %08x\\n",(unsigned)qa_stage); exit((int)(code&255));
#else
 qa_done();
#endif
}'''
if old not in src: raise SystemExit('qa_fail source pattern not found')
src=src.replace(old,new)
src += r'''
#ifdef HOST_QA
int main(int argc,char**argv){
 const char*save=(argc>1)?argv[1]:"hostqa_v3.sav";
 FILE*f=fopen(save,"rb");
 if(f){fread((void*)HOST_SRAM,1,sizeof(HOST_SRAM),f);fclose(f);}
 init_new_game();load_game();init_graphics();sound_init();
 if(game_mode==MODE_SPACE)generate_space();else generate_surface();
 gameplay_qa();
 f=fopen(save,"wb"); if(!f){perror("save");return 90;} fwrite((const void*)HOST_SRAM,1,sizeof(HOST_SRAM),f);fclose(f);
 printf("QA_STAGE=%08x SRAM126=%02x KEYS=%u WORLD=%u LV=%u XP=%u WPN=%u ARM=%u CHM=%u ENDING=%u POSTGAME=%u\\n",(unsigned)qa_stage,(unsigned)HOST_SRAM[126],(unsigned)keys_found,(unsigned)current_world,(unsigned)player_level,(unsigned)player_xp,(unsigned)weapon,(unsigned)armor,(unsigned)charm,(unsigned)ending,(unsigned)postgame);
 return (qa_stage==0x51564131u||qa_stage==0x51564132u)?0:91;
}
#endif
'''
(root/'host_qa_v3.c').write_text(src)
subprocess.run(['clang','-DQA_AUTORUN','-DHOST_QA','-O2','host_qa_v3.c','-o','host_qa_v3'],cwd=root,check=True)
save=root/'hostqa_v3.sav'
if save.exists(): save.unlink()
for boot,expect in [(1,0xA5),(2,0x5A)]:
    p=subprocess.run([str(root/'host_qa_v3'),str(save)],cwd=root,text=True,capture_output=True)
    sys.stdout.write(p.stdout); sys.stderr.write(p.stderr)
    if p.returncode: raise SystemExit(f'boot {boot} failed rc={p.returncode}')
    data=save.read_bytes(); got=data[126] if len(data)>126 else -1
    if got!=expect: raise SystemExit(f'boot {boot} SRAM marker {got:#x} expected {expect:#x}')
    print(f'PASS host boot {boot}: SRAM marker {got:#04x}')
print('PASS: V3 RPG gameplay QA completed two fresh-process boots with SRAM persistence')
