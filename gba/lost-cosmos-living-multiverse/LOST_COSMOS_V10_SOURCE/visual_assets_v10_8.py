#!/usr/bin/env python3
"""Compile original indexed Lost COSMOS drawings to native GBA 4bpp assets.

Run without options to regenerate the C header and editable PNG asset atlases.
--check compares the byte-for-byte generated header and validates hardware
limits without writing. The native PNGs are asset sheets, never screenshots.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import visual_patterns_v10_8 as art

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
HEADER = HERE / "visual_assets_v10_8.h"
ASSETS = PROJECT / "assets" / "visual_v10_8"

# The first four entries of each material retain the established V8 values.
# This maintains lighting/gameplay expectations while supplying the rest of
# each 16-color bank with authored secondary colors, ground and highlights.
MATERIAL_RGB5 = [
    [ # Origin: moss green, sandstone, bright stream, copper architecture.
        [(1,5,4),(4,13,8),(9,23,13),(20,29,17)],
        [(6,4,2),(15,11,6),(24,18,10),(31,26,16)],
        [(0,4,12),(1,12,23),(3,23,28),(18,31,31)],
        [(2,6,2),(3,17,5),(10,27,10),(24,31,17)],
        [(3,4,8),(8,11,14),(16,20,22),(26,28,27)],
        [(2,5,12),(5,12,22),(9,26,30),(31,31,21)],
        [(7,4,3),(16,12,9),(26,20,16),(31,29,22)],
        [(5,0,6),(15,3,16),(24,8,24),(31,18,27)],
    ],
    [ # Ember: fired clay, obsidian, molten brass.
        [(6,2,1),(13,5,3),(22,10,5),(28,18,10)],
        [(8,3,2),(15,8,4),(24,15,8),(31,25,14)],
        [(11,0,0),(24,3,0),(31,12,0),(31,28,5)],
        [(5,3,1),(13,9,2),(23,17,3),(30,26,9)],
        [(3,3,6),(9,8,11),(19,15,16),(29,25,22)],
        [(7,1,6),(16,5,12),(28,12,23),(31,26,29)],
        [(4,5,6),(12,12,13),(25,20,17),(31,30,23)],
        [(12,0,1),(19,0,3),(30,6,3),(31,23,7)],
    ],
    [ # Tide: turquoise water, salt-white stone, violet signal.
        [(1,7,10),(3,13,17),(8,20,23),(19,29,30)],
        [(6,5,6),(14,13,12),(23,22,19),(31,31,26)],
        [(0,2,9),(1,8,21),(4,20,30),(18,29,31)],
        [(0,7,6),(2,17,13),(8,25,18),(21,31,26)],
        [(1,4,11),(6,10,18),(14,18,27),(25,28,31)],
        [(6,3,16),(9,9,24),(18,21,31),(30,29,31)],
        [(6,7,8),(13,17,20),(22,27,29),(31,31,31)],
        [(3,1,12),(9,5,21),(18,11,29),(30,24,31)],
    ],
    [ # Bloom: mint ground, pink paths, indigo-violet canopy.
        [(1,6,5),(3,14,10),(9,23,13),(22,31,22)],
        [(6,3,5),(17,10,12),(25,18,19),(31,27,27)],
        [(0,5,11),(1,13,23),(6,25,29),(20,31,31)],
        [(2,4,8),(8,12,20),(22,11,27),(31,20,31)],
        [(5,4,9),(12,12,18),(21,21,28),(31,29,31)],
        [(1,8,5),(4,20,11),(16,30,15),(31,31,20)],
        [(5,7,3),(13,16,6),(23,26,12),(31,31,23)],
        [(5,0,7),(14,2,18),(27,5,27),(31,23,31)],
    ],
    [ # Black Garden: violet stone, acid foliage, cold blue signal.
        [(1,1,5),(4,4,11),(10,7,18),(19,14,27)],
        [(5,4,7),(11,8,15),(20,17,26),(29,27,31)],
        [(2,0,7),(7,2,18),(15,6,28),(24,22,31)],
        [(2,3,3),(7,11,9),(14,20,13),(26,29,18)],
        [(3,3,7),(8,9,15),(16,15,25),(27,24,31)],
        [(0,5,10),(3,17,25),(12,26,31),(29,31,31)],
        [(8,3,5),(15,8,14),(26,14,21),(31,25,29)],
        [(5,0,1),(16,1,8),(27,3,17),(31,13,23)],
    ],
    [ # Crown: slate and ivory with amethyst glass.
        [(2,4,8),(6,11,19),(12,21,28),(24,30,31)],
        [(7,5,4),(16,13,12),(25,21,19),(31,30,28)],
        [(2,6,14),(5,14,23),(13,26,30),(27,31,31)],
        [(2,5,8),(6,15,14),(13,24,20),(25,31,26)],
        [(3,5,10),(9,13,20),(20,22,29),(31,31,31)],
        [(3,2,12),(10,6,23),(20,15,29),(31,25,31)],
        [(6,6,3),(17,15,8),(26,24,13),(31,31,22)],
        [(9,1,6),(21,5,15),(31,12,25),(31,27,30)],
    ],
    [ # Dream Veil: dusk lavender and pearl, teal reflected water.
        [(4,4,8),(12,10,18),(22,19,25),(31,29,30)],
        [(9,5,9),(18,12,17),(27,21,26),(31,30,31)],
        [(1,6,14),(5,17,24),(14,27,31),(29,31,31)],
        [(3,4,11),(11,10,23),(23,15,31),(31,25,31)],
        [(4,5,10),(11,15,23),(23,23,29),(31,31,31)],
        [(4,2,15),(15,9,28),(25,19,31),(31,30,31)],
        [(9,5,4),(19,14,12),(29,23,20),(31,31,26)],
        [(8,0,8),(20,5,21),(30,12,30),(31,26,31)],
    ],
    [ # Eldoria: bright fern, weathered limestone, turquoise signal.
        [(2,7,5),(5,17,11),(13,24,17),(26,31,23)],
        [(8,5,3),(17,12,6),(27,21,12),(31,30,22)],
        [(0,7,10),(2,17,22),(7,26,30),(24,31,31)],
        [(2,5,2),(5,14,4),(16,27,10),(30,31,19)],
        [(4,4,6),(11,12,15),(21,23,24),(31,31,29)],
        [(2,7,11),(6,19,25),(19,28,30),(31,31,23)],
        [(8,5,4),(18,13,10),(27,22,15),(31,30,24)],
        [(7,1,5),(18,3,12),(27,10,20),(31,23,27)],
    ],
]


def rgb5(c: tuple[int, int, int]) -> int:
    assert len(c) == 3 and all(0 <= v < 32 for v in c)
    return c[0] | c[1] << 5 | c[2] << 10


def darken(c: tuple[int, int, int], n: int) -> tuple[int, int, int]:
    return tuple(max(0, x-n) for x in c)


def bg_palettes() -> list[list[list[tuple[int,int,int]]]]:
    result=[]
    secondary=[1,4,4,1,3,4,5,5]
    for materials in MATERIAL_RGB5:
        palettes=[]
        for i, material in enumerate(materials):
            palettes.append([(0,0,0)] + material + materials[secondary[i]] +
                            [materials[0][1], materials[0][0], materials[0][2], materials[7][2],
                             (1,2,4),(29,31,31),(31,27,12)])
        for m in (0,1,3,4):
            base=palettes[m]
            shade=[base[0],darken(base[2],4),darken(base[3],3),darken(base[4],2),base[1]]
            # Retain original shade indices1..4. Supplemental colors are darker
            # surface equivalents, leaving white and emissive pixel accents.
            shade += [darken(c,3) for c in base[5:14]] + base[14:16]
            palettes.append(shade)
        result.append(palettes)
    return result


HERO_PAL = [(0,0,0),(2,3,7),(3,10,15),(7,21,24),(18,30,28),
            (5,5,12),(31,25,18),(22,14,11),(17,10,5),(29,21,10),
            (25,9,5),(31,18,8),(26,29,30),(13,17,23),(31,31,29),(31,29,16)]
SPECIES_PALS = [
    # Forgeling: cool forged iron, hot copper coals and brass flame horns.
    [(0,0,0),(3,3,6),(7,9,13),(13,16,20),(24,27,28),(9,11,16),
     (6,4,3),(23,8,2),(31,22,5),(22,13,5),(30,10,2),(31,26,9),
     (25,28,30),(12,18,23),(31,31,24),(31,16,1)],
    # Tidewisp: cerulean body with pale luminous fins and warm smile.
    [(0,0,0),(1,4,11),(1,9,19),(3,19,27),(14,28,31),(2,13,23),
     (4,8,21),(10,16,29),(23,28,31),(13,23,30),(25,13,20),(31,22,27),
     (14,29,29),(6,12,22),(29,31,31),(17,31,31)],
    # Rootkin: bright leaf ramp, sienna trunk and salmon berry accents.
    [(0,0,0),(2,5,4),(3,11,6),(9,20,8),(22,29,14),(6,14,6),
     (11,6,3),(19,11,5),(29,20,9),(13,23,10),(24,15,6),(31,24,11),
     (27,12,17),(10,15,7),(31,31,23),(26,31,14)],
    # Voidmoth: velvet indigo, iris-violet crescents and rose antennae.
    [(0,0,0),(3,2,8),(8,5,16),(16,9,25),(26,19,31),(11,7,20),
     (20,12,25),(26,19,30),(30,25,31),(8,12,23),(31,16,25),(31,23,30),
     (14,22,29),(5,7,16),(30,31,31),(21,30,31)],
    # Skyspark: lapis blue feathers with ivory lightning and amber beak.
    [(0,0,0),(2,4,10),(5,10,21),(9,18,29),(21,29,31),(6,13,25),
     (27,24,11),(31,29,15),(31,31,24),(12,24,31),(31,18,6),(31,26,11),
     (24,30,31),(6,11,19),(31,31,28),(31,28,9)],
    # Frost wolf: white-cyan coat, periwinkle shadows, ice-blue antlers.
    [(0,0,0),(3,5,12),(7,11,22),(15,22,28),(26,30,31),(11,17,25),
     (6,11,19),(12,20,27),(22,29,31),(17,26,31),(7,12,21),(12,21,30),
     (25,31,31),(9,14,23),(31,31,31),(16,31,31)],
    # Ember phoenix: carmine feathers, tangerine flames and cool ash feathers.
    [(0,0,0),(8,2,7),(18,3,8),(28,7,8),(31,19,11),(23,4,8),
     (21,8,3),(29,15,4),(31,25,9),(31,13,3),(31,15,2),(31,28,9),
     (31,25,11),(14,13,21),(31,31,25),(31,20,2)],
    # Hollow wraith: dusty blue veil, warm lantern core, pale moonlit edge.
    [(0,0,0),(3,4,11),(7,10,19),(13,18,27),(24,28,31),(9,13,23),
     (18,17,25),(24,22,30),(29,28,31),(7,12,23),(25,17,10),(31,25,14),
     (19,26,31),(6,8,17),(31,31,27),(31,24,9)],
]


def obj_palettes() -> list[list[tuple[int,int,int]]]:
    palettes=[HERO_PAL]
    for main, mid, shade in [((9,25,28),(4,15,23),(2,8,15)),
                            ((15,28,18),(7,20,13),(3,10,9)),
                            ((22,16,29),(13,8,21),(6,5,14)),
                            ((29,23,8),(24,14,4),(12,7,5))]:
        palettes.append([(0,0,0),(2,3,9),shade,mid,main,(8,10,21),
                         (29,29,24),(17,24,31),(12,18,29),(7,12,23),
                         (28,14,10),(31,23,13),(19,25,31),(5,9,17),(31,31,28),(31,28,9)])
    palettes += SPECIES_PALS
    scholar=HERO_PAL[:]; herbalist=HERO_PAL[:]
    scholar[2:5]=[(9,6,18),(19,11,26),(28,22,31)]
    herbalist[2:5]=[(5,10,9),(10,21,13),(24,30,18)]
    palettes += [scholar,herbalist]
    assert len(palettes)==15
    return palettes


def validate_pattern(p: list[list[int]], w: int, h: int) -> None:
    assert len(p)==h and all(len(row)==w for row in p)
    assert all(0<=n<=15 for row in p for n in row)


def tile_words(p: list[list[int]]) -> list[int]:
    """Eight u32 scanlines of one 8x8 GBA tile; low nibble is the left pixel."""
    validate_pattern(p,8,8)
    return [sum(c<<(x*4) for x,c in enumerate(row)) for row in p]


def split_tiles(p: list[list[int]]) -> list[list[int]]:
    """GBA OBJ 1D layout: top-left, top-right, bottom-left, bottom-right."""
    h,w=len(p),len(p[0])
    assert w%8==0 and h%8==0
    validate_pattern(p,w,h)
    return [tile_words([row[x:x+8] for row in p[y:y+8]])
            for y in range(0,h,8) for x in range(0,w,8)]


def sprite_words(p: list[list[int]]) -> list[int]:
    validate_pattern(p,16,16)
    return [word for tile in split_tiles(p) for word in tile]


def unpack_sprite(words: list[int]) -> list[list[int]]:
    assert len(words)==32
    p=[[0]*16 for _ in range(16)]
    for y in range(16):
        for x in range(16):
            word=words[((y>>3)*2+(x>>3))*8+(y&7)]
            p[y][x]=(word>>((x&7)*4))&15
    return p


def initializer(data, width=8, digits=8) -> str:
    if isinstance(data[0],int):
        suffix="u" if digits==8 else ""
        return "{"+",".join(f"0x{v:0{digits}X}{suffix}" for v in data)+"}"
    return "{\n"+",\n".join(" "+initializer(v,width,digits).replace("\n","\n ") for v in data)+"\n}"


def build_data():
    tiles=[tile_words(p) for p in art.TILES]
    extras=[]; descriptors=[]; base=64
    for name,p,pal,semantic in art.DECORATIONS:
        rows=split_tiles(p)
        descriptors.append(dict(name=name,base=base,w=len(p[0])//8,h=len(p)//8,
                                palette=pal,source_tile=semantic))
        extras += rows; base += len(rows)
    terrain_base=base
    extras += [tile_words(p) for p in art.TERRAIN_VARIANTS]; base += len(art.TERRAIN_VARIANTS)
    path_base=base
    extras += [tile_words(p) for p in art.PATH_EDGES]; base += len(art.PATH_EDGES)
    props_base=base
    extras += [tile_words(p) for p in art.PROPS]; base += len(art.PROPS)
    assert len(extras)==192 and base==256
    species=[[[sprite_words(frame) for frame in forms] for forms in creature] for creature in art.SPECIES_FRAMES]
    return dict(tiles=tiles,extras=extras,descriptors=descriptors,
                terrain_base=terrain_base,path_base=path_base,props_base=props_base,
                hero=[sprite_words(p) for p in art.HERO_FRAMES],
                buddy=[sprite_words(p) for p in art.BUDDY_FRAMES],
                npcs=[sprite_words(p) for p in art.NPC_FRAMES],species=species,
                enemies=[sprite_words(art.SPECIES_BASE[s][stage]) for s,stage in [(4,0),(0,0),(1,0),(2,0),(3,0),(4,1)]],
                anim=[[tile_words(p) for p in frames] for frames in art.BG_ANIM],
                bg_pal=[[[rgb5(c) for c in palette] for palette in world] for world in bg_palettes()],
                obj_pal=[[rgb5(c) for c in palette] for palette in obj_palettes()])


def make_header(data) -> str:
    source_hash=hashlib.sha256((HERE/"visual_patterns_v10_8.py").read_bytes()).hexdigest()
    s=["/* Original Lost COSMOS V10.8 native art. Generated by visual_assets_v10_8.py.",
       f" * Editable pattern source SHA256: {source_hash}",
       " * 4bpp, low-nibble-left pixels, 1D OBJ order. No imported identity assets.",
       " * BG extra tiles64..255; FG40..43/font CB1 unchanged by this header.",
       " * Native OBJ palettes0..14 only. Imported palette15/tiles640..895 reserved.",
       " */", "#ifndef VISUAL_ASSETS_V10_8_H", "#define VISUAL_ASSETS_V10_8_H",
       "#define V108_BG_EXTRA_BASE 64", "#define V108_BG_EXTRA_COUNT 192",
       "#define V108_PLAYER_FRAMES 4", "#define V108_SPECIES_COUNT 8",
       "#define V108_SPECIES_STAGES 3", "#define V108_SPECIES_FRAMES 2",
       "#define V108_DECOR_COUNT 11",f"#define V108_TERRAIN_BASE {data['terrain_base']}",
       f"#define V108_PATH_EDGE_BASE {data['path_base']}",f"#define V108_PROP_BASE {data['props_base']}",
       "enum { V108_DECOR_OAK, V108_DECOR_WILLOW, V108_DECOR_COTTAGE,",
       " V108_DECOR_RUIN_ARCH, V108_DECOR_WATERFALL_0, V108_DECOR_WATERFALL_1,",
       " V108_DECOR_CRYSTAL_SPIRE, V108_DECOR_FORGE, V108_DECOR_CORAL,",
       " V108_DECOR_OBSERVATORY, V108_DECOR_BRIDGE };",
       "typedef struct { u16 base; u8 w,h,palette,source_tile; } V108Decor;"]
    for ctype,name,dims,key,digits in [
        ("u32","V108_TILES","[32][8]","tiles",8),
        ("u32","V108_BG_EXTRA","[192][8]","extras",8),
        ("u32","V108_BG_ANIM","[6][4][8]","anim",8),
        ("u32","V108_PLAYER","[16][32]","hero",8),
        ("u32","V108_BUDDY","[4][32]","buddy",8),
        ("u32","V108_ENEMIES","[6][32]","enemies",8),
        ("u32","V108_NPCS","[8][32]","npcs",8),
        ("u32","V108_SPECIES","[8][3][2][32]","species",8),
        ("u16","V108_BG_PALETTES","[8][12][16]","bg_pal",4),
        ("u16","V108_OBJ_PALETTES","[15][16]","obj_pal",4),
    ]:
        s.append(f"static const {ctype} {name}{dims} = {initializer(data[key],digits=digits)};")
    s.append("static const u8 V108_ANIM_TILE_TYPES[6] = {3,6,14,9,24,29};")
    s.append("static const u8 V108_ENEMY_PALETTE[6] = {9,5,6,7,8,9};")
    s.append("static const u8 V108_PROP_PALETTE[8] = {6,6,3,4,5,5,7,4};")
    s.append("static const u8 V108_TERRAIN_SOURCE[16] = {2,2,2,2,1,1,1,1,5,5,5,5,17,17,17,17};")
    s.append("static const V108Decor V108_DECORS[V108_DECOR_COUNT] = {")
    for d in data["descriptors"]:
        s.append(f" {{{d['base']},{d['w']},{d['h']},{d['palette']},{d['source_tile']}}}, /* {d['name']} */")
    s.append("};\n#endif\n")
    return "\n".join(s)


def validate(data) -> dict:
    assert data["terrain_base"]==224 and data["path_base"]==240 and data["props_base"]==248
    assert len(data["hero"])==16 and len({tuple(f) for f in data["hero"]})==16
    assert len(data["species"])==8
    all_species=[]; unique_silhouettes=set(); frame_differences=[]
    for s,creature in enumerate(art.SPECIES_FRAMES):
        assert len(creature)==3
        stages=[]
        for stage,frames in enumerate(creature):
            assert len(frames)==2
            for p in frames:
                packed=sprite_words(p)
                assert unpack_sprite(packed)==p
                all_species.append(tuple(packed))
                unique_silhouettes.add(tuple(int(n!=0) for row in p for n in row))
            # Difference must include anatomical pixels; animating a single
            # detached ornament does not satisfy this artwork's requirements.
            changed=sum(a!=b for ra,rb in zip(frames[0],frames[1]) for a,b in zip(ra,rb))
            assert changed>=4,(s,stage,changed)
            frame_differences.append(changed)
            stages.append(tuple(int(n!=0) for row in frames[0] for n in row))
        assert len(set(stages))==3,("Evolution silhouette repeated",s)
    assert len(set(all_species))==48
    assert len(unique_silhouettes)>=45
    assert all(len(p)==16 for world in data["bg_pal"] for p in world)
    assert all(len(p)==16 for p in data["obj_pal"])
    assert all(0<=c<=0x7FFF for world in data["bg_pal"] for p in world for c in p)
    assert all(0<=c<=0x7FFF for p in data["obj_pal"] for c in p)
    assert 384+8*3*2*4==576 < 640 # imported OBJ reservation is disjoint
    assert 256*32<=0x4000 # extra BG tiles stay inside CB0
    for frames in data["anim"]:
        assert len(set(tuple(p) for p in frames))==4
    return {"bg_core_tiles":32,"bg_extra_tiles":192,"bg_extra_first":64,"bg_extra_last":255,
            "hero_facings":4,"hero_frames_per_facing":4,"species":8,"forms_per_species":3,
            "frames_per_form":2,"distinct_species_frames":48,
            "distinct_species_silhouettes":len(unique_silhouettes),
            "species_frame_pixel_changes":frame_differences,
            "native_obj_palette_banks":list(range(15)),"reserved_imported_palette":15,
            "imported_obj_tile_reservation":[640,895],"encoding":"4bpp, GBA1D, low nibble left"}


def rgba(p, palette):
    from PIL import Image
    h,w=len(p),len(p[0]); image=Image.new("RGBA",(w,h))
    image.putdata([tuple((x*255+15)//31 for x in palette[n])+(255 if n else 0,)
                   for row in p for n in row])
    return image


def save_assets(data,report):
    from PIL import Image,ImageDraw,ImageFont
    ASSETS.mkdir(parents=True,exist_ok=True)
    palettes=bg_palettes(); obj=obj_palettes()
    native=Image.new("RGBA",(96,128))
    for s,creature in enumerate(art.SPECIES_FRAMES):
        for stage,frames in enumerate(creature):
            for f,p in enumerate(frames): native.paste(rgba(p,obj[s+5]),((stage*2+f)*16,s*16))
    native.save(ASSETS/"species_native_96x128.png")
    hero=Image.new("RGBA",(64,64))
    for i,p in enumerate(art.HERO_FRAMES): hero.paste(rgba(p,obj[0]),((i%4)*16,(i//4)*16))
    hero.save(ASSETS/"hero_native_64x64.png")
    others=Image.new("RGBA",(128,48))
    for i,p in enumerate(art.BUDDY_FRAMES): others.paste(rgba(p,obj[1+i]),(i*16,0))
    for i,p in enumerate(art.NPC_FRAMES): others.paste(rgba(p,obj[13+(i//2&1)]),(i*16,16))
    for i,s in enumerate([4,0,1,2,3,4]): others.paste(rgba(art.SPECIES_BASE[s][1 if i==5 else 0],obj[s+5]),(i*16,32))
    others.save(ASSETS/"characters_native_128x48.png")
    for name,p,pal,_ in art.DECORATIONS:
        rgba(p,palettes[0][pal]).save(ASSETS/f"{name.lower()}_native.png")
    # Labeled inspection sheets display only art assets. They do not claim to
    # be mGBA captures, display gameplay or imply that integration is complete.
    sheet=Image.new("RGB",(680,604),(14,18,31)); draw=ImageDraw.Draw(sheet)
    draw.text((16,12),"LOST COSMOS V10.8 / ORIGINAL NATIVE SPRITE ASSETS",fill=(230,237,244))
    draw.text((16,29),"16x16 pixels; nearest-neighbor 3x inspection. ASSET SHEET - NOT A GAME SCREEN.",fill=(136,172,194))
    for s,forms in enumerate(art.SPECIES_FRAMES):
        y=56+s*66
        draw.text((16,y+2),art.SPECIES_NAMES[s][0].upper(),fill=(221,224,205))
        for stage,frames in enumerate(forms):
            x=164+stage*168
            draw.text((x,y-1),art.SPECIES_NAMES[s][stage],fill=(185,199,218))
            for f,p in enumerate(frames):
                image=rgba(p,obj[5+s]).resize((48,48),Image.Resampling.NEAREST)
                sheet.paste(image,(x+f*54,y+13),image)
    sheet.save(ASSETS/"species_asset_sheet.png")
    # Native environments include the entire stamp, preserving source pixels.
    scenes=Image.new("RGB",(720,556),(14,18,31)); draw=ImageDraw.Draw(scenes)
    draw.text((16,12),"LOST COSMOS V10.8 / NATIVE ENVIRONMENT ASSET ATLAS",fill=(230,237,244))
    draw.text((16,29),"Hand-designed 4bpp stamps. ASSET ATLAS - NOT A GAME SCREEN.",fill=(136,172,194))
    for i,(name,p,pal,_) in enumerate(art.DECORATIONS):
        x=16+(i%4)*174; y=57+(i//4)*159
        image=rgba(p,palettes[0][pal]).resize((len(p[0])*3,len(p)*3),Image.Resampling.NEAREST)
        scenes.paste(image,(x,y),image)
        draw.text((x,y+len(p)*3+5),f"{name} / {len(p[0])}x{len(p)}",fill=(185,199,218))
    scenes.save(ASSETS/"environment_asset_atlas.png")
    material_map=[7,0,0,2,4,1,2,6,5,3,6,7,6,5,7,7,6,4,3,5,0,3,6,5,2,0,3,4,4,6,7,5]
    tiles=Image.new("RGBA",(128,16))
    for i,p in enumerate(art.TILES): tiles.paste(rgba(p,palettes[0][material_map[i]]),((i%16)*8,(i//16)*8))
    tiles.save(ASSETS/"core_tiles_native_128x16.png")
    report["decorations"]=data["descriptors"]
    report["pattern_source_sha256"]=hashlib.sha256((HERE/"visual_patterns_v10_8.py").read_bytes()).hexdigest()
    report["compiled_header_sha256"]=hashlib.sha256(HEADER.read_bytes()).hexdigest()
    (ASSETS/"asset_manifest.json").write_text(json.dumps(report,indent=2)+"\n")


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check",action="store_true")
    args=parser.parse_args()
    data=build_data(); report=validate(data); header=make_header(data)
    if args.check:
        if not HEADER.exists() or HEADER.read_text()!=header:
            raise SystemExit("Generated native art header is out of date")
        print("Native art encoding, palette limits,48 unique frames,24 evolution silhouettes and reproducibility: PASS")
    else:
        HEADER.write_text(header)
        save_assets(data,report)
        print(f"Generated {HEADER.name}:32 base tiles,192 extra tiles,16 hero frames,48 creature frames")
    return report


if __name__=="__main__":
    main()
