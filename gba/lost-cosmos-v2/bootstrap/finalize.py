from pathlib import Path

root = Path(__file__).resolve().parents[1] if Path(__file__).parent.name == 'bootstrap' else Path('.')

def replace_required(path: Path, old: str, new: str):
    text = path.read_text()
    if old not in text:
        raise SystemExit(f'bootstrap patch target missing in {path}: {old[:80]!r}')
    path.write_text(text.replace(old, new))

src = root / 'lost_cosmos_v2.c'
replace_required(src, 'static volatile u16* screenblock(int sb){ return (volatile u16*)(0x06000000 + sb*2048); }', 'static volatile u16* screenblock(int sb){ return VRAM16 + sb*1024; }')
replace_required(src, 'static void upload_bg_tile(int id,const u32*t){ vram_copy32((volatile u32*)(0x06000000 + id*32),t,8); }', 'static void upload_bg_tile(int id,const u32*t){ vram_copy32(VRAM32 + id*8,t,8); }')
replace_required(src, 'for(y=0;y<8;y++)t[y]=0x22222222u; vram_copy32((volatile u32*)(0x06004000+63*32),t,8);', 'for(y=0;y<8;y++)t[y]=0x22222222u; vram_copy32(VRAM32 + (0x4000/4) + 63*8,t,8);')
replace_required(src, "for(g=0;g<43;g++){for(y=0;y<8;y++)t[y]=0;for(x=0;x<5;x++)for(y=0;y<7;y++)if(FONT[g][x]&(1u<<y))tile_pixel(t,x+1,y,1);vram_copy32((volatile u32*)(0x06004000+(64+g)*32),t,8);}", "for(g=0;g<43;g++){for(y=0;y<8;y++)t[y]=0;for(x=0;x<5;x++)for(y=0;y<7;y++)if(FONT[g][x]&(1u<<y))tile_pixel(t,x+1,y,1);vram_copy32(VRAM32 + (0x4000/4) + (64+g)*8,t,8);}")
replace_required(src, 'for(y=28;y<52;y++)map_put(26,y,T_PATH,1,C_FREE,0);', 'for(y=28;y<52;y++)map_put(26,y,T_PATH,1,C_FREE,(y==28)?TR_DOOR:0);')
replace_required(src, 'for(x=9;x<50;x++)map_put(x,51,T_METAL,1,C_FREE,0);', 'for(x=9;x<50;x++)map_put(x,51,T_METAL,1,C_FREE,(x==9)?TR_SHIP:0);')
replace_required(src, 'for(x=10;x<=48;x++)map_put(x,52,T_BRIDGE,1,C_FREE,0);', 'for(x=10;x<=48;x++)map_put(x,52,T_BRIDGE,1,C_FREE,(x==10)?TR_SHIP:0);')
replace_required(src, 'for(x=10;x<=50;x++)map_put(x,51,T_PATH,1,C_FREE,0);', 'for(x=10;x<=50;x++)map_put(x,51,T_PATH,1,C_FREE,(x==10)?TR_SHIP:0);')

routes = root / 'verify_routes.py'
replace_required(routes, 'for y in range(28,52):put(c,t,26,y)', 'for y in range(28,52):put(c,t,26,y,FREE,2 if y==28 else 0)')
replace_required(routes, 'for x in range(9,50):put(c,t,x,51)', 'for x in range(9,50):put(c,t,x,51,FREE,1 if x==9 else 0)')
replace_required(routes, 'for x in range(10,49):put(c,t,x,52)', 'for x in range(10,49):put(c,t,x,52,FREE,1 if x==10 else 0)')
replace_required(routes, 'for x in range(10,51):put(c,t,x,51)', 'for x in range(10,51):put(c,t,x,51,FREE,1 if x==10 else 0)')
text = routes.read_text()
if 'trigger_checks=[' not in text:
    text += '''\ntrigger_checks=[\n ("origin door",0,1,(26,28),2),("origin ship trigger",0,1,(12,49),1),\n ("ember ship trigger",1,1,(9,51),1),("ember lift trigger",1,1,(20,20),7),("ember X trigger",1,0,(53,10),4),\n ("tide ship trigger",2,1,(10,52),1),("tide lift trigger",2,1,(22,45),7),("tide Y trigger",2,0,(50,12),5),\n ("bloom ship trigger",3,1,(10,51),1),("bloom lift trigger",3,1,(31,31),7),("bloom Z trigger",3,2,(52,11),6),\n ("black secret trigger",4,1,(24,14),9),("crown core trigger",5,1,(55,8),10),\n]\nfor name,w,l,(x,y),expected in trigger_checks:\n c,t=gen(w,l)\n if t[y][x]!=expected: raise SystemExit(f"FAIL trigger: {name} got {t[y][x]} expected {expected}")\n print('PASS trigger:',name)\n'''
    routes.write_text(text)

verify = root / 'verify_v2.py'
text = verify.read_text()
needle = "if data[0xB2] != 0x96: fail('fixed header byte mismatch')"
if 'software version mismatch' not in text:
    if needle not in text: raise SystemExit('verify_v2 header patch target missing')
    text = text.replace(needle, needle + "\nif data[0xBC] != 2: fail('software version mismatch')\nif hashlib.sha256(data[4:0xA0]).hexdigest() != '08a0153cfd6b0ea54b938f7d209933fa849da0d56f5a34c481060c9ff2fad818': fail('Nintendo logo block mismatch')")
    verify.write_text(text)

print('PASS: bootstrap source patched to final V2 fixes')
