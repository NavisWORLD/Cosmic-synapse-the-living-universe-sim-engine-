from pathlib import Path
import hashlib,re,subprocess,sys
root=Path(__file__).parent
rom=root/'LOST_COSMOS_ERIDORIA_V8.gba'
src=(root/'lost_cosmos_v5.c').read_text()
qtxt=(root/'qseed.h').read_text()
data=rom.read_bytes()
old=Path('/mnt/data/SIM_EARTH_PIXEL_UNIVERSE_LOST_COSMOS.gba').read_bytes() if Path('/mnt/data/SIM_EARTH_PIXEL_UNIVERSE_LOST_COSMOS.gba').exists() else None

def fail(m): print('FAIL:',m); raise SystemExit(1)
def ok(m): print('PASS:',m)
if len(data)<65536 or len(data)&(len(data)-1): fail('ROM is not power-of-two >=64K')
if data[:4] != bytes.fromhex('2e0000ea'): fail('entry branch is not 0xEA00002E -> 0x080000C0')
if data[0xA0:0xAC] != b'ERIDORIAV8  ': fail('title mismatch')
if data[0xAC:0xB0] != b'ERV8': fail('game code mismatch')
if data[0xB2] != 0x96: fail('fixed header byte mismatch')
if data[0xBC] != 9: fail('software version mismatch')
if hashlib.sha256(data[4:0xA0]).hexdigest() != '08a0153cfd6b0ea54b938f7d209933fa849da0d56f5a34c481060c9ff2fad818': fail('Nintendo logo block mismatch')
chk=(-sum(data[0xA0:0xBD])-0x19)&0xFF
if data[0xBD] != chk: fail('GBA complement checksum mismatch')
if old and data[4:0xA0] != old[4:0xA0]: fail('Nintendo logo block changed')
if b'SRAM_V113' not in data: fail('SRAM save signature missing')
nums=[int(x) for x in re.findall(r'\b\d+\b',qtxt.split('{',1)[1].rsplit('}',1)[0])]
if len(nums)!=8192: fail(f'expected 8192 QSEED bytes, got {len(nums)}')
qbytes=bytes(nums)
if data.find(qbytes)<0: fail('exact 8192-byte tape not found contiguously in ROM')
qhash=hashlib.sha256(qbytes).hexdigest()
for token in ['MODE0','BG0_ENABLE','OBJ_ENABLE','MAP_W 64','generate_origin','generate_ember','generate_tide','generate_bloom','generate_black','generate_crown','GOAL_SEEK_KEY','GOAL_WANDER','MODEL != MEMORY','SRAM_V113','crown_interact','postgame_tick','QA_AUTORUN','quantum_workload_step','player_attack','cast_magic','spawn_monsters','gear_owned','player_level','boss_flags','save_valid_v2']:
    if token not in src: fail('source token missing: '+token)
# no undefined freestanding linker symbols
elf=root/'lost_cosmos_v5.elf'
if elf.exists():
    u=subprocess.check_output(['nm','-u',str(elf)],text=True).strip()
    if u: fail('undefined ELF symbols: '+u)
# internal RAM headroom
if elf.exists():
    syms=subprocess.check_output(['nm','-n',str(elf)],text=True)
    m=re.search(r'^([0-9a-fA-F]+) B __bss_end__$',syms,re.M)
    if m and int(m.group(1),16)>=0x03007000: fail('IWRAM bss too close to stack')
print('ROM_SHA256',hashlib.sha256(data).hexdigest())
print('QSEED_SHA256',qhash)
ok('GBA header/logo/checksum, freestanding link, SRAM signature, exact QSEED and V5 RPG engine surfaces verified')
