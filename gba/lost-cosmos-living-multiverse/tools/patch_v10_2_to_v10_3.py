#!/usr/bin/env python3
"""Explicit 100% pinned native engine patch. Work on fresh V10.2 copy only.
Neither original V10 nor the shipped V10.3 source is modified unless exact input contract holds.
"""
from pathlib import Path
import hashlib,subprocess,sys
root=Path(__file__).resolve().parents[1]; c=root/'LOST_COSMOS_V10_SOURCE/lost_cosmos_v5.c'
old='de5912103418260bbe74c062762571ed88846ce4aa709cc7d959f6db6bac52e1'
new=(root/'tools/engine_v10_3_source.sha256').read_text().strip()
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
if h(c)==new:print('V10.3 target already exact; source left untouched.');sys.exit(0)
if h(c)!=old:sys.exit('FAIL CLOSED: target source is neither exact frozen V10.2 nor final V10.3')
p=subprocess.run(['patch','--batch','--fuzz=0',str(c)],input=(root/'tools/engine_v10_2_to_v10_3.diff').read_bytes(),stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
if p.returncode:sys.exit('FAIL: diff rejected: '+p.stdout.decode())
if h(c)!=new:sys.exit('FAIL CLOSED: patch did not create exact pinned V10.3 output')
print('PASS: pinned V10.2 source -> exact V10.3 target',new)
