# Cadence Experiment Queue

Backlog for the `cadence-experiment-loop`. Each experiment is a few dozen lines, confirm-or-kill,
version-stamped. Pick highest-value `ready` (ties → cheapest). Experiments spawn sharper experiments.

| id | question | method | our interest | cost | status |
|---|---|---|---|---|---|
| EXP-01 | Does ANY arousal gene setting stabilize the fast reward-flip (fix the oscillation / sub-1.0 cap)? | sweep threshold/heat/youth/decay/tolerance on the reward-flip, measure post-flip hold vs baseline | answers the open Q to Bernhard; gates [[cadence-library-status]] "tuned-genes open" | ~5 min | **done 2026-10-07: REFUTED (coarse). best slow-decay 0.72 vs 0.64 baseline, none >=0.90. See EXPERIMENT-RESULTS.md** |
| EXP-02 | Does our reward-flip finding reconcile with Bernhard's `benchmarks/reversal` 39/40 pass? | run his own odour/reversal nursery, compare regime (continuing life vs our bandit) | is the gap our setup or the mechanism? | ~10 min | ready |
| EXP-03 | Is "measurable transfer" between two brains real and causal? | twin-brain ablation ... | makes [[noesis-transfer-graph-not-citation-graph]] concrete | ~15 min | **DONE-superseded by V(S) program M1 (EXP-08): twin-brain ablation built, genuine transfer +0.219 ~3.6σ** |
| EXP-04 | Does the transfer signal SEPARATE genuine learning from wash? | genuine vs wash witness delta | [[noesis-wash-reduces-to-two-irreducibles]] on Cadence | ~15 min | **DONE-superseded by M1+M2 (EXP-08/10): fakes price to ~0/neg; per-mind attribution gap +0.542** |
| EXP-05 | Is the portable-mind byte-identical property robust under mid-stream snapshot/restore? | snapshot a learning brain mid-stream, restore in a fresh process, assert bit-identical continuation + digest match | [[portable-swappable-jarvis-mind]] Idea 1 (the one demonstrated property) | ~5 min | ready |
| EXP-06 | Where is the acquisition floor/ceiling vs scale? | scan module sizes + #contexts, measure acquisition hold | sizes the "small net" fit for integration candidates | ~10 min | ready |
| EXP-07 | Does Cadence avoid catastrophic forgetting of an unrelated skill? | teach skill A, then B, check A retained (nursery's "stable pair") | persistence relevance for a learned local policy | ~10 min | ready |

## Spawned follow-ups
- **EXP-01b** (ready) — joint-gene + scale sweep: slow-decay x young region crossed, plus 16x8 vs
  32x16 vs 64x32 net sizes, to test whether stabilization is a joint-gene or scale effect rather
  than single-axis. Spawned by EXP-01's REFUTED coarse result (best 0.72, none >=0.90).
