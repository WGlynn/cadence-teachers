# EXP-36: adversarial market (sandbagging collusion and fake need; self-reported lists vs probe + ledger)

- Date: 2026-10-09 (original, iter24); 2026-10-10 (bug-fixed rerun, iter26) | Cadence version: v0.78.0 (original); v0.80.0 main `19bee92` (rerun) | Program iter: iter23 (smoke), iter24, iter26
- Script: `exp/EXP-36_adversarial_market.py` (fixed); buggy original `exp/EXP-36_adversarial_market.py.dup-bug.bak` | Evidence: `exp/EXP-36-fixed.out`, `exp/EXP-36-fixed.json`, `exp/EXP-36-fixed.jsonl` (current); `exp/EXP-36.out`, `exp/EXP-36.json` (superseded)

## Summary
- Question: can colluders mint fake pay and soak lessons in the teaching market, and which defences (probe on a
  committed copy, once-per-item provenance ledger, reciprocity) stop them?
- Setup: EXP-34 FIX world (notes, drift-check, rehearse, neediest-first, pay = measured gain). 8 brains: 0-4 honest,
  5 fake-need (claims to know nothing), 6 colluding teacher, 7 sandbagger (answers wrong before the lesson so 6 is paid).
  Modes: LIST (self-reported lists and self-run tests), PROBE+LEDGER, SMART (sandbagger also fools probes, ledger is the
  only defence), RECIP (SMART + need weighted by lessons given / received). 16 rounds, 6 seeds.
- Prediction (docstring, original): "LIST leaks large fake pay and loses throughput; PROBE+LEDGER leaks ~0; SMART leaks a
  bounded amount (at most one credit per item), set by the ledger." Rerun RUN GATE (iter26, before running): honest
  knowledge rises slower in every mode; LIST still mints large fake pay; PROBE+LEDGER ~0; SMART fake pay higher than
  .052 but bounded; RECIP <= SMART.
- Result (current, fixed rerun; fake pay minted / real gain caused by colluder / lessons absorbed by attackers / honest
  final knowledge): LIST 13.094 / 0.161 / 0.93 / 0.680; PROBE+LEDGER 0.042 / 0.203 / 0.30 / 0.946; SMART 0.151 / 0.073 /
  0.83 / 0.834; RECIP 0.177 / 0.177 / 0.69 / 0.912. SEM not reported in the outputs (per-seed rows are in the json).
  Superseded buggy run (iter24): LIST 14.354 / 0.016 / 0.93 / 0.726; PROBE+LEDGER 0.000 / 0.052 / 0.37 / 0.966; SMART
  0.052 / 0.016 / 0.85 / 0.924; RECIP 0.130 / 0.021 / 0.76 / 0.936.
- Verdict: iter24 result SUPERSEDED by the iter26 fixed rerun. Current: SUPPORTIVE. Self-reported lists are
  catastrophic (fake pay about 80x the real gain); probe + ledger nearly stops minting; a probe-fooling sandbagger is
  bounded in minting but costs honest knowledge 0.11 (0.834 vs 0.946); reciprocity recovers throughput (0.912) but does
  not cut fake pay (prediction RECIP <= SMART was WRONG). The attack is not solved.

## Reflection
- What it means: pay-on-measured-gain is not enough when the student reports its own tests or need; measurement must be
  done by the protocol on a committed copy, with each student-item credited once. The remaining hole is a sandbagger
  that also fools probes: it always looks neediest and soaks most lessons. PROBE+LEDGER's residual 0.042 is, by code
  reasoning (not separately measured), a gross-vs-net gap: pay counts items newly right while true gain is net accuracy
  change, so forgetting during a lesson shows up as "fake" pay.
- Process: the original script ran the whole lesson block twice per teacher per round; only the second copy counted
  pay and knowledge while the first spent ledger credits, so SMART/RECIP fake pay was understated by construction and
  two iter24 conclusions ("the ledger caps it at .052", "reciprocity barely helps") were wrong. The rerun also moved
  Cadence 0.78 to 0.80 at the same time, so version and bug-fix effects are not separated (iter26 judges the fix
  dominates because it halves lessons). The adversaries are scripted, not learning. In PROBE+LEDGER the attacker cannot
  detect the probe by construction (stated scope). The rerun did write a RUN GATE with prediction and window check first.
- Lesson: when a result looks better than expected for a defence, audit the accounting path for double-counting; and an
  attack test needs the "attacker sees through the probe" case, because that is where the real residual lives.
- Next: litepaper updated to the fixed numbers (`docs/SPAWN-LITEPAPER.md` and Desktop PDF v6, per HANDOFF; v5 has the
  old numbers and is not to be shared). Next rung:
  repeat-need detection from the ledger (an item already taught that the probe still says is missing), run on top of
  RECIP; pay on persisting gain (designed) to close the gross-vs-net gap.
