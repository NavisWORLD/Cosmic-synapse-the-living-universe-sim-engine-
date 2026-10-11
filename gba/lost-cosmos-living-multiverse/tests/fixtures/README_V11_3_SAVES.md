# V11.3 SRAM fixtures (real, not synthesized)

Both files were written by the shipped V11.3 source (commit 1cf8786,
local build sha256 2ec4644f46ea46db709f039426b818f5cbdc817eef2252371fe8c07720f86451)
running in libmGBA with controller input only:

- `v11_3_opening.sav` (sha256 19264b8e25c52368ab34b99b4963c5751b603f8aa4072267a9cae162eac4d3d1):
  NEW GAME, opening skipped with START, arrived in Brindlemark. No progress.
- `v11_3_elder.sav` (sha256 a3051bd1154d6d08c377e95c9ef2249c01303d4df4a7fd9067e468788740e3d9):
  same, then the Brindle Elder was spoken to (story_flags bit 0, ST_TOWN).

Neither has the campaign block (LC11 bytes 656-679 are zero).
`tests/test_mgba_prologue_migration.py` loads copies of them with the current ROM.
