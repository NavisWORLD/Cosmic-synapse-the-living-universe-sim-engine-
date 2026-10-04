"""Run actual native logic under simulated MMIO; no emulator claim."""
from pathlib import Path
import os, subprocess
root=Path(__file__).resolve().parents[1]
game=root/'LOST_COSMOS_V10_SOURCE'
subprocess.run(['python3','host_qa_v5.py'],cwd=game,check=True,capture_output=True)
pre=(game/'host_qa_v5.c').read_text().split('\n#ifdef HOST_QA\nint main(',1)[0]
body=r'''
#include <assert.h>
#include <stdio.h>
#ifndef LC_COMPLETION_RUNTIME_H
static int completion_available(int i){(void)i;return 0;}
#endif
int main(void){
 init_new_game();init_graphics();intro=0;
 story_flags|=ST_HEART|ST_CITY|ST_DREAM;
 assert(completion_available(0));
 puts("PASS completion story entry requires actual earned progress");
}
'''
src=game/'completion_test_host.c';src.write_text(pre+body)
exe=game/'completion_test_host'
subprocess.run([os.environ.get('LC_HOST_CC','gcc'),'-DQA_AUTORUN','-DHOST_QA','-O2',str(src),'-o',str(exe)],cwd=game,check=True)
subprocess.run([str(exe)],cwd=game,check=True)
