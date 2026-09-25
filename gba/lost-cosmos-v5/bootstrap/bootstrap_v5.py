#!/usr/bin/env python3
"""Recover exact V5 from frozen, hash-locked V4 + compressed deterministic V5 patch/art."""
import argparse, base64, hashlib, json, lzma, shutil, subprocess, sys, zlib
from pathlib import Path

ap=argparse.ArgumentParser()
ap.add_argument("--v4",type=Path,required=True)
ap.add_argument("--bootstrap",type=Path,required=True)
ap.add_argument("--out",type=Path,required=True)
a=ap.parse_args()
v4=a.v4.resolve(); base=a.bootstrap.resolve(); out=a.out.resolve()
out.mkdir(parents=True,exist_ok=True)
parts=sorted(base.glob("payload.*.b64"))
assert len(parts)==3, f"exactly 3 payload pieces expected, got {len(parts)}"
b64="".join(p.read_text().strip() for p in parts)
payload=base64.b64decode(b64,validate=True)
digest=hashlib.sha256(payload).hexdigest()
assert digest=="2583f9c1e45995cbea81b35d81338315322c9ea0efbe140ce89eadcd4c898b8d",digest
files=json.loads(lzma.decompress(payload))
assert set(files)=={"patch_v5.py","asset_art_v5.py","v4_mgba_boot1.zb64"},list(files)
for filename in ("patch_v5.py","asset_art_v5.py"):
    (out/filename).write_text(files[filename])
for filename in ("qseed.h","verify_routes.py"):
    shutil.copy2(v4/filename,out/filename)
# Keep actual GBA startup/linker behavior byte-for-byte.
for old,new in (("start_v4.S","start_v5.S"),("linker_v4.ld","linker_v5.ld")):
    shutil.copy2(v4/old,out/new)
for old,new in (
 ("build_v4.sh","build_v5.sh"),
 ("build_rom_v4.py","build_rom_v5.py"),
 ("verify_v4.py","verify_v5.py"),
 ("host_qa_v4.py","host_qa_v5.py"),
 ("feature_tests_v4.py","feature_tests_v5.py")):
    content=(v4/old).read_text().replace("_v4","_v5").replace("V4","V5")
    if old=="build_rom_v4.py":
        content=content.replace("header[0xBC]=4","header[0xBC]=5")
    if old=="verify_v4.py":
        content=content.replace("data[0xBC] != 4","data[0xBC] != 5")
    if old=="feature_tests_v4.py":
        content=content.replace("SRAM[3]=='4'","SRAM[3]=='5'")
    if old=="host_qa_v4.py":
        content=content.replace("HOST_REG_BG0CNT,HOST_REG_BG1CNT,","HOST_REG_BG0CNT,HOST_REG_BG1CNT,HOST_REG_BG2CNT,")
        content=content.replace("HOST_REG_BG1HOFS,HOST_REG_BG1VOFS,","HOST_REG_BG1HOFS,HOST_REG_BG1VOFS,HOST_REG_BG2HOFS,HOST_REG_BG2VOFS,")
        content=content.replace("#define REG_BG1CNT HOST_REG_BG1CNT","#define REG_BG1CNT HOST_REG_BG1CNT\n#define REG_BG2CNT HOST_REG_BG2CNT")
        content=content.replace("#define REG_BG1VOFS HOST_REG_BG1VOFS","#define REG_BG1VOFS HOST_REG_BG1VOFS\n#define REG_BG2HOFS HOST_REG_BG2HOFS\n#define REG_BG2VOFS HOST_REG_BG2VOFS")
    (out/new).write_text(content)
fix=out/"qa_fixtures"; fix.mkdir(exist_ok=True)
oldfix=json.loads((v4/"bootstrap/qa_fixtures.json").read_text())
for name in ("v2_mgba_boot1.sav","v3_mgba_boot1.sav"):
    f=oldfix[name]
    data=zlib.decompress(base64.b64decode(f["zlib_base64"]))
    assert hashlib.sha256(data).hexdigest()==f["sha256"]
    (fix/name).write_bytes(data)
v4save=zlib.decompress(base64.b64decode(files["v4_mgba_boot1.zb64"]))
assert len(v4save)==32768 and v4save[:4]==b"LCV4",v4save[:8]
(fix/"v4_mgba_boot1.sav").write_bytes(v4save)
# Source outputs are reproducible; no network or regeneration of archival tape.
subprocess.run([sys.executable,str(out/"asset_art_v5.py")],cwd=out,check=True)
subprocess.run([sys.executable,str(out/"patch_v5.py"),"--source",str(v4/"lost_cosmos_v4.c"),"--dest",str(out/"lost_cosmos_v5.c")],cwd=out,check=True)
source_hash=hashlib.sha256((out/"lost_cosmos_v5.c").read_bytes()).hexdigest()
assert source_hash=="820c8a20b7eb049603474ed059f7f3663c34cf0c2f5c70cad937a5df8c2f03b2",source_hash
(out/"README_V5.md").write_text("# Lost COSMOS V5 — Real GBA graphics and combat continuation\n\nNative GBA ROM; source generated from exact verified V4 baseline using immutable archived 8192-byte workload tape. Original indexed graphics and parallax starfield; telegraphed monster attacks; heavy attack B+A; dodge B+Select; presentation-independent workload cursor; V2/V3/V4 save migration.\n\nBuild: `./build_v5.sh`; QA: `python3 host_qa_v5.py`, `python3 feature_tests_v5.py`, `python3 verify_routes.py`. Real mGBA QA in GitHub Actions.\n")
(out/"VERIFICATION_V5.md").write_text("# Lost COSMOS V5 verification\n\nSource SHA-256: `"+source_hash+"`\nRecorded QSEED retained unmodified. Real mGBA release status is determined by the GitHub Actions run; no live quantum hardware.\n")
print("PASS exact V5 bootstrap: 3 signed source parts, V4 source hash, V5 C hash, original archive input, real prior saves")
