# V11.1 content and visual completion

User spec: Cory Davis / Emeth's 2026-10-03 Content Bible and ten supplied art references.

Preserve the existing story, original world IDs, QSEED, roster identities, combat, and every historical SRAM offset. Content worlds are additional physical regions with new room IDs 70..77, not replacements for the authored campaign.

- [x] Reproduce and fix Eldoria's input starvation inside the save journal. Verify unchanged CRC results, torn-save recovery, and the real shrine controller sequence.
- [x] Encode all 100 items, 100 characters, and 100 skills with stable IDs and explicit art-cell mappings. Generate native 4bpp art from the supplied catalog cells; never use the labeled sheets as gameplay sprites.
- [x] Add additive, checksummed content persistence, inventory/crafting/equipment, learnable abilities and expedition encounters. Keep old campaign balance and the four existing spells intact.
- [x] Use a quiet field HUD, safe 240x160 pages, paginated party profiles/actions and first-class offline Beast Box access. Portraits belong in profiles; followers remain small.
- [x] Add the eight content regions and gated quest/encounter progression using the supplied map references. Never mark undiscovered content as encountered.
- [x] Verify real-controller menus, campaign, new content, old-save migration, native framebuffer captures and reproducible ROM bytes. Package matching source, evidence and a Delta-compatible .gba.

Resolved conflicts: retain the previously accepted 2x5 pause selector as the landing screen; L/R changes tabs within a screen, SELECT opens contextual actions. Beast Box remains directly reachable. Permanent XYZ debug values and double-START release shortcuts stay removed. The original campaigns retain their world names and numeric identities; the new content map uses the Bible's world names. All bridge status is local/offline; no cloud handshake is invented.

Verified final native ROM: ab8e059d52688e9ad351fa6394c9e5fb394634c4c4e379b4149c7446b5f21cc4. The controller route earned eight beacons and ten bosses, crafted the Builder set, evolved/renamed the same imported identity, and loaded three distinct CRC slots after a cold boot. Retained original campaign controller checks passed through Hollow Grove. Public export/import restored the earned identity and stage/level/bond in a fresh isolated native build. Physical Delta and complete original five-act acceptance remain unclaimed.
