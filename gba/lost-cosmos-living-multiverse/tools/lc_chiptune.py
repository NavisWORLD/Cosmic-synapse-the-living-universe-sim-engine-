#!/usr/bin/env python3
"""Compile the original Lost Cosmos chiptune score into lc_music_data.h.

Every melody below was written for this cartridge. Nothing is transcribed.
Notation: NOTE:TICKS separated by spaces, 'r' is a rest, '|' is a bar line.
Drums: k kick, s snare, h hat, c crash. One tick = track tempo in frames.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'LOST_COSMOS_V10_SOURCE' / 'lc_music_data.h'
NAMES = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
DRUMS = {'r': 0, 'k': 1, 's': 2, 'h': 3, 'c': 4}
TABLE = 84  # note byte 1 = C2 (MIDI 36)


def midi(tok):
    n = NAMES[tok[0]]
    i = 1
    while tok[i] in '#b':
        n += 1 if tok[i] == '#' else -1
        i += 1
    return n + 12 * (int(tok[i:]) + 1)


def stream(text, drums=False, wave=False, loop=True):
    out = []
    for tok in text.replace('|', ' ').split():
        name, ticks = tok.split(':')
        ticks = int(ticks)
        assert 0 < ticks < 256, tok
        if drums:
            code = DRUMS[name]
        elif name == 'r':
            code = 0
        else:
            code = midi(name) - 35
            assert 1 <= code <= TABLE - (12 if wave else 0), tok
        out += [code, ticks]
    out += [0xFE if loop else 0xFF, 0]
    return out


def ticks(text):
    return sum(int(t.split(':')[1]) for t in text.replace('|', ' ').split())


# --- Title: "Lattice Dawn" (D major, unhurried arpeggios) ---
TITLE_LEAD = """
D5:2 A4:2 F#5:2 A4:2 E5:4 D5:2 B4:2 | A4:4 F#4:2 A4:2 B4:6 r:2 |
G4:2 B4:2 D5:2 G5:2 F#5:4 E5:2 D5:2 | E5:6 C#5:2 A4:6 r:2 |
D5:2 F#5:2 A5:2 F#5:2 G5:4 F#5:2 E5:2 | D5:4 B4:2 D5:2 E5:6 r:2 |
B4:2 D5:2 G5:2 B5:2 A5:4 G5:2 F#5:2 | E5:4 C#5:2 E5:2 D5:8 |"""
TITLE_BASS = """
D3:4 A3:4 D3:4 A3:4 | B2:4 F#3:4 B2:4 F#3:4 | G2:4 D3:4 G2:4 D3:4 | A2:4 E3:4 A2:4 C#3:4 |
D3:4 A3:4 D3:4 A3:4 | B2:4 F#3:4 B2:4 F#3:4 | G2:4 D3:4 G2:4 B2:4 | A2:4 E3:4 D3:8 |"""
TITLE_DRUM = " ".join(["k:4 h:4 s:4 h:4"] * 7 + ["k:4 h:4 s:2 s:2 c:4"])

# --- Overworld: "Synapse Road" (G major, walking pace) ---
OVER_LEAD = """
G4:2 B4:2 D5:3 B4:1 C5:2 E5:2 D5:4 | B4:2 G4:2 A4:2 B4:2 A4:6 r:2 |
G4:2 B4:2 D5:3 G5:1 F#5:2 E5:2 D5:4 | C5:2 B4:2 A4:2 F#4:2 G4:6 r:2 |
E5:2 D5:2 C5:2 E5:2 D5:2 B4:2 G4:4 | C5:2 B4:2 A4:2 C5:2 B4:4 D5:4 |
E5:2 F#5:2 G5:3 E5:1 D5:2 B4:2 C5:2 A4:2 | B4:2 A4:2 F#4:2 A4:2 G4:8 |"""
def bounce(r, f, o):
    return f"{r}:2 {r}:2 {f}:2 {r}:2 {o}:2 {r}:2 {f}:2 {r}:2"
