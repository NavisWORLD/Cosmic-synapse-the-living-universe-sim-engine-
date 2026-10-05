# Spark Gate — Sol's native companion bridge

Open `arcade/sol-spark-gate/`. Grok's current Spark page is embedded unchanged,
alongside the existing handheld. “Send to handheld” patches its verified 32 KB
save with the actual three Spark sprites. You can also upload a current Vercel
Spark `.qbeast`; its public recorded-run card must reproduce the exact genome.
The existing QBEAST validator and cage ledger own admission and identity.

In the game: START → PARTY → your companion → CHAT. D-pad selects letters,
A adds, L erases, SELECT sends, B returns. Replies describe real game goals,
evolution, training, rest and saves. They are local authored game dialogue.
The seeded GBA chirps honor SYSTEM → AUDIO. They are chip sounds, not browser
speech. Grok's browser voices, live motion, wild encounters, gallery and clips
remain in the original Spark page.

The unmodified Spark renderer supplies 64px art. Deterministic RGB5 quantization
reduces it to 32px, 4bpp tiles with 15 opaque colors. SPK1 stores the two later
forms, blink regions, gait, tempo, and quantized voice properties. The native
roster selects stages at the existing earned gates, independently of web XP.
Art refreshes change only RAM/VRAM. The original public profile, stats, seed,
growth record, journal pages and manual slots remain authoritative.

## SRAM contract

| Bytes | Record | Owner |
|---|---|---|
| 0–24575 | main page and two journal banks | existing game |
| 24576–24703 | journal metadata | existing game |
| 24704–24831 | SPK1 metadata, second/third palettes | Sol adapter |
| 24832–25475 | LCX1 profile and first-form art | existing mailbox |
| 25476–25539 | LCG1 growth | existing cage |
| 25600–31743 | three manual slots | existing game |
| 31744–32767 | second/third 512-byte tile sets | Sol adapter |

SPK1 version 1 has 128 metadata bytes. Identity, native seed and BCP1 checksum
are bound to LCX1. CRC32 covers metadata with its checksum field zeroed, the
1024-byte tail and the first-form 544-byte palette/art. It excludes the LCX1
ready/consumed flags, which the game legitimately changes. Unknown versions,
invalid palettes, bounds or CRC fall back to supplied first-form LCX1 art.
Old ROMs ignore the extension and still show the supplied first form.

Upload your own matching battery save to refresh the art while preserving
every other journey byte. Keep the public art receipt and `.sav` together.
The extension supports the active mailbox identity; it does not claim a full
native sprite atlas for every creature retained in the browser ledger.

Recorded IBM count distributions are historical game seeds. There is no live
quantum link, consciousness claim, health interpretation or GBA model inference.

## Verification

`node --test arcade/sol-spark-gate/*.test.mjs` checks deterministic shapes,
all eight islands, receipt corruption and journey byte preservation.
`tests/test_sol_spark_native.py` checks actual native import/evolution, cache
reload, blink/gait, identity isolation, bounded typing and audio controls with
simulated MMIO. `tests/test_mgba_sol_spark.py` runs the real ROM with controller
input, verifies visible art and chat, captures native audio/video, exports a
battery save and verifies cold boot. No emulator memory writes or savestates.
