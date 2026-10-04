#!/usr/bin/env python3
"""Additive V8 text-inset repair. Refuses unknown/re-patched sources."""
from pathlib import Path
import sys
root=Path(sys.argv[1]) if len(sys.argv)>1 else Path(".")
p=root/"lost_cosmos_v5.c"
s=p.read_text()
old="""static void ui_wrap_text(int row,const char*s,int pal,int maxrows){int col=0,r=0;char word[28];int wi=0;while(*s&&r<maxrows){while(*s==' ')s++;wi=0;while(*s&&*s!=' '&&wi<27)word[wi++]=*s++;word[wi]=0;if(!wi)break;if(col&&col+wi+1>29){r++;col=0;if(r>=maxrows)break;}if(col){ui_text(col,row+r," ",pal);col++;}ui_text(col,row+r,word,pal);col+=wi;}}"""
new="""/* Text never touches a framed panel's left/right border. Keep a 2-tile
   inset across BOTH the first and all wrapped lines of dialogue/story. */
static void ui_wrap_text(int row,const char*s,int pal,int maxrows){
 int col=2,r=0;char word[28];int wi=0;
 while(*s&&r<maxrows){
  while(*s==' ')s++;
  wi=0;while(*s&&*s!=' '&&wi<27)word[wi++]=*s++;
  word[wi]=0;if(!wi)break;
  if(col>2&&col+wi+1>29){r++;col=2;if(r>=maxrows)break;}
  if(col>2){ui_text(col,row+r," ",pal);col++;}
  ui_text(col,row+r,word,pal);col+=wi;
 }
}"""
assert s.count(old)==1, "Unrecognized engine; abort rather than overwrite."
p.write_text(s.replace(old,new))
t=root/"v8_view_story_tests.py"
s=t.read_text()
needle=' set_world_palette(0);ui_clear();ui_frame(11,19,15);ui_text(4,13,"ARIN READS",15);'
checks=''' /* Regression: story and NPC dialog may not overwrite framed borders.
    A long line must wrap INSIDE the left and right panel margins. */
 ui_clear();ui_frame(0,19,15);
 ui_wrap_text(5,"ABCDEFGHIJKLMNO PQRSTUVW XYZZZZ",15,2);
 assert((screenblock(UI_MAP_BASE)[5*32+0]&1023)==61);
 assert((screenblock(UI_MAP_BASE)[5*32+2]&1023)==64+font_index('A'));
 assert((screenblock(UI_MAP_BASE)[5*32+29]&1023)==61);
 assert((screenblock(UI_MAP_BASE)[6*32+0]&1023)==61);
 assert((screenblock(UI_MAP_BASE)[6*32+2]&1023)==64+font_index('X'));
 assert((screenblock(UI_MAP_BASE)[6*32+29]&1023)==61);
'''
assert s.count(needle)==1, "Unrecognized test; abort rather than overwrite."
t.write_text(s.replace(needle,checks+needle))
print("Applied V8 framed text inset and six regression assertions.")