OVER_BASS = " | ".join([
    bounce('G2', 'D3', 'G3'), bounce('D3', 'A3', 'D3'), bounce('G2', 'D3', 'G3'), "C3:2 C3:2 G3:2 C3:2 D3:2 D3:2 A2:2 D3:2",
    bounce('C3', 'G3', 'C3'), bounce('G2', 'D3', 'G3'), "C3:2 C3:2 G3:2 C3:2 D3:2 D3:2 A3:2 D3:2", "D3:2 D3:2 A2:2 D3:2 G2:8"])
OVER_DRUM = " ".join(["k:2 h:2 s:2 h:2 k:2 h:2 s:2 h:2"] * 7 + ["k:2 h:2 s:2 h:2 k:2 k:2 s:2 s:2"])

# --- Battle: "Spark Clash" (E minor, driving) ---
BATTLE_LEAD = """
E5:1 r:1 E5:1 r:1 G5:2 E5:2 B4:2 D5:2 E5:4 | E5:1 r:1 E5:1 r:1 A5:2 G5:2 F#5:2 D5:2 E5:4 |
C5:2 E5:2 G5:2 C6:2 B5:2 G5:2 E5:4 | D5:2 F#5:2 A5:2 D6:2 C6:2 A5:2 B5:4 |
E5:1 r:1 E5:1 r:1 G5:2 E5:2 B4:2 D5:2 E5:4 | E5:1 r:1 E5:1 r:1 A5:2 G5:2 F#5:2 D5:2 E5:4 |
G5:2 F#5:2 E5:2 D5:2 C5:2 B4:2 A4:2 B4:2 | E5:4 B4:2 E5:2 G5:2 F#5:2 E5:4 |"""
def pump(lo, hi, n=4):
    return " ".join([f"{lo}:2 {hi}:2"] * n)
BATTLE_BASS = " | ".join([pump('E2', 'E3'), pump('E2', 'E3'), pump('C3', 'C4'), pump('D3', 'D4'),
    pump('E2', 'E3'), pump('E2', 'E3'), pump('C3', 'C4', 2) + " " + pump('B2', 'B3', 2), pump('E2', 'E3')])
BATTLE_DRUM = " ".join(["k:2 h:2 s:2 h:2 k:1 k:1 h:2 s:2 h:2"] * 7 + ["k:2 s:2 k:2 s:2 k:1 k:1 s:2 s:2 c:2"])

# --- Lys rival: "Skyspark Rival" (A minor with a raised seventh) ---
RIVAL_LEAD = """
A4:3 C5:3 E5:2 D5:3 C5:3 B4:2 | A4:2 G4:2 A4:2 C5:2 D5:6 r:2 |
F5:3 E5:3 D5:2 E5:3 C5:3 A4:2 | B4:2 C5:2 D5:2 E5:2 G#4:6 r:2 |
A5:3 G5:3 E5:2 F5:3 E5:3 D5:2 | C5:2 D5:2 E5:2 G5:2 A5:6 r:2 |
F5:2 E5:2 D5:2 C5:2 B4:2 C5:2 D5:2 B4:2 | A4:4 E4:2 A4:2 C5:2 B4:2 A4:4 |"""
RIVAL_BASS = " | ".join([pump('A2', 'A3'), pump('F2', 'F3', 2) + " " + pump('G2', 'G3', 2), pump('D3', 'D4'),
    pump('E2', 'E3'), pump('A2', 'A3'), pump('F2', 'F3', 2) + " " + pump('G2', 'G3', 2),
    pump('D3', 'D4', 2) + " " + pump('E2', 'E3', 2), pump('A2', 'A3')])
RIVAL_DRUM = " ".join(["k:3 k:3 s:2 k:2 h:2 s:4"] * 7 + ["k:3 k:3 s:2 s:2 s:2 c:4"])

