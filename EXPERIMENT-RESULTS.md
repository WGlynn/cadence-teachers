# Cadence Experiment Results

Append-only, newest on top. Each row version-stamped. Insight is the number, pass or fail.

> **North star:** the V(S) TRANSFER PROGRAM (`~/cadence-lab/VS-TRANSFER-PROGRAM.md`) is the standing
> top-priority thread per Will 2026-10-07. EXP-08/09+ advance it.

## EXP-48 — does 0.83's episodic memory generalize the Stone Age chain or record it? — 2026-10-13
- **Version:** Cadence v0.83.0 `23dba71`. **Script:** `exp/EXP-48_generalize_or_record.py`. V5 replica + 3 irrelevant weather bits; teach under 4 combinations, test under the 4 never seen.
- **Result (12 seeds, per-state greedy accuracy seen / unseen):** memory corrective .89 / .84 (gap +.05, 9 of 12 seeds lose nothing); memory natural .64 / .58; without memory .53 / .53 and .32 / .33. On unseen weather memory beats no memory by .31 (corrective; sampled full-chain .920 vs .201).
- **Verdict: SUPPORTIVE (3/4; P2 failed toward generalization).** The memory generalizes over irrelevant novelty; EXP-46's acquisition-only limit answered for this kind of novelty, not for new recipes. Detail: experiments/EXP-48.md.

## EXP-44 — graded text: readout operating point or brain size? — 2026-10-13
- **Version:** Cadence v0.81.0 `736fee9` (pre-registered; last 8 runs from a pinned worktree after upstream removed the gene in 0.82). **Script:** `exp/EXP-44_operating_point.py`.
- **Result (3 seeds, greedy held-out after pass 2):** control .253 (SEM .010); 0.81 gene target .3 .183, target 1/28 .068 (each 1 of 3 brains failed to settle); actor step .2 .229; twice as wide .213 (top-answer share .88). Table on the same grades .346.
- **Verdict: NULL (3/4 held; P3 failed).** Neither operating point nor width lifts it; by the decision rule the gap to the table is exploration. Detail: experiments/EXP-44.md; program iter34.

## EXP-47 — after the caregiver leaves: `live` vs `step` drift of a memory brain's Stone Age chain — 2026-10-13
- **Version:** Cadence v0.83.0 `23dba71`, EXP-46's memory brain. **Script:** `exp/EXP-47_alone_live_vs_step.py`. Paired: both paths from each seed's same taught brain; reproduces EXP-46's end point exactly.
- **Result (12 seeds, corrective, 80 alone):** greedy full-chain 12/12 on both paths (identical per seed); per-state all four right 9 -> 5 through `live`, 9 -> 9 through `step` (dipped to 6 at 40); sampled .955 / .972. Reward-alone learners improve alone on both paths (.75 -> .88 / .90).
- **Verdict: BOUNDARY (2/4 held).** Upstream's caveat (greedy stall through `step`) does not reproduce on this chamber; the measurable drift is on the `live` side and only the per-state reading shows it. Detail: experiments/EXP-47.md.

