#!/usr/bin/env python3
"""Fail-closed exact-source progression patch, never targets prior game binary/saves."""
from pathlib import Path
import hashlib,subprocess,sys
r=Path(__file__).resolve().parents[1]
c=r/'LOST_COSMOS_V10_SOURCE/lost_cosmos_v5.c'
old='79d00898a284b33282695c880d7de46988f99a3c38d2ab83c14c9125253f3ac7'
new=(r/'tools/engine_v10_4_source.sha256').read_text().strip()
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
if h(c)==new:print('V10.4 exact target already exists; nothing modified');sys.exit(0)
if h(c)!=old:sys.exit('FAIL CLOSED: refusing to patch source not matching frozen V10.3')
p=subprocess.run(['patch','--batch','--fuzz=0',str(c)],input=(r/'tools/engine_v10_3_to_v10_4.diff').read_bytes(),stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
if p.returncode:sys.exit('FAIL CLOSED: unified source diff rejected: '+p.stdout.decode())
if h(c)!=new:sys.exit('FAIL CLOSED: patched source hash mismatch')
print('PASS: reproduced pinned V10.4 native engine exact SHA',new)
