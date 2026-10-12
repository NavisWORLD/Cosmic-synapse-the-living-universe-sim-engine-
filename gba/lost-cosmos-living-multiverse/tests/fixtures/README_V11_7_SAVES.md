# V11.7 SRAM fixture (real, not synthesized)

- `v11_7_act1_complete.sav` (sha256 767cc1e846dd8f992383b478387a8d214e46f3d386fb519bd236cd864c3af20a):
  written by the V11.7 source (ACT I THE FIRST HEART, PR #62) in the
  recorded controller-only `test_mgba_act1_heart.py --route restore --reply 0`
  run (local QA build sha256
  f931c33d397fa50e8d2170b0dd91cbb6404d4c1913d5748fecc1cb996816bd2c) in libmGBA.
  Q00-Q09 done, saved after the Act I ending, before LEASH OFF existed:
  SRAM 7296..7815 is erased (0xFF), so there is no LCL1 record.

`tests/test_mgba_leash.py` loads a copy with the current ROM and checks that
the record is created empty (older-save flag set), LEASH is OFF, Act I quest
state is intact and the beast roams.
