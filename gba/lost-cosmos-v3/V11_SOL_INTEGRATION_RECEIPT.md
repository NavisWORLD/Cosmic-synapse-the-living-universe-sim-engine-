# Lost COSMOS V11 — SOL V3 integration receipt

Owner: Cory Davis / NavisWORLD

This V11 enhancement branch intentionally preserves and carries forward the verified **SIM EARTH // THE LOST COSMOS V3: Cosmic RPG** source produced on `feature/pixel-universe-gba-rpg-003`.

## Exact inherited SOL source

The following files on `feature/lost-cosmos-v11-enhanced-001` were compared directly against the finished SOL V3 branch and are byte-identical Git blobs:

- `gba/lost-cosmos-v3/lost_cosmos_v3.c`
  - Git blob: `137feed7f32b3a7623438a3031902abcdc511d1c`
  - Published gameplay C SHA-256: `3d9b4caf42dded4bf2345a9ced987604cb702e325239dfe79999df16ad31e1cd`
- `gba/lost-cosmos-v3/README_V3.md`
  - Git blob: `b64e3feb952bb513890db27683bceadcaf89385d`
- `gba/lost-cosmos-v3/VERIFICATION_V3.md`
  - Git blob: `33b5f58166e2655853a90b68f6c83b61a41a5928`
- `.github/workflows/pixel-universe-gba-v3.yml`
  - Original SOL branch blob before V11 trigger integration: `894b7d3f0130b359218287da924c833bd77150e8`

The V11 branch was created from verified Lost COSMOS V10.8 integration commit
`af2bdfbdc21b671c891ea1fb32973356f5fce31f`. Git history shows the SOL V3 branch is already an ancestor of that integration, so no destructive cherry-pick or duplicate rewrite was necessary.

## Verified SOL V3 gameplay milestone carried forward

- SOL V3 branch: `feature/pixel-universe-gba-rpg-003`
- Verified gameplay/source commit: `906e15b02e0601e3d267fe14554ca4ef3699dd72`
- Verification documentation follow-up: `9ec29f48d3e5030de85a54c7fddf689de221de56`
- Successful native mGBA workflow run: `36098821373`
- Exact CI release ROM SHA-256: `b35be00de7b370be95431ef677c8a4be7bb56f962c538cf8dd50491833607752`
- Save signature: `SRAM_V113`; save magic: `LCV3`
- Frozen 8,192-byte QSEED SHA-256:
  `9bcecc3732fe48107554cc2041cff6088f418290fb850ec0c9b89cdc375f54c8`

Inherited game systems include the six-region scrolling RPG, action combat, enemy drops, XP/level progression, inventory, consumables, equipment, four spells, ten-tab pause interface, ship travel, persistent COSMOS buddy settings, player-controlled Crown endings and postgame.

The V3 verification establishes scripted native mGBA progression and SRAM persistence. It does **not** replace extended human balance/visual review or Delta iPhone acceptance.

## V11 integration action

The V3 native workflow is now configured to run on pushes to both:

- `feature/pixel-universe-gba-rpg-003`
- `feature/lost-cosmos-v11-enhanced-001`

This receipt marks the point where the finished SOL RPG work is explicitly carried into the V11 enhancement line without discarding the later V10.8 source/history.
