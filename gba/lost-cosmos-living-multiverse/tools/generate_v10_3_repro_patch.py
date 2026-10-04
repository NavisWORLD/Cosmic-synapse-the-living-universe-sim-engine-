#!/usr/bin/env python3
"""Maintainer utility: explicit hash-pinned reproducible source diff, never edits historical source."""
from pathlib import Path
import hashlib,difflib
r=Path(__file__).resolve().parents[1]; a=r/'baseline/v10_2_lost_cosmos_v5.c';b=r/'LOST_COSMOS_V10_SOURCE/lost_cosmos_v5.c'
assert hashlib.sha256(a.read_bytes()).hexdigest()=='de5912103418260bbe74c062762571ed88846ce4aa709cc7d959f6db6bac52e1','frozen V10.2 baseline differs'
p=''.join(difflib.unified_diff(a.read_text().splitlines(keepends=True),b.read_text().splitlines(keepends=True),fromfile='lost_cosmos_v5.c',tofile='lost_cosmos_v5.c',n=4))
(r/'tools/engine_v10_2_to_v10_3.diff').write_text(p)
(r/'tools/engine_v10_3_source.sha256').write_text(hashlib.sha256(b.read_bytes()).hexdigest()+'\n')
print('V10.2 baseline',hashlib.sha256(a.read_bytes()).hexdigest())
print('V10.3 target',hashlib.sha256(b.read_bytes()).hexdigest())
print('patch length',len(p))
