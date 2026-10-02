#!/usr/bin/env python3
"""Exact main C reconstruction from immutable v10.5 to v10.6; header changes separately SHA-manifest-pinned."""
from pathlib import Path
import hashlib,subprocess,sys
r=Path(__file__).resolve().parents[1]
c=r/'LOST_COSMOS_V10_SOURCE/lost_cosmos_v5.c'
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=(r/'tools/engine_v10_5_source.sha256').read_text().strip()
new=(r/'tools/engine_v10_6_source.sha256').read_text().split()[0]
if h(c)==new:print('PASS already exact V10.6 '+new);sys.exit(0)
if h(c)!=old:sys.exit('FAIL CLOSED: input is not frozen exact V10.5')
p=subprocess.run(['patch','--batch','--fuzz=0',str(c)],input=(r/'tools/engine_v10_5_to_v10_6.diff').read_bytes(),stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
if p.returncode:sys.exit('FAIL CLOSED patch failed: '+p.stdout.decode())
if h(c)!=new:sys.exit('FAIL CLOSED: reconstructed V10.6 SHA mismatch')
print('PASS exact V10.5 -> V10.6 native engine C SHA '+new)
