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
- **EXP-50** (ready; was "EXP-46a", spawned 2026-10-13 by Cadence 0.83 + EXP-43/44) — on EXP-43's judged-w3 graded text, does
  0.83's episodic memory (`Brain.compose(memory_choice=True)`, records keyed by situation that vote in the choice)
  close the gap to the counts table (.254 Cadence vs .346 table)? The memory is table-shaped, so this is the direct
  test. Honest counter-prediction from upstream: memory_choice LOWERED a history-free bandit (0.86 -> 0.75), and
  per-character grading with done=True is close to a contextual bandit. Arms: control (0.83 compose) vs memory_choice;
  3 seeds, 2 passes, greedy + sampled held-out. NOTE: 0.82 changed the composed default (working_memory_scale 12 -> 1.2),
  so the control must be re-measured on 0.83, not borrowed from EXP-43/44.
- **EXP-46b** (DONE 2026-10-13 as EXP-46; was ready, spawned 2026-10-13 by Will forwarding the Stone Age V5 repo) — re-run our EXP-39 Stone Age COLD
  rebuild (our code, not the third-party repo) on 0.83 with a memory_choice arm, sparse-reward and per-step-graded,
  at the budgets where EXP-39 failed (sparse 150/500). Upstream 0.83 reports a 4-step crafting chain from reward
  alone 9.1% -> 73.2% and caregiver-corrected 38.1% -> 98.7%; does it hold on our version of the chain? Context:
  ali12mahmood12345-boop/cadence-stone-age V5 (0.81, 5 seeds): corrective_teacher 18.8% sampled vs random 12.4%,
  founder 7.6%, grade_only 0.2%, greedy 0.0% on every arm; their grade_only failure conflicts with our EXP-39
  (per-step grade 12/12 within 40 episodes, inventory observable). Upstream's 0.82 release notes verify on that env
  (corrective teacher 18.8 -> 26.4%; 4-step chain from corrections 21.0 -> 44.8%, reward alone 0 -> 13.4%).
- **EXP-51** (ready; was "EXP-46c", spawned 2026-10-13 by EXP-45) — which gene sinks the default brain on the Stone Age chain? Start
  from V5's brain (compose defaults, arousal) and move one gene at a time toward the delayed-credit point (actor step 1.0 -> .1
  first, then critic rate .3 -> 5, arousal off, width), grade-v5 signal, per-state greedy accuracy primary, 12 seeds.
- **EXP-49** (ready, spawned 2026-10-13 by Will: "imagine running a noesis lite in the simulation") — a teacher market on
  the Stone Age chain paid by twin-ablation transfer on held-out per-state accuracy, vesting after time alone, wash teachers
  (random, wrong-chain, echo, stake whale), two-dimension finality. Design: docs/NOESIS-LITE-SIM.md (local). Run after EXP-48
  answers generalization (the market should pay on held-out situations).
