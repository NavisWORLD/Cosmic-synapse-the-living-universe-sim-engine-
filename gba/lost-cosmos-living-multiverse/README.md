# Lost COSMOS — The Living Multiverse

Original Eridoria game and COSMOS world by Cory Davis / NavisWORLD.

This branch contains the **actual editable native Game Boy Advance C game** built from the author's existing V10.7 source lineage. Current ERL8 development candidate adds original indexed native visual assets, 24 connected story chapter rooms, actual local encounters and Guardian interactions, versioned independent SRAM quest state, controller-driven ending credits and recovery-safe save journaling. It does **not** contain the author's private manuscript, private author-review matrix or personal Beast Box user data.

## Actual native build and validation

```sh
cd LOST_COSMOS_V10_SOURCE
bash build_v5.sh
cd ..
python3 tests/test_end_credits_v10_8.py
python3 tests/test_story_completion_native.py
```

The GitHub Actions workflow compiles the real freestanding ARM7TDMI ROM, verifies two identical builds, verifies native C save and credits tests, then tests the ROM through genuine libmGBA controller inputs, real audiovisual capture, battery save, and two cold boots. The deterministic editable source ZIP and ROM are produced as versioned CI artifacts along with their checksums. Source-C simulated MMIO tests are **not** equivalent to an independent emulator playthrough.

## Release acceptance

The author-supplied book remains private. Deeper manuscript-by-manuscript narrative acceptance, actual fresh-player end-to-end gameplay of all three ending choices, real user-origin BCP1 importer tests, backed-up old real-user SRAM migration, and independent Delta-on-iPhone validation remain outstanding until genuine evidence is recorded. Maintain PR #19 as draft; no 'complete game' marketing or unapproved source merge.

Keep previous V10–V10.7 release snapshots intact in the author's original versioned archives. The current game uses distinct cartridge code ERL8 and must not silently overwrite older saves.