## EXP-46 — 0.83 episodic memory on the Stone Age chain (V5 replica), read state by state — 2026-10-13
- **Version:** Cadence v0.83.0 `23dba71`, default composition, `memory_choice=True` at its own defaults. **Script:** `exp/EXP-46_episodic_memory_stone_age.py`. Replica check: without memory, corrective on V5's seeds = .264, upstream's published 0.82 V5 figure exactly.
- **Result (12 seeds):** without -> with memory, sampled full-chain / per-state greedy accuracy: corrective .193 -> .963 / .58 -> .94; reward alone .092 -> .777 / .29 -> .75; V5's grade .006 -> .917 / .44 -> .90; after 80 alone through live, corrective .276 -> .955 sampled but all-four-right 9 -> 5 of 12 (a stage drifts, the context covers it).
- **Verdict: SUPPORTIVE (4/5 held; P5 failed: 0.82's context alone lifted corrective to .58).** Upstream's 0.83 claim replicates on an outside chamber with an instrument search cannot pass. Detail: experiments/EXP-46.md.

## EXP-45 — Stone Age chain: grade vs brain 2x2 + search check (V5 replica) — 2026-10-13
- **Version:** Cadence v0.83.0 `23dba71`, both brains on the 0.81 composition. **Script:** `exp/EXP-45_stone_age_2x2.py`. Replica of Stone Age V5's chamber reproduces V5's per-seed corrective numbers exactly (28/24/20/11/11).
- **Result (12 seeds):** per-state greedy accuracy, our delayed-credit brain: grade-dense 1.00, V5's grade .96, corrective .96, world reward .58; V5's default brain + arousal: .33 / .33 / .42 / .42 (collapse onto "wood" in all states common). V5 corrective sampled full-chain .227, with the carried context erased each decision .098; a no-knowledge never-repeat searcher gets .304.
- **Verdict: SUPPORTIVE (5/5 predictions held).** V5's grade_only failed on the brain's operating point, not the grade; V5's full-chain metric mostly measures in-attempt search. Detail: experiments/EXP-45.md.

## EXP-36 (fixed) — attack test re-measured after duplicated-lesson bug — 2026-10-10
- **Version:** Cadence v0.80.0 main `19bee92`. **Script:** `exp/EXP-36_adversarial_market.py` (bug fixed; old in `.dup-bug.bak`).
- **Result:** fake pay / honest final: LIST 13.09 / .680 · PROBE+LEDGER .042 / .946 · SMART .151 / .834 · RECIP .177 / .912.
- **Verdict: CONFIRMED (bug material).** Smart sandbagger ~3x the logged fake pay and costs .11 honest knowledge; reciprocity
  protects throughput, not pay. iter24 numbers superseded. Detail: VS-TRANSFER-PROGRAM iter26.

## EXP-35b — pedigree share at K=96 (teachers choose own vs relay) — 2026-10-09
- **Version:** Cadence v0.78.0 / `750c8ef`. **Script:** `exp/EXP-35b_pedigree_controller.py` (ROUNDS=30 SEEDS=6).
- **Result:** all arms final .828-.850, within ~2 SEM; discovery .34-.39; relaying falls .45 -> .33 with share.
- **Verdict: VOID (amended 2026-10-09).** Originally logged REFUTED. The test was blind: royalty was credited to whatever move the origin made that round, so the Discover estimate never saw its pay and the share never reached the decision. The staged CREDIT=fixed patch has its own leaks (review 2026-10-09: founder-item royalty counted as Discover pay; positive-only royalty guard; optimistic 0.05 priors; PI arm winds up). Rerun Will-gated after those are fixed. Detail: VS-TRANSFER-PROGRAM iter25.

## EXP-11 smoke — Reinforcement (patch-world substrate) twin-ablation foundation — 2026-10-08
- **Version:** Cadence v0.78.0 / `750c8ef`. **Script:** `exp/EXP-11_smoke_reinforcement.py`.
- **Question:** before building M2-synergy on the richer equilibrium `Reinforcement` substrate, does
  it (a) learn a trivial 4-context bandit on 0.78, and (b) snapshot/from_snapshot to an EXACT twin?
- **Result:** (a) acc 0.75 -> **1.00** after 400 act/feedback steps (learns to ceiling, more headroom
  than the plain `Brain` bandit which capped lower); (b) **TWIN EXACT** — snapshot (19,337 bytes) then
  `from_snapshot` gives identical greedy actions on all 4 contexts.
- **Verdict: foundation VALIDATED.** The substrate learns and the byte-identical twin fork works, so
  the M2-synergy harness has a sound base.
- **Design finding (why synergy is NOT a quick run, recorded honestly):** genuine super-additive
  synergy does not reduce to twin-ablation the way additive worth does. Any split where each
  contributor teaches a disjoint PART of the task is additive coverage (= EXP-10, partial credit per
  part, not zero-alone). True "each-alone=0, together=positive" needs an IRREDUCIBLE task (XOR across
  two sense-channels; one bit gives zero info about the answer), which forces the contributions to be
  PERCEPTUAL PREREQUISITES (learn to read each channel). Whether those prerequisites persist and
  compose when the held-out XOR task is introduced is transfer/curriculum learning = Cadence's OWN
  open issue #115. So a synergy probe is coupled to an unproven upstream question; first cut likely
  INCONCLUSIVE. Not rushed at hour 22 to avoid mislabeling additive coverage as synergy.

## EXP-10 — multi-mind per-contributor worth attribution (program M2, additive) — 2026-10-08
- **Version:** Cadence v0.78.0 / `750c8ef`. **Script:** `exp/EXP-10_vs_multimind_attribution.py`.
- **Question:** in a multi-mind collaboration with some genuine + some fake minds (interior structure
  identical: N nodes, acyclic, each a consistent novel sub-map on a disjoint block), does measured
  transfer (a) localize worth to the SPECIFIC genuine minds, and (b) scale with genuine fraction?
- **Method:** K=8 / 4 blocks(minds) of 2 contexts / 16x8 brain, 1200-step witness, 12 seeds. Student
  ingests the collaboration's composite map; transfer measured per-block (after-baseline) and aggregate.
- **Result — per-mind (blocks 0,1 genuine / 2,3 fake in ONE collaboration):** genuine minds mean
  transfer **+0.250**, fake minds **-0.292**, attribution gap **+0.542**. Proportional curve
  (f=#genuine/4): 0.00:-0.292  0.25:-0.115  0.50:-0.021  0.75:+0.052  1.00:+0.208 — monotonic,
  ~linear; f=1.0 matches EXP-08 genuine +0.219 (consistency check passes).
- **Verdict: CONFIRMED (M2 additive).** Transfer attributes worth PER-CONTRIBUTOR — genuine minds get
  positive localized transfer, fake minds negative, WITHIN the same collaboration that is interior-
  indistinguishable. Aggregate worth tracks genuine fraction. This is the Shapley-relevant per-node
  property Noesis needs, measured.
- **Honest caveats:** per-block SEMs large (0.09-0.12; 2 contexts/block => acc quantized to 0.5 steps);
  block-0-genuine +0.125 is within ~1 SEM of zero (noisy), though block-1 + both fake blocks + the
  aggregate gap are clear. The proportional curve re-expresses EXP-09's gamma via block structure; the
  NEW result is per-mind LOCALIZATION, not the aggregate curve. **SCOPE: additive/per-node attribution
  only. Super-additive SYNERGY (worth only in the combination, XOR-style) is NOT tested and remains
  open (M2-synergy) — a small bandit cannot cleanly represent it.** Do not round up.

## EXP-09 — v(S) transfer vs coordinated-but-wrong prior (program M4) — 2026-10-07
- **Version:** Cadence v0.75.0 / `88f4dde`. **Script:** `exp/EXP-09_vs_gamma_coordinated_prior.py`.
- **Question:** does transfer resist a fake whose prior agrees with the exogenous task T on a tunable
  fraction gamma — past peer-prediction's agreement crossover (~gamma*=0.70, paper 6.1)?
- **Method:** K=8 / 2 actions / 16x8, 1600-step witness, 8 seeds. Fake teaches rule R_gamma agreeing
  with T on ~gamma of contexts; measure transfer to T. gamma 1.0=genuine, 0.5=chance, 0.0=anti.
- **Result (iter4, clean curve — low-gamma 20 seeds, crossover 12 seeds):** transfer rises
  MONOTONICALLY with gamma: 0.0:-0.281  0.25:-0.188  0.5:-0.062  0.625:+0.021  0.75:+0.021
  0.875:+0.094  1.0:+0.135 (SEM 0.03-0.06). (iter3 8-seed was noisier/non-monotonic; resolved.)
- **Verdict: SUPPORTIVE, clean curve.** Worth bar (transfer>0.10) crossed firmly in gamma=0.875-1.0;
  everything at gamma<=0.75 prices to ~zero. A coordinated fake must agree with T on ~90%+ of contexts
  before transfer registers worth -> you cannot coordinate-fake a causal delta the way you fake
  agreement (faking collapses into contributing).
- **Honest caveats:** the ~0.70 peer-prediction figure is CONCEPTUAL (different mechanism), NOT a
  matched in-harness baseline — a real PP scorer is still owed before "crossover higher than 0.70" is
  decision-grade. Mixed-N curve (labeled). Absolute transfer modest (partial mastery at K=8).
  Infra: greedy act() probed PURE -> eval clone dropped; witness-ingest is the bottleneck.

## EXP-08 — v(S) via measurable transfer: twin-brain ablation separation (program M1) — 2026-10-07
- **Version:** Cadence v0.75.0 / `88f4dde`. **Script:** `exp/EXP-08_vs_transfer_separation.py`.
- **Question:** does measured transfer (snapshot b; feed one twin a witness; compare twins on an
  exogenous held-out task T) SEPARATE a genuine witness from a surface-matched fake — i.e. produce
  non-zero separation where INTERIOR scoring produced 0.0% (`wash_sim.rs`)?
- **Method:** K=8 contexts / 2 actions / 16x8 brain, 1600-step continuing-stream witness, 16 seeds.
  Three witnesses matched on surface stats (steps, context marginals, reward rate): genuine (teaches
  T), fake_random (reward decoupled from ctx/action), fake_wrong (teaches anti-correlated T').
  Held-out greedy eval via save/load clone. transfer = acc_after - acc_baseline.
- **Result (iter2):**
  | witness | mean transfer to T |
  |---|---|
  | genuine | **+0.219** (SEM 0.060, ~3.6 sigma) |
  | fake_random | +0.008 |
  | fake_wrong | -0.242 |
  - baseline on T = 0.523 (clean chance 0.50). separation genuine-vs-random +0.211, vs-wrong +0.461.
  - own-task diagnostic: fake_wrong on its OWN task T' = 0.719 (it DID learn), genuine on T' = 0.258.
- **Verdict: SEPARATES — program milestone M1 CROSSED.** Measured transfer is NOT worth-blind: a
  surface-matched fake prices to ~0, a wrong-prior fake to negative, while genuine transfers. The
  own-task diagnostic shows worth is TASK-SPECIFIC (competence on the wrong task is not worth on the
  exogenous task) — the exogenous-task-selection point made measurable.
- **Honest caveats:** fake is SURFACE-matched, NOT interior-feature-matched (that is M2, the true
  `wash_sim.rs` adversary, not yet tested). Genuine mastery is partial at K=8 (5/16 seeds no
  transfer), so absolute separation is modest; the mean, not the per-seed, is the signal. iter1 (K=4)
  gave a coarser +0.31 with a fake leak later confirmed as K=4 chance-overlap artifact.
- **Next:** EXP-09 (M4 gamma sweep), then M2 feature-matched fake.

## EXP-01 — arousal gene sweep (reward-flip stabilization) — 2026-10-07
- **Version:** Cadence main `88f4dde` / v0.75.0 (clone `~/_cadence_study`).
- **Script:** `~/cadence-lab/exp/EXP-01_arousal_gene_sweep.py` (8 configs x 6 seeds, 16x8 net,
  continuing-stream `brain.live`, +1/-1 reward, flip at t=1200/2400). Metric = mean of last 4
  post-flip greedy evals.
- **Result:**
  | config | post_hold_mean | best_seed |
  |---|---|---|
  | default | 0.677 | 0.94 |
  | rouse-easy (thr/2) | 0.667 | 0.94 |
  | rouse-hard (thr*2) | 0.573 | 0.75 |
  | hot (heat*2) | 0.625 | 0.94 |
  | young (youth*2) | 0.708 | 1.00 |
  | slow-decay (decay/2) | **0.719** | 1.00 |
  | tol-tight (tol/2) | 0.677 | 1.00 |
  | combo (thr/2, heat*2) | 0.615 | 0.88 |
  - Defaults: threshold 0.2, decay 0.9, tolerance 2.0, floor 0.1, fast 0.05, slow 0.005, heat 2.0,
    youth 100, value_surprise 1.0, record_surprise 0.0, need 0.0.
- **Verdict: REFUTED (coarse-sweep).** Single-axis gene tuning does NOT stabilize the fast reward-flip
  at small scale. Best (slow-decay) lifts post-flip hold to 0.72 vs 0.64 baseline step path — a real
  but modest gain, not stabilization (bar was >=0.90 mean). Several configs reach 1.00 on a lucky
  seed, none holds in the mean.
- **Honest caveats:** single-field perturbations only (no joint search), 6 seeds, tiny 16x8 net,
  acquisition itself only ~0.7. A joint-gene sweep or a larger net could still find a stable region;
  this refutes *coarse* tuning, not the existence of a stabilizing operating point.
- **Sharpened question for Bernhard:** single-axis sweep of threshold/heat/youth/decay/tolerance on a
  16x8 net got post-flip hold to 0.72 (vs 0.64), none >=0.90. Is stabilization a joint-gene / scale
  effect, or is a fast-flipping bandit simply adversarial to the equilibrium dynamics and the wrong
  way to drive it? (Updates the reward-flip draft with v0.75 gene data.)
- **Spawned:** EXP-01b (joint-gene + scale sweep around slow-decay/young region).

## 2026-10-08 — EXP-01 rerun with corrected eval (closes #164)
- Bernhard closed #164 as an evaluation-protocol mismatch: training uses done=True (1-step episodes), but clone_eval ran 4 cues without resetting the clone. Fix: `c2.reset()` before every cue (keeps learned params + memory).
- Applied to all 4 harnesses (EXP-01 + cadence-reward-flip/{online_reward_flip,cadence_reward_flip_minimal,arousal_compare}.py; .bak copies kept).
- Rerun, runtime 0.78.0 tag on clone `750c8ef`, 8 configs: post-flip hold = 1.000 on every config, best seed 1.00. The earlier "arousal does not stabilize reversal" finding is RETRACTED; it was our measurement bug.
- Scope: this bandit only; not a general reversal guarantee (Bernhard's caveat).
