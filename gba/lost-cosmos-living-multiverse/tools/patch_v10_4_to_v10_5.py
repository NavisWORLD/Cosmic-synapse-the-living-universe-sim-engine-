#!/usr/bin/env python3
"""Reconstruct exact V10.5 engine from frozen SHA-pinned V10.4 source.
The three NEW G5 .h files and updated atlas geometry/data are separate package
sources; this checks the full main native engine C file, not the entire ROM.
"""
from pathlib import Path
import hashlib,subprocess,sys
r=Path(__file__).resolve().parents[1]
c=r/'LOST_COSMOS_V10_SOURCE/lost_cosmos_v5.c'
old=(r/'tools/engine_v10_4_source.sha256').read_text().strip()
new=(r/'tools/engine_v10_5_source.sha256').read_text().strip()
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
if h(c)==new:print('V10.5 exact target exists; no changes');sys.exit(0)
if h(c)!=old:sys.exit('FAIL CLOSED: source does not match frozen V10.4')
p=subprocess.run(['patch','--batch','--fuzz=0',str(c)],input=(r/'tools/engine_v10_4_to_v10_5.diff').read_bytes(),stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
if p.returncode:sys.exit('FAIL CLOSED: source patch failed: '+p.stdout.decode())
if h(c)!=new:sys.exit('FAIL CLOSED: reconstructed V10.5 source hash does not match pinned target')
print('PASS exact V10.4 -> V10.5 native engine C, SHA',new)
