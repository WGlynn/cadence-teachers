# Cadence Experiment Results

Append-only, newest on top. Each row version-stamped. Insight is the number, pass or fail.

> **North star:** the V(S) TRANSFER PROGRAM (`~/cadence-lab/VS-TRANSFER-PROGRAM.md`) is the standing
> top-priority thread per Will 2026-10-07. EXP-08/09+ advance it.
>
> Note 2026-10-16 (program re-rank): EXP-12 to EXP-35 and EXP-37 to EXP-43 have no rows here; their
> write-ups are in experiments/EXP-XX.md and the program log (VS-TRANSFER-PROGRAM.md).

## EXP-69: marking a miss with salience= instead of charging it keeps replay open, but the marks still cost the chain learner (PARTIAL) - 2026-10-21
- **Version:** Cadence 0.84.3 + Unreleased, main `be372b8`, `lateral=-0.5` set explicitly (upstream #220). **Script:** `exp/EXP-69_salience_mark.py` (imports EXP-68). Pre-registered `2ee8712`, check PASS (recorded in `39753c6`). Hidden chain, natural signal, ctx5 96 / pen@.005 48 / sal@.005 96 / sal@1 48 lives, seeds 69_000+, 1,030 s.
- **Code read first:** `step(salience=)` reaches only the episodic memory. `_received` stores the reward (0.0) on the replay path, so the exact-zero test (`generic.py` 3223) does not stop at a marked miss; `_record_outcome` (3153-3154) makes it a known outcome written at value 0; the actor-critic (3385) never sees it; `live()` takes no salience.
- **Result:** sampled success ctx5 .459; pen@.005 .068 (-.365, .054); sal@.005 .337 (-.122, .046, 95% -.212 to -.032); sal@1 .353 (-.080, .068). sal@.005 minus pen +.280 (.047). Replay stopped at a miss: 0 of 3,756 successes (sal@.005) vs 422 of 428 (pen).
- **Verdict: PARTIAL (BOUNDARY; loop INCONCLUSIVE).** The mark avoids the replay harm and recovers about three quarters of the cost's loss; the zero-valued writes it adds still cost about .12, matching EXP-68's replay-restored cell (-.119). Candidate cause (untested): aliased place records. Memory track (#210 / #202). Detail: experiments/EXP-69.md.

## EXP-62i: the delayed-credit brain's price for late knowledge is exposure, and the cross-family gap sat in the zero (MOSTLY EXPOSURE) - 2026-10-20
- **Version:** Cadence 0.84.3 source at `c7dc2f0`. **Script:** `exp/EXP-62i_exposure.py` (EXP-62h's harness, budget 6, lesson 80; A and D1; stage-3 scaffold on every other lesson attempt). Pre-registered `f19bb0f`, pilot `f14333b` (N capped at 720), raw `8377298`, write-up `05e042f`. 720 fresh students (7_500_000+), 18,936 s.
- **Result:** late/early worth ratio (worth against the random-label null): A off .004, A on .394, D1 off .320, D1 on .039. phi_A +1.234 (95% +.910 to +1.674). A's rise +.390 (+.293 to +.489), mostly late worth (+.050, +.034 to +.067). D1 fell -.281 (-.411 to -.160).
- **Exploratory (stored rows of 62h and 62i):** the random-label null hurts D1 (-.119 / -.129 vs untaught) and not A. Against an untaught twin, D1's late-only teacher is worth about 0 and the A-D1 gap is +.037 (-.078 to +.147, 62h) / +.029 (62i off), not detected.
- **Verdict: MOSTLY EXPOSURE (loop: REFUTED for "the brain sets the rate").** Exposure sets A's price; the EXP-62h cross-family difference sat in the choice of zero. Detail: experiments/EXP-62i.md; EXP-62h carries an addendum.

## EXP-62h — scaled by how much each brain absorbs, the cross-family brain still prices late knowledge differently (RATE DEPENDS ON THE BRAIN) — 2026-10-20
- **Version:** Cadence v0.84.3 `8dc92d8`. **Script:** `exp/EXP-62h_scaled_rate.py` (EXP-62g's harness, budget 6). Pre-registered `043dd25`, pilot `0ae8bf9` (N 840 capped at 720). 720 fresh students (7_400_000+), 14,501 s.
- **Result:** scaled D (D / know-4 worth): A .874, C .937, D1 .610. A-C +.064 (95% -.025 to +.153); A-D1 -.263 (95% -.349 to -.180). Late/early worth ratio A .044, C .009, D1 .326. Same order on all three.
- **Verdict: RATE DEPENDS ON THE BRAIN (loop: CONFIRMED).** The exchange rate between kinds of knowledge depends on the judge's architecture even after scaling; the order does not. Both n 48 exploratory scaled readings (62g, 62b addendum) are withdrawn. Detail: experiments/EXP-62h.md.

## EXP-68 — the cost's harm is a switch in the memory's replay (MEMORY SWITCH) — 2026-10-20
- **Version:** Cadence v0.84.3 `8dc92d8`. **Script:** `exp/EXP-68_memory_switch.py` (imports EXP-67). Pre-registered + check PASS `90da30b`. Hidden chain, natural signal, 7 arms x 48 lives, seeds 68_000+, 1,358 s.
- **Result:** sampled success ctx5 .413; per-miss cost 1e-6 .068, 1e-4 .071, .005 .127. Memory blind to the cost (learner still pays it) .417. Replay restored only .294 (+.167 over pen); writes removed only .142 (+.015).
- **Verdict: MEMORY SWITCH (SUPPORTIVE; loop CONFIRMED).** The harm is the replay rule (`generic.py` 3221-3223: credit flows back only through steps whose reward is exactly 0.0), with the write rule (`reward != 0`, 3154) mattering only together with it. Off-program (memory track, #202 / #210). Detail: experiments/EXP-68.md.

## EXP-67 — a failure cost makes a teacherless learner timid at every size, and the size barely matters (TIMID AT EVERY SIZE) — 2026-10-20
- **Version:** Cadence v0.84.3 `8dc92d8`. **Script:** `exp/EXP-67_reward_only_penalty.py` (imports EXP-66). Pre-registered + check PASS `55dbccd`. Natural signal only, 13 arms x 96 lives, seeds 67_000+, 4,646 s.
- **Result:** hidden chain sampled success (ctx5 .349): per-miss cost .005 / .01 / .02 / .05 = .039 / .044 / .100 / .070 (all at least 4.6 SEM below); gated .10 / .09 / .07; repeat-miss-only .12 / .16 / .21 / .18 (penr minus pen +.08 to +.12, 2.4-3.1 SEM). Invisible chain: no arm moves (within 1.6 SEM). No arm helps at the 3-SEM bar.
- **Verdict: TIMID AT EVERY SIZE (BOUNDARY; loop INCONCLUSIVE).** The harm is flat over a tenfold range of cost, which looks like a threshold (candidate: #210's reward != 0 episodic-write eligibility; untested), not a dose. Off-program (memory track, #202). Detail: experiments/EXP-67.md.

## EXP-62g — a brain built differently ranks knowledge the same way; the gap scales with how much it absorbs (MAGNITUDE ONLY) — 2026-10-20
- **Version:** Cadence v0.84.3 `8dc92d8`. **Script:** `exp/EXP-62g_budget_cross_family.py` (EXP-62f's instruments and readings plus a decision-budget knob). Pre-registered `d241ca0`, sweep `f74362f` (untaught only: 6 decisions per attempt chosen), pilot `38bb2ed`. Lesson 80, 48 fresh students (7_200_000+), 1,315 s.
- **Result:** A (delayed-credit) early +.173 / late +.027 / know-4 +.204, D = +.146 (.037). D1 (memory-choice architecture with A's learning rule) +.414 / +.073 / +.451, D = +.341 (.038). D2 (arousal off) identical to D1 everywhere. Same order on all three. D_A - D_D1 = -.195 (3.6 SEM). Exploratory: scaled by each brain's know-4, late/early .16 vs .18 and D/know-4 .71 vs .76, no difference detected (wide intervals).
- **Verdict: MAGNITUDE ONLY (loop: INCONCLUSIVE).** The order of worth survives a change of architecture as well as size; the raw gap does not, and here it looks like scale (D1 absorbs about twice as much). EXP-62f closed at its pilot (ceiling) and is superseded by this. For #198: arousal inert; the memory-choice brain's near-blindness came from its default learning rule. Detail: experiments/EXP-62g.md.

## EXP-62b — instrument dependence: the two content-taking brains agree on order, differ on the early-vs-late exchange rate (MAGNITUDE ONLY) — 2026-10-19
- **Version:** Cadence v0.84.3 `8dc92d8`. **Script:** `exp/EXP-62b_instrument_order.py` (EXP-62's harness). Pre-registered `39ab1a4`, pilot `10a35a4`. Lesson 80, 48 fresh students (7_000_000+), zero = random-label null, 2,802 s.
- **Result:** A (delayed-credit) early +.264 / late +.064 / know-4 +.432, D = +.201 (.026). C (delayed-credit variant) +.339 / +.036 / +.458, D = +.302 (.029). B (default memory brain, actor step .1 = EXP-64) +.039 / +.007 / +.069, blind. D_A - D_C = -.102 (2.8 SEM). Same order on A and C (know-4 > early > late).
- **Verdict: MAGNITUDE ONLY (loop: INCONCLUSIVE).** The judge sets the exchange rate between kinds of contribution, not their order, on this task family. For #198: the actor step alone does not open the default memory brain to content. Next: a content-taking instrument from a different family (candidate EXP-62f). Detail: experiments/EXP-62b.md.

## EXP-66 — a cost for each miss, with and without the gate keyed on it: the gate adds 18 / 3 over the cost, never holds a correct move; gains need a teacher — 2026-10-19
- **Version:** Cadence v0.84.3 `8dc92d8`. **Script:** `exp/EXP-66_penalty_gate.py` (imports EXP-65 / 63 / 56). Pre-registered `f8d0be0`; check PASS and pilot (p = .05 by stage-1 forecast-error AUC .774) `d38cbda`. Seeds 66_000+, 768 lives.
- **Result (clean greedy passes, discordant pairs):** invisible pooled ctx5 11 / out5t 16 / pen 21 / peng 36; peng vs pen 18 / 3 (p .0015); pen vs ctx5 17 / 7 (p .064); peng vs out5t 23 / 3; out5t vs ctx5 12 / 7 (p .36, was 18 / 4 on 0.83). Hidden pooled peng vs ctx5 18 / 0, peng vs pen 10 / 2 (p .039). Visible pooled peng vs ctx5 8 / 5 (no loss). peng held 58,563 invisible-chain decisions, all misses. All but one invisible-chain clean pass came with corrective teaching (reward alone: 1 / 0 / 0 / 0); under reward alone the penalty lowers sampled success (hidden .365 -> .076).
- **Verdict: SUPPORTIVE (loop: CONFIRMED); P0 failed (the oracle gate's gain did not survive 0.84.x).** For #202: the signal is the reward argument of step(), holding a non-boundary decision whose reward is below 0. Queued EXP-67 (reward-only penalty grid). Detail: experiments/EXP-66.md.

## EXP-62e — a non-superiority margin: the skill price replicates a fourth time; anti-echo carries information and fails the margin by .002 — 2026-10-19
- **Version:** Cadence v0.84.3 `8dc92d8` (same version as EXP-62d; no identity gate needed). **Script:** `exp/EXP-62e_margin_zero.py` (EXP-62's harness unchanged, EXP-62d's analysis plus the margin rule). Pre-registered 2026-10-19 (`cb60045`). Lesson 80, 216 fresh students (6_800_000+), zero = mean of {null, untaught, random, anti-echo}, run 3,784 s.
- **Result:** know-1..4 +.069 / +.146 / +.254 / +.416, ordered, Spearman .614 (n 864); know-1 beats null 7.5 SEM, random 7.2, untaught 5.6, anti-echo 4.1; fake pay .024. Upper bounds vs margin .031: null -.004, untaught +.016, random -.003, **anti-echo +.033**, wrong-chain -.079, echo -.118. Exploratory: anti-echo's labels are right .25 vs random's .20 in all four runs (by design: labels follow mistakes); pooled over 432 students anti-echo +.016 (3.4 SEM), random -.014; anti-echo earns about 38% of know-1's worth edge over random and carries about 38% of its label-information edge.
- **Verdict: BOUNDARY 4/5 (loop: INCONCLUSIVE).** Non-superiority failed on anti-echo by .002. The four zero-point failures share one cause: the declared uninformative class held an informative arm. Last zero-point redesign as pre-registered; EXP-62b next. Run outside the 1-per-24h cap on Will's live instruction. Detail: experiments/EXP-62e.md.

## EXP-62d — pooled uninformative zero: the skill price replicates a third time (Spearman .64, separation test passes); abstain trips the 2-SEM rule — 2026-10-19
- **Version:** Cadence v0.84.3 `8dc92d8` (run gate: EXP-62c students 0-1 bit-identical on it, actions + labels, all 10 arms). **Script:** `exp/EXP-62d_pooled_zero.py` (EXP-62's harness unchanged). Pre-registered 2026-10-17 (`8b46525`). Lesson 80, 72 fresh students (6_600_000+), zero = mean of {null, untaught, random, anti-echo}.
- **Insight:** know-1..4 +.070 / +.140 / +.249 / +.421 (SEMs .016-.020), Spearman .636 (n 288); know-1 beats every uninformative arm by >= 2.07 SEM paired; wrong-chain -.089, echo -.172; fake pay .007. Untaught +.029 (2.57 SEM) above the pooled zero; null and random -.017. Exploratory: pooled over EXP-62/62c/62d (216 students) every uninformative arm sits within +-.015 of the zero and know-1 is +.065 (7.2 SEM); permuting the uninformative arms within student shows the 2-SEM rule false-fails ~9% at n 72 and n 216 alike.
- **Verdict: BOUNDARY (4/5; loop: INCONCLUSIVE on the zero-point criterion).** The measure separates skill from noise three times out of three; the 2-SEM zero rule is the wrong test (significance, not equivalence). EXP-62e (non-superiority margin 1/32, 216 students) pre-registered as the last zero-point redesign. Detail: experiments/EXP-62d.md.

## EXP-62c — fresh students, zero = anti-echo: the skill price replicates (Spearman .61); the zero point is a noise band — 2026-10-17
- **Version:** Cadence v0.83.0 + Unreleased `6499e56`. **Script:** `exp/EXP-62c_best_fake_zero.py` (EXP-62's harness, declared settings). Pre-registered `aa364c5`. Lesson 80, 72 fresh students, committed zero = anti-echo.
- **Insight:** know-1..4 +.073 / +.162 / +.300 / +.436, Spearman .612 (n 288); wrong-chain -.071, echo -.095; random +.027, abstain +.032 (both about 1.4 SEM); fake pay .034. Anti-echo fell below the null (-.012), reversing EXP-62. Exploratory: know-1 beats every uninformative arm by >2 SEM paired; vs a pooled uninformative zero all fakes sit within +-.02.
- **Verdict: BOUNDARY (4/5; loop: INCONCLUSIVE on the zero-point criterion).** The point-estimate "every fake <= 0" rule against a single noisy fake fails by chance; EXP-62's leak reading withdrawn. EXP-62d (pooled zero, noise allowance, separation test) pre-registered and queued. Detail: experiments/EXP-62c.md.

## EXP-62 — Noesis-lite v2: transfer prices skill on a content-taking brain; the zero point is the best fake, not noise — 2026-10-17
- **Version:** Cadence v0.83.0 + Unreleased `6499e56`. **Script:** `exp/EXP-62_content_market_committed_null.py`. Pre-registered `e6d6d82`; pilot + window decision + amendment A1 `aaafac7`. EXP-58's delayed-credit brain, EXP-52's market, 72 shared students x 10 twins, lesson 40 primary (window rule), 80 exploratory; worth = taught minus the committed counterfactual (pooled stronger of null / untaught; it was the random-label null at both lengths).
- **Insight:** lesson 40: know-1..4 +.054 / +.068 / +.138 / +.236 (ordered), Spearman .400 (n 288); random -.028, wrong-chain -.054, echo -.075, abstain -.016, anti-echo +.023 (SEM .019); fake pay .041. Lesson 80 (exploratory): ladder +.059 to +.391, Spearman .530, anti-echo +.031 (1.6 SEM). Worth tracks label correctness across all 8 arms (r .99, descriptive); anti-echo's labels are right .25 vs random .19 because the corrective schedule leaks which action just failed.
- **Correction 2026-10-17:** the anti-echo leak reading did not replicate on fresh seeds (EXP-62c); withdrawn.
- **Verdict: BOUNDARY (4/5; loop: INCONCLUSIVE on the zero-point criterion, every other CONFIRM criterion met).** First run where the measure prices skill on a content brain against a committed null; the remaining gap is the zero point (best declared fake, not uniform noise). EXP-62c queued. Detail: experiments/EXP-62.md.

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
