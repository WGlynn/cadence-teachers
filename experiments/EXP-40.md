# EXP-40: are our brains too small? (brain size x world size)

- Date: 2026-10-10 | Cadence version: 0.80.0 (`19bee92`) | Program iter: iter31 (ABANDONED by Will at 30/144, see HANDOFF)
- Script: `exp/EXP-40_brain_size.py` (runs on the `teachers` library) | Evidence: `exp/EXP-40-full.json/.jsonl`, pilot `exp/EXP-40-pilot.jsonl`

## Summary
- Question: would bigger Cadence brains teach and learn better in our peer network, and does it depend on how much there is to know?
- Setup: teachers.network.run_network (EXP-33 peer network: 8 brains, founders know K/8 contexts, random pairs grade each other, M=16). Arms 'base' (no fix) and 'both' (notes + drift-check + rehearse); brain sizes (16,8) default, (32,16), (64,32); K = 32 and 96 contexts; 12 seeds.
- Prediction (pre-registered, before the pilot): "at K=32 size changes nothing beyond noise in either arm (EXP-33). At K=96 the default brain forgets more and plateaus lower in 'base'; (64, 32) lifts 'base' final knowledge by >= .05 and cuts forgetting; under 'both' the size effect shrinks (stale teaching, not capacity, is the main limit)."
- Pilot (2 seeds, done 2026-10-10; final network knowledge, sizes 16x8 / 32x16 / 64x32): K=32 base .801 / .820 / .877
  (SEM .074 / .039 / .018); K=32 both .992 / .988 / .984 (ceiling); K=96 base .663 / .653 / .702; K=96 both .916 / .878 / .910.
  Forgetting per lesson falls with size in 'base' (K=32: .045 / .037 / .026). K=96 runs take ~350 s each, so the 12-seed
  full run is ~3 h at 3 workers (next window). Early read: size helps a little where nothing else does ('base'), not once
  stale teaching is fixed ('both'); 2 seeds is not evidence.
- Revised prediction (written after the 2-seed pilot, before the 12-seed run; the original prediction above stands and is
  scored as written on all 12 seeds; this revision is scored only on seeds 2-11, which the pilot did not run, so it is not
  tested on the data that shaped it). A difference counts as an effect when it clears 2 SEM (unpaired, over seeds).
  (a) 'both', either K: no size effect: |final(64x32) - final(16x8)| < .02 at K=32 and < .03 at K=96.
  (b) 'base', K=32: 64x32 beats 16x8 by >= .03 in final knowledge, and forgetting per lesson falls with size
      (16x8 > 32x16 > 64x32). This reverses the original "nothing at K=32" for 'base'.
  (c) 'base', K=96: 64x32 beats 16x8 by .02 to .05 in final knowledge (smaller than the original >= .05).
  (d) Overall: size helps only where stale teaching is left unfixed: the 64x32 - 16x8 gain in 'base' exceeds the gain in
      'both' at both K.
- Result: ABANDONED by Will at 30/144 (see HANDOFF). (Full 12-seed run started 2026-10-10 ~17:00; stopped at 30 of 144 runs at 17:15 on Will's call to put EXP-42 first; resumable with the same command, checkpoint exp/EXP-40-full.jsonl).
- Verdict: ABANDONED by Will at 30/144 (see HANDOFF).

## Reflection
- PENDING.
