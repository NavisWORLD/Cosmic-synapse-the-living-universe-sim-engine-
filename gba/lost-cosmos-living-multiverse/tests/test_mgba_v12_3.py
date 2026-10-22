#!/usr/bin/env python3
"""V12.3 on the real cartridge in mGBA, controller only (memory is only READ, never written).

A starter save gets a V12.2-format Living World block written into the .sav file before boot
(layout byte 0, old item ids: moon_berry, star_candy, star_shard, twin_pistol equipped). The
cartridge must migrate it (glowcap, star_shard merged, fiddle_bow equipped) and save layout 1.
Then: CAST shows 5 Mote forms incl. Shading + stand-in bible characters, QUESTS shows biomes,
SELECT opens Acts II-V scene dialogue, and all four boss battles (Forest Guardian, Grumbleback v2.1,
Moth Swarm, Guardian Statues lane fight) are played to the end through the controller while the
cartridge streams 2 KB boss frames by DMA. Screenshots + contact sheet are written to --out."""
from __future__ import annotations
import argparse, json, shutil, struct, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / "tools")); sys.path.insert(0, str(ROOT))
from mgba import Mgba, sha256
import test_mgba_beast_home as bh
from test_mgba_menu_visual import goto_index

LW = 7936
OLD = json.load(open(ROOT.parent / "LOST_COSMOS_V10_SOURCE/tools_v12/v12_2_items/items_v12_2.json"))
NEW = json.load(open(ROOT.parent / "LOST_COSMOS_V10_SOURCE/v12_assets/text/items.json"))
oi = {it["id"]: i for i, it in enumerate(OLD)}; ni = {it["id"]: i for i, it in enumerate(NEW)}

def lw_sum(b):
    s = 0x4C573132
    for x in b[:252]: s = (s * 31 + x) & 0xFFFFFFFF
    return s

def write_v12_2_block(sav: Path):
    d = bytearray(sav.read_bytes()); blk = bytearray(256)
    blk[0:3] = b"LW\x01"; blk[3] = 0; blk[4] = 0
    for k, n in (("moon_berry", 5), ("star_candy", 2), ("star_shard", 1), ("healing_herbs", 3), ("last_map", 1)):
        blk[8 + oi[k]] = n
    for i in range(6):
        o = 76 + i * 12; blk[o:o + 6] = bytes([40, 70, 60, 30, 50, 1])
    blk[76 + 8] = oi["twin_pistol"] + 1
    blk[252:256] = struct.pack("<I", lw_sum(blk)); d[LW:LW + 256] = blk; sav.write_bytes(bytes(d))

OLD_ROM = Path("/home/box/backups/lost_cosmos/v12_2b/lost_cosmos_v12_2b.gba"); OLD_ELF = Path("/home/box/backups/lost_cosmos/v12_2b/lost_cosmos_v5.elf")
def open_lw(emu):
    emu.tap("START", hold=8, release=8)
    bh.wait(emu, lambda: emu.read_symbol("game_mode") == 2, "pause", 120, 2)
    goto_index(emu, 9); emu.tap("A", hold=8, release=8)
    bh.wait(emu, lambda: emu.read_symbol("pause_page") == 9, "SYSTEM", 120, 2)
    tap(emu, "DOWN", 7); emu.tap("A", hold=8, release=8); emu.step((), 20); tap(emu, "A"); emu.step((), 30)

