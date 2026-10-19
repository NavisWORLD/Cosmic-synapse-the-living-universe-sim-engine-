#!/usr/bin/env python3
"""V12 LIVING WORLD asset converter (grit-equivalent; grit is not installed on
the build box or in CI). PNG -> 4bpp/8bpp GBA tiles, BGR555 palettes, BG maps;
JSON text -> ROM tables. Writes v12_art.c/.h and v12_text.h. Deterministic."""
import json, re, sys
from pathlib import Path
from PIL import Image
R=Path(__file__).resolve().parent.parent; A=R/'v12_assets'/'art'; T=R/'v12_assets'/'text'
def bgr(c): r,g,b=c[:3]; return (r>>3)|((g>>3)<<5)|((b>>3)<<10)
def palrgb(name): return [tuple(x) for x in json.load(open(A/'palettes'/f'{name}.json'))['rgb']]
def nearest(rgb,pal,start=0):
    best=None
    for i in range(start,len(pal)):
        d=sum((a-b)**2 for a,b in zip(rgb,pal[i]))
        if best is None or d<best[0]: best=(d,i)
    return best[1]
def indexed(path,pal,transparent=True):
    im=Image.open(path).convert('RGBA'); w,h=im.size; px=im.load(); cache={}; out=[[0]*w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            p=px[x,y]
            if transparent and (p[3]<128 or p[:3]==pal[0]): continue
            k=p[:3]
            if k not in cache: cache[k]=nearest(k,pal,1 if transparent else 0)
            out[y][x]=cache[k]
    return out,w,h
def tile4(img,x0,y0):
    words=[]
    for y in range(8):
        v=0
        for x in range(8): v|=(img[y0+y][x0+x]&15)<<(4*x)
        words.append(v)
    return words
def frames4(img,w,h,fw,fh,nframes=None):
    n=nframes or w//fw; t=[]
    for f in range(n):
        for ty in range(fh//8):
            for tx in range(fw//8):
                yy=ty*8; xx=f*fw+tx*8
                if yy+8>h: t.append([0]*8)
                else: t.append(tile4(img,xx,yy))
    return t
C=[]; H=[]
def emit_u32(name,tiles):
    flat=[w for t in tiles for w in t]
    C.append(f'const u32 {name}[{len(flat)}]={{'+','.join(f'0x{w:08X}u' for w in flat)+'};')
    H.append(f'extern const u32 {name}[{len(flat)}];'); return len(flat)*4
def emit_u16(name,vals):
    C.append(f'const u16 {name}[{len(vals)}]={{'+','.join(f'0x{v:04X}' for v in vals)+'};')
    H.append(f'extern const u16 {name}[{len(vals)}];'); return len(vals)*2
def emit_u8(name,vals):
    C.append(f'const u8 {name}[{len(vals)}]={{'+','.join(str(v) for v in vals)+'};')
    H.append(f'extern const u8 {name}[{len(vals)}];'); return len(vals)
def pal16(name): p=palrgb(name); return [bgr(c) for c in (p+[(0,0,0)]*16)[:16]]
total=0
CRE=['zeref','kairo','frost','kitten','shardhowl','velvetcoil']
COMP={'zeref':'zeref_spider','kairo':'kairo_jelly','frost':'frost_spider','kitten':'kitten_jelly','shardhowl':'shardhowl_spider','velvetcoil':'velvetcoil_jelly'}
rep=json.load(open(A/'tile_report.json'))['sprites']
for c in CRE:
    p=palrgb('creature_'+c); img,w,h=indexed(A/'sprites'/f'creature_{c}.png',p)
    total+=emit_u32(f'v12_cre_{c}_tiles',frames4(img,w,h,64,64)); total+=emit_u16(f'v12_cre_{c}_pal',pal16('creature_'+c))
    fr=rep['creature_'+c]['frames']; H.append(f'#define V12_CRE_{c.upper()}_FRAMES {len(fr)}')
    q=palrgb('companion_'+COMP[c]); img,w,h=indexed(A/'sprites'/f'companion_{COMP[c]}.png',q)
    total+=emit_u32(f'v12_comp_{c}_tiles',frames4(img,w,h,32,32)); total+=emit_u16(f'v12_comp_{c}_pal',pal16('companion_'+COMP[c]))
CH=['arin','traveler','hollis','edric','bryn','quillan','hesper','grumbleback','rime','cinderwake','thorne','sethra','malakar','counterfeit']
MO=['mote','mote_linework','mote_wash','mote_still_here']
for c in CH:
    p=palrgb('char_'+c); img,w,h=indexed(A/'sprites'/f'char_{c}.png',p)
    total+=emit_u32(f'v12_chr_{c}_tiles',frames4(img,w,h,32,32)); total+=emit_u16(f'v12_chr_{c}_pal',pal16('char_'+c))
H.append(f'#define V12_CHR_FRAMES {Image.open(A/"sprites"/"char_arin.png").size[0]//32}')
for c in MO:
    p=palrgb('char_'+c); img,w,h=indexed(A/'sprites'/f'char_{c}.png',p)
    total+=emit_u32(f'v12_chr_{c}_tiles',frames4(img,w,h,64,64)); total+=emit_u16(f'v12_chr_{c}_pal',pal16('char_'+c))
ip=palrgb('items'); total+=emit_u16('v12_items_pal',pal16('items'))
total+=emit_u16('v12_items_b_pal',pal16('items_b'))
def raw4(path):
    im=Image.open(path); assert im.mode=='P'; w,h=im.size; b=im.tobytes()
    return [[b[y*w+x]&15 for x in range(w)] for y in range(h)],w,h
H.append('#define V12_ITEMS_BANKED 1')
order=json.load(open(A/'sprites'/'items_16x16_order.json'))
for nm,f in [('v12_icons_a','items_16x16.png'),('v12_icons_b','items_16x16_frame2.png')]:
    img,w,h=raw4(A/'sprites'/f); t=[]
    for i in range(len(order['items_16x16'])):
        x0=(i%(w//16))*16; y0=(i//(w//16))*16
        t+= [tile4(img,x0,y0),tile4(img,x0+8,y0),tile4(img,x0,y0+8),tile4(img,x0+8,y0+8)]
    total+=emit_u32(nm,t)
img,w,h=raw4(A/'sprites'/'items_weapons_32x16.png'); total+=emit_u32('v12_weapons',frames4(img,w,h,32,16))
img,w,h=raw4(A/'sprites'/'items_lanterns_16x24_2f.png')
img+= [[0]*w for _ in range(8)]; total+=emit_u32('v12_lanterns',frames4(img,w,h+8,16,32))  # 16x24 padded to 16x32, 2 frames per lantern
p=palrgb('wisp_dark'); img,w,h=indexed(A/'sprites'/'wisp_dark.png',p)
total+=emit_u32('v12_wisp_tiles',frames4(img,w,h,32,32)); total+=emit_u16('v12_wisp_pal',pal16('wisp_dark'))
H.append(f'#define V12_WISP_FRAMES {w//32}')
for bgname in ['forest','cave']:
    p=palrgb('bg_'+bgname); img,w,h=indexed(A/'bg'/f'{bgname}_map_512x256.png',p,transparent=False)
    uniq={}; tl=[]; mp=[]
    for ty in range(32):
        for tx in range(64):
            t=tuple(tile4(img,tx*8,ty*8))
            if t not in uniq: uniq[t]=len(tl); tl.append(list(t))
            mp.append(uniq[t])
    assert len(tl)<=512,len(tl)
    # 64x32 map as two 32x32 screenblocks, BG size 1 order
    sb=[0]*2048
    for ty in range(32):
        for tx in range(64): sb[(tx//32)*1024+ty*32+(tx%32)]=mp[ty*64+tx]
    total+=emit_u32(f'v12_bg_{bgname}_tiles',tl); total+=emit_u16(f'v12_bg_{bgname}_map',sb); total+=emit_u16(f'v12_bg_{bgname}_pal',pal16('bg_'+bgname))
    H.append(f'#define V12_BG_{bgname.upper()}_TILES {len(tl)}')
for sc in ['forest','cave']:
    im=Image.open(A/'scenes'/f'zeref_{sc}_mode4.png'); assert im.mode=='P' and im.size==(240,160)
    pal=im.getpalette()[:768]; pal+= [0]*(768-len(pal))
    total+=emit_u8(f'v12_scene_{sc}_px',list(im.tobytes())); total+=emit_u16(f'v12_scene_{sc}_pal',[bgr(pal[i*3:i*3+3]) for i in range(256)])
H.append(f'#define V12_ART_BYTES {total}')
hdr='/* GENERATED by tools_v12/convert_v12.py from v12_assets/art (Cosmo GBA art v3b). Do not edit. */\n'
(R/'v12_art.c').write_text(hdr+'typedef unsigned int u32;typedef unsigned short u16;typedef unsigned char u8;\n'+'\n'.join(C)+'\n')
(R/'v12_art.h').write_text(hdr+'#ifndef V12_ART_H\n#define V12_ART_H\n'+'\n'.join(H)+'\n#endif\n')
# ---------- text ----------
def up(s,n=None):
    s=s.upper().replace('&','AND').replace('"',"'").replace(';',',').replace('(','').replace(')','')
    s=re.sub(r"[^A-Z0-9\-/:.?*!>+,'= ]",' ',s); s=re.sub(' +',' ',s).strip()
    if n and len(s)>n:
        cut=s[:n+1].rfind(' ')  # V12.2: cut on a word, never mid-word
        s=s[:cut] if cut>n//2 else s[:n]
    return s[:n] if n else s
def cs(s): return '"'+s.replace('\\','\\\\').replace('"','\\"')+'"'
I=json.load(open(T/'items.json')); M=json.load(open(T/'creature_moods.json')); Q=json.load(open(T/'quests.json'))
CHJ=json.load(open(T/'characters.json')); N=json.load(open(T/'npc_lines.json')); E=json.load(open(T/'endings.json'))
ids=[i['id'] for i in I]; icon={}
for k,v in enumerate(order['items_16x16']): icon[v]=(0,k)
for k,v in enumerate(order['weapons_32x16']): icon[v]=(1,k)
for k,v in enumerate(order['lanterns_16x24']): icon[v]=(2,k)
CAT={'consumable':0,'food':1,'weapon':2,'armor':3,'accessory':4,'lantern':5,'key':6,'material':7}
RAR={'common':0,'uncommon':1,'rare':2,'legendary':3,'unique':3,'epic':2}
S=['hp','atk','def','spd','focus','mood','hunger','energy']
o=['/* GENERATED by tools_v12/convert_v12.py from v12_assets/text (Emeth). Original game text. */','#ifndef V12_TEXT_H','#define V12_TEXT_H',
   'typedef struct{const char*id;const char*name;const char*desc;u8 cat,rarity,sheet,icon;s8 st[8];}V12Item;',
   f'#define V12_ITEM_COUNT {len(I)}','static const V12Item V12_ITEMS[V12_ITEM_COUNT]={']
for it in I:
    st=it.get('stat',{}); sh,ic=icon.get(it['id'],(0,0))
    if it['id'] not in icon: print('WARN no icon',it['id'],file=sys.stderr)
    o.append(' {%s,%s,%s,%d,%d,%d,%d,{%s}},'%(cs(it['id']),cs(up(it['name'],14)),cs(up(it['description'],56)),CAT[it['category']],RAR.get(it.get('rarity','common'),0),sh,ic,','.join(str(max(-128,min(127,int(st.get(k,0))))) for k in S)))
o.append('};')
PM=json.load(open(A/'sprites'/'items_palette_map.json'))['bank']
o.append('static const u8 V12_ITEM_BANK[V12_ITEM_COUNT]={'+','.join('1' if PM.get(it['id'],'A')=='B' else '0' for it in I)+'};')
ACT=sorted({m['action'] for m in M}); TRG=[m['trigger'] for m in M]
o.append('typedef struct{const char*name;const char*line;u8 trigger,action;}V12Mood;')
o+= [f'#define V12_TRIG_{t.upper()} {i}' for i,t in enumerate(TRG)]
o+= [f'#define V12_ACT_{a.upper()} {i}' for i,a in enumerate(ACT)]
o.append(f'#define V12_MOOD_COUNT {len(M)}'); o.append(f'#define V12_ACT_COUNT {len(ACT)}')
o.append('static const char*const V12_ACT_NAMES[V12_ACT_COUNT]={'+','.join(cs(up(a.replace('_',' '),14)) for a in ACT)+'};')
o.append('static const V12Mood V12_MOODS[V12_MOOD_COUNT]={'+','.join('{%s,%s,%d,%d}'%(cs(up(m['name'],14)),cs(up(m['idle_line'],56)),i,ACT.index(m['action'])) for i,m in enumerate(M))+'};')
o.append('typedef struct{const char*name;const char*summary;const char*giver;u8 act;s8 reward[3];}V12Quest;')
o.append(f'#define V12_QUEST_COUNT {len(Q)}'); o.append('static const V12Quest V12_QUESTS[V12_QUEST_COUNT]={')
for q in Q:
    rw=[ids.index(r) for r in q.get('reward_item_ids',[]) if r in ids][:3]; rw+=[-1]*(3-len(rw))
    o.append(' {%s,%s,%s,%d,{%d,%d,%d}},'%(cs(up(q['name'],26)),cs(up(q['summary'],84)),cs(up(q.get('giver',''),20)),q['act'],*rw))
o.append('};')
o.append('typedef struct{const char*name;const char*look;const char*pose;}V12Char;')
o.append(f'#define V12_CHAR_COUNT {len(CHJ)}')
o.append('static const V12Char V12_CHARS[V12_CHAR_COUNT]={'+','.join('{%s,%s,%s}'%(cs(up(c['name'],22)),cs(up(c.get('visual_description',''),190)),cs(up(c.get('idle_pose',''),110))) for c in CHJ)+'};')
o.append('static const char*const V12_CHAR_IDS[V12_CHAR_COUNT]={'+','.join(cs(c['id']) for c in CHJ)+'};')
lines=[(up(n['name'],16),up(l,56)) for n in N for l in n['lines']]
o.append(f'#define V12_NPC_LINE_COUNT {len(lines)}')
o.append('static const char*const V12_NPC_LINES[V12_NPC_LINE_COUNT][2]={'+','.join('{%s,%s}'%(cs(a),cs(b)) for a,b in lines)+'};')
o.append('static const char*const V12_ENDINGS[%d][2]={'%len(E)+','.join('{%s,%s}'%(cs(up(e['name'],20)),cs(up(e['final_line'],56))) for e in E)+'};')
o.append('#endif')
(R/'v12_text.h').write_text('\n'.join(o)+'\n')
print('art bytes',total,'items',len(I),'moods',len(M),'quests',len(Q),'chars',len(CHJ),'npc lines',len(lines))
