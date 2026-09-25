# Lost COSMOS V4 — Test receipt

- Source lineage: V3 SHA-256 `3d9b4caf42dded4bf2345a9ced987604cb702e325239dfe79999df16ad31e1cd`.
- V4 game C SHA-256 `83bdde8e628ada112f172443336628d988ec977b464d0aadb5249d1e0b6805ca`.
- Exact archived 8,192-byte tape SHA-256 `9bcecc3732fe48107554cc2041cff6088f418290fb850ec0c9b89cdc375f54c8`.
- Local build: native freestanding ARM GBA, 65,536-byte ROM; GBA header/logo/checksum/entry, SRAM signature and exact tape presence validated.
- Local gameplay tests: six-region authored route/trigger/guardian checks; two new-process C tests with shared SRAM (A5 then 5A); NPC dialogue/quest/reward/journal features, V2→V4 and V3→V4 real mGBA save-fixture migration passed.
- GitHub development branch: `feature/pixel-universe-gba-visual-npc-004`.
- **Real mGBA V4 emulator verification: PENDING.** Do not label V4 fully verified until a V4 GitHub Actions run succeeds and its exact ROM hash is recorded.

The QA harness exercises scripted native game functions and save state transitions; it cannot establish prolonged human-controlled game feel, high-end graphic quality, unrestricted NPC pathfinding, iPhone Delta compatibility or the underlying archived workload's original scientific provenance. The offline quantum buddy remains a classical deterministic software agent.