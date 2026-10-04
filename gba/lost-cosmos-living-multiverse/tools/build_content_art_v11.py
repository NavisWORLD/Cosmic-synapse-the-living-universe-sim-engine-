#!/usr/bin/env python3
"""Extract individual provided art cells; labels and sheet panels never enter OAM.

The six NPCs without a dedicated sheet cell use explicitly recorded adaptations
of provided cells. Palette variants distinguish these; no hidden franchise art.
Native fields use one shared 15-colour actor palette so ten enemies plus six
NPCs cannot exhaust GBA palette banks. Battles retain per-character palettes.
"""
import hashlib, json
from collections import deque
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'content/art_sources'
NPC_X=[7,310,639,964,1292,1614,1914]
NPC_Y=[114,369,590,790,1025,1267]
NPC_MAP=[(0,0),(1,0),(2,0),(3,0),(4,0),(0,1),(1,1),(3,4),
         (2,1),(3,1),(5,1),(4,1),(0,2),(5,3),(1,2),(4,3),(2,2),
         (3,2),(4,2),(4,4),(0,3),(1,4),(1,3),(2,3),(2,3),(3,3),
         (4,3),(0,4),(1,4),(2,4)]
ADAPTED_NPCS={10:'Coral Wisp becomes the ancient volcanic signal; warm palette.',
 13:'Mothling becomes the quiet apiary keeper; leaf palette.',
 15:"Echo of the Son becomes the cartographer's pale echo.",
 21:'Prayer Keeper becomes the Confessor; deep violet palette.',
 23:'Crown Seneschal becomes the fallen saint; dim palette.'}
