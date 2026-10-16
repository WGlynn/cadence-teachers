# Cadence Experiment Results

Append-only, newest on top. Each row version-stamped. Insight is the number, pass or fail.

> **North star:** the V(S) TRANSFER PROGRAM (`~/cadence-lab/VS-TRANSFER-PROGRAM.md`) is the standing
> top-priority thread per Will 2026-10-07. EXP-08/09+ advance it.
>
> Note 2026-10-16 (program re-rank): EXP-12 to EXP-35 and EXP-37 to EXP-43 have no rows here; their
> write-ups are in experiments/EXP-XX.md and the program log (VS-TRANSFER-PROGRAM.md).

## EXP-65 — the outcome gate on signals Cadence receives: the label is safe but too sparse, the forecast error is blind — 2026-10-16
- **Version:** Cadence v0.83.0 `6499e56` (EXP-63's head; three stored EXP-63 rows recompute identically). **Script:** `exp/EXP-65_inbrain_gate.py`. New arms gate during training only: lab5 (hold a decision when the corrective teacher's label follows it), td5 (hold when the brain's own signed forecast error for it is below 0), out5t (EXP-63's oracle during training only, the matched ceiling). Comparators: EXP-63's ctx5 / hold5 / out5 rows on the same seeds (invisible chain 48 per signal, hidden 24). Pre-registered `93d5645`, amended before the full run `75dfc6a` (check scope, review fixes; no arm or prediction changed). 3 workers, 25 min.
- **Insight:** invisible chain, corrective: clean greedy passes lab5 9 vs ctx5 5 of 48 (8 / 4, p .39) vs out5t 19 (lab5 5 / out5t 15, p .041); lab5 never held a correct move (stage 2 -.005), held 32% of misses (the guided share) and loses exactly at stage-1 first try (-.19 vs out5t). out5t = out5 on clean passes (19, 17 hidden): the whole gain is made in training. td5: stage-1 AUC miss vs invisible WOOD .525 (SEM .005, 96 lives); held 6,707 correct moves (3,824 the WOOD); clean 2 vs 5 pooled, sampled -.108 (.035) vs ctx5. P1 failed, P2 P4 P5 P6 held, P3 failed.
- **Verdict: BOUNDARY (loop: INCONCLUSIVE); forecast arm BLIND.** No in-library signal stands in for the world's failure flag in this chamber: the label is precise but covers only taught decisions, the forecast error is available everywhere but blind. Strengthens the #202 comment (the gene needs a per-decision failure input). EXP-66 queued. Detail: experiments/EXP-65.md.

