#!/usr/bin/env python3
"""Export only the ROM's explicitly prepared public LCEX snapshot.
The private owner ledger is never read. Accepts a 32KiB SRAM battery; emits
BCP1/empty-guest BCG1, native art and SHA-256 receipt for offline import.
"""
from pathlib import Path
import argparse,hashlib,json,re,struct,zipfile,zlib
from import_beastbox import parse_bcp1,check_guest_bcg1,field_tiles_32
R=Path(__file__).resolve().parents[1];G=R/'LOST_COSMOS_V10_SOURCE'
def c_array(path,name):
 s=path.read_text();a=s.index('{',s.index(name));depth=1;b=a+1
 while depth:
  if s[b]=='{':depth+=1
  if s[b]=='}':depth-=1
  b+=1
 return [int(x.rstrip('uUlL'),0) for x in re.findall(r'0x[0-9a-fA-F]+[uUlL]*|\b\d+[uUlL]*\b',s[a+1:b-1])]
def native_art(species,stage):
 if species:
  data=c_array(G/'visual_assets_v10_8.h','V108_SPECIES')
  offset=((species-1)*3+min(stage,2))*2*32;words=data[offset:offset+32];palbank=5+species-1
 else:
  words=c_array(G/'visual_assets_v10_8.h','V108_BUDDY')[:32];palbank=1
 palettes=c_array(G/'visual_assets_v10_8.h','V108_OBJ_PALETTES')
 palette=struct.pack('<16H',*palettes[palbank*16:(palbank+1)*16])
 frame=bytearray()
 for ty in range(8):
  for tx in range(8):
   for yy in range(8):
    for xx in range(0,8,2):
     pair=[]
     for dx in [0,1]:
      sx=(tx*8+xx+dx)//4;sy=(ty*8+yy)//4
      pair.append((words[((sy//8)*2+sx//8)*8+sy%8]>>(sx%8*4))&15)
     frame.append(pair[0]|pair[1]<<4)
 return bytes(frame)*4,palette

def export(save:Path,out:Path,source_dir:Path=G):
 s=save.read_bytes()
 if len(s)!=32768:raise ValueError('Expected the ROM\'s 32 KiB SRAM battery save.')
 b=s[6208:6400]
 if b[:4]!=b'LCE\x01' or b[191]!=0xa5 or zlib.crc32(b[:180])!=struct.unpack_from('<I',b,180)[0]:
  raise ValueError('No verified prepared export. In PARTY, select a bonded beast and EXPORT TO BEAST BOX.')
 bcp=b[16:80];bcg=b[80:140];profile=parse_bcp1(bcp);check_guest_bcg1(bcg)
 species=b[156]
 if species>=128:
  tiles=bytes(c_array(source_dir/'imported_companion.h','lc_imported_companion_tiles'))
  palette=bytes(c_array(source_dir/'imported_companion.h','lc_imported_companion_palette'))
  receipt=source_dir/'import_receipt.json'
  expected=json.loads((receipt if receipt.exists() else R/'content/v11_1_import_receipt.json').read_text())
  if hashlib.sha256(tiles).hexdigest()!=expected['tiles_sha256'] or hashlib.sha256(palette).hexdigest()!=expected['palette_sha256']:
   raise ValueError('Local art does not match the public import receipt.')
  if profile['public_identity']!=expected['BCP1_game_profile']['public_identity']:
   raise ValueError('Prepared public identity does not match this compiled beast.')
 elif species<=8:tiles,palette=native_art(species,b[7])
 else:raise ValueError('Unsupported public species.')
 label=b[144:156].split(b'\0',1)[0].decode('ascii')
 files={'gba/companion_tiles.4bpp':tiles,'gba/companion_palette.bgr555':palette,
        'gba/companion_profile.bin':bcp,'gba/companion_state.bin':bcg,
        'gba/companion_field_tiles.4bpp':field_tiles_32(tiles)}
 public={'schema':'lost-cosmos-public-beast-v11.1','name':label,
         'public_identity':profile['public_identity'],'game_profile':profile,
         'portable_seed_hash':struct.unpack_from('<I',b,160)[0],
         'game_progress':{'level':b[5],'bond':b[6],'stage':b[7],
                          'experience':struct.unpack_from('<H',b,164)[0],
                          'hp':struct.unpack_from('<H',b,166)[0],
                          'attack':b[168],'defense':b[169],'flags':b[170],'affinity':b[171]},
         'origin':'LOST COSMOS offline SRAM export','private_memory_included':False}
 files['companion.profile.json']=(json.dumps(public,indent=2)+'\n').encode()
 receipt={'schema':'lost-cosmos-public-export-receipt-v1','public_identity':profile['public_identity'],
          'files':{n:hashlib.sha256(v).hexdigest() for n,v in files.items()},
          'lineage':'public snapshot; private ledger remains external',
          'network_handshake':False,'private_memory_included':False}
 files['receipt.json']=(json.dumps(receipt,indent=2)+'\n').encode()
 out.parent.mkdir(parents=True,exist_ok=True)
 with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED) as z:
  for n,v in sorted(files.items()):z.writestr(n,v)
 print(json.dumps({'package':str(out),'public_identity':profile['public_identity'],'sha256':hashlib.sha256(out.read_bytes()).hexdigest()},indent=2))
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--save',type=Path,required=True);a.add_argument('--out',type=Path,required=True);a.add_argument('--source-dir',type=Path,default=G);o=a.parse_args();export(o.save,o.out,o.source_dir)
