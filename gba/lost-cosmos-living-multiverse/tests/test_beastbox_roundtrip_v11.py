"""Public snapshot format tests; these fixtures are not controller gameplay proof."""
import contextlib, hashlib, io, json, struct, sys, tempfile, unittest, zipfile, zlib
from pathlib import Path
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R/'tools'))
from export_beastbox_v11 import export, c_array, G
from import_beastbox import import_export, InvalidExport

class RoundTrip(unittest.TestCase):
 def snapshot(self, folder):
  # Construct only the documented public export page, with real public art.
  save=bytearray(32768);b=bytearray(192);b[:4]=b'LCE\x01'
  b[5:8]=bytes([12,75,1]);b[16:80]=bytes(c_array(G/'imported_companion.h','lc_imported_companion_bcp1'))
  b[80:85]=b'BCG1\x01';b[85]=b[22];b[144:149]=b'STAY\0';b[156]=128
  struct.pack_into('<IHH',b,160,1838690571,7,98);b[168:172]=bytes([68,55,8,0])
  struct.pack_into('<I',b,180,zlib.crc32(b[:180]));b[191]=0xa5;save[6208:6400]=b
  source=folder/'public_fixture.sav';source.write_bytes(save);out=folder/'public.zip'
  with contextlib.redirect_stdout(io.StringIO()):export(source,out)
  return out
 def altered(self, source, dest, mutate):
  with zipfile.ZipFile(source) as z:files={n:z.read(n) for n in z.namelist()}
  mutate(files)
  with zipfile.ZipFile(dest,'w') as z:
   for n,v in files.items():z.writestr(n,v)
 def test_round_trip_identity_progress_and_art(self):
  with tempfile.TemporaryDirectory() as td:
   d=Path(td);p=self.snapshot(d);r=import_export(p,d/'installed')
   self.assertEqual(r['BCP1_game_profile']['public_identity'],'f5a4cb6d')
   self.assertEqual(r['game_progress']['bond'],75);self.assertEqual(r['game_progress']['stage'],1)
   self.assertEqual(r['portable_seed_hash'],1838690571)
   h=(d/'installed/imported_companion.h').read_text()
   self.assertIn('LC_IMPORT_DISPLAY_NAME "STAY"',h);self.assertIn('LC_IMPORT_HAS_PROGRESS',h)
   self.assertTrue((d/'installed/content_v11_import_receipt.h').is_file())
 def test_changed_art_rejects(self):
  with tempfile.TemporaryDirectory() as td:
   d=Path(td);p=self.snapshot(d);bad=d/'bad.zip'
   self.altered(p,bad,lambda f:f.__setitem__('gba/companion_tiles.4bpp',bytes(8192)))
   with self.assertRaises(InvalidExport):import_export(bad,d/'out')
 def test_missing_receipt_rejects(self):
  with tempfile.TemporaryDirectory() as td:
   d=Path(td);p=self.snapshot(d);bad=d/'bad.zip';self.altered(p,bad,lambda f:f.pop('receipt.json'))
   with self.assertRaises(InvalidExport):import_export(bad,d/'out')
 def test_cross_profile_mismatch_rejects_with_updated_hash(self):
  with tempfile.TemporaryDirectory() as td:
   d=Path(td);p=self.snapshot(d);bad=d/'bad.zip'
   def mutate(f):
    doc=json.loads(f['companion.profile.json']);doc['game_profile']['game_stats'][0]+=1
    f['companion.profile.json']=json.dumps(doc).encode();receipt=json.loads(f['receipt.json'])
    receipt['files']['companion.profile.json']=hashlib.sha256(f['companion.profile.json']).hexdigest()
    f['receipt.json']=json.dumps(receipt).encode()
   self.altered(p,bad,mutate)
   with self.assertRaises(InvalidExport):import_export(bad,d/'out')
 def test_torn_public_page_rejects(self):
  with tempfile.TemporaryDirectory() as td:
   d=Path(td);self.snapshot(d);p=d/'public_fixture.sav';b=bytearray(p.read_bytes());b[6399]=0;p.write_bytes(b)
   with self.assertRaises(ValueError):export(p,d/'out.zip')

if __name__=='__main__':unittest.main()
