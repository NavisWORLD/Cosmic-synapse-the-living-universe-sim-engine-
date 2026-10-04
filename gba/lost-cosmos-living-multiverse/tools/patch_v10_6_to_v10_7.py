#!/usr/bin/env python3
"""Fail-closed exact original frozen V10.6 -> new V10.7 native engine patch."""
from pathlib import Path
import hashlib,subprocess,sys
r=Path(__file__).resolve().parents[1]; c=r/'LOST_COSMOS_V10_SOURCE/lost_cosmos_v5.c'
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=(r/'tools/engine_v10_6_source.sha256').read_text().split()[0]
new=(r/'tools/engine_v10_7_source.sha256').read_text().split()[0]
if h(c)==new:print('PASS already exact V10.7 '+new);sys.exit(0)
if h(c)!=old:sys.exit('FAIL CLOSED: input does not match immutable exact V10.6 C source')
p=subprocess.run(['patch','--batch','--fuzz=0',str(c)],input=(r/'tools/engine_v10_6_to_v10_7.diff').read_bytes(),stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
if p.returncode:sys.exit('FAIL CLOSED: '+p.stdout.decode())
if h(c)!=new:sys.exit('FAIL CLOSED: rebuilt C does not match pinned source checksum')
print('PASS exact V10.6 -> V10.7 native engine C SHA '+new)