# --- Victory jingle: "Signal Kept" (plays once) ---
WIN_LEAD = "C5:2 E5:2 G5:2 C6:6 r:2 A5:2 B5:2 C6:2 D6:2 E6:10"
WIN_BASS = "C3:6 r:2 G3:6 r:2 F3:4 G3:4 C3:8"
WIN_DRUM = "k:2 k:2 s:4 r:4 k:2 s:2 k:4 k:4 c:8"

# --- The Quiet: "Held Breath" (D dorian, slow, no drums) ---
QUIET_LEAD = """
D5:6 F5:2 E5:8 | C5:6 A4:2 G4:8 | A4:6 C5:2 D5:4 E5:4 | F5:12 r:4 |
G5:6 F5:2 E5:4 D5:4 | C5:6 E5:2 D5:8 | A4:4 G4:4 F4:4 E4:4 | D4:12 r:4 |"""
QUIET_BASS = "D3:16 C3:16 F3:16 A#2:16 G2:16 C3:16 A2:16 D3:16"
QUIET_DRUM = "r:128"

# name, lead, bass, drum, tempo (frames per tick), duty, envelope step, bass volume code, loop
TRACKS = [
    ('TITLE', TITLE_LEAD, TITLE_BASS, TITLE_DRUM, 7, 2, 3, 2, True),
    ('OVERWORLD', OVER_LEAD, OVER_BASS, OVER_DRUM, 7, 2, 2, 2, True),
    ('BATTLE', BATTLE_LEAD, BATTLE_BASS, BATTLE_DRUM, 5, 1, 2, 1, True),
    ('RIVAL', RIVAL_LEAD, RIVAL_BASS, RIVAL_DRUM, 5, 0, 2, 1, True),
    ('VICTORY', WIN_LEAD, WIN_BASS, WIN_DRUM, 5, 2, 3, 1, False),
    ('QUIET', QUIET_LEAD, QUIET_BASS, QUIET_DRUM, 10, 2, 0, 3, True),
]


def carray(name, data):
    body = ",".join(str(v) for v in data)
    return f"static const u8 {name}[{len(data)}]={{{body}}};\n"


def main():
    lines = ["/* Generated by tools/lc_chiptune.py. Original Lost Cosmos score. Do not edit. */\n"]
    freqs = []
    for code in range(TABLE + 1):
        if code == 0:
            freqs.append(0)
            continue
        hz = 440.0 * 2 ** ((code + 35 - 69) / 12)
        freqs.append(max(0, min(2047, round(2048 - 131072 / hz))))
    lines.append(f"static const u16 LC_NOTE_RATE[{len(freqs)}]={{{','.join(map(str, freqs))}}};\n")
    for i, (name, lead, bass, drum, tempo, duty, env, bvol, loop) in enumerate(TRACKS):
        n = ticks(lead)
        assert ticks(bass) == n and ticks(drum) == n, (name, n, ticks(bass), ticks(drum))
        lines.append(carray(f"LC_{name}_LEAD", stream(lead, loop=loop)))
        lines.append(carray(f"LC_{name}_BASS", stream(bass, wave=True, loop=loop)))
        lines.append(carray(f"LC_{name}_DRUM", stream(drum, drums=True, loop=loop)))
    lines.append("static const LcTrack LC_TRACKS[%d]={\n" % len(TRACKS))
    for name, lead, bass, drum, tempo, duty, env, bvol, loop in TRACKS:
        lines.append(f" {{LC_{name}_LEAD,LC_{name}_BASS,LC_{name}_DRUM,{tempo},{duty},{env},{bvol}}},\n")
    lines.append("};\n")
    for i, t in enumerate(TRACKS):
        lines.append(f"#define LC_SONG_{t[0]} {i}\n")
    OUT.write_text("".join(lines))
    print(f"wrote {OUT.relative_to(ROOT)}: {len(TRACKS)} tracks")


if __name__ == '__main__':
    main()
