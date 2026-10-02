from pathlib import Path
import difflib,hashlib
r=Path(__file__).resolve().parents[1]
v103=(r/'baseline/v10_3_lost_cosmos_v5.c').read_text()
v104=(r/'LOST_COSMOS_V10_SOURCE/lost_cosmos_v5.c').read_text()
assert hashlib.sha256(v103.encode()).hexdigest()=='79d00898a284b33282695c880d7de46988f99a3c38d2ab83c14c9125253f3ac7'
diff=''.join(difflib.unified_diff(v103.splitlines(keepends=True),v104.splitlines(keepends=True),fromfile='v10_3_lost_cosmos_v5.c',tofile='v10_4_lost_cosmos_v5.c'))
(r/'tools/engine_v10_3_to_v10_4.diff').write_text(diff)
hash104=hashlib.sha256(v104.encode()).hexdigest()
(r/'tools/engine_v10_4_source.sha256').write_text(hash104+'\n')
print('STAGED_V104_SHA256',hash104)