import zlib
def seal_lw_into_journal(src: Path, dst: Path):
    d = bytearray(src.read_bytes()); M = 24576
    def valid(b):
        m = M + b * 64
        return d[m:m + 4] == b"LCJ8" and d[m + 15] == 0xA8 and struct.unpack("<I", d[m + 8:m + 12])[0] == zlib.crc32(bytes(d[(b + 1) * 8192:(b + 2) * 8192]))
    a, b = valid(0), valid(1)
    if not (a or b): raise RuntimeError("no valid journal bank")
    bank = 1 if (b and (not a or ((struct.unpack("<I", d[M + 68:M + 72])[0] - struct.unpack("<I", d[M + 4:M + 8])[0]) & 0xFFFFFFFF) - 1 < 0x7FFFFFFF)) else 0
    base = (bank + 1) * 8192; d[base + LW:base + LW + 256] = d[LW:LW + 256]
    d[M + bank * 64 + 8:M + bank * 64 + 12] = struct.pack("<I", zlib.crc32(bytes(d[base:base + 8192])))
    dst.write_bytes(bytes(d))

def tap(emu, k, n=1):
    for _ in range(n): emu.tap(k, hold=8, release=8); emu.step((), 4)

BT = dict(kind=0, state=1, phase=2, nphases=3, hp=4, zhp=5, anim=6, afr=7, hit_ok=11, lane=12, swing=13, sweeps=14, mask=15)
def bt(emu):
    r = {k: emu.read_symbol("lw_bt", width=1, offset=o) for k, o in BT.items()}
    r["tick"] = emu.read_symbol("lw_bt", width=2, offset=16); r["frame"] = emu.read_symbol("lw_bt", width=2, offset=20)
    return r

