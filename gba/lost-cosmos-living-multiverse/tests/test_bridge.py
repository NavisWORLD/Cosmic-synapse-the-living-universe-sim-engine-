import io, json, struct, sys, tempfile, unittest, zipfile, zlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]/'tools'))
from import_beastbox import import_export, InvalidExport, expected_genesis

def fnv(text):
 h=2166136261
 for b in text.encode(): h=((h^b)*16777619)&0xffffffff
 return h

class ImportTests(unittest.TestCase):
 def setup_export(self,path,measured=False,badcrc=False,profile=True,tamper_stats=False):
  raw=bytearray(60);raw[:4]=b'BCG1';raw[4]=1
  if measured:raw[6]=1
  stats,temper,name=expected_genesis('nebula-test')
  p=bytearray(64);p[:4]=b'BCP1';p[4]=1;p[5]=2;p[6]=0
  p[8:18]=bytes(stats);p[18:23]=bytes(temper)
  if tamper_stats:p[8]+=1;p[9]-=1
  p[24:28]=struct.pack('<I',fnv('identity|1|nebula-test'))
  p[60:64]=struct.pack('<I',(zlib.crc32(p[:60])+(1 if badcrc else 0))&0xffffffff)
  details={'schema':'beast-cage-creature-v1','version':1,'id':f"bb-{fnv('identity|1|nebula-test'):08x}",
           'seed':'nebula-test','family':'void','baseLook':'nebula','name':name,
           'game':{'stats':dict(zip(('hp','energy','signal','memory','resonance','agility','chaos','stability','curiosity','evolution'),stats)),'level':1,'experience':0},
           'appearance':{'hueShift':0},
           'temperament':dict(zip(('curiosity','energy','playfulness','caution','independence'),temper))}
  if tamper_stats:details['game']['stats']['hp']+=1;details['game']['stats']['energy']-=1
  with zipfile.ZipFile(path,'w') as z:
   z.writestr('gba/companion_tiles.4bpp',bytes(range(256))*32)
   z.writestr('gba/companion_palette.bgr555',bytes(32))
   z.writestr('gba/companion_state.bin',raw)
   if profile:
    z.writestr('gba/companion_profile.bin',p)
    z.writestr('companion.profile.json',json.dumps(details))
 def test_good(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp)/'example.zip';self.setup_export(p)
   r=import_export(p,Path(tmp)/'out')
   self.assertEqual(r['BCP1_game_profile']['public_identity'],f"{fnv('identity|1|nebula-test'):08x}")
   self.assertEqual(r['portable_seed_hash'],fnv('lost-cosmos|nebula-test'))
   self.assertTrue((Path(tmp)/'out'/'imported_companion.h').exists())
 def test_old_bcg_only(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp)/'old.zip';self.setup_export(p,profile=False)
   self.assertIsNone(import_export(p,Path(tmp)/'out')['BCP1_game_profile'])
 def test_crc_rejects(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp)/'bad.zip';self.setup_export(p,badcrc=True)
   with self.assertRaises(InvalidExport):import_export(p,Path(tmp)/'out')
 def test_seeded_stats_tamper_rejects(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp)/'tampered.zip';self.setup_export(p,tamper_stats=True)
   with self.assertRaises(InvalidExport):import_export(p,Path(tmp)/'out')
 def test_owner_signal_rejects(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp)/'owner.zip';self.setup_export(p,measured=True)
   with self.assertRaises(InvalidExport):import_export(p,Path(tmp)/'out')

if __name__=='__main__':unittest.main()