## EXP-63 — key the hold on the outcome: the gain stays, the invisible-action break goes — 2026-10-15
- **Version:** Cadence v0.83.0 `6499e56` (stored EXP-57/59/60 rows recompute identically at this head). **Script:** `exp/EXP-63_outcome_gate.py`. ctx5 / hold5 (observation gate) / out5 (outcome gate: hold only decisions the chamber answered as failures) on the invisible-action chain (48 fresh seeds per signal), ctx5 / out5 on the hidden and visible chains (24 per signal); 120 attempts (pilot-fixed).
- **Insight:** invisible chain clean greedy passes out5 19 vs ctx5 5 vs hold5 1 of 96 (out5-only 18 / ctx5-only 4, p .004), stage-2 first try +.068 vs ctx5 and +.216 vs hold5 (EXP-59's -.15 replicates for hold5); hidden 17 vs 4 of 48 (p .001); visible 37 vs 34 (neutral). All invisible-chain clean passes came with corrections. The outcome is an oracle here: neither observation nor reward tells a miss from the invisible WOOD, so a gene keyed this way needs a failure input `step()` does not take.
- **Verdict: SUPPORTIVE (5/5; CONFIRMED).** Comment drafted for upstream #202 (Will posts). Detail: experiments/EXP-63.md.

## EXP-61 — it was the brain: the default memory brain blocks a teacher's content — 2026-10-14
- **Version:** Cadence v0.83.0 `23dba71`. **Script:** `exp/EXP-61_default_brain_step_alone.py`. EXP-58's protocol (alone phase through step) with EXP-53's default memory brain; know-4 vs random vs untaught, 24 students at 40 and 120, EXP-53's seeds.
- **Insight:** content -.049 (SEM .085) at 40, +.016 (.066) at 120, against +.469 on the delayed-credit brain (EXP-58); every arm within ~.06 of EXP-53, so the step-vs-live alone path is not what hid content. Being corrected at all still +.268 at 40.
- **Verdict: SUPPORTIVE (2/2).** The default brain's operating point blocks content; Noesis-lite v2 (EXP-62) runs on the delayed-credit brain. Detail: experiments/EXP-61.md.

## EXP-59 — where the hold rule breaks: a correct action that changes nothing visible — 2026-10-14
- **Version:** Cadence v0.83.0 `23dba71`. **Script:** `exp/EXP-59_hold_boundary.py`. Observations A, A, B, C (WOOD correct but invisible); place / ctx5 / hold5, 48 fresh seeds per signal, 120 attempts.
- **Insight:** hold erases the invisible correct WOOD: stage-2 first try -.157 vs plain context (3.7 SEM), clean passes 2 vs 9 of 96 (7 vs 0), corrective sampled .48 vs .81; no cost where the observation changes. The gate must key on "the decision changed nothing", which the observation cannot always tell.
- **Verdict: SUPPORTIVE (3/3, the predicted break).** Detail: experiments/EXP-59.md.

## EXP-58 — a teacher's content finally gets through: the delayed-credit brain — 2026-10-14
- **Version:** Cadence v0.83.0 `23dba71`. **Script:** `exp/EXP-58_content_delayed_credit_brain.py`. EXP-53's chamber/schedule/seeds with EXP-45's delayed-credit brain (alone phase through step: no arousal genes); know-4 vs random vs untaught, 24 students at 40 and 120.
- **Insight:** content +.193 (5.8 SEM) at 40, +.469 (11 SEM) at 120; know-4 student .93; random labels worth nothing (-.08 vs untaught). First channel with measurable content (EXP-52..55 were null on the default memory brain). Confound: alone phase path differs (EXP-61 splits it).
- **Verdict: SUPPORTIVE (3/3).** Noesis-lite v2 now has something to price. Detail: experiments/EXP-58.md.

## EXP-60 — the hold rule on the normal chain, where the inventory is visible — 2026-10-14
- **Version:** Cadence v0.83.0 `23dba71`. **Script:** `exp/EXP-60_hold_on_visible_chain.py`. EXP-57's arms on EXP-45's visible-inventory observation; 48 fresh seeds per signal (place on 24).
- **Insight:** hold vs plain context 75 vs 75 clean greedy passes of 96 (14 vs 14), first try +.006; place-only 39 vs 40 of 48. The rule's gain (EXP-57) is specific to chains where the observation does not show progress; it is neutral elsewhere.
- **Verdict: SUPPORTIVE (3/3).** Detail: experiments/EXP-60.md.

## EXP-57 — keep misses out of the temporal context: confirmed on fresh seeds — 2026-10-14
- **Version:** Cadence v0.83.0 `23dba71`. **Script:** `exp/EXP-57_confirm_hold_greedy.py` (EXP-56's chamber/arms). Fresh seeds 57000+, ctx5 vs hold5, 48 per signal at 120 attempts, 24 at 240.
- **Insight:** clean greedy passes of the ambiguous chain 38/96 with hold vs 4/96 without at 120 (McNemar 36 vs 2, p < .0001; 29/48 vs 2/48 with corrections), 23 vs 9 of 48 at 240 (p = .007); first-try accuracy +.17 (7 SEM); sampled success +.25 (predicted flat). A clean pass never fires the rule, so the gain is in what training stored. Cadence's replay path already applies this rule; the context key does not.
- **Verdict: SUPPORTIVE (3/4).** Detail: experiments/EXP-57.md.

## EXP-56 — on an ambiguous chain, do misses wash the memory that matters out of Cadence's context? — 2026-10-14
- **Version:** Cadence v0.83.0 `23dba71`. **Script:** `exp/EXP-56_ambiguous_chain_trace.py`. Huncho's V7.2 A/B/A/B chain on our V5 chamber; place / ctx .5 / ctx .8 / ctx .5 with misses held out; natural + corrective; 24 seeds.
- **Insight:** context beats place (sampled +.30; clean greedy 5/48 vs 0/48, on V7.2's 11/100 vs 0/100). Holding misses out did not help recovery after a miss on these seeds (+.01; on fresh seeds in EXP-57 it did, +.13, less than at first try), so the predicted after-miss concentration failed; it raised first tries (+.10) and clean greedy passes 17/48 vs 5/48 (post-hoc, confirmed in EXP-57). Slower fade (.8) is worse.
- **Verdict: NULL (1/4).** Detail: experiments/EXP-56.md.

## EXP-55 — demonstrations at every decision, with and without upstream's surprise rule (PR #197) — 2026-10-14
- **Version:** PR #197 head `8d99c75` (pinned `~/_cadence_197`). **Script:** `exp/EXP-55_every_decision_demonstrations.py`. EXP-53's chamber/seeds; know-4 vs random demonstrations at every guided decision, rule off/on, untaught; 24 students per length.
- **Insight:** content at 240 is -.16 with every row taught (random demonstrations beat right ones, 3.4 SEM): readout saturation. The rule removes it (+.19; know-4 student .72 -> .88) but content stays ~0 (+.03). Side check: with memory_choice the rule reads the cortex answer (right .34) while the brain acts on the memory vote (right .97).
- **Verdict: BOUNDARY (2/4).** No content-carrying channel through step(teacher=) yet. Detail: experiments/EXP-55.md.

## EXP-54 — does teaching only where the answer differs (upstream PR #197) let a label's content through? — 2026-10-14
- **Version:** PR #197 head `8d99c75` (0.83.0 + opt-in `learning_surprise`, unmerged), pinned worktree `~/_cadence_197`. **Script:** `exp/EXP-54_surprise_teaching.py`. EXP-53 exactly with the gene on; every-row arms = EXP-53's rows, valid after a bit-identical gate. 24 students per length.
- **Insight:** content under the gene -.008 / +.125 / +.003 at 40 / 120 / 240 (every-row +.013 / +.107 / +.068); gene effect on know-4 within 1.3 SEM of zero at every length. The rule dropped random labels at chance (.20) and the perfect teacher's less often (.13 to .16): right after an executed mistake the brain's answer is mostly that mistake. Free-phase budget exhaustion (0.1 to 0.5% of lessons) is the founder's, gene off and on alike.
- **Verdict: NULL (gate held, 0/3).** In mistake-only teaching the surprise rule is not what hid content. Next: demonstrations at every guided decision, where the rule has answered rows to remove. Detail: experiments/EXP-54.md.

## EXP-53 — does the content of a teacher's labels matter, and at what lesson length? — 2026-10-13
- **Version:** Cadence v0.83.0 `23dba71`. **Script:** `exp/EXP-53_does_content_matter.py`. Paired twins (know-4 / random labels / untaught), lessons of 40, 120, 240 attempts, 24 students each.
- **Result:** content (know-4 minus random) +.013 / +.107 / +.068 (SEMs about .06); correction itself is worth +.25 at 40 attempts for either teacher; untaught catches up at longer lessons.
- **Verdict: NULL (1/4).** Label content could not be seen at any length (pooled 120-240 about +.09, about 2 SEM). Students learn from being corrected, not from the answer; market work waits for a channel that carries content. Detail: experiments/EXP-53.md.

## EXP-52 — Noesis-lite v1.1: priced against a form-matched null — 2026-10-13
- **Version:** Cadence v0.83.0 `23dba71`. **Script:** `exp/EXP-52_noesis_lite_null_counterfactual.py`. Twins taught / random-label null / untaught; know-k teachers (k = 1..4) and three fakes; 72 worth samples per teacher.
- **Result:** vs null, fakes price at or below zero (random -.07, wrong-chain -.21, echo -.27) but genuine teachers are also near zero (know-4 +.013; Spearman with k .06): a teacher who knows the whole chain is worth no more than one labelling at random (accuracy .661 vs .648; untaught .46). Vs no teacher, random +.104 (EXP-49 reproduces).
- **Verdict: BOUNDARY (1/5).** The null fixes fake pricing on average but shows the lesson channel carries no content at 40 attempts: students learn from being corrected, not from what they are told. Next EXP-53: does content matter at longer lessons. Detail: experiments/EXP-52.md.

## EXP-49 — Noesis-lite v1: a teacher market paid by twin-ablation transfer — 2026-10-13
- **Version:** Cadence v0.83.0 `23dba71`. **Script:** `exp/EXP-49_noesis_lite_market.py`. EXP-48's weather chamber; worth on unseen weather after 20 attempts alone, taught minus untaught twin; replication; bar .125.
- **Result (3 markets x 6 students x 7 teachers):** genuine teachers worth +.17 to +.30, pay share .716; random-label fake +.179 (about 3 SEM above zero), wrong-chain +.061, echo -.036; fakes take .285 of pay; Spearman(pay, skill) .05; genuine worth survives vesting (.86).
- **Verdict: BOUNDARY (1/5 held).** Priced against "no teacher", the market pays random labels (they unstick a stuck student) and cannot rank skill. Next: a form-matched null counterfactual (random-label twin) and more students (EXP-52). Detail: experiments/EXP-49.md.

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
- **Note 2026-10-16 (program re-rank):** VOID above is superseded. iter27 (patched credit) was NULL, a
  credit-design failure; iter28 (CREDIT=item, Cadence v0.80.0 `19bee92`, 12 seeds) is SUPPORTIVE: ALPHA 0 / 0.9 / PI
  Discover pay per move .0036 / .0071 / .0049; Discover share last 10 rounds .51 / .63 / .53; new discoveries
  54.0+-1.0 / 57.8+-0.8 / 55.3+-1.3; final .790 / .811 / .798. Accuracy +.021 (~2 SEM, no claim); PI part wrong
  (set point shrinks by construction). Detail: experiments/EXP-35b.md, VS-TRANSFER-PROGRAM iter28.

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
- **Note 2026-10-16 (program re-rank):** the numbers above are pre-fix. After the #164 eval fix (iter8, 12 seeds):
  genuine minds +0.375 vs fake -0.479, gap +0.854 (was +0.542); proportional curve f=0..1:
  -0.542/-0.302/-0.052/+0.198/+0.448, linear. See VS-TRANSFER-PROGRAM iter8.

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
- **Note 2026-10-16 (program re-rank):** the numbers above are pre-fix, and the claim that everything at
  gamma<=0.75 prices to ~zero is RETRACTED (iter8; the "act() is PURE" probe was wrong, #164). After the fix
  (crossover band, 12 seeds): gamma 0.625 +0.125 (.074), 0.75 +0.135 (.054), 0.875 +0.281 (.049), 1.0 +0.469
  (.045); credit rises roughly proportionally with agreement. The low-gamma half (0.0-0.5) has not been rerun.
  The paper's gamma*=0.70 is on a different axis (EXP-15, iter9). See VS-TRANSFER-PROGRAM iter8, M4.

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
- **Note 2026-10-16 (program re-rank):** the numbers above are pre-fix. After the #164 eval fix (iter8, 16 seeds):
  genuine +0.422 (SEM .045) vs fake_random -0.109, fake_wrong -0.578; separation +0.531. See VS-TRANSFER-PROGRAM iter8.

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