def run(rom, elf, out):
    out.mkdir(parents=True, exist_ok=True)
    rep = dict(suite="real_mgba_v12_3", rom_sha256=sha256(rom), controller_only=True, memory_writes=False, shots=[])
    bh.starter_save(out / "starter_src.sav"); sav = out / "v123.sav"; shutil.copyfile(out / "starter_src.sav", sav)
    def shot(emu, name):
        p = out / name; emu.screenshot(p); rep["shots"].append(str(p))
    # A genuine V12.2b save: the V12.2b cartridge opens the Living World and uses one healing herb
    # (3 -> 2), so the block it saves has layout byte 0 and V12.2 item ids.
    with Mgba(OLD_ROM, elf=OLD_ELF, save_path=sav, trace_path=out / "v122_inputs.jsonl") as emu:
        bh.new_game(emu, "v122"); emu.step((), 30); open_lw(emu)
        tap(emu, "START"); emu.step((), 5); tap(emu, "A"); emu.step((), 10)
        tap(emu, "B"); emu.step((), 10); tap(emu, "B"); emu.step((), 30)
        emu.export_save(out / "v12_2b_made.sav")
    # V12.2b never journaled its LW block (the bug V12.3 fixes), so a cold boot would restore the
    # page without it. Stand in for the player's next V12.2b game save: seal the LW tail into the
    # latest journal bank exactly as save_journal.h's commit would (file-level, before boot).
    seal_lw_into_journal(out / "v12_2b_made.sav", sav)
    old = sav.read_bytes()[LW:LW + 256]
    rep["v12_2b_block"] = dict(layout=old[3], healing=old[8 + oi["healing_herbs"]], moon_berry=old[8 + oi["moon_berry"]], star_candy=old[8 + oi["star_candy"]])
    if old[0:3] != b"LW\x01" or old[3] != 0: raise RuntimeError(f"V12.2b did not write a layout-0 LW block {rep['v12_2b_block']}")
    with Mgba(rom, elf=elf, save_path=sav, trace_path=out / "v123_inputs2.jsonl") as emu:
        bh.continue_game(emu, "v123b")
        emu.step((), 30); open_lw(emu)
        if not emu.read_symbol("lw_active", width=1): raise RuntimeError("living world did not open")
        rep["items_migrated"] = emu.read_symbol("lw_items_migrated", width=1)
        shot(emu, "v123_00_forest.png")
        emu.step((), 900)
        rep["synapse_lines"] = dict(hits=emu.read_symbol("lw_synapse_hits", width=2), swaps=emu.read_symbol("lw_synapse_swaps", width=2))
        tap(emu, "START"); emu.step((), 5); shot(emu, "v123_01_items_migrated.png")
        tap(emu, "START"); tap(emu, "START"); emu.step((), 5)
        if emu.read_symbol("lw_page", width=1) != 3: raise RuntimeError("QUESTS page not open")
        shot(emu, "v123_02_quests_biome.png")
        rep["quest_rows"] = [bh.ui_row(emu, r) for r in (16, 17, 18)]
        results = {}
        for sel, name in ((2, "forest_guardian"), (3, "grumbleback"), (4, "moth_swarm"), (5, "guardian_statues")):
            while emu.read_symbol("lw_sel", width=1) != sel: tap(emu, "DOWN")
            emu.step((), 4); shot(emu, f"v123_10_quest_{name}.png")
            d0 = emu.read_symbol("lw_bt_dma_frames", width=2)
            tap(emu, "A"); emu.step((), 2)
            if not emu.read_symbol("lw_bt_active", width=1): raise RuntimeError(f"{name}: battle did not start")
            seen_phase = set(); shots_taken = 0; f = 0
            while f < 5000:
                b = bt(emu)
                if b["state"] in (5, 6): break
                keys = ()
                if name == "guardian_statues":
                    if b["state"] == 4 and (b["mask"] >> b["lane"]) & 1:
                        safe = [k for k in range(3) if not (b["mask"] >> k) & 1]
                        keys = ("LEFT",) if safe and safe[0] < b["lane"] else ("RIGHT",)
                else:
                    if b["state"] == 1 and b["afr"] == 1 and b["tick"] == 0: keys = ("RIGHT",)
                    elif b["hit_ok"] == 1: keys = ("A",)
                emu.step(keys, 1); emu.step((), 1); f += 2
                if (b["phase"], b["state"]) not in seen_phase and shots_taken < 6:
                    seen_phase.add((b["phase"], b["state"])); emu.step((), 1); f += 1
                    shot(emu, f"v123_2{list(results).__len__()}_{name}_p{b['phase']+1}_s{b['state']}.png"); shots_taken += 1
            b = bt(emu); emu.step((), 6); shot(emu, f"v123_3{len(results)}_{name}_result.png")
            res = dict(won=b["state"] == 5, zhp=b["zhp"], phases=b["phase"], frames=f, dma_frames=emu.read_symbol("lw_bt_dma_frames", width=2) - d0,
                       pal_slot=9 + b["kind"], pal=[emu.read16(0x05000200 + (9 + b["kind"]) * 32 + 2 * i) for i in range(16)])
            results[name] = res
            if not res["won"]: raise RuntimeError(f"{name}: controller play did not win {res}")
            if res["dma_frames"] < 40: raise RuntimeError(f"{name}: too few streamed frames {res}")
            tap(emu, "A"); emu.step((), 6)
            if emu.read_symbol("lw_bt_active", width=1) or emu.read_symbol("lw_page", width=1) != 3: raise RuntimeError(f"{name}: did not return to QUESTS")
        rep["battles"] = results
        if results["grumbleback"]["pal"][14] != ((72 >> 3) | ((40 >> 3) << 5) | ((104 >> 3) << 10)):
            raise RuntimeError(f"Grumbleback palette index 14 is not violet {results['grumbleback']['pal']}")
        # Acts II-V scene dialogue (q3_11 = row 10)
        while emu.read_symbol("lw_sel", width=1) != 10: tap(emu, "DOWN")
        tap(emu, "SELECT"); emu.step((), 4)
        if emu.read_symbol("lw_page", width=1) != 5: raise RuntimeError("SELECT did not open the scene reader")
        shot(emu, "v123_40_scene_q3_11_box1.png"); tap(emu, "A"); tap(emu, "A"); emu.step((), 4); shot(emu, "v123_41_scene_q3_11_box3.png")
        rep["scene_rows"] = [bh.ui_row(emu, r) for r in (0, 4, 6, 7, 8)]
        tap(emu, "B"); emu.step((), 4)
        tap(emu, "START"); emu.step((), 5)   # CAST
        tap(emu, "DOWN", 4); emu.step((), 6); shot(emu, "v123_50_cast_mote_shading.png")
        rep["cast_shading"] = dict(form=emu.read_symbol("lw_cast_form", width=1), row=bh.ui_row(emu, 16), name=bh.ui_row(emu, 2))
        if rep["cast_shading"]["form"] != 3 or "3 OF 5" not in rep["cast_shading"]["row"]: raise RuntimeError(f"Shading is not form 3 of 5 {rep['cast_shading']}")
        tap(emu, "DOWN", 16); emu.step((), 6); shot(emu, "v123_51_cast_ravenswood_standin.png")
        rep["cast_standin"] = dict(name=bh.ui_row(emu, 2), row=bh.ui_row(emu, 16))
        tap(emu, "B"); emu.step((), 10); tap(emu, "B"); emu.step((), 30)
        if emu.read_symbol("lw_active", width=1): raise RuntimeError("did not leave the living world")
        exported = emu.export_save(out / "v123_export.sav")
    # V12.3 journal fix: a fresh cold boot keeps the migrated LW block (no V12.2 loss on reboot)
    shutil.copyfile(exported, out / "v123_reboot.sav")
    with Mgba(rom, elf=elf, save_path=out / "v123_reboot.sav", trace_path=out / "v123_inputs3.jsonl") as emu:
        bh.continue_game(emu, "v123c"); emu.step((), 30); open_lw(emu)
        rep["reboot"] = dict(items_migrated=emu.read_symbol("lw_items_migrated", width=1), healing=emu.read_symbol("lw_inv", width=1, offset=ni["healing_herbs"]),
                             patches=emu.read_symbol("lw_journal_patches", width=2))
    if rep["reboot"]["healing"] != rep["v12_2b_block"]["healing"] or rep["reboot"]["items_migrated"] != 0:
        raise RuntimeError(f"LW block lost across a cold boot {rep['reboot']}")
    d = exported.read_bytes(); blk = d[LW:LW + 256]
    mig = dict(layout=blk[3], glowcap=blk[8 + ni["glowcap"]], star_shard=blk[8 + ni["star_shard"]], healing=blk[8 + ni["healing_herbs"]],
               zeref_weapon=blk[76 + 8], fiddle_bow_plus1=ni["fiddle_bow"] + 1, checksum_ok=struct.unpack("<I", blk[252:256])[0] == lw_sum(blk))
    rep["migration"] = mig
    if rep["items_migrated"] != 1 or mig["layout"] != 1 or mig["glowcap"] != rep["v12_2b_block"]["moon_berry"] or mig["star_shard"] != rep["v12_2b_block"]["star_candy"] or mig["healing"] != rep["v12_2b_block"]["healing"] or not mig["checksum_ok"]:
        raise RuntimeError(f"V12.2 save not migrated {mig} items_migrated={rep['items_migrated']}")
    rep["passed"] = True
    (out / "v12_3_report.json").write_text(json.dumps(rep, indent=2) + "\n")
    print(json.dumps({k: rep[k] for k in ("suite", "rom_sha256", "migration", "passed")}, indent=2))
    print(json.dumps({k: {kk: v[kk] for kk in ("won", "zhp", "frames", "dma_frames")} for k, v in rep["battles"].items()}))

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--rom", type=Path, default=ROOT.parent / "LOST_COSMOS_V10_SOURCE/LOST_COSMOS_V10_OPENING_QA.gba")
    ap.add_argument("--elf", type=Path, default=ROOT.parent / "LOST_COSMOS_V10_SOURCE/lost_cosmos_v5.elf")
    ap.add_argument("--out", type=Path, default=ROOT.parent / "artifacts/mgba_v12_3")
    a = ap.parse_args(); run(a.rom.resolve(), a.elf.resolve(), a.out.resolve())