# Enemy rows: sheet row 5 col 2 is an unlabeled Confessed stand-in;
# row 5 has no Echo of Malakar, so its boss silhouette is recoloured.
ENEMY_MAP=[(i%10,i//10) for i in range(70)]
ENEMY_MAP[55]=(0,6)  # author index 85, Echo of Malakar
ENEMY_MAP[56]=(5,5); ENEMY_MAP[57]=(6,5)
ENEMY_MAP[58]=(7,5); ENEMY_MAP[59]=(8,5)
ITEM_MAP=[
 (0,0),(1,0),(2,0),(3,0),(5,0),(6,0),(8,0),(9,0),(10,0),(12,0),
 (0,1),(1,1),(2,1),(4,1),(5,1),(6,1),(8,1),(9,1),(11,1),(12,1),
 (0,2),(1,2),(3,2),(4,2),(6,2),
 (7,2),(8,2),(9,2),(10,2),(11,2),(0,3),(1,3),(2,3),(3,3),(4,3),
 (5,3),(7,3),(8,3),(10,3),(12,3),(0,4),(1,4),(2,4),(3,4),(4,4),
 (5,4),(7,4),(9,4),(11,4),(12,4),
 (0,5),(1,5),(2,5),(3,5),(5,5),(7,5),(8,5),(9,5),(11,5),(12,5),
 (9,7),(6,8),(6,6),(11,8),(6,6),(8,8),(7,6),(10,4),(9,6),(11,8),
 (0,6),(1,6),(2,6),(4,6),(5,6),(7,6),(8,6),(10,6),(6,6),(12,6),
 (0,7),(2,7),(3,7),(4,7),(5,7),(7,7),(9,7),(10,7),(11,7),(12,7),
 (0,8),(2,8),(3,8),(4,8),(6,8),(7,8),(8,8),(9,8),(11,8),(12,8)]

def cell(sheet,col,row,kind):
    if kind=='npc':
        return sheet.crop((NPC_X[col]+10,NPC_Y[row]+6,NPC_X[col+1]-10,NPC_Y[row+1]-43))
    if kind=='enemy':
        xs=[110,287,469,650,834,1024,1201,1377,1556,1737,1917]
        ys=[75,222,369,516,658,864,1054,1277]
        return sheet.crop((xs[col]+6,ys[row]+5,xs[col+1]-6,ys[row+1]-31))
    if kind=='item':
        x=5+col*147.1; y=51+row*136.4
        # Cinder Poker's supplied wide cell spans two icon columns.
        return sheet.crop((int(x+6),int(y+6),int(x+(289 if (col,row)==(3,0) else 141)),int(y+130)))
    return sheet.crop((col*160+12,row*160+18,(col+1)*160-12,(row+1)*160-8))

def foreground(im,kind):
    im=im.convert('RGB');w,h=im.size;p=im.load()
    # Background panels are low saturation dark blue/brown; skill plates teal.
    def background(rgb):
        r,g,b=rgb
        if kind=='skill':return r<36 and 40<g<150 and 45<b<160
        if kind=='item':return 30<r<110 and g<85 and b<75 and 8<r-g<40 and g>b
        return r<57 and g<62 and 25<b<108
    seen=set();todo=deque()
    for x in range(w):
        for y in [0,h-1]:
            if background(p[x,y]):seen.add((x,y));todo.append((x,y))
    for y in range(h):
        for x in [0,w-1]:
            if (x,y) not in seen and background(p[x,y]):seen.add((x,y));todo.append((x,y))
    while todo:
        x,y=todo.popleft()
        for nx,ny in [(x-1,y),(x+1,y),(x,y-1),(x,y+1)]:
            if 0<=nx<w and 0<=ny<h and (nx,ny) not in seen and background(p[nx,ny]):
                seen.add((nx,ny));todo.append((nx,ny))
    mask=Image.new('L',(w,h),255);m=mask.load()
    for x,y in seen:m[x,y]=0
    # Remove isolated panel noise; keep detached stars/horns near the main art.
    bbox=mask.getbbox()
    if not bbox:raise ValueError('No visible art cell')
    im=im.convert('RGBA');im.putalpha(mask)
    return im.crop(bbox)

def fit(im,canvas,visible):
    im=im.copy();im.thumbnail((visible,visible),Image.Resampling.NEAREST)
    out=Image.new('RGBA',(canvas,canvas));out.alpha_composite(im,((canvas-im.width)//2,canvas-im.height-2))
    return out

def variant(im,index):
    if index not in ADAPTED_NPCS and index!=85:return im
    rgb=im.copy();pix=rgb.load()
    for y in range(im.height):
        for x in range(im.width):
            r,g,b,a=pix[x,y]
            if index==10:r,g,b=min(255,r+90),g//2,b//2
            elif index==13:r,g,b=r//2,min(255,g+35),b//2
            elif index==15:r,g,b=min(255,(r+b)//2+30),min(255,g+25),min(255,b+45)
            elif index==21:r,g,b=min(255,r+30),g//2,min(255,b+35)
            else:r,g,b=r//2,g//2,min(255,b+30)
            pix[x,y]=(r,g,b,a)
    return rgb

def palette(images):
    pixels=[c[:3] for im in images for c in im.getdata() if c[3]>127]
    sample=Image.new('RGB',(len(pixels),1));sample.putdata(pixels)
    q=sample.quantize(colors=15,method=Image.Quantize.MEDIANCUT)
    raw=q.getpalette()[:45]
    raw += [0]*(45-len(raw))
    return [(0,0,0)]+[tuple(raw[i:i+3]) for i in range(0,45,3)]

def indexed(im,pal):
    # GBA 5-bit rounding. Index zero is transparency, never inferred from RGB.
    out=[]
    for r,g,b,a in im.getdata():
        out.append(0 if a<128 else min(range(1,16),key=lambda k:
                    (r-pal[k][0])**2+(g-pal[k][1])**2+(b-pal[k][2])**2))
    return out

def words(indices,w):
    result=[]
    for ty in range(0,w,8):
        for tx in range(0,w,8):
            for y in range(8):
                result.append(sum(indices[(ty+y)*w+tx+x]<<(x*4) for x in range(8)))
    return result

def rgb15(pal):return [(r>>3)|((g>>3)<<5)|((b>>3)<<10) for r,g,b in pal]

def main():
    sheets={k:Image.open(SOURCE/f'{k}.webp') for k in ['npc','enemy','item','skill']}
    catalog=json.loads((ROOT/'content/v11_1_catalog.json').read_text())
    originals=[variant(foreground(cell(sheets['npc'],*coord,'npc'),'npc'),i) for i,coord in enumerate(NPC_MAP)]
    originals += [variant(foreground(cell(sheets['enemy'],*coord,'enemy'),'enemy'),i+30) for i,coord in enumerate(ENEMY_MAP)]
    field=[fit(im,32,20 if i<70 else 24) for i,im in enumerate(originals)]
    battle=[fit(im,32,30) for im in originals]
    shared=palette(field)
    manifest={'version':'11.1','characters':[],'items':[],'skills':[],
              'source_hashes':{k:hashlib.sha256((SOURCE/f'{k}.webp').read_bytes()).hexdigest() for k in sheets}}
    chunks=['/* GENERATED individual 4bpp cells. Never display a supplied catalog panel. */',
            '#ifndef V11_ART_H','#define V11_ART_H',
            'static const u16 V11_FIELD_PALETTE[16]={'+','.join(hex(x) for x in rgb15(shared))+'};']
    def emit(name,data,typ='u32'):
        chunks.append(f'static const {typ} {name}[{len(data)}]={{'+','.join(hex(x)+'u' for x in data)+'};')
    fieldwords=[];battlewords=[];battlepals=[]
    previews=[]
    for i,im in enumerate(field):
        pal=palette([battle[i]]);idx=indexed(im,shared);fieldwords+=words(idx,32)
        battlewords+=words(indexed(battle[i],pal),32);battlepals+=rgb15(pal)
        co=NPC_MAP[i] if i<30 else ENEMY_MAP[i-30]
        box=im.getchannel('A').getbbox()
        manifest['characters'].append(dict(id=catalog['characters'][i]['id'],source='npc' if i<30 else 'enemy',
           cell=list(co),adaptation=ADAPTED_NPCS.get(i,'Echo palette variant' if i==85 else None),
           palette_colors=16,canvas=32,visible_width=box[2]-box[0],visible_height=box[3]-box[1],
           visible_pixels=sum(n!=0 for n in idx)))
        show=Image.new('RGB',(32,32),(15,19,35));show.paste(im,mask=im.getchannel('A'));previews.append(show)
    emit('V11_FIELD_ART',fieldwords);emit('V11_BATTLE_ART',battlewords);emit('V11_BATTLE_PALETTES',battlepals,'u16')
    for kind,coords in [('items',ITEM_MAP),('skills',[(i%10,i//10) for i in range(100)])]:
        allwords=[];allpals=[]
        for i,co in enumerate(coords):
            k='item' if kind=='items' else 'skill'
            try:im=fit(foreground(cell(sheets[k],*co,k),k),16,14)
            except ValueError as exc:raise ValueError(f'{kind} {i} {co}: {exc}') from exc
            pal=palette([im]);idx=indexed(im,pal);allwords+=words(idx,16);allpals+=rgb15(pal)
            box=im.getchannel('A').getbbox()
            manifest[kind].append(dict(id=catalog[kind][i]['id'],source=k,cell=list(co),palette_colors=16,
             canvas=16,visible_width=box[2]-box[0],visible_height=box[3]-box[1],visible_pixels=sum(n!=0 for n in idx)))
        emit('V11_'+kind.upper()+'_ART',allwords);emit('V11_'+kind.upper()+'_PALETTES',allpals,'u16')
    chunks+=['#endif',''];(ROOT/'LOST_COSMOS_V10_SOURCE/content_v11_art.h').write_text('\n'.join(chunks))
    (ROOT/'content/v11_1_art_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    # Native-resolution atlas for visual QA; each displayed box has its content ID.
    contact=Image.new('RGB',(480,600),(15,19,35));d=ImageDraw.Draw(contact)
    for i,im in enumerate(previews):
        x=(i%10)*48;y=(i//10)*60;contact.paste(im,(x+8,y+4));d.text((x+3,y+39),str(i+1),(180,215,235))
    dest=ROOT/'artifacts/content_art';dest.mkdir(parents=True,exist_ok=True)
    contact.resize((960,1200),Image.Resampling.NEAREST).save(dest/'characters.png')
    print('Generated 100 field actors, 100 battle actors, 200 item/skill icons; 4bpp.')

if __name__=='__main__':main()
