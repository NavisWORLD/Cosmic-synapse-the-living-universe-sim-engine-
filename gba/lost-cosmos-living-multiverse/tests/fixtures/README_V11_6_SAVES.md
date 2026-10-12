# V11.6 SRAM fixtures (real, not synthesized)

All three were written by the shipped V11.6 source (main 5531862, the commit
that went live on Pages as ROM 4acdc8d5...; local QA build sha256
b57de2af0d174b2034a6e5a6112a9d215ffc93059992e3df1560288995a0e20a) running in
libmGBA with controller input only, before ACT I THE FIRST HEART existed:

- `v11_6_prologue_done.sav` (sha256 667e765143d236b1eb3652e2019b74bb2cfb77754efa93a48d2f7ef9528b47cd):
  the V11.6 `test_mgba_prologue.py --choice 2` run. Q00-Q04 done, Q05 active,
  never entered Oakwood.
- `v11_6_mid_ravenswood.sav` (sha256 6fa2442bf536f11df7ef54881314812fff6eb46163574ae3070f60af37424907):
  NEW GAME, opening skipped, Brindle Elder, Oakwood gate, Lord Ravenswood
  (old route: story_flags ST_TOWN|ST_OAKWOOD = 3), saved in Oakwood.
- `v11_6_old_act1_heart.sav` (sha256 c73a2e9f5aefafc1a708874cce7557720603b915a0e00b566ecd377f50e3ff1b):
  the V11.6 `test_mgba_act1_controller.py` run: old Act I route through the
  rune puzzle, the Malakar duel and the First Heart (story_flags 31), saved in
  the Cragstone temple.

None has the ACT I block (LC11 bytes 728-735 are zero).
`tests/test_mgba_act1_migration.py` loads copies of them with the current ROM.
