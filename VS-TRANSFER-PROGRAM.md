# V(S) TRANSFER PROGRAM — the standing north star of the Cadence experiment loop

> Will, 2026-10-07: *"continue spending computing power to try solving the problem until we get
> there ... this is the Cadence loop from now on."* The daily Cadence experiment loop
> (`cadence-experiment-loop`) advances THIS program first, every fire, until the solved-criteria
> below are met or a hard wall is proven. Generic queue items are secondary.

Keep every claim honest-floor-first ([F·teammate-not-salesman]). Numbers, not hopes. Version-stamp
against the live clone (`~/_cadence_study`, kept at HEAD by the monitor loop).

---

## THE PROBLEM (grounded — do not re-derive from memory)

Canonical statement: `~/Desktop/Research/vs-value-measurement-problem-paper-2026-10-07.md`.
Noesis grounding: `~/noesis/ARCHITECTURE.md §v(S)` + `~/noesis/docs/research/WASH-PROBLEM-INDEX.md`.

The impossibility core (a conservation law, not a cleverness gap): **any INTERIOR signal** — v(S)
computed from graph topology + content statistics — **is worth-blind.** A genuine collaboration and a
matched acyclic fake score identically (measured 0.0% separation, `node/examples/wash_sim.rs`). You
cannot out-feature it; the fake matches every new feature by construction.

Two irreducible pieces must come from OUTSIDE the graph:
1. a **capital-rooted independence anchor** (independence that costs money to fake, not a free key);
2. a **learned v(S) on exogenous realized-use labels, isomorphism-invariant** under structure-
   preserving relabeling.

## OUR ANGLE (angle 3 of the paper — "squarely your domain")

**Measurable transfer instead of declared citation.** If nodes are LEARNING AGENTS (Cadence brains),
the edge a->b means "b ingested a as a witness and b's measurable behavior changed by delta on a
held-out task", verified by **twin-brain ablation** (snapshot b, feed one twin the witness, compare
twins on a held-out exogenous task). Transfer is NOT worth-blind the way citation is: the consequence
is a measured behavioral fact inside b, not topology. A fake that produces the delta had to carry
real task-information -> "faking" collapses into "contributing."

The honest catch (not hidden): this RELOCATES worth to exogenous-task-selection. It works only if the
held-out task is exogenous and informationally-disjoint from the adversary. We do NOT claim to have
built the exogenous-task oracle; we test whether, GIVEN one, transfer measurement separates — and
how robustly.

Two measured lessons (added 2026-10-16):
1. Zero point: an untaught twin pays a fake for jolting a stuck student (EXP-49, +.179). Price against a
   form-matched null on the same instrument (EXP-52; also EXP-16/18), and check that abstaining is not
   paid against that null.
2. Instrument validity: the measuring brain must take in content (EXP-61 +.016 vs EXP-58 +.469 under the
   same protocol), and the choice of brain moves the price.

---

> **Design note 2026-10-16 (Will, designed not measured):** layered anchors, brains as instruments with an OPH/DI obstruction readout, and exogeneity relative to the attacker. Local technical note `DESIGN-NOTE-layered-anchors-2026-10-16.md` (not published); plain version on Will's Desktop.

## SOLVED-CRITERIA (when does the loop stop / ping Will)

A chain of increasingly hard bars. Each is a real milestone; ping Will on each crossing.

- **M1 — separation exists.** Measured transfer separates genuine from a surface-matched fake on an
  exogenous task (genuine transfers, fakes ~0), robust across seeds/sizes.
  [STATUS: CROSSED on the K=8 bandit (iter2; rerun iter8 after the #164 fix): genuine +0.422 (SEM .045)
  vs fake_random -0.109, fake_wrong -0.578, 16 seeds, bit-identical on 0.78-0.83 and on the #203 head.
  Robust across sizes is NOT shown (K=4 pre-fix and K=8 only, one module size). Off the bandit: on the
  default 0.83 memory brain, genuine does not separate from a random-label fake against the form-matched
  null (EXP-52: know-4 +.013, Spearman .06), and against an untaught twin a random fake earns +.179
  (EXP-49). Untested on a brain that takes in content (EXP-62).]
- **M1b: content validity.** Before pricing on any instrument, show that the instrument takes in
  content: know-max minus the form-matched null > 0 by 2 SEM, with that null and the counterfactual rule
  committed in advance. Evidence so far: fails on the default 0.83 memory brain (EXP-52/53/55/61); holds
  on the delayed-credit brain (EXP-58, +.469, 11 SEM). (Added 2026-10-16.)
  [STATUS 2026-10-27: CROSSED on the delayed-credit brain on two releases, v0.84.3 (EXP-73) and 0.89.0 (EXP-77b). v0.84.3 (EXP-73, 216 fresh students): know-1..4 +.057 / +.163 / +.269 / +.436, Spearman .638; zero = measured-chance arms (labels right .200 / .203); every knowledge-free arm under the 1/32 margin; know-1 beats anti-echo by 4.0 SEM; knowledge-free pay .023. Fifth zero attempt (disclosed); EXP-62e's original rule also passes on this data. 0.89.0 under its founder defaults (EXP-77b, 216 fresh students, harness ported, zero admitted by construction): know-1..4 +.075 / +.157 / +.249 / +.385, Spearman .549; every knowledge-free arm under the 1/32 margin (untaught +.021 the highest); know-1 beats anti-echo by 5.7 SEM; knowledge-free pay .005; the old per-run interval check also passes (null .1993, random .1987). EXP-77 (0.88.1) is VOID by that interval check and not re-scored. Limits: one instrument, one chamber, one lesson length.]
- **M2 — feature-matched fake.** Separation survives a fake matched on ALL interior features the
  paper's impossibility uses (novelty, synergy, acyclic topology, content-stats), not just surface
  stats. This is the adversary class of wash_sim.rs. Here it is matched by construction (EXP-10's
  interior is identical); no interior scorer from wash_sim.rs has been run in the harness yet.
  [STATUS: ADDITIVE CROSSED on the bandit (EXP-10, iter8 rerun: genuine +0.375 vs fake -0.479, gap
  +0.854, linear in genuine fraction). SYNERGY crossed for data-channel synergy (EXP-18, +0.375, about 4
  sigma) and for learned sequential composition (EXP-19 N=300, +0.72 SEM .18; about 12 effective
  outcomes; 4/12 founders never learn the chain). XOR-style representational synergy is not
  representable on the substrates tried (EXP-12/12b-f, 14/14b; the search was not exhaustive). Recorded
  as a boundary of the instrument: it under-pays combinations and opens no wash hole.]
- **M3 — isomorphism-invariance.** The transfer measure provably satisfies v(S)=v(phi(S)) for any
  structure-preserving relabeling phi of everything v may see. (The paper's formal success criterion.)
  [STATUS: EMPIRICAL ONLY, not proven (EXP-16, iter10). On the bandit the paired genuine-minus-fake is
  +0.500 in 95/96 cells. Limits: the constant is forced by learning at ceiling; one random context
  permutation per task was tested (not the 8!-element group); the instrument was not relabeled; the
  paired form was chosen after seeing the data. The raw twin delta moves by up to 0.500 per instrument.
  This does not discharge Noesis gate WASH-PROBLEM-INDEX row 9 (learned v(S) over graph features).]
- **M4 — coordinated-prior robustness.** Separation holds against a coordinated-but-wrong prior past
  the peer-prediction crossover (paper reports gamma*=0.70 for correlated-agreement). Transfer should
  beat that because it reads a causal delta, not agreement.
  [STATUS: CROSSED on a matched comparison, by construction (EXP-15, iter9). Transfer: genuine +0.448 vs
  ring -0.052 / +0.073 / +0.198 at a_R .5 / .625 / .75, independent of c because the transfer arm never
  reads c. PP flips at c* about .5 (run on noiseless rule vectors, no SEM; the margin at a_R .75 is
  +0.004). The EXP-09 curve after the fix is proportional (0.625 +0.125, 0.75 +0.135, 0.875 +0.281, 1.0
  +0.469). The iter4 claim "<=0.75 ~zero" is RETRACTED. The paper's gamma*=0.70 is on a different axis.
  Still owed: the EXP-09 low-gamma half (0-0.5) after the fix, and PP on brain behaviour.]
- **M5 — exogenous anchor honesty.** State precisely what exogenous ingredient the measure still
  assumes (the disjoint task / capital-independent reference set) and whether any part of it can be
  sourced from a cost-bearing real signal rather than assumed. This is the irreducible-1 anchor; may
  end as an honest boundary ("this is what still must come from outside"), which is itself a result.
  [STATUS: STATED AS A BOUNDARY (iter11, EXP-17, M5-EXOGENOUS-ANCHOR.md). q* = 0.500 is set by the
  symmetric design (a_R .5, uniform adversary pool, saturated learning); it is not a measured property.
  No cost-bearing task source is built. Derived from EXP-17's own model, not measured: an adversary that
  knows T and supplies only the states where its rule disagrees flips prices at
  q* = (1 - a_R)/(2 - a_R), which is .33 at a_R .5, so .5 is an upper bound. RESTATED: the measure assumes three outside
  ingredients, not one: the task T, the instrument I (the receiving brain) and the null N (the
  counterfactual contribution) (EXP-49/52/58/61).]

"Solved" = M1, M1b, M2-M4 crossed with measured robustness + M5 stated with T, I and N.
Realistically this is a long program; the loop's job is to advance it one honest rung per
fire and never fake a rung.

---

## RUN GATE (every experiment, before any run longer than ~10 min) — added 2026-10-09
Cause of ~1/3 of this program's failed runs: effect outside the visible window (too small = noise,
too big/easy = ceiling). Fill these four lines in the iteration entry BEFORE launching:
1. PREDICTION: the expected result, written down.
2. WINDOW: the key knob (budget / population / seeds / difficulty) swept at >= 2-3 values in a pilot
   UNDER THE EXACT RUN CONDITIONS; the chosen value shows the effect clearly, not at 0% or 100%.
3. VARIANCE: the thing being selected or compared actually varies (no EXP-23 repeat).
4. METRIC: the score cannot be passed by a degenerate policy (no EXP-19 fed-only repeat).
5. CHAIN (added 2026-10-10 after iter27): name the mechanism chain (knob -> signal -> estimate -> choice -> outcome)
   and print each link per arm in the pilot. A smoke test (does it run) is NOT the pilot. A link that never moves
   (an estimate stuck at its prior) is a design bug: fix it, do not run.
If any line fails, redesign instead of running.
AFTER every experiment (Will 2026-10-10): write `experiments/EXP-XX.md` (Summary + Reflection, template in
`experiments/TEMPLATE.md`), including nulls, voids and reruns. `python experiments/check.py` must pass.

## FRONTIER (update every fire — one line: where we actually are)

2026-10-29 (iter50, EXP-05b SUPPORTIVE, on 0.91.1 c9c8080, library & tooling): a brain saved mid-life (pending action, mid-wait, after either reset) continues bit for bit in a fresh process, and deepcopy forks equal save/load forks, on three brains (apical included) over 108 cuts. Off the V(S) ladder; no milestone moves. The V(S) program is still waiting on Will: CAL-1 (draft in experiments/CAL-1.md), CAL-2, or the registered zero test.

2026-10-27 (iter49, EXP-77b CROSSED, on 0.89.0 81345d8): **M1b crossed on the current release.** Will lifted the hold; the full run finished 216/216 (3,284 s). All six CONFIRM criteria hold at 0.89.0's founder lateral: know-1..4 +.075 / +.157 / +.249 / +.385, Spearman .549, every knowledge-free arm under the 1/32 margin (untaught +.021 the highest), know-1 beats anti-echo by 5.7 SEM, knowledge-free pay .005; zero admitted by construction. The old per-run interval check also passes (null .1993, random .1987), so the rule change did not do the work. EXP-77 stays VOID. M1b is now crossed on v0.84.3 (EXP-73) and 0.89.0 (EXP-77b), one instrument. Next: the next rung on the current API (instrument dependence, EXP-62b / 62h / 62i line), or CAL-1 / CAL-2 (Will-gated).

2026-10-27 (iter49, EXP-77b PRE-REGISTERED, HELD, on 0.89.0 81345d8): Will's go for admission by construction (pre-reg 4eb09f6). Port gate IDENTICAL on 0.89.0 (the new recall position term does not reach this brain); construction audit ADMITTED; pilot stop check passed (know-4 +.431). Full run held by Will (token budget to the ETM doc sweep). No milestone moves. Next: the full run when Will lifts the hold.

2026-10-26 (iter48, EXP-77 VOID, on 0.88.1 d66f8ea): the EXP-62 harness is ported to 0.85+ (`scales={'trace': 12.0}`; gate IDENTICAL with lateral -0.5). At 0.88.1's founder lateral every M1b criterion holds (know-1..4 +.060 / +.147 / +.250 / +.397, Spearman .581, know-1 beats anti-echo 4.1 SEM), but the pre-registered zero admission check failed: null labels right .1958, interval [.1919, .1997], though uniform by construction (2.1 SE chance draw; the check false-fails ~10% of runs). VOID kept. M1b stays crossed on v0.84.3 only. Next (Will's go): EXP-77b, admission by construction plus the old check reported, fresh seeds.

2026-10-25 (iter47, EXP-73 CROSSED, on v0.84.3, Will's go): **M1b crossed**, the first milestone since 10-09. Transfer prices skill on the delayed-credit brain against a measured-chance zero (know-1..4 +.057 / +.163 / +.269 / +.436, Spearman .638), every knowledge-free arm under the margin, know-1 beats anti-echo by 4.0 SEM. Fifth zero attempt, disclosed; EXP-62e's original rule also passes on this data. Same night, off-ladder: EXP-71/72/72b/74/75 on Bernhard's V0.5B runner; upstream docs adopted EXP-72 (main d66f8ea). Next: port the EXP-62 harness to the current API and re-cross on a current release.

2026-10-23 (iter46, EXP-05 VOID by its own check, on 0.85.1 + 41 main 4ac887c, library & tooling): the snapshot/restore identity test stopped at check k4. After youth both test brains settled on one greedy action, so 6 of 14 continuations had a single action, and no data life ran. In the check life alone, every fresh-process restore and every deepcopy / save-load fork ended on the uninterrupted brain's checkpoint bytes (14/14). Event records matched in 52 of 56; the other 4 differ only in `last_arousal`, which a load clears by documentation. Off the V(S) ladder; no milestone moves. Next: EXP-05b (behaviour-piloted task, `last_arousal` compared at `live` only).
2026-10-22 (iter45, EXP-69b VOID, check on v0.85.0): Cadence 0.85 moved the episodic machinery into `memories.EpisodicRecords` (`4894ef0`), so the EXP-68/69 harness no longer imports and the pre-registered code gate voided the run before any data. EXP-08 on 0.85.1 still SEPARATES (+0.422 / -0.148 / -0.578; pinned to the 0.84.3 laws it is byte-identical). Off the V(S) ladder; no milestone moves. Next: port the harness to `EpisodicRecords` with an equivalence reading, then EXP-69c / EXP-70 (both need Will's go; 0.85.1 adds `live(salience=)`).
2026-10-21 (iter44, EXP-69 PARTIAL, on 0.84.3 main be372b8, memory track): on the reward-only hidden chain, marking each miss with `step(salience=)` instead of a .005 cost keeps the memory's replay open (0 stops in 3,756 successes) and recovers +.280 of a .365 loss, but still sits .122 below no cost (95% .032 to .212) because each mark writes the miss as a zero record. Off the V(S) ladder; no milestone moves. Next: EXP-70 (is the residual the aliasing?), and the #210 docs addendum (Will-gated).
2026-10-20 (iter43, EXP-62i MOSTLY EXPOSURE, on 0.84.3 source c7dc2f0): scaffolding half the lesson attempts to stage 3 moved the delayed-credit brain's late/early ratio from .004 to .394 (phi_A +1.23, 95% +.91 to +1.67). D1's ratio fell to .04 because its random-label null stopped hurting it; against an untaught twin the EXP-62h cross-family gap is not detected (+.037, 95% -.08 to +.15). The rate is set by exposure and by the zero, not by the brain alone. Next (Will-gated): a registered zero test (untaught as a second zero, per-stage accuracy stored).
2026-10-20 (iter42, EXP-62h RATE DEPENDS ON THE BRAIN, on v0.84.3): powered (n 720) on one task, scaled by each brain's own range, the cross-family brain prices late knowledge at about a third of early, the delayed-credit brains at almost nothing (scaled D .61 vs .87, difference -.26, 95% -.35 to -.18); near relatives not different (+.06, -.03 to +.15). Order holds across size and architecture; the exchange rate does not, even scaled. Both n 48 exploratory scaled readings withdrawn. Next: test whether the rate difference is exposure (late-only teachers only reach students who get far), by scaffolding students to stage 3.

2026-10-20 (iter41, EXP-62g MAGNITUDE ONLY, on v0.84.3): a cross-family brain (memory-choice architecture with the delayed-credit brain's learning rule), on a task made harder by an untaught-only sweep (6 decisions per attempt), ranks early / late / full knowledge exactly as the reference does; the early-late gap is 3.6 SEM bigger, but it absorbs about twice as much of everything, and scaled by that the exchange rate agrees (.16 vs .18, wide intervals). The order of worth holds across size and architecture on this task family. EXP-62b re-read scaled: its near relatives still differ (.46 vs .66), so scaling is not a general fix. Next: a scaled-rate test with both kinds of pair.

2026-10-19 (iter40, EXP-62b MAGNITUDE ONLY, on v0.84.3): two content-taking brains (A delayed-credit, C its variant) rank equal-size early / late teachers identically but price late knowledge at about 1/4 vs 1/9 of early (D +.201 vs +.302, 2.8 SEM apart); the default memory brain with only a lower actor step (EXP-64) is blind. The judge sets the exchange rate, not the order, on this task family. Next: an instrument from a different family.

2026-10-19 (iter39, EXP-62e BOUNDARY 4/5, on v0.84.3): fourth replication of the skill price on 216 fresh students (know-1..4 +.069 / +.146 / +.254 / +.416, Spearman .61, know-1 beats every uninformative arm by >= 4.1 SEM, fakes .024 of pay). The margin rule failed on anti-echo (+.023, upper bound .033 vs .031). Mechanism (exploratory, logged fields): anti-echo's labels are right .25 vs .20 for random labels in every run, so it was never uninformative; the instrument prices it in proportion (about 38% of know-1's information edge, about 38% of its worth edge). Zero-point work closed as pre-registered; next rung EXP-62b.

2026-10-19 (iter38, EXP-62d BOUNDARY 4/5, on v0.84.3): third replication of the skill price on a third disjoint student set (know-1..4 +.070 / +.140 / +.249 / +.421, Spearman .64, know-1 beats every uninformative arm by >= 2.07 SEM paired, fakes .007 of pay); the pooled-zero 2-SEM rule failed on abstain (+.029, 2.57 SEM). Diagnosis (permutation of the real data): that rule false-fails ~9% at any n, so it tests significance where the question is equivalence. EXP-62e pre-registered: non-superiority margin 1/32, 216 fresh students, declared the last zero-point redesign; then EXP-62b.

2026-10-17 (iter37, EXP-62c BOUNDARY 4/5): on 72 fresh students the skill price replicates and strengthens (know-1..4 +.073 / +.162 / +.300 / +.436, Spearman .61, fakes .034 of pay; know-1 beats every uninformative arm by >2 SEM paired). The zero-point criterion failed again from the other side (zero = anti-echo drew low; random and abstain +.03). EXP-62's leak reading is withdrawn: the uninformative arms are a +-.03 noise band at n 72. The binding issue is now the decision rule, not the measure: EXP-62d (pooled zero + noise allowance + separation test) is pre-registered and queued.

2026-10-17 (iter36, EXP-62 BOUNDARY 4/5): on the delayed-credit brain, against a committed null (the random-label null won the pooled rule), transfer PRICES SKILL: know-1..4 +.054 / +.068 / +.138 / +.236, ordered, Spearman .40 (n 288); wrong-chain, echo, random and abstain all below zero; fakes take .041 of pay. Only the zero point failed: anti-echo +.023 (1.2 SEM), and worth tracks label information across all arms (r .99), so the measure prices the elimination bit the corrective schedule leaks. M1b not formally crossed. Binding question now: price against the best fake in a declared class (EXP-62c, fresh seeds), then instrument dependence (EXP-62b).

2026-10-16 (re-rank, no new rung): no milestone has moved since iter13 (10-09).

Status on the bandit:
- M1 and additive M2 are crossed.
- M4 is crossed, but its immunity to coordination holds by construction.
- M3 is empirical only: one permutation per task, learning saturated.
- M5 is a boundary whose q* = .5 is set by the symmetric design.

Off the bandit, the measure failed its first richer substrate:
- Against an untaught twin, a random-label fake earned +.179 (EXP-49).
- Against a form-matched null, fakes priced at or below 0, but skill was invisible on the default brain: know-4 +.013, Spearman .06 (EXP-52).
- Content reaches only the delayed-credit brain: +.469, 11 SEM (EXP-58), vs +.016 on the default brain (EXP-61).

So v(S) depends on the instrument I and the null N, not only the task T. The binding open question is whether transfer prices skill on a brain that takes in content, against a committed null. That is EXP-62: ready since 10-14, not yet run.

2026-10-13 (iter34): EXP-44 NULL (pre-registered on 0.81; finished on a pinned worktree after upstream removed the gene): on graded text neither a readout operating point (0.81's intrinsic plasticity, a smaller actor step) nor twice the width lifts a Cadence brain past the control (.253; gene .183 / .068 with 1 of 3 brains unsettled each, actor .229, wide .213); the table on the same grades stays at .346. By the decision rule the remaining gap is exploration. Teaching track the same day: EXP-45-48 on the Stone Age chain (operating point decides whether a brain can be taught at all; 0.83's episodic memory makes the default brain learn the chain and replicates upstream's table).

2026-10-10 (iter33): EXP-43 BOUNDARY (pre-registered, revised after a pilot): a teacher that grades how good the guess was (not whether it was right) takes a Cadence brain to .254 on held-out Alice with 3 characters (right/wrong .202, always space; told-the-answer bigram .292); a lookup table on the same judged grades reaches .346, past the bigram. Learning from every right/wrong outcome collapses onto space (9/9). On text the limit is now the brain, not the grade; 4 runs collapsed onto action 0, mechanism not pinned down.

2026-10-10 (iter32): EXP-42 BOUNDARY (pre-registered): learning Alice one character at a time from right/wrong grades alone, a Cadence brain reaches .225 held out (always-space .202; graded lookup table .231-.242; told-the-answer bigram .291, 4-gram .502). A grade carries <= 1 bit per character; contexts grow as 28^n. EXP-40 (brain size) stopped by Will at 30/144 runs, resumable; iter31 left to it.

2026-10-10 (iter30): EXP-39 SUPPORTIVE (pre-registered): on a 4-step prerequisite chain a grading teacher gets 12/12 students solving in 40 episodes; sparse reward alone needs ~1500 (11/12); hidden inventory = unlearnable; a reverse curriculum under sparse reward CAUSES the collapse onto late-chain moves (0/12 at every budget). Our earlier 'teach backwards' advice is withdrawn.

2026-10-10 (iter29): EXP-38 SUPPORTIVE: never re-teach an item the student already passed. Attacker soak .69 -> .30, honest .927 -> .946 (~2.6 SEM); total fake pay unchanged (ledger-capped, only moves to the colluder); repeat-rate penalty adds nothing; an adaptive attacker blinds the detector yet stays contained. EXP-36's fake-pay metric counted only the colluder.

2026-10-10 (iter28): EXP-35b SUPPORTIVE with correct credit (CREDIT=item, 12 seeds): share 0.9 vs 0 doubles Discover pay per move (.0036 -> .0071), raises late discovery .51 -> .63 (~4 SEM) and new discoveries 54.0 -> 57.8 (~3 SEM); accuracy +.021 (~2 SEM, no claim). PI controller fell to .14 (its set point shrinks by construction). iter27 NULL superseded as a credit-design failure.

2026-10-10 (iter27): EXP-35b rerun (patched credit) = NULL, and the share channel is STARVED, not refuted. Royalty on discoveries is ~1/40 of direct pay, so estD never leaves PRIOR (.0100 at alpha 0, .0099 at 0.9); discovery rate is set by PRIOR vs estT, not by the share. PI controller drove alpha to 0. Next: open the effect window (pilot royalty size / PRIOR) before any rerun. Pedigree claims unchanged: record, attribution, teaching price.

2026-10-10 (iter26): EXP-36 had a duplicated-lesson bug. Fixed rerun: the probe-fooling sandbagger is worse than logged (fake pay .15, honest knowledge .83 vs .95 without it); reciprocity recovers throughput (.91) but not fake pay. Lists still catastrophic (~80x). Next: repeat-need detection on top of reciprocity. EXP-35b still VOID, rerun Will-gated.

2026-10-09 (iter25): EXP-35b VOID (credit bug: the share never reached the move choice). Its numbers (all arms .83-.85, discovery .34-.39) measure nothing about the share. The staged CREDIT=fixed patch still leaks (founder-item royalty counted as Discover pay, positive-only guard, stale 0.05 priors, PI windup; review 2026-10-09). Fix those, then rerun on Will's go. Pedigree claims that stand: record, attribution, teaching price.

2026-10-09 (iter21): Network ceiling LIFTED (.79 -> .99): plateau was stale teaching; the provenance ledger (notes) fixes it. Partner choice only speeds the start. Next: partner choice on the fixed network, then EXP-35 pedigree-share controller.

2026-10-09 (iter19): Teaching ability is heritable and evolves; children's doing already selects it (DO arm best). Pedigree price = teacher INCENTIVE, not a breeding signal. Specialist teachers >> overconfident ones (+0.2). Over-teaching hurts (8/8 -> 1/8). Next: replicate seeds for EXP-27.

2026-10-09 (iter18): Teaching is NOT redundant (40 trips: taught 8/8 vs self-taught 1/8). Evolving better teachers still unshown (underpowered null); pedigree-only selection erodes knowledge -> price on doing AND pedigree. Powered run next.

2026-10-09 (iter16): Rung 3 NULL. Selecting by teaching = selecting by doing here; child failures are student-side (seed), so iter15 "doing != teaching" is RETRACTED. Teaching ability must become a varying heritable trait (inherited teaching STRATEGY, or a task where off-path guidance matters).

2026-10-09 (iter15): GENERATIONS WORK by parent-grading (94% per-generation fidelity over 5 gens; label teaching fails 0/20). Doing != teaching measured: 5/88 perfect doers raise failing children. Next: rung 3, select parents by teaching score vs doing score.

2026-10-09 (iter14): TEACHING GAME rung 1 WORKS. Teacher brains paid by measured student gains find key/door 12/12 runs; Shapley fastest (round 39) and budget-balanced; leave-one-out pays 1.83x. Next: free-rider game, then generations.

2026-10-09 (iter13): M2-SYNERGY CROSSED for learned sequential composition on Cadence key-door (EXP-19 N=300: alone 0, together +0.58, synergy ~4 sigma, Shapley ~even, fakes 0). XOR-style synergy still open. Now building the teaching game (EXP-21 table -> EXP-20b learning teachers).

2026-10-08 (iter12): M2-SYNERGY CROSSED for data-channel synergy (EXP-18: synergy +0.375 ~4 sigma, Shapley splits 50/50, LOO overpays 1.7x). Learned-composition synergy (#115 / XOR wall) still OPEN.

2026-10-08 (iter11): M5 STATED AS BOUNDARY (EXP-17: task-pool capture flips at q*=0.5; see M5-EXOGENOUS-ANCHOR.md). Open: M2 XOR-style synergy, a proof for M3, scale (item 4), and any M5 construction; M4 is immune to c by construction.

2026-10-08 (iter8, post-#164 eval fix): **M1 CROSSED (stronger, +0.42 vs fakes <=-0.11) · M2 ADDITIVE CROSSED (gap +0.854) · M3 EMPIRICAL ONLY (EXP-16: paired 95/96 cells; one permutation per task; learning saturated) · M4 CROSSED on a matched PP baseline, immune to c by construction (EXP-15: PP flips at c~0.5 coordination, transfer unaffected given exogenous T; cost = M5) · M2 SYNERGY OPEN.** Numbers below this line are pre-fix.

Pre-fix: **M1 CROSSED · M4 SUPPORTIVE (clean curve) · M2 ADDITIVE CROSSED · M2 SYNERGY OPEN.**
M1 (iter2): genuine transfer +0.219 (~3.6 sigma) vs surface-matched fakes ~0/neg; task-specific.
M4 (iter4): monotonic gamma curve, worth only at gamma>=0.875. M2-additive (iter5, EXP-10): in a
multi-mind collaboration that is interior-INDISTINGUISHABLE, transfer attributes worth PER-CONTRIBUTOR
(+0.250 genuine vs -0.292 fake, gap +0.542) and scales ~linearly with genuine fraction -- the Shapley
per-node property, measured. **NEXT RUNG = M2-SYNERGY** (super-additive, combination-only worth):
NOT representable in a small bandit -> needs a different task/substrate (compositional perception, or
a richer brain where two witnesses jointly enable a held-out task neither enables alone). Also owed:
M4 matched peer-prediction baseline; M3 isomorphism-invariance. M2-synergy is the hard open core.

---

## ITERATION LOG (append-only, newest on top; version-stamp each)

### iter50 (2026-10-29): EXP-05b, mid-stream snapshot/restore byte identity on 0.91.1: SUPPORTIVE
- Cadence 0.91.1, main `c9c8080`. Off the V(S) ladder (library & tooling): the program waits on Will-gated CAL-1 / CAL-2 / the registered zero test, so the loop took the best ready queue item. Pre-registered `96c111a` after a three-lens review that caught an unpinned task, a wrong cache premise and a weak variance guard. Check PASS; all three arms CONFIRMED pooled and on each of three brains (plain, learned code, apical): 108/108 restores, 108/108 deepcopy and 108/108 save/load forks exact over 96,408 event records plus final bytes. Harnesses may fork with `deepcopy`. No milestone moves. Write-up experiments/EXP-05b.md, results row, atlas iter50.

### iter49 (2026-10-27): EXP-77b, M1b on Cadence 0.89.0, zero admitted by construction: CROSSED
- Version: Cadence 0.89.0 (`81345d8`). Pre-registered `4eb09f6` (Will's go for the one rule change: zero admitted by construction, the old per-run interval reported only); port gate with lateral -0.5 IDENTICAL to EXP-62e student 0; construction audit ADMITTED; pilot passed its stop check (know-4 +.431). Full run held by Will, then run 16:47 to about 17:40 (216/216, 3,284 s).
- Result: CONFIRM on all six criteria (experiments/EXP-77b.md): know-1..4 +.075 / +.157 / +.249 / +.385, Spearman .549, know-1 beats anti-echo by 5.7 SEM, knowledge-free pay .005. The old interval check also passes (null .1993 [.1954, .2032], random .1987 [.1948, .2026]), so the rule change did not do the work. EXP-77 stays VOID.
- Milestone: M1b now crossed on two releases, v0.84.3 (EXP-73) and 0.89.0 (EXP-77b), on one instrument.

### iter48 (2026-10-26): EXP-77, M1b on Cadence 0.88.1 (founder lateral): VOID
- Version: Cadence 0.88.1 (`d66f8ea`). Harness ported (EXP-58 compose: `scales={'trace': 12.0}` when the old name is refused); gate with lateral -0.5 IDENTICAL to EXP-62e student 0. Pre-registered `1f5f677`; pilot passed its stop check.
- Result: all six CONFIRM criteria hold; VOID by the zero admission check (null labels .1958 [.1919, .1997], uniform by construction). Not re-scored (experiments/EXP-77.md).
- Milestone: none moves. M1b stays crossed on v0.84.3. Will told in session (live).

### iter47 (2026-10-25): EXP-73, M1b with a measured-chance zero: CROSSED
- Version: Cadence v0.84.3 (worktree; the EXP-62 harness does not run on 0.85+). Pre-registered 042fccb, identity gate IDENTICAL.
- Result: CONFIRM on all six criteria (experiments/EXP-73.md). Also passes EXP-62e's original rule (anti-echo upper bound .021 < .031).
- Milestone: M1b CROSSED on one instrument. Will told in session (live).

### iter46 (2026-10-23): EXP-05, mid-stream snapshot/restore byte identity: VOID
- Cadence 0.85.1 + 41 commits, main `4ac887c`. Pre-registered `6d710c3`. The check (life 99, plain and learned-code brains, 76 s) failed k4: after 6 of 14 cuts the reference continued with one action. The design's task did not keep the policy moving after youth, and the post-reversal cuts did not occur. No data life ran. Seen in the check only: final checkpoint bytes identical at 14/14 restores and 14/14 forks; event records identical in 52 of 56, the other 4 differing only in `last_arousal` (None after load, documented). Write-up experiments/EXP-05.md, results row, atlas iter46. EXP-05b queued.

### iter45 (2026-10-22): EXP-69b, the salience mark at lateral 0.0: VOID
- Cadence 0.85.0 / 0.85.1. The pre-registered check stopped at import (`Brain._received` moved to `memories.EpisodicRecords`, commit `4894ef0`); code gate failed; no data. Write-up experiments/EXP-69b.md, results row, atlas iter45. EXP-70 and EXP-69c blocked on a harness port.

### iter44 (2026-10-21): EXP-69, salience= as the failure mark on the reward-only chain: PARTIAL
- Version: Cadence 0.84.3 + Unreleased, main `be372b8`, `lateral=-0.5` explicit. Pre-registered `2ee8712`, check PASS (`39753c6`). Hidden chain, natural signal, 288 lives, 1,030 s.
- Result: ctx5 .459; pen@.005 .068 (-.365); sal@.005 .337 (-.122, 2.65 SEM, 95% -.212 to -.032); sal@1 .353 (-.080, n 48). Rescue over the cost +.280 (6.0 SEM). Replay stopped at a miss 0 of 3,756 successes with the mark, 422 of 428 with the cost.
- Reading: memory track, not a V(S) rung. Upstream's two named remedies for #210 differ on this learner: a small cost stops replay at every miss; a salience mark keeps it open but its zero-valued writes still cost about .12. At 48 lives the residual would have read as no harm (-.085, 1.3 SEM); the registered 96 lives made it visible.

### iter43 (2026-10-20): EXP-62i, the exposure test: MOSTLY EXPOSURE
- Version: Cadence 0.84.3 source at `c7dc2f0`. Pre-registered `f19bb0f`, pilot `f14333b` (N 720), raw `8377298`, write-up `05e042f`. Budget 6, lesson 80, 18,936 s.
- Result: R(A) .004 off to .394 on; R(D1) .320 off to .039 on; phi_A +1.234 (+.910 to +1.674). Exploratory: D1's late worth was the harm random late labels do; against untaught, both brains price late knowledge near 0 without the scaffold.
- Reading: M5 refined. The judge's exchange rate is not a fixed property of the brain: it moves with the curriculum (exposure) and with the declared zero (decoy vs absence). A payout rule must pin the judge's whole setup, including baseline and practice conditions.

### iter42 (2026-10-20): EXP-62h, scaled exchange rate across a near-relative and a cross-family pair: RATE DEPENDS ON THE BRAIN
- Version: Cadence v0.84.3 `8dc92d8`. Pre-registered `043dd25`, pilot `0ae8bf9` (N 720). Budget 6, lesson 80, 14,501 s.
- Result: scaled D A .874, C .937, D1 .610; A-D1 -.263 (95% -.349 to -.180); A-C +.064 (-.025 to +.153).
- Reading: M5 (the instrument as an outside ingredient) gets its first powered answer on this task family: the judge sets the exchange rate between kinds of contribution, across architectures, and scaling does not remove it; it does not set the order.

### iter41 (2026-10-20): EXP-62g, cross-family instrument on a harder task: MAGNITUDE ONLY
- Version: Cadence v0.84.3 `8dc92d8`. Pre-registered `d241ca0`, sweep `f74362f`, pilot `38bb2ed`. Budget 6, lesson 80, 48 fresh students, 1,315 s. EXP-62f (same question at budget 10) closed at its pilot: D1 at ceiling (SUPERSEDED).
- Result: A D +.146 (.037), D1 D +.341 (.038), difference -.195 (3.6 SEM); D2 = D1; same order on all three; scaled late/early .16 vs .18 (exploratory).
- Reading: order agrees across a change of architecture; raw magnitude does not, and the exploratory scaling suggests the difference is how much each brain absorbs rather than how it values late against early. M5 (instrument as an outside ingredient) not decided; the scaled-rate question is next.

### iter40 (2026-10-19): EXP-62b, instrument dependence: MAGNITUDE ONLY
- Version: Cadence v0.84.3 `8dc92d8`. Pre-registered `39ab1a4`, pilot `10a35a4`. Lesson 80, 48 fresh students, 2,802 s.
- Result: A D +.201 (.026), C D +.302 (.029), D_A - D_C -.102 (2.8 SEM); B blind (know-4 +.069).
- Reading: order agrees, magnitude does not, across two near-relative instruments; a different-family instrument is needed before any general claim. M5 (instrument as an outside ingredient) not decided.

### iter39 (2026-10-19): EXP-62e, non-superiority margin 1/32 on 216 fresh students: BOUNDARY 4/5
- Version: Cadence v0.84.3 `8dc92d8`. Pre-registered `cb60045`. Lesson 80, 216 fresh students (6_800_000+), run 3,784 s. Run outside the loop's 1-per-24h cap on Will's live instruction (EXP-62d ran the same morning).
- Result: ladder +.069 / +.146 / +.254 / +.416 ordered, Spearman .614; separation passes (>= 4.1 SEM); wrong-chain -.093, echo -.134; fake pay .024; anti-echo +.023 (3.6 SEM), upper bound .033 > margin .031.
- Reading: the instrument is right and the class was wrong. Labels follow mistakes, so anti-echo names the right action 1 time in 4 against 1 in 5 for random labels (logged label accuracy .25 vs .20 in all four runs); pooled over 432 students it is worth +.016 (3.4 SEM) and earns about the share of know-1's worth that its share of label information predicts. EXP-62's original leak reading was right; EXP-62c's withdrawal was wrong (inside the noise at n 72). M1b not formally crossed; the measure prices information continuously near zero.

### iter38 (2026-10-19): EXP-62d, pooled uninformative zero with a 2-SEM allowance: BOUNDARY 4/5
- Version: Cadence v0.84.3 `8dc92d8` (main moved 0.83.0 -> 0.84.3 between pre-registration and run; run gate: EXP-62c students 0-1 reproduced bit-identically, actions + labels, all 10 arms). Pre-registered `8b46525`. Lesson 80, 72 fresh students (6_600_000+), run 1,191 s.
- Result: ladder +.070 / +.140 / +.249 / +.421 ordered, Spearman .636; separation passes (know-1 vs untaught 2.07 SEM, the rest 3.3-4.4); wrong-chain -.089, echo -.172; fake pay .007; untaught +.029 (2.57 SEM) fails "no fake above zero by 2 SEM".
- Reading: skill pricing on instrument I is now robust across three disjoint student sets. The zero-point failures are a test-design problem: the 2-SEM rule over a four-arm class false-fails ~9% at any n under exact equality and more under any small real gap. Pooled over 216 students the uninformative arms sit within +-.015 (exploratory). EXP-62e (non-superiority margin 1/32, n 216, ~1% false-fail) pre-registered and declared the last redesign. M1b still not formally crossed.

### iter37 (2026-10-17): EXP-62c, fresh students with the zero declared as anti-echo: BOUNDARY 4/5
- Version: Cadence v0.83.0 + Unreleased `6499e56`. Pre-registered `aa364c5`. Lesson 80 (chosen from EXP-62's full data before the run), 72 fresh students, run 1,339 s.
- Result: ladder +.073 / +.162 / +.300 / +.436 ordered, Spearman .612; wrong-chain -.071, echo -.095; random +.027, abstain +.032; fake pay .034; anti-echo -.012 vs null (EXP-62: +.023 / +.031).
- Reading: skill pricing on instrument I = delayed-credit brain is robust across two independent student sets and two lengths; the zero point is a +-.03 band of uninformative arms whose order shuffles. The "every fake <= 0 vs one fake" rule is a max-of-noisy-estimates test and fails by chance. EXP-62's leak interpretation withdrawn (addendum in EXP-62.md). M1b still not formally crossed.

### iter36 (2026-10-17): EXP-62, Noesis-lite v2 on the content-taking brain against a committed null: BOUNDARY 4/5
- Version: Cadence v0.83.0 + Unreleased `6499e56`. Pre-registered `e6d6d82`, pilot + amendment A1 `aaafac7`, run 1,997 s.
- RUN GATE: (1) prediction in experiments/EXP-62.md before the pilot; (2) window: lessons 40/80/120 piloted under run conditions, rule picked 40 (80 excluded by the .90 ceiling guard on 3 students), 80 run as declared exploratory; (3) variance: know-k varies label correctness .35 / .49 / .70 / 1.00 by construction; (4) metric: priced against the committed stronger counterfactual, abstain and anti-echo arms included; (5) chain printed in the pilot: label correctness -> taught accuracy -> CF accuracy -> worth, every link moved.
- Result (40): ladder +.054 / +.068 / +.138 / +.236 ordered, Spearman .400; random -.028, wrong-chain -.054, echo -.075, abstain -.016, anti-echo +.023 (SEM .019); fake pay .041. 80 (exploratory): ladder to +.391, Spearman .530, anti-echo +.031.
- Reading: transfer prices skill on instrument I = delayed-credit brain with null N = random-label teacher; the zero point leaks: worth follows label information (r .99 across arms), and the corrective schedule gives any labeller one elimination bit per mistake. Re-priced against anti-echo (exploratory) the ladder holds (know-1 +.030 to know-4 +.213). Milestones: M1 and additive M2 re-cross on this chain (genuine positive, fakes non-positive except the leak-carrying one); M1b BOUNDARY.

### iter35 (program evidence, logged late 2026-10-16): Noesis-lite pricing (EXP-49, EXP-52) and the content sub-track (EXP-48/53/54/55/58/61)
- Numbering: iter14 to iter34 are teaching and text work. From iter35 on, only runs that touch M1-M5 take iteration
  numbers. EXP-49 and EXP-52 are Noesis-lite pricing, which is program work; they and the content sub-track were run
  2026-10-13/14 and logged here late (old entries not renumbered).
- Version: Cadence v0.83.0 `23dba71`; EXP-54/55 on PR #197 head `8d99c75` (pinned `~/_cadence_197`).
- EXP-48 (2026-10-13, the weather chamber EXP-49 uses): 12 seeds, per-state greedy accuracy seen / unseen: memory
  corrective .89 / .84 (gap +.05, 9 of 12 seeds lose nothing); memory natural .64 / .58; without memory .53 / .53 and
  .32 / .33. On unseen weather memory beats no memory by .31 (corrective; sampled full-chain .920 vs .201).
  SUPPORTIVE (3/4; P2 failed toward generalization).
- EXP-49 (2026-10-13, Noesis-lite v1, worth = taught minus untaught twin; 3 markets x 6 students x 7 teachers):
  genuine teachers worth +.17 to +.30, pay share .716; random-label fake +.179 (about 3 SEM above zero), wrong-chain
  +.061, echo -.036; fakes take .285 of pay; Spearman(pay, skill) .05; genuine worth survives vesting (.86).
  BOUNDARY (1/5 held): priced against "no teacher", the market pays random labels (they unstick a stuck student) and
  cannot rank skill.
- EXP-52 (2026-10-13, Noesis-lite v1.1, priced against a form-matched random-label null; 72 worth samples per teacher):
  vs null, fakes price at or below zero (random -.07, wrong-chain -.21, echo -.27) but genuine teachers are also near
  zero (know-4 +.013; Spearman with k .06); accuracy .661 vs .648; untaught .46. Vs no teacher, random +.104 (EXP-49
  reproduces). BOUNDARY (1/5).
- EXP-53 (2026-10-13): content (know-4 minus random) +.013 / +.107 / +.068 at 40 / 120 / 240 attempts (SEMs about
  .06); correction itself is worth +.25 at 40 attempts for either teacher; pooled 120-240 about +.09, about 2 SEM.
  NULL (1/4).
- EXP-54 (2026-10-14, PR #197 surprise rule): content under the gene -.008 / +.125 / +.003 at 40 / 120 / 240
  (every-row +.013 / +.107 / +.068); gene effect on know-4 within 1.3 SEM of zero at every length. NULL (gate held, 0/3).
- EXP-55 (2026-10-14, demonstrations at every decision): content at 240 is -.16 with every row taught (random
  demonstrations beat right ones, 3.4 SEM): readout saturation. The rule removes it (+.19; know-4 student .72 -> .88)
  but content stays ~0 (+.03). BOUNDARY (2/4).
- EXP-58 (2026-10-14, EXP-45's delayed-credit brain): content +.193 (5.8 SEM) at 40, +.469 (11 SEM) at 120; know-4
  student .93; random labels worth nothing (-.08 vs untaught). SUPPORTIVE (3/3).
- EXP-61 (2026-10-14, EXP-58's protocol on the default memory brain): content -.049 (SEM .085) at 40, +.016 (.066) at
  120; every arm within ~.06 of EXP-53. Being corrected at all still +.268 at 40. SUPPORTIVE (2/2): the default
  brain's operating point blocks content.
- Program reading (2026-10-16 re-rank): no milestone moved; v(S) depends on the instrument I and the null N, not only
  the task T. New rung M1b; restated M5; next = EXP-62 (see FRONTIER 2026-10-16 and NEXT ITERATIONS).
- Write-ups: experiments/EXP-48.md, EXP-49.md, EXP-52.md, EXP-53.md, EXP-54.md, EXP-55.md, EXP-58.md, EXP-61.md.

### iter34 — 2026-10-13 — EXP-44 readout operating point vs size on graded text = NULL (neither lever; the gap is exploration)
- Version: Cadence v0.81.0 `736fee9`; the first full run crashed 2026-10-11 on an unsettled homeostasis brain; amendment pushed (5fc77c7) before the remaining 8 runs, which finished from a pinned 0.81 worktree after upstream's 0.82 removed the gene.
- Result (greedy held-out after pass 2, 3 seeds): control .253 (SEM .010; pass 1 reproduces EXP-43 exactly); homeo-0.3 .183 (n=2), homeo-width .068 (n=2), each 1 of 3 unsettled; actor-small .229; wide .213, top-answer share .88. Table .346.
- Verdict: NULL, 3 of 4 held (P3, capacity, failed). Next lever: exploration, with 0.83's episodic memory as the candidate (EXP-50). Write-up: experiments/EXP-44.md.

### iter33 — 2026-10-10 — EXP-43 judged grades = BOUNDARY (the grade can carry it; the brain does not yet take it in)
- Version: Cadence v0.80.0 `19bee92`; modules (32, 16). Alice ch.1 train, ch.2 held out. Always-learning (step) 5 arms x 3 seeds x 6 passes; live (EXP-42 protocol) 4 arms x 3 seeds x 3 passes.
- RUN GATE: pre-registered (5666d17); pilots printed the chain (grade -> reward -> agree -> accuracy) and caught two collapsed arms; design + predictions revised in the open (f347d38); primary metric declared before results (db6242d). The revision's mechanism story (the calm trap) did not survive a healthy control.
- Result (greedy held-out, 6 passes): right/wrong w1 .202, w3 .202, partial .202 (all always-space); judged w1 .240/.274 (+1 seed collapsed .275 -> .070); judged w3 .254 (SEM .016). Teacher-2 .292, teacher-4 .506; table on judged w3 .346. Live outcome-w1 reproduces EXP-42 exactly.
- Verdict: 4 of 8 held (P1, P5, P6, P7). Write-up: experiments/EXP-43.md.

### iter32 — 2026-10-10 — EXP-42 text from grades alone = BOUNDARY (one bit per character is not enough)
- Version: Cadence v0.80.0 `19bee92`; modules (32, 16), arousal on. Alice ch.1 (10,891 chars) x 3 passes, ch.2 (10,468) held out, prequential. 3 seeds x arms w1 / w3 / seq.
- RUN GATE: pre-registered (experiments/EXP-42.md, pushed 51baa5a before the full run); Will's speedrun call, a 600-character smoke run only (no window pilot).
- Result (held out): Cadence w1 .225 (SEM .004), w3 .215, seq .200; majority .202; graded tabular bandit w1 .231, w3 .242; supervised counts bigram .291, trigram .419, 4-gram .502. Samples loop ('w w w').
- Verdict: all six predictions held. Next levers: more passes, richer grades, a drilling teacher, Cadence's token-window connectome. Write-up: experiments/EXP-42.md.

### iter31 (note, logged 2026-10-16): EXP-40 brain size in the peer network = ABANDONED by Will at 30/144 runs
- Teaching track. The 12-seed run was stopped at 30 of 144 runs on 2026-10-10 on Will's call to put EXP-42 first, then
  abandoned ("abandon exp-40", HANDOFF). No result is claimed. Write-up: experiments/EXP-40.md.

### iter30 — 2026-10-10 — EXP-39 prerequisite chain = SUPPORTIVE (grading is the teacher's value; 'teach backwards' withdrawn)
- Version: Cadence v0.80.0 `19bee92`; brain at the key-door protocol-3 operating point, `step`. 12 seeds x B 40/150/500/1500 x 5 arms.
- RUN GATE: pre-registered (experiments/EXP-39.md, pushed 599756b before the full run); pilot swept the budget (the window) and printed the chain; prediction revised after the pilot in the open.
- Result (solved of 12 at B=40/150/500/1500): SPARSE-FWD 0/0/1/11; SPARSE-BWD 0/0/0/0; GRADE-FWD 12/12/12/12; GRADE-BWD 8/12/12/12; BLIND 0/0/0/0.
- Verdict: all five predictions held. Write-up: experiments/EXP-39.md.

### iter29 — 2026-10-10 — EXP-38 repeat-need detection = SUPPORTIVE (exclusion, not detection, does the work)
- Version: Cadence v0.80.0 `19bee92`. EXP-36 world, 16 rounds, 12 seeds, 979s at 6 workers.
- RUN GATE: prediction in the docstring; pilot (2 seeds, same conditions) printed the chain (repeat rate -> need -> routing -> honest knowledge) and exposed a METRIC gap (EXP-36 counted fake pay to the colluder only); fake_all added and prediction revised before the full run.
- Result RECIP / REPEAT / REPEAT+RATE / ADAPT: honest .927 / .946 / .943 / .952; absorbed .69 / .30 / .30 / .30; fake pay all teachers .708 / .734 / .776 / .451; sandbagger repeat rate 1.00 / 1.00 / 1.00 / 0.00 (honest ~.02).
- Verdict: all five predictions held. Write-up: experiments/EXP-38.md.

### iter28 — 2026-10-10 — EXP-35b with item credit = SUPPORTIVE (the share drives discovery)
- **Version:** Cadence v0.80.0 `19bee92`. N=8, K=96, 30 rounds, 12 seeds, D=40, PRIOR=0.01, 6 workers, 1992s.
- **Design change:** CREDIT=item. Discover is credited ALL pay on items the brain found by a Discover move (own teaching
  + royalty); each move's value = decayed pay / decayed move count (PRIOR = one pseudo-move).
- **RUN GATE.** PREDICTION in the docstring (see experiments/EXP-35b.md). WINDOW + CHAIN: pilot 3 seeds x PRIOR .01/.002,
  full length; every link moved with ALPHA (Discover pay/move .0034 -> .0071 and .0022 -> .0064; Discover share
  .39 -> .44 and .35 -> .42). VARIANCE: arms differ by construction. METRIC: network-new discoveries and accuracy
  cannot be passed by a degenerate policy.
- **Result (mean +- SEM, 12 seeds), ALPHA 0 / 0.9 / PI:** Discover pay per move .0036 / .0071 / .0049; Discover share
  last 10 rounds .51 / .63 / .53; new discoveries 54.0+-1.0 / 57.8+-0.8 / 55.3+-1.3; final .790 / .811 / .798;
  PI share path .57 -> .13.
- **Verdict:** prediction held on pay (~5 SEM), late discovery (+.12, ~4 SEM) and new discoveries (+3.8, ~3 SEM, better
  than predicted); accuracy +.021 just outside the predicted +-.02 band (~2 SEM, no claim); PI part WRONG (set point
  shrinks by construction). Pedigree share driving discovery: first valid support, small world, one PRIOR.
- Evidence: `exp/EXP-35b-item-2026-10-10.out`, `exp/EXP-35b-K96-R30-item.json/.jsonl`, pilot `exp/EXP-35b-pilot-item-P*.jsonl`.
  Write-up: `experiments/EXP-35b.md`.

### iter27 — 2026-10-10 — EXP-35b rerun with patched credit = NULL; share channel starved
- **Version:** Cadence v0.80.0. N=8, K=96, 30 rounds, 6 seeds, D=40, PRIOR=0.01, 6 workers (~17 min per credit mode).
  Smoke (ROUNDS=2 SEEDS=2) passed: alpha-0 rows identical orig vs fixed (.561).
- **PREDICTION (docstring, written before running):** under fixed, estD and network-new discoveries rise with alpha
  (0.9 > 0); under orig they do not. **WRONG.**
- **Result (per-arm mean +- SEM over 6 seeds):**
  orig  0.0: final .799, discovering .34+-.05, novel/round 1.69+-.13, estD .0041 · 0.9: .804, .38+-.04, 1.83+-.06, .0034 ·
  PI: .788, .35+-.03, 1.73+-.05 (alpha path .56 -> .29).
  fixed 0.0: final .771, discovering .66+-.01, novel 2.04+-.03, estD .0100+-.0000 · 0.9: .776, .67+-.02, 2.01+-.02,
  .0099+-.0002 · PI: .783, .63+-.02, 2.01+-.02 (alpha path .56 -> 0.00).
- **Verdict: NULL in both credit modes, for a measurable reason.** (1) Under fixed, discovery royalty is .001/round vs
  direct pay .038 (~1/40), so estD stays at PRIOR at every alpha. The share reaches the decision now (the iter25 bug is
  fixed) but carries almost no money. (2) The fixed-vs-orig jump in discovery (.34 -> .66) happens at alpha 0 too, so it
  comes from the PRIOR (.0100 > estT ~.007 makes Discover the default), not the share. The knob that moved behaviour was
  PRIOR, which is a design artifact. (3) More discovery under fixed cost accuracy (.77 vs .80): over-discovering crowds
  out doing. (4) The PI controller learned to drop the share to 0 under fixed, consistent with it buying nothing.
- **Effect-window failure ([[pilot-finds-the-effect-window]]):** the smoke test checked plumbing, not whether the royalty
  could ever be big enough to matter. Next before any rerun: pilot the royalty-to-direct ratio (more onward teaching of
  discoveries, longer horizon, or royalty paid on downstream use) and sweep PRIOR to confirm it, not the share, drives
  the baseline. Only then is "share drives discovery" testable at this scale.
- Design notes unaffected: they already did not claim the share drives discovery.
- Evidence: `exp/EXP-35b-full-2026-10-10.out`, `exp/EXP-35b-K96-R30-{orig,fixed}.json/.jsonl`, smoke in `exp/smoke/`.

### iter26 — 2026-10-10 — EXP-36 duplicated-lesson bug found; iter24 attack numbers re-measured
- **Version:** Cadence v0.80.0 main `19bee92` (iter24 ran on 0.78; 0.79 #160/#158 changed live() learning, so
  this rerun differs from iter24 by version AND by the fix; the fix is the point).
- **Bug:** `EXP-36_adversarial_market.py` ran the whole lesson block TWICE per teacher per round. Only the 2nd copy
  counted fake pay and recorded new knowledge; the 1st copy still spent ledger credits. So the ledger was pre-drained
  before the counted lesson, which understates SMART/RECIP fake pay by construction (iter24 "ledger caps it at .052").
  LIST and PROBE+LEDGER are less affected. Buggy script kept as `.dup-bug.bak`; iter24 evidence `EXP-36.out` kept.
- **RUN GATE.** PREDICTION (written before running): honest knowledge rises slower in every mode (half the lessons);
  LIST still mints large fake pay; PROBE+LEDGER ~0; SMART fake pay HIGHER than .052 (credits no longer pre-drained) but
  bounded (one credit per student-item); RECIP <= SMART. WINDOW: iter24 settings (16 rounds, 6 seeds) already showed
  every mode away from 0% and 100%. VARIANCE: modes differ by construction. METRIC: fake pay = paid minus true gain,
  cannot be passed by a degenerate policy.
- **Result (16 rounds, 6 seeds, 881s at 3 workers):** fake pay / real gain by colluder / lessons absorbed by attackers /
  honest final: LIST 13.09 / .161 / 93% / .680 · PROBE+LEDGER .042 / .203 / 30% / .946 · SMART .151 / .073 / 83% / .834 ·
  RECIP .177 / .177 / 69% / .912. (iter24 buggy: 14.35/.016/93%/.726 · 0/.052/37%/.966 · .052/.016/85%/.924 · .130/.021/76%/.936.)
- **Verdict: bug CONFIRMED material; two iter24 conclusions change.**
  (1) The smart sandbagger is worse than reported: fake pay ~3x (.151 vs .052) and it costs honest knowledge .11
  (.834 vs .946), not .04. "The ledger caps it" holds only for minting (bounded), not for throughput.
  (2) Reciprocity is NOT "barely helps": it does not cut fake pay (.177, prediction RECIP <= SMART WRONG) but recovers
  most of the throughput loss (.912 vs .834) by pushing the soaker down the queue. Its role = throughput defence.
  (3) PROBE+LEDGER fake pay is .042, not 0. From the code: paid counts items newly right, true gain is the net accuracy
  change, so any forgetting during the lesson shows up as "fake" pay. It is a gross-vs-net gap, not attacker fraud
  (code reasoning, not separately measured). Pay-on-persisting-gain (designed) would close it.
  (4) LIST still catastrophic (~80x not ~900x; the old ratio's denominator was the buggy .016).
  Caveat: version moved 0.78 -> 0.80 at the same time; the fix dominates (it halves lessons), but not separated.
- Design notes (kept outside this repo) updated to the fixed numbers; an older copy still had the old numbers (regenerate before
  any further sharing). Next rung unchanged and now more important: repeat-need detection vs the smart sandbagger,
  run on top of RECIP.
- Evidence: `exp/EXP-36-fixed.out/.json/.jsonl`, buggy script `exp/EXP-36_adversarial_market.py.dup-bug.bak`.

### iter25 — 2026-10-09 — EXP-35b pedigree share at K=96, teachers choose own vs relay = NULL
- **Version:** Cadence v0.78.0 / `750c8ef` (clone not yet ff'd to v0.80). N=8, K=96, 30 rounds, 6 seeds, D=40, 1619s.
- final acc (SEM) / network-knows / discovering / relaying: a0.0 .828 (.007) / .89 / .34 / .45 · a0.3 .850 (.010) / .91 / .35 / .42 ·
  a0.6 .838 (.006) / .89 / .35 / .34 · a0.9 .848 (.005) / .88 / .36 / .33 · PI .840 (.009) / .91 / .39 / .35 (alpha path .56 -> .95 -> .37).
- **AMENDED same day: test was blind, verdict VOID.** Credit bug: an origin's royalty was credited to whatever move it made that round (usually Teach), and Discover always paid 0 when made, so the Discover estimate decayed to ~0 at any share. The share never reached the decision. Fix staged: `CREDIT=fixed` (royalty credits Discover) + pay logging (estT/estD/royalty/direct); iter25 checkpoint kept as `exp/EXP-35b-K96-R30-iter25.jsonl`. Rerun pending (CREDIT=orig vs fixed, arms 0.0/0.9/PI).
- Original verdict REFUTED (prediction: low share under-discovers, PI >= best fixed). Non-monotone, spread ~2 SEM. Only robust effect:
  higher share shifts teaching from relayed to own items. Discovery barely moves, so the share does not buy exploration in
  this world. Pilot (2 seeds) effect was noise: lesson = pilots find the window, they do not confirm the effect.
- Ops: first launch (15:14) died at ~29 min under CPU contention (Will gaming, 6 workers on 6 cores) with zero output
  (results only written at end). Script now checkpoints per job to `exp/EXP-35b-K96-R30.jsonl` and resumes.
- Evidence: `exp/EXP-35b.out`, `exp/EXP-35b-K96.json`, `exp/EXP-35b-K96-R30.jsonl`.

### iter24 — 2026-10-09 — attack test (EXP-36) + Maarten's weight filter (EXP-37)
- **EXP-36 (16 rounds, 6 seeds; brain 5 fake-need, 6+7 sandbagging colluders):** fake pay minted / lessons absorbed by
  attackers / honest final knowledge: LIST 14.35 (real gain .016, ~900x) / 93% / .726 (stuck) · PROBE+LEDGER 0 / 37% / .966 ·
  SMART (sandbagger also fools probes) .052 / 85% / .924 · RECIP .130 / 76% / .936.
  Predictions confirmed: self-reported lists are catastrophic; probe+ledger stops minting; the ledger caps a probe-fooling
  attacker. NOT solved: a smart sandbagger still soaks 85% of lessons (always looks neediest); reciprocity barely helps.
  Next layer (designed): repeat-need detection from the ledger: an item already taught to a brain that the probe still
  says it lacks = forgetting or lying; stop routing that item to it.
- **EXP-37 (16 seeds, K=8):** weight change genuine 2.59 / fake_wrong 2.44 / noise 1.44; worth +.42 / -.58 / +.01;
  corr(weight change, worth) = -0.02. Internal change is worth-blind; usable only as a "learned anything" pre-filter.
- Evidence: `exp/EXP-36.out/.json`, `exp/EXP-37.out/.json`. EXP-35b full run in progress.

### iter23 — 2026-10-09 — EXP-35 pedigree-share controller = NULL (gate skipped) + EXP-36 attack smoke + "immune system"
- **EXP-35 (K=48, 16 unknown, 20 rounds, 6 seeds):** final .948 / .955 / .947 / .967 at share 0 / .3 / .6 / .9;
  PI .952 (drove the share to 0). Discovery effort rises only 29% -> 37% with the share; every arm ends with the
  network knowing 100%. **Null, partly my process error:** ran a 2-round smoke, not a window pilot (RUN GATE line 2).
  Flaws: (1) ceiling, the world is fully discovered within 20 rounds; (2) discovery pays even at share 0 because the
  discoverer teaches its own find and keeps all pay; (3) relaying is not a choice (teachers pick items at random),
  so half of what the share controls is absent. Next: EXP-35b, K=96 (two-thirds unknown), teachers CHOOSE own vs
  relayed items by expected pay, window pilot first.
- **EXP-36 smoke (1 seed, 2 rounds, directional only):** self-reported lists: colluders mint 1.125 fake pay vs .062
  real (18x), honest knowledge .70; probe + ledger: 0 fake pay, .77; smart sandbagger that also fools probes: .03
  (ledger caps it). Still open: attackers absorb 39-54% of lessons (fake need is rewarded by neediest-first);
  added RECIP arm (need weighted by lessons given / received). Full run queued.
- Framing (Will): "the antivirus of Cadence brain cells". Closer to an IMMUNE SYSTEM: structural (probe, ledger,
  reciprocity) so attacks do not pay whatever their form, not signature-matching.
- Maarten G question (what does a brain gain, neurons or nodes; measure without tests?): neither, weights + memory
  records; internal change is worth-blind (EXP-08 fake moved weights fully, worth 0) but usable as a cheap PRE-FILTER.
  Reply draft: Desktop/People/maarten-reply-brain-gains-2026-10-09.md. Testable: weight-change vs measured transfer.

### iter22 — 2026-10-09 — partner choice on the fixed network (EXP-34 FIX=1) + DESIGN RULE adopted
- With notes + drift-check + rehearse, 16 rounds, 8 seeds: final RANDOM .981 · ORACLE (neediest first) .991 ·
  INFORMED chooser .982. Curve: ORACLE reaches .96 by round 8 vs RANDOM round 12 (~25% faster), consistent
  across seeds. Learned chooser = random (25% neediest picks): pay per round too noisy to learn from.
- **Design rule (Will 2026-10-09, adopted):** teaching is neediest-first, hard-wired, not learned.
- **ATTACK SURFACE (Will: "this attack vector is huge"):** a self-reported "what I know" list routes the scarce
  resource. Attacks: (1) SANDBAGGING: student answers wrong before / right after, faking measured gain, colluding
  teacher minted pay (breaks budget balance; pay-on-gain does NOT stop it); (2) fake need; (3) sybils; (4) over-
  claiming (self-limiting). Defences (designed, not built): probe need on a committed copy instead of trusting
  claims; credit each item to a brain once (provenance ledger); pay only on gains that persist on fresh tasks.
  Residual: depends on honest test supply (M5); trigger-gated deliberate under-performers open.
  QUEUED: EXP-36 adversarial market (sandbag pairs + fake-need sybils; lists vs probe+ledger; measure minted fake
  pay and knowledge throughput). Prediction: lists leak large fake pay; probe+ledger ~0 beyond the M5 residual.
- Evidence: `exp/EXP-34-fix.out/.json`.

### iter21 — 2026-10-09 — the plateau was STALE TEACHING; the provenance ledger fixes it (EXP-33) · partner choice is not the bottleneck (EXP-34)
- **EXP-34 (16 rounds, 6 seeds):** final knowledge RANDOM .841 · ORACLE (always the neediest) .824 ·
  INFORMED chooser .809. Oracle leads early (round 2: .75 vs .70; round 4: .83 vs .79) then all hit the same
  ~.82 ceiling. Informed chooser did not learn (42% neediest picks vs random 53%). Prediction partly met
  (oracle faster early); final: no difference. Lesson: the ceiling was the binding constraint.
- **EXP-33 (same world, 16 rounds, 6 seeds), each brain keeps NOTES (answer at time of learning):**
  base .790 · big brain (2x) .816 · rehearse .940 · **drift-check .982** · **both .991 (SEM .002)**.
  Forgetting per lesson 4.2% -> 0.8%. Prediction CONFIRMED: fixes reach ~1.0, capacity was not the limit.
  Biggest single fix = drift-check: a teacher refuses to teach items whose current answer no longer matches
  its notes. The plateau was mostly brains teaching what they had forgotten.
- **Design consequence: the ledger that pays also keeps knowledge from rotting.** The provenance record the
  pedigree pay needs (what was learned, from whom, what the answer was) is the same record that stops stale
  teaching. Honest floor: notes are an external record, not inside the brain.
- Next: re-run partner choice ON TOP of the fix (ceiling gone, choice may now matter); then EXP-35 pedigree
  share: fixed 0 / .3 / .6 vs a PI controller, with a new DISCOVER move (explore the world alone).

### iter20 — 2026-10-09 — peer-to-peer (EXP-31) + the teaching-market sim (EXP-32) + design notes + UI
- Will: teaching must be peer-to-peer and bidirectional; build the full teaching-market requirements now.
- **EXP-31 (8 brains, K=32, each knows one slice, specialist rule, 12 rounds, 6 seeds):** one-way RING
  0.57 -> 0.76 by round 2, plateau 0.78; random PEER both-ways 0.57 -> 0.79. Prediction (peer clearly faster)
  WRONG: ring faster early, peer slightly higher late. Both PLATEAU ~0.78: likely forgetting (short mixed
  lessons overwrite older ones; brains keep teaching what they have since forgotten). Open.
- **EXP-32 (teaching market: any-to-any, bidirectional, partner choice learned by a Cadence chooser from pay,
  pay = student's measured gain on the true rule, 30% pedigree share to the knowledge origin, budget-balanced):**
  final knowledge CHOOSE 0.842 (SEM .010, runs .80-.86) vs PEER random 0.791 (SEM .037, runs .70-.91).
  Paid == measured gain exactly in every run. Choosers barely learned to pick needy peers (61% vs 58%).
  Prediction partly met: small, not yet significant edge; much more consistent. WHAT to teach still random.
- Artifacts: design notes (kept outside this repo), `ui/spawn-sim.html` (built by
  `ui/build_spawn_ui.py` from `exp/EXP-32.json`; Desktop copy). Evidence: `exp/EXP-31.out/.json`, `exp/EXP-32.out/.json`.

### iter19 — 2026-10-09 — teaching is selected through children's doing (EXP-27 powered) + knowing-your-limits (EXP-29) + over-teaching (EXP-30)
- **EXP-27 powered (P=24, 6 kids, 20 gens, M=32, single run per arm):** focus 0.53 ->
  DO 0.85 (pop acc .943, teaching .852) · TEACH 0.81 (acc .879, teaching .830) · BOTH 0.64 (acc .922, teaching .854).
  Teaching ability IS heritable and evolves under all three rules. **Written prediction WRONG:** expected BOTH
  best; DO best on every measure. Reason: a child's own score already carries its parent's teaching gene, so
  selecting good children selects good teaching with fresher evidence. TEACH-only erodes knowledge (3rd time).
  **Design consequence: doing selects teaching; payment rewards it.** A pedigree price is not needed to decide
  who breeds; it IS needed as the teacher's incentive (our sim has no teacher agency; evolution does the work).
  Caveat: one run per arm, focus noisy (BOTH .82 -> .64 last 5 gens); needs 3-5 replicate seeds.
- **EXP-29 (two half-knowing teachers, K=32):** teachers full-acc A .91 (lucky guesses on its unknown half),
  B .72. Student acc at M=32/64/128 per teacher: specialists (teach own half only) .84/.89/.90 ·
  overconfident (teach everything) .66/.65/.68 · one teacher alone .63/.66/.63.
  Prediction (b) confirmed: overconfident teachers cancel out. (a) partly: student beats B and the teacher
  average (.81) but only ties A. **Knowing the limits of your own knowledge is a teaching skill worth ~0.2.**
- **EXP-30 (over-teaching, key-door parent grading):** pass at 300/600/1000/1500 trips = 8/8, 5/8, 2/8, 1/8.
  Prediction confirmed: over-drilling is real and monotone. Mechanism unknown. Design consequence: cap teaching
  budgets, or pay on gain at the best stopping point, not on effort.
- Evidence: `exp/EXP-27-powered.out`, `exp/EXP-27.json`, `exp/EXP-29.out/.json`, `exp/EXP-30.out/.json`.

### iter18 — 2026-10-09 — teaching is NOT redundant (EXP-28); selection-on-teaching still underpowered (EXP-27)
- **EXP-28 (matched budgets, same students, key-door):** clean pass, world reward vs parent grading:
  40 trips 1/8 vs 8/8 · 100: 3/8 vs 8/8 · 300: 5/8 vs 8/8 · 600: 7/8 vs 5/8. Matches the written
  prediction: teaching is a large speed/reliability multiplier; the world catches up by 600. Unexplained:
  taught students DROP at 600 (over-drilling?). Teaching does not raise the ceiling (EXP-26: student <= teacher).
- **EXP-27 run 1 (M=128):** ceiling. Founders were trained longer than the pilot's teacher (1.00 vs .69), so
  every focus teaches everything. Pilot conditions did not match the run: my error.
- Re-pilot under run conditions (perfect teacher): M=32 focus 0/.5/1 -> .833/.865/.943; M=64 -> .818/.849/.964.
- **EXP-27 run 2 (M=32, P=8, 3 kids, 8 gens): NULL.** Focus drifts in both arms (DO .57->.76, TEACH .57->.70).
  Effect (~0.11) is swamped by student noise + mutation at this population size: underpowered, not broken.
  TEACH lost MORE knowledge (pop acc .855 vs .898): picking children by the parent's teaching alone lets
  poor learners through. Design consequence = the racehorse rule: price on doing AND pedigree, not pedigree alone.
- Next: EXP-27 powered (P=24, 6 kids, 20 gens) + BOTH arm (own acc + parent teaching). Prediction:
  BOTH keeps most knowledge and evolves highest focus; TEACH-only erodes knowledge; DO-only evolves focus slowly.

### iter17 — 2026-10-09 — pilots for a TEACHING trait (new rule: pilot + written prediction before any long run)
- Process fix (Will: "every time we build something the result is 'this was redundant'"): several runs
  failed on flaws checkable in minutes (fed-only loophole, founder prior, label route, no trait variance
  in EXP-23). From here every experiment gets a cheap signal pilot + a written prediction first.
- **EXP-24 (key-door grading strategies):** 5/6 strategies teach 12/12 even at 40 trips; only reward
  strength matters (faint 0.2 -> 50%, mid 0.5 -> 92%, >=1.0 -> 100%). Key-door is too easy to teach:
  per-step grading + visible key = a lookup. Not a usable teaching trait. (`exp/EXP-24-M100/M40`)
- **EXP-25 (memory door: chest absent half the time, door without key costs, blind):** founders do NOT
  learn it with `step` RL (<= 0.50 memoryless ceiling at 1000 trips; 0.00 at 3000, collapse to pressing).
  Boundary on our setup, not a Cadence capability claim (benchmark memory results use `live`+arousal).
- **EXP-26 (tutor FOCUS on the student's current mistakes; K=32 bandit, M=128 graded steps):**
  focus 0 / .25 / .5 / .75 / 1 -> child acc .625 / .625 / .664 / .688 / .688 (teacher itself .69).
  A real, graded teaching trait, invisible to the teacher's own doing. Student cannot exceed teacher.
- Next: EXP-27 evolution, focus gene inherited with mutation, DO vs TEACH selection. Prediction
  (written before running): focus rises in both arms; faster and knowledge better kept in TEACH.

### iter16 — 2026-10-09 — Cadence 0.78.0 / `750c8ef` — rung 3: selection by teaching vs doing (EXP-23) = NULL + retraction
- Pop 6 passing founders (from 12 candidates), 3 children each by parent-grading (M=200), 5 gens.
  DO arm keeps children by own pass; TEACH arm breaks ties by the parent's teaching score.
- **Result: identical.** Pop pass 1.00 every gen in both arms; pop teaching 0.94/0.94/0.94/1.00/0.94 in BOTH;
  parent->child teaching correlation -0.08 (DO), undefined (TEACH, no variance).
- **Why (verified by re-testing all saved children):** the 4 failing children sit in the SAME seed slots in
  both arms, under different parents. Failure is a property of the student's random init, not the teacher.
  Among passing parents teaching ability has no variance here: grading copies the parent's whole policy.
- **RETRACTION:** iter15's "doing != teaching measured (5/88)" is withdrawn (struck through above).
  What stands from iter15: inheritance by grading works (94%/gen), labels fail, flaws are copied,
  a lost skill is never recovered.
- Consequence for the game: teaching ability must be a real, varying, heritable trait before selection
  on it can matter. Candidates: (a) teachers differ in STRATEGY (what to show / how to grade: EXP-20b
  lesson choice), and children inherit the strategy; (b) a harder skill where wrong guidance in off-path
  states actually misleads the learner, so off-path knowledge (invisible to doing) matters for teaching.
- Evidence: `exp/EXP-23.out`, `exp/EXP-23.json`, `exp/exp23_brains/`.

### iter15 — 2026-10-09 — Cadence 0.78.0 / `750c8ef` — generations: brain-to-brain inheritance (EXP-22)
- Founders: 12 lesson-trained (key+door, N=300) + 12 end-to-end trained (600 full-task trips) on the
  key-door corridor. Each generation = a FRESH Cadence brain taught only by its parent, 300 trips, 5 gens.
- **Run A, teaching by LABELS (`step(teacher=parent_action)`): FAILED, 0/20 passing parents produced a
  passing child.** Diagnosis (EXP-22-diag): the child learned the chain (takes key, opens door) and its
  cold per-state answers match the parent exactly, but in a live trip it keeps pressing lamp/levers after
  the floor run (action momentum). Labels shape the graph but did not reach the reward-trained actor.
  Knowledge transferred, habit did not. Kept as `exp/EXP-22-label-*`.
- **Run B, teaching by GRADING (child acts, parent pays +1 when the child's move matches the parent's,
  -0.25 otherwise; no task script, the parent brain is the only judge): WORKS.**
  passing lineages by generation  L: 10,10,9,8,8,8   E: 10,9,8,8,8,7  (of 12 each)
  passing parent -> passing child: **83/88 = 94% per generation**
  failing parent -> passing child: **0/32** (a lost skill is never re-invented)
  passing parent -> IDENTICAL full policy in child: 82/88 (flaws included: off-path errors are inherited)
- ~~DOING != TEACHING, measured: 5/88 passing parents produced failing children.~~ **RETRACTED in
  iter16:** EXP-23 shows child failure is set by the CHILD's random init (same child seeds fail under
  different parents). Those 5 were almost certainly bad students, not bad teachers.
- Consequence: with ~94% fidelity and no selection, a lineage keeps the skill ~0.94^g (about 74% after
  5 gens). Pricing/selecting parents by TEACHING score is what can stop that decay. This is rung 3.
- Honest limits: one small world, one skill, 24 lineages; grading needs the parent to be queried live
  (cost); the 5 bad-teacher cases are a small n.
- Evidence: `exp/EXP-22-grade-s*.json/.out`, `exp/EXP-22-label-s*`, `exp/EXP-22-diag.py`.

### iter14 — 2026-10-09 — Cadence 0.78.0 / `750c8ef` — the teaching game: measured table (EXP-21) + learning teachers (EXP-20b)
- EXP-21: every lesson coalition (null, 4 singles, 10 pairs over {key, door, lamp, spam}) taught to 12
  real Cadence key-door students (protocol-3 point, N=300/slot, clean-trip score). Only key+door pays:
  v(AB) +0.82 (10/12 students clean). All 14 other coalitions ~0, incl. key+key, key+spam, key+lamp
  (a bad partner poisons a good lesson). Odd: key+null trips worked on 2/12 (key+key on 0) - unexplained.
- EXP-20b: two teacher BRAINS (Brain.compose, 5-way lesson choice, `step` learning) play 1500 rounds
  against that measured table; each paid only by a credit rule. 12 runs per rule.
  shapley: converged to key/door 12/12 (median round 39), last-300 key/door 0.96, lamp/spam 0.02, payout = 1.00x value.
  loo:     12/12 (median 47), same end state, payout = **1.83x value** (overpays).
  equal:   12/12 (median 54), same end state, payout = 1.00x.
- **VERDICT: rung 1 of the teaching game WORKS.** Teacher brains paid by their students' measured gains
  discover the complementary split and drop spam/lamp. Shapley is fastest AND budget-balanced.
- Honest limits: in this pure-complement game every rule converges; the payoff table rarely lets one
  teacher free-ride, so equal-split's free-rider weakness is not tested. Teachers choose from a fixed
  menu (they pick lessons, they do not author them). Payoffs are looked up from 12 measured students,
  not re-measured live each round. No generations yet.
- Next rungs: (a) a game where free-riding is possible (one lesson can teach the whole task) to separate
  Shapley from equal-split; (b) generations: students become teachers, credit flows up the pedigree;
  (c) inheritance test (do good-teacher lineages out-teach good-doer lineages).
- Evidence: `exp/EXP-21-s*.json/.out`, `exp/EXP-20b.out`, scripts EXP-21 / EXP-20b / EXP-20.

### iter13 — 2026-10-09 — Cadence 0.78.0 / `750c8ef` — EXP-19 teamwork on Cadence's own key-door world (LEARNED composition)
- World/brain = benchmarks/keydoor protocol-3 operating point. Key teacher (+1 for taking the key, door
  pays 0), door teacher (starts holding, +1 for opening), fake key (rewards the lamp). Every coalition
  gets 2N trips (missing slot = null trips), interleaved. Test = 30 greedy full-task trips, no learning.
- Run 1 (N=100, score = fed): CONTAMINATED. 4/12 untouched founders pass by interact-everything, and
  the fake passed 3 seeds the same way (seeds 4, 5, 11 per exp/EXP-19-fedonly.out). Kept as `exp/EXP-19-fedonly.out`.
- Run 2 (N=100, score = CLEAN trip: fed with zero wrong presses): v(A) +0.09, v(B) -0.06, v(AB) +0.44,
  fakes -0.08; synergy +0.41 (SEM .21, ~2 sigma). Composition sloppy at 100 trips. Door teacher
  interferes with key skill (holding-start trips penalize touching the chest).
- **Run 3 (N=300, clean): v(A) -0.06, v(B) -0.08, v(AB) +0.58 (SEM .15), fake pair -0.08. Synergy +0.72
  (SEM .18, ~4 sigma). AB fully clean on 8/12 seeds; the other 4 founders never learn the chain.
  Shapley key +0.31 / door +0.28 (near-even; interference washed out with practice).**
- **M2-SYNERGY VERDICT: CROSSED for LEARNED sequential composition on real Cadence brains** (each
  lesson alone 0, together +0.58; fake 0). NOT XOR-style representational synergy (still the iter7
  wall). Small world, one delay (2), 12 seeds.
- New thread (Will): the score rates LESSONS, so it trains teachers. End goal = a game that rewards
  teaching ability passed down generations. Next: EXP-21 full lesson payoff table on real students,
  EXP-20b learning teacher brains play it.
- Evidence: `exp/EXP-19-N300-s{0,4,8}.out`, `exp/EXP-19.out` (N=100 clean), `exp/EXP-19-fedonly.out`.

### iter12 — 2026-10-08 — Cadence 0.78.0 / `750c8ef` — EXP-18 key/lock synergy (M2-SYNERGY, data-channel)
- Design: the creature can't host XOR (iter7), so the XOR lives in the DATA. A = rewards masked by a
  per-step random sign pad; B = the pad. Alone each is noise; together = the real lesson. Zero point =
  twin fed an equal-length pure-noise stream (EXP-16 lesson). 12 seeds, K=8, 1600 steps.
- v(A) +0.083 (SEM .058) · v(B) +0.062 (.103) · **v(AB) +0.521 (.070)** · fake key v(B') +0.115,
  v(AB') +0.031. **Synergy v(AB)-v(A)-v(B) = +0.375 (SEM .090, ~4 sigma).**
- Credit rules: solo 0.08/0.06 (sum 0.15, under-credits) · leave-one-out 0.46/0.44 (sum 0.90 = 1.7x the
  real value, over-credits) · **Shapley 0.27/0.25 (sum 0.52 = v(AB), fair 50/50 split)**. Note: Shapley
  summing to v(AB) is algebra, not a finding; the finding is that the split is ~even and LOO double-counts.
- Fake key: Shapley gives B' +0.03 AND drops honest A to 0.00. Honest A is not paid when paired with a
  fake. Correct for "worth of this coalition", harsh for the honest party; pricing must decide whether
  to pay A on its best coalition, not just the one it landed in.
- Partial key p=0.5/0.625/0.75/0.875/1.0 -> -0.05/+0.19/+0.37/+0.48/+0.52: monotonic in key quality.
- **M2-SYNERGY VERDICT: CROSSED FOR DATA-CHANNEL SYNERGY ONLY.** The attribution machinery prices
  combination-only worth fairly with real learners. NOT shown: a brain composing two learned skills
  (Cadence #115 / XOR wall, still open). Noise: the noise-twin zero point is one twin per seed (accN
  ranges 0.25-0.875); an ensemble of noise twins would cut the SEM.
- Design consequence for pedigree / teaching market: price contributions with coalition Shapley over twins, NEVER
  single leave-one-out ablation (overpays synergistic pairs ~2x).
- Evidence: `exp/EXP-18.out`, script `exp/EXP-18_keylock_synergy.py`.

### iter11 — 2026-10-08 — Cadence 0.78.0 / `750c8ef` — EXP-17 task-pool capture + M5 statement
- Adversary controls fraction q of the scoring-task pool (fills it with its own rule). Means: g_T +0.385,
  g_R -0.031, f_T -0.104, f_R +0.458. Paired worth falls linearly; **crossover q* = 0.500**.
- **M5 VERDICT: STATED AS A BOUNDARY (with a number).** Transfer needs an honest majority of TASKS, just
  as PP needs an honest majority of REFERENCES (EXP-15 c*~0.5). It does not escape the exogenous-anchor
  class; it relocates the anchor to a checkable object (a task) and makes peer collusion worthless.
  Cost-bearing task sources (realized use after the fact via a capital-independence filter like noesis
  independent_use_gate lib.rs:7323; commit-reveal ordering; bonded task supply) are all UNBUILT.
  Full statement: `M5-EXOGENOUS-ANCHOR.md`. Evidence: exp/EXP-17.out.

### iter10 — 2026-10-08 — Cadence 0.78.0 / `750c8ef` — EXP-16 isomorphism-invariance (M3)
- phi = context permutation and/or action swap, applied to witness + T; instrument (brain init) NOT
  relabeled. 3 tasks x 4 phi x 8 instruments x {genuine, fake(agree 0.5)} = 192 transfers.
- **Raw twin-delta v = acc_after - acc_base is invariant only in EXPECTATION.** Per instrument it moves
  by up to 0.500 under phi (EXP-16 recheck; 0.25 was the n=1 ensemble gap); ensemble gap max_phi|v_n(phiS)-v_n(S)| at n=8 = 0.125 / 0.062 / 0.031 on the
  3 tasks (n=1 up to 0.25). Cause identified: the noise is the instrument's PRIOR (acc_base), which
  mirrors under action-swap (base -> 1-base) while acc_after saturates (genuine 1.0, fake 0.5).
- **Paired form v_pair = transfer(witness) - transfer(reference witness) on the same instrument cancels
  the prior: genuine-minus-fake = 0.500 in 95/96 cells** (one 0.625). So invariance holds per instance
  once the measure is defined RELATIVE to a reference on the same twin, not against the instrument's own
  baseline.
- **M3 VERDICT: CROSSED EMPIRICALLY for the paired measure, on this bandit; NOT a proof.** Caveats: the
  exactness leans on learning saturating (after = 1.0 / 0.5); with partial learning the paired form
  should still cancel the prior but will carry learning noise. Only context-perm + action-swap tested
  (one random context permutation per task plus the action swap, not the full 8!-element group), 3 tasks. Design consequence: the v(S) used in pricing should
  be the paired / reference-relative transfer, averaged over an instrument ensemble.
  Evidence: exp/EXP-16-t{0,1,2}.out.

### iter9 — 2026-10-08 — Cadence 0.78.0 / `750c8ef` — EXP-15 MATCHED peer-prediction baseline (M4)
- Found: the old "PP crossover gamma*=0.70" (noesis peer_prediction_sim.rs:130-141) is on a DIFFERENT
  axis (fraction of PP reference pool coordinated) than EXP-09's gamma (prior's agreement with T). The
  EXP-09 comparison was never like-for-like. EXP-15 scores ONE adversary with BOTH mechanisms.
- Adversary: ring witnesses all teaching rule R (agrees with T on a_R). PP = Correlated-Agreement vs a
  reference pool (P=10) with fraction c ring, rest honest at 0.9 accuracy. Transfer = twin ablation on T.
- Transfer (independent of c): genuine +0.448(.040); ring a_R=0.5: -0.052, 0.625: +0.073, 0.75: +0.198.
  Genuine always beats ring; ring credit is proportional to how right it actually is.
- PP crossover (ring >= genuine): c*=0.5 at a_R 0.5 and 0.625, c*=0.6 at a_R 0.75. Once about half the
  reference pool is ring, PP ranks the ring above the genuine contributor (at c=1.0 genuine ~0).
- **M4 VERDICT: CROSSED on the matched comparison**, with an honest asymmetry: transfer's immunity to c is
  fully by construction (the transfer arm never reads c; EXP-15 write-up), since it consumes an exogenous held-out T that PP does not have. What is shown:
  given an exogenous T, coordination of the reference pool buys a ring nothing under transfer, whereas it
  flips PP at c~0.5. The cost of that is exactly M5 (where T comes from). PP c* here depends on P and
  honest accuracy (design params), so c*~0.5 is not a universal constant. Evidence: exp/EXP-15.out.

### iter8 — 2026-10-08 — Cadence 0.78.0 / `750c8ef` — #164 eval fix applied, M1/M2/M4 RERUN
- Bernhard closed #164: our evals ran K greedy act() probes back-to-back with no reset, but training
  is 1-step episodes (done=True), so probes inherited each other's state. The "act() is PURE" probe
  (iter4) was wrong. Fix: brain.reset() before every probe + once after (keeps params + memory).
  Applied to EXP-01/08/09/10 (.bak kept). ALL prior M1/M2/M4 numbers are superseded by these.
- **M1 (EXP-08, 16 seeds): STRONGER.** genuine +0.422 (SEM .045) vs fake_random -0.109, fake_wrong
  -0.578; separation +0.531. Own-task diagnostic still clean (fake_wrong 1.00 on T', 0.00 transfer).
- **M2-additive (EXP-10, 12 seeds): STRONGER.** genuine minds +0.375 vs fake -0.479, gap +0.854
  (was +0.542). Proportional curve f=0..1: -0.542/-0.302/-0.052/+0.198/+0.448, linear.
- **M4 (EXP-09 crossover band, 12 seeds): CHANGED SHAPE.** gamma 0.625:+0.125(.074) 0.75:+0.135(.054)
  0.875:+0.281(.049) 1.0:+0.469(.045). The old "~zero until gamma>=0.875" threshold was partly the
  bug. Now credit rises roughly PROPORTIONALLY with agreement: a 62.5%-agreeing prior earns ~27% of
  genuine credit. Arguably correct (a 5/8-right prior carries real info), but the claim "coordinated
  fakes price to ~0 below 0.875" is RETRACTED. Low-gamma half (0.0-0.5) not rerun yet. Matched PP
  baseline now matters more: the comparison is proportional-vs-PP, not threshold-vs-0.70.

### iter7 — 2026-10-08 — Cadence 0.78.0 — Dongyang fast-cadence math + XOR-depth findings
- **Input:** Dongyang Stephen Chen "Fast Cadence: holographic recovery channels for OPH System-1
  learning" (`~/Desktop/Cadence/C__Users_dongy_reports_fast_cadence_method.md`). Will: extract the raw speed
  math, reverse-engineer into our cadence for a speedup, keep on synergy. OPH = Bernhard's (Observer
  Patch Holography), CC BY-NC-SA (research/reimplement ok; commercial needs license). Raw math
  extracted -> `~/cadence-lab/DONGYANG-FAST-CADENCE-MATH.md`.
- **Speedup regime finding (EXP-13 settle profile, equilibrium Reinforcement, 2-col):** settle_budget
  64->16 = 1.36x free (acc 1.00 held), hard correctness floor ~16 sweeps (acc craters to 0.50 at 8).
  Dongyang's 15x = his LINEARISED (beta->0) mode, a DEPTH phenomenon (L^2 chain diffusion over 12
  layers); his holographic channel only beats identity-copy at front ~2 seams. cadence's own
  ACCELERATION.md = GPU/batch, orthogonal. => at our shallow depth his method buys little UNLESS we
  go deep.
- **XOR learnability (the synergy prerequisite):** copy-b1 / copy-b2 learn to 1.00 (EXP-12 smoke,
  factored input + cue, twin exact). XOR-from-scratch: shallow 2-col caps ~0.50 (EXP-12/12b);
  DEEP (perc->hidden->policy, settle_budget=48) is WORSE at 0.00 (EXP-12c) -- systematically wrong,
  the signature of the front/perception column never learning (credit not reaching it).
- **RESOLVED discriminator (EXP-12e/12f):** deep-XOR at sb=48 = action `None` on every ctx (never
  qualifies -> never trains); deep copy-b1 learns to 1.00 (stack not broken, polarity fine). Raising
  settle_budget 48->100 FIXES None (0% None, it settles+trains) but the creature then collapses to a
  CONSTANT action [0,0,0,0] -> acc 0.50. So the None was a settling-budget artifact; the real wall is
  that the equilibrium Reinforcement creature CANNOT LEARN XOR under this RL-reward setup (constant-
  action collapse at adequate settling), deep or shallow.
- **VERDICT — Dongyang's speedup is NOT our lever for synergy.** His method accelerates deep
  settling/credit; our wall is not settling speed (at adequate settling the creature still can't
  represent XOR). Reverse-engineering his full method into our experiments is NOT warranted: shallow
  doesn't need it (1.36x free knob suffices), and going deep does not unlock synergy. Dongyang math
  extracted + captured regardless (`DONGYANG-FAST-CADENCE-MATH.md`); `Fid_l`~transfer-edge candidate
  isomorphism still worth a calibrate-claim pass someday.
- **Honest caveats:** sb=100/220 rows are 1 seed; constant-collapse not 20-seed-robust (but
  consistent with shallow 0.50 x3 seeds + deep-sb48 None x3). RL hyperparams (reward_scale 4.0,
  exploration 0.1, discount 0.0, batch 4) un-tuned -> "can't represent XOR" is too strong; honest form
  = "doesn't learn XOR under this RL setup across shallow/deep/budget." The UNTESTED alternative:
  SUPERVISED admission (`bootstrap`/`observe` with labeled XOR examples) instead of RL reward -- may
  learn XOR where RL-reward collapses. That is the real next fork for synergy, not a speedup.
- **SUPERVISED RESOLUTION (EXP-14/14b) — caveat CLOSED.** Control copy-b1 supervised passes clean
  (acc 1.00). Shallow XOR supervised: passed=False, acc 0.50, preds collapse to near-constant (real
  linear-inseparability wall, NOT an RL artifact). Deep XOR supervised with ample settling (sb256 AND
  sb512 give BYTE-IDENTICAL preds => fully converged, NOT settling-limited): still passed=False, acc
  0.50; preds are LINEAR (seed11 0.08/0.40/0.55/0.85 ~= 0.4*b1+0.35*b2). => the equilibrium creature
  (perc->(hidden)->readout, widths 4-12, fan_in 9) does NOT represent XOR across shallow/deep x RL/
  supervised x converged-settling x seeds. Robust within what was tried.
- **FINAL VERDICT (iter7):** (1) Dongyang's speedup is NOT our lever -- deep failure is converged,
  not settling-limited, so faster settling cannot help. (2) The XOR-channel synergy probe hits a hard
  substrate wall: combination-only worth = non-additive = XOR-like nonlinearity, which this substrate
  won't form (one-hot/atomic-context substrates make XOR a trivial lookup = no synergy; factored-
  channel substrates where synergy is meaningful can't fit the nonlinearity -- that TENSION may itself
  be the honest result). Honest boundary: did NOT exhaustively search wirings (more columns,
  fan_in, parameter_prior); cannot claim "cadence fundamentally can't do XOR", only "not on the
  architectures tried". Striking enough to possibly raise with Bernhard (bears on equilibrium-brain
  representational power for non-linearly-separable fns). NEXT FORK (Will): redesign the irreducible
  task (combination-only but not XOR-hard), try a richer wiring/substrate, or park synergy and clear
  the owed solo rungs M4 matched-PP-baseline / M3 isomorphism-invariance.
- Evidence: `exp/EXP-12_smoke_synergy.py`+`.out`, `exp/EXP-12b_xor_ceiling.py`, `exp/EXP-12c_xor_deep.py`+`.out`,
  `exp/EXP-13_settle_profile.py`+`.out`, `exp/EXP-12d` (timeout), `exp/EXP-12e_xor_polarity.py`+`.out`,
  `exp/EXP-12f_xor_budget_unlock.py`+`.out`.


### iter1 — 2026-10-07 — Cadence 0.75.0 / `88f4dde` — EXP-08 K=4, 8 seeds, 1200 steps
- genuine transfer +0.375, fake_random +0.062, fake_wrong +0.062; separation +0.31; baseline 0.41.
- VERDICT: SEPARATES (coarse). First measured non-zero separation on the transfer construction.
- Caveats that drove iter2: K=4 quantizes acc to 0.25; fake_wrong leaked because a random wrong rule
  overlaps T on ~half of 4 contexts by chance (artifact, not real transfer); "matched" = surface-
  matched (steps/marginals/reward-rate), not interior-feature-matched (that is M2).
- Evidence: `exp/EXP-08-iter1.out`, script `exp/EXP-08_vs_transfer_separation.py`.

### iter6 — 2026-10-08 — Cadence 0.78.0 / `750c8ef` — M2-synergy foundation + design crux
- Read patch-world: byte-identical twin EXISTS (`Reinforcement.snapshot`/`from_snapshot`, incl RNG).
- EXP-11 smoke: equilibrium `Reinforcement` creature learns a 4-ctx bandit to **1.0** (more headroom
  than the plain Brain bandit) and the twin fork is **exact**. Harness foundation VALIDATED.
- **Design crux (honest, blocks a quick synergy run):** super-additive synergy does NOT reduce to
  twin-ablation like additive worth. A disjoint-part split = additive coverage (EXP-10), not zero-
  alone. True each-alone=0/together-positive needs an IRREDUCIBLE task (XOR over 2 sense-channels),
  which forces contributions to be PERCEPTUAL PREREQUISITES whose composition = transfer/curriculum
  learning = **Cadence open issue #115** (one of the two roadmap issues flagged as our transfer
  territory). So M2-synergy is COUPLED to #115; a first probe is likely INCONCLUSIVE until #115 is
  understood. Not rushed at hour-22 to avoid mislabeling additive coverage as synergy.
- Next: design the XOR-channel scaffolding probe deliberately (fresh session); its result doubles as a
  datapoint on #115. Evidence: `exp/EXP-11_smoke_reinforcement.py`.

### iter5 — 2026-10-08 — Cadence 0.78.0 / `750c8ef` — EXP-10 M2 (additive per-mind attribution)
- Also this day: monitor re-ran EXP-08 (M1) on v0.78 -> reproduces bit-identically (no drift).
- **Per-mind:** one collaboration, blocks 0,1 genuine / 2,3 fake (interior-identical). genuine minds
  mean transfer +0.250, fake minds -0.292, **attribution gap +0.542**. Worth LOCALIZES to the
  contributing minds within one collaboration.
- **Proportional:** aggregate transfer vs genuine fraction f: 0.0:-0.292 0.25:-0.115 0.5:-0.021
  0.75:+0.052 1.0:+0.208 (monotonic ~linear; f=1.0 matches EXP-08 genuine +0.219).
- VERDICT: **CONFIRMED — M2 ADDITIVE crossed.** Per-contributor (Shapley-relevant) worth attribution
  is measured, not argued. Honest: per-block SEM large (2 ctx/block quantizes to 0.5); block-0-genuine
  +0.125 within ~1 SEM of 0. **Super-additive SYNERGY (M2-synergy) NOT tested — a bandit can't cleanly
  represent XOR-style combination-only worth. That is the remaining M2 bar.**
- Evidence: `exp/EXP-10.out`, script `exp/EXP-10_vs_multimind_attribution.py`.

### iter4 — 2026-10-07 — Cadence 0.75.0 / `88f4dde` — EXP-09 M4-harden (split by hardware limit)
- **iter4a (low-gamma half, 20 seeds)** — transfer to T: gamma 0.0:-0.281(SEM.055) 0.25:-0.188(.054)
  0.5:-0.062(.032). Confirms at 20 seeds: a fake correlated with T at <=0.5 gives transfer
  indistinguishable from zero/negative. The "worthless fake prices to <=0" half is now FIRM.
- **iter4b (crossover band, 12 seeds)** — gamma 0.625:+0.021(SEM.044) 0.75:+0.021(.036)
  0.875:+0.094(.033) 1.0:+0.135(.045). Combined full curve is now MONOTONIC (iter3's non-monotonic
  wobble was 8-seed noise, resolved). Worth-threshold (>0.10) crossed firmly in gamma=0.875-1.0;
  everything at gamma<=0.75 prices to ~zero. A coordinated fake must agree with T on ~90%+ of
  contexts before transfer registers worth -> faking collapses into contributing.
- **M4 now: SUPPORTIVE with a clean curve** (noise objection resolved). Still owes a MATCHED in-harness
  peer-prediction scorer before "crossover higher than PP's 0.70" is decision-grade (the 0.70 number
  is from a different mechanism). Mixed-N (20-seed low half + 12-seed crossover), honestly labeled.
- Infra: probed greedy act() = PURE (clone==direct, stable) -> dropped save/load clone from eval in
  EXP-08+09. Real bottleneck is the witness ingest (1600 brain.live steps x seeds ~240s/20-seed-row),
  so >12-seed x 7-gamma runs exceed the 590s inline cap. Full-resolution harden belongs in the loop
  (no inline cap). Incremental per-gamma printing added so partial rows survive a timeout.
- Evidence: `exp/EXP-09.out` (iter4a), `exp/EXP-09-crossover.out` (iter4b).

### iter3 — 2026-10-07 — Cadence 0.75.0 / `88f4dde` — EXP-09 M4 gamma sweep, K=8, 8 seeds
- transfer to T vs prior-agreement gamma: 0.0:-0.344  0.25:-0.234  0.5:-0.078  0.625:+0.047
  0.75:+0.000  0.875:+0.094  1.0:+0.141 (SEM 0.04-0.09). baseline 0.578.
- Worth-threshold (transfer>0.10) crossed only between gamma=0.875 and 1.0. Peer-prediction agreement
  crossover ~gamma*=0.70 (paper 6.1) => here the worth bar sits HIGHER: a coordinated fake must carry
  nearly all the real T-information before transfer registers worth. Directionally: you cannot
  coordinate-fake a causal delta the way you can fake agreement -> faking collapses into contributing.
- VERDICT: SUPPORTIVE, NOT decision-grade. Curve noisy/non-monotonic at 8 seeds (gamma=0.75 dips to
  +0.000); the gamma*=0.70 comparison is CONCEPTUAL, not a matched peer-prediction baseline.
- Open: (a) rerun at 16-32 seeds for a clean crossover; (b) run an ACTUAL peer-prediction scorer in
  the same harness for a like-for-like crossover comparison. Both queued.
- Evidence: `exp/EXP-09.out`, script `exp/EXP-09_vs_gamma_coordinated_prior.py`.

### iter2 — 2026-10-07 — Cadence 0.75.0 / `88f4dde` — K=8, 16 seeds, 1600 steps, T'=anti-correlated
- genuine transfer **+0.219** (SEM 0.060, ~3.6 sigma above 0); fake_random **+0.008**; fake_wrong
  **-0.242**; baseline on T **0.523** (clean chance). separation genuine-vs-random **+0.211**,
  genuine-vs-wrong **+0.461**.
- own-task diagnostic: fake_wrong on its own T' = **0.719** (it DID learn), genuine on T' = 0.258.
  => competence on the wrong task is NOT worth on the exogenous task. Task-specificity measured.
- VERDICT: SEPARATES cleanly. **M1 crossed.** iter1's fake leak confirmed as K=4 chance-overlap
  artifact (fake_random +0.06 -> +0.008; fake_wrong +0.06 -> -0.24 once T' made anti-correlated).
- Honest open: genuine mastery partial at K=8 (5/16 seeds no transfer), so absolute separation is
  modest; fake is SURFACE-matched only (not interior-feature-matched = M2).
- Evidence: `exp/EXP-08.out`, script `exp/EXP-08_vs_transfer_separation.py`.

---

## NEXT ITERATIONS (the backlog the loop pulls from; keep ordered by value)

**2026-10-27 update (Will: "if v(S) can learn then that means more discovery between cadence teachers and v(S)"):** Noesis adopted calibration as its success measure (valuations today graded against later independent use; Noesis `docs/research/calibration-is-homeostasis.md`). The teacher market is the lag-free lab for it: worth is realized in minutes as student gain, fakes are controlled, and independence is controlled (fresh students). New candidates (Will-gated, pre-register with criteria first): **CAL-1** calibration-graded v(S): an estimator predicts each teacher's worth before teaching and is scored against realized student gain; does a v(S) trained on past realized transfer beat structural signals on held-out teachers and resist the EXP-08 fake classes? **CAL-2** multi-generation calibration in the heritable teaching game: does a learned v(S) predict which teachers' students later teach well? Existing support: EXP-62e priced anti-echo in proportion to the information it carried (about 38% of know-1's information edge, about 38% of its worth edge), i.e. pay tracked delivered information, the cost-to-fake line.

Previous list (ordered ~2026-10-08) superseded 2026-10-16; full re-rank in _rerank-2026-10-16.json.

**2026-10-21 update (iter44):** EXP-69 DONE, PARTIAL: the salience mark keeps replay open and recovers about three quarters of the cost's harm, but its writes still cost about .12 on the hidden chain. New candidate (memory track): EXP-70, is that residual the aliasing (visible chain, and marked misses kept out of the place records)? The V(S) top candidates from iter43 are unchanged.

**2026-10-21 update (iter43):** EXP-62i DONE, MOSTLY EXPOSURE; the cross-family gap sat in the zero (exploratory). New top candidates (Will-gated): the registered zero test; the per-stage look at why random late labels stop hurting D1 under the scaffold.

**2026-10-20 update (iter42):** EXP-62h DONE, RATE DEPENDS ON THE BRAIN (cross-family). New top: the exposure test (scaffold students to stage 3 so late-only teachers reach every brain; does the delayed-credit brains' late/early ratio rise toward D1's?). Pre-register before any data.

**2026-10-20 update (iter41):** EXP-62g DONE, MAGNITUDE ONLY (order holds across architecture; gap scales with uptake). EXP-62f SUPERSEDED. EXP-62b re-read scaled the same day (addendum in EXP-62b.md): its near relatives absorb equally (.43 vs .46) yet still differ on the scaled rate (D/know-4 .46 vs .66), so scaling is not a general fix. New top: pre-register a scaled exchange-rate test that includes both a near-relative pair and a cross-family pair, powered to separate about .10.

**2026-10-19 update (iter39):** EXP-62e DONE, BOUNDARY 4/5 (anti-echo carries information: labels right .25 vs .20; it fails the margin by .002). Zero-point redesigns closed as committed. New top: **EXP-62b** (item 2 below). For any later zero, use the random-label null alone or a class whose label accuracy is measured at chance.

**2026-10-19 update (iter38):** EXP-62d DONE, BOUNDARY 4/5 (abstain tripped the 2-SEM rule; the rule, not the measure, is the problem). New top: **EXP-62e** (below), then EXP-62b. No further zero-point redesign after EXP-62e.

000. **EXP-62e: non-superiority margin, powered for the class.** Milestone: M1b. Pre-registered in experiments/EXP-62e.md (2026-10-19, before any data); script exp/EXP-62e_margin_zero.py ready. EXP-62's harness, lesson 80, 216 fresh students (6_800_000+), pooled uninformative zero; CONFIRM needs ordered + Spearman >= .3 (n 864), know-4 >= .2, every fake's worth + 1.645 SEM < 1/32, know-1 beats every uninformative arm by 2 SEM paired, fake pay <= .10. KILL: any fake >= know-2. Cost ~56 min at 4 workers. Ready for the next loop fire.

**2026-10-17 update (iter37):** EXP-62c DONE, BOUNDARY 4/5 (zero point failed from the other side; leak reading withdrawn). New top: **EXP-62d** (below), then EXP-62b.

00. **(DONE 2026-10-19, iter38: BOUNDARY 4/5) EXP-62d: pooled zero with a noise allowance and a separation test.** Milestone: M1b. Pre-registered in experiments/EXP-62d.md (written 2026-10-17, before any data). EXP-62's harness, lesson 80, 72 fresh students (seeds 6_600_000 + student). Zero = per-student mean of the declared uninformative class {null, untaught, random, anti-echo}. CONFIRM if: know-1 < know-2 < know-3 < know-4 and Spearman >= .3 (n 288); know-4 >= .2; no uninformative arm and neither misleading arm (wrong-chain, echo) above zero by more than 2 SEM; know-1 beats every uninformative arm by >= 2 SEM paired; fakes take <= .10 of pay (pay vs the pooled zero, batches of 6, mean > 0 and t > 2). KILL: any fake >= know-2. Why: two BOUNDARYs on a criterion that fails by chance; this replaces it with a noise-aware test stated before seeing new data. Cost ~22 min. Ready for the next loop fire.

**2026-10-17 update (iter36):** item 1 (EXP-62) DONE, BOUNDARY 4/5 (zero-point criterion only). New order: **0. EXP-62c** (below), then item 2 (EXP-62b), then the rest unchanged.

0. **EXP-62c: price against the best fake in a declared class.** Milestone: M1b. What: EXP-62's harness and lesson 40 on FRESH seeds (6_400_000 + student), committed zero = anti-echo (the best labeller that sees only what the corrective schedule gives it: the executed action was wrong), pre-registered before any run; same CONFIRM criteria with fakes = random, wrong-chain, echo, abstain priced against anti-echo, plus Spearman and know-4 >= .2 against anti-echo (EXP-62's exploratory re-read gave know-4 +.213, know-1 +.030). Why: converts EXP-62's only failure into a decided test; the class argument fixes the zero point in advance rather than post hoc. Cost: about 15 min at 4 workers (72 x 10 twins at ~4.5 s). Kill: any non-anti-echo fake >= know-2 vs anti-echo. Ready.

1. **EXP-62, sharpened: does transfer price skill on a brain that takes in content, against a committed null?**

   **Milestone:** New rung M1b (content validity). Also re-crosses M1 and additive M2 on a multi-step chain, and tests the angle's premise ('a fake that produces the delta had to carry real task-information').

   **What:** Rung 0. Do this in the same fire, before the pilot, with no compute: apply the status corrections listed below; log EXP-49/52 plus the content sub-track (EXP-48/53/54/55/58/61) as iter35; replace NEXT ITERATIONS with this list; write the RUN GATE lines.

   Rung 1. Merge EXP-52's market (exp/EXP-52_noesis_lite_null_counterfactual.py) with EXP-58's delayed-credit brain and its alone phase run through step. Five changes:
   (a) Shared student seeds across teachers. EXP-52's seed base includes TEACHERS.index(kind) (line 69), so every teacher got different students, and the null and untaught twins were rebuilt for every job. Build them once per student instead. That gives a know-k ladder within each student and roughly halves compute.
   (b) Price against the stronger counterfactual. Worth = taught minus whichever of {random-label null, untaught} has the higher pooled mean on this instrument. This is a fixed rule, not a per-student max, which would push every price down and make the fake bar easier to pass. Report both counterfactuals.
   (c) Window pilot under the exact run conditions: 3 students, lesson lengths 40/80/120, know-1..4 plus random. EXP-58's know-4 is .932 at 120, close to ceiling. At 40 the steps between know-k levels are about .05.
   (d) Finalize pay on batches of 6 students per teacher. This replaces EXP-52's two-student > .125 rule, which leaked .209 of pay to fakes.
   (e) Log every twin's per-state greedy actions and every teacher's label stream, so items 5 and 6 can run mostly from saved data.

   Arms:
   - know-1..4;
   - random, wrong-chain, echo;
   - abstain (this is the untaught twin, so it costs nothing);
   - anti-echo: labels uniformly among the 4 actions other than the student's executed mistake. This is one line of code, because the labeller already receives `a` and fires only after executed mistakes (EXP-49 line 63).

   **Why now:** This is the binding question, and both lenses and all three readers agree. Each earlier run tested a different combination, and none tested all three conditions together:
   - EXP-49 was fooled: against an untaught twin a random fake earned +.179.
   - EXP-52 was blind: against the form-matched null, know-4 scored +.013 and Spearman was .06.
   - EXP-58/61 found content on only one brain: +.469 (11 SEM) on the delayed-credit brain vs +.016 on the default brain.
   That leaves exactly one untested combination: a brain that takes in content, the form-matched null and a known-skill ladder.

   Two more reasons:
   - EXP-62 has been ready since 10-14 and lost the 10-15 and 10-16 fires to the #202 memory track.
   - Every later chain rung reuses this harness.

   **Cost:** 1 fire. About 1-2 h of code (merging two existing scripts), about 3 min of pilot, and an estimated 25-35 min full run at 4 workers (72 students x about 10 twins x about 10 s per 120-attempt twin, scaled from EXP-58's 461 s). These are estimates, not measurements.

   **Ready:** Ready. Rung 0 has to land first in the same fire; otherwise the stale list keeps sending the loop to the queue.

   **Kill or confirm:** Pre-register the following.

   CONFIRM if all of these hold:
   - means are ordered know-1 < know-2 < know-3 < know-4, and pooled Spearman(worth, k) >= .3 (EXP-52's metric, n >= 288);
   - know-4 >= .2 against the stronger counterfactual;
   - every task-blind fake, abstain included, has mean <= 0;
   - fakes take <= .10 of pay.
   Then transfer prices skill on an instrument that takes in content, and the angle stands, with the instrument I and the null N named.

   KILL (angle refuted under its best conditions): any task-blind fake earns worth >= know-2 with adequate power.

   DECISIVE FOR NOESIS WITHOUT KILLING THE ANGLE:
   - Content is large but Spearman < .1. Then transfer is a pass/fail filter, not a price.
   - Anti-echo is > 0 by 2 SEM. Then the zero point has to be the best fake in a declared, committed class, not uniform noise, because the corrective schedule leaks one elimination bit per mistake to whoever does the labelling.

2. **EXP-62b: does the price among genuine contributions depend on which brain measures it? (absorbs EXP-64)**

   **PRE-REGISTERED 2026-10-19** in experiments/EXP-62b.md (48 fresh students, seeds 7_000_000+, zero = random-label null per EXP-62e, instruments A / B / C fixed as below, pilot rule on know-4 validity only). Script exp/EXP-62b_instrument_order.py.

   **Milestone:** Restated M5 (the instrument I as an outside ingredient) and the instrument axis of M3, which EXP-16 held fixed. Decides whether a worth independent of the instrument exists.

   **What:** Use EXP-62's harness, shared student seeds and chosen lesson length.

   Genuine teachers whose content is equal in size but different in kind:
   - know-early-2 (stages 0 and 1);
   - know-late-2 (stages 2 and 3);
   - know-4.
   Plus the random null and the untaught twin. Labels arrive only after mistakes the student executes, so late-stage knowledge reaches a student only if that brain gets that far. That is where instruments should disagree.

   Three instruments in one run:
   - (A) the delayed-credit brain;
   - (B) EXP-64's brain: the default memory brain with ONLY actor_eta .1 and actor_eta_bias .01 changed. This gives upstream its #198 reading at the same time;
   - (C) one delayed-credit variant, written into the pre-registration before any data (for example modules (64,) with critic rate 2). This guarantees two instruments that take in content even if B turns out blind. C must not be chosen by checking which brain separates.

   24 students.

   **Why now:** EXP-58 vs EXP-61 already shows that changing only the brain moves measured worth by about .45 (5.8 combined SEM), with the same contributions, task and oracle. If the ORDER of worth also depends on the brain, v(S) is defined only relative to a committed instrument, and whoever picks that instrument sets the price.

   After EXP-62 this is the cheapest way to falsify 'v(S) is a property of the contribution'. Folding EXP-64 in turns a 9-minute diagnostic into a comparison that can support a decision.

   I chose the early/late design over re-running the know-k ladder on a second brain. On any brain that takes in content, more knowledge giving more transfer is close to forced. The informative question is which knowledge each brain can use.

   **Cost:** 1 fire. Small code delta on top of EXP-62. About 15-25 min of compute at 4 workers (estimate).

   **Ready:** Blocked on EXP-62 (the harness and the chosen lesson length). The design is otherwise complete.

   **Kill or confirm:** CONFIRM: on every instrument that takes in content (content > 2 SEM), early-2, late-2 and know-4 come out in the same price order, and the early/late ratio agrees within about 2 SEM. Ordinal worth is then robust to the instrument, and only its scale is set by the instrument.

   KILL FOR NOESIS: the early/late order flips significantly between two instruments that both take in content. Then no worth exists independently of the instrument, and I and N must be committed from outside, in advance, just like T.

   If B is blind: that is the #198 reading (the actor step alone is not the block), and C carries the comparison. EXP-51 stays parked.

   **Added readout (design note 2026-10-16):** price inconsistency across the instruments as an OPH-style obstruction; prediction: fakes leave larger obstruction than genuine teachers. No extra compute (computed from the run's own rows).

3. **EXP-62c: M3 off the bandit, plus the in-expectation argument from the code**

   **Milestone:** M3 (isomorphism-invariance). Moves it from 'empirical on a saturated bandit' toward an argument. Bears on Noesis gate WASH-PROBLEM-INDEX row 9.

   **What:** Rung A, about 0.25 day, no compute, can run in any fire (including while EXP-62 computes in the background). Read Brain.compose initialization and the step/act update path. Check two things:
   - whether initial weights are exchangeable when input and output units are permuted;
   - whether the learning law and the action choice are permutation-equivariant.
   Look for argmax tie-breaking toward low indices, biases tied to particular actions, and positional context. If both properties hold, write the short argument that expected paired transfer is invariant under consistent relabeling.

   Rung B, 1 fire. Use the EXP-62 harness at a lesson length where learning does not saturate. Apply about 12-20 random consistent permutations of action indices and weather-input order to the chamber, the teachers' labels and the readout together. Same student seeds. Teachers know-2, know-4 and wrong-chain. Paired worth against EXP-62's committed counterfactual.

   State explicitly that relabeling the instrument itself is not covered; that is item 2.

   **Why now:** EXP-16's limits:
   - one permutation per task, not the 8!-element group;
   - learning at ceiling, which forces the .500;
   - the paired form was chosen after seeing the data.
   The 'provably' bar is unmet.

   The code read is the only route to an argument, and it costs almost nothing. One plausible invariance breaker is an inference, not measured: the text runs collapsed onto action 0 (EXP-43), which points at index-dependent behaviour.

   I ranked this above scale (the value lens had it 6th) because rung A is nearly free, and rung B reuses item 1's harness with no new build.

   **Cost:** About 1.25 total: 0.25 day of reading, plus 1 fire of about 25 min compute (estimate).

   **Ready:** Rung A is ready now. Rung B is blocked on EXP-62.

   **Kill or confirm:** CONFIRM: initialization is exchangeable and the learning law is equivariant in the code, and each teacher's worth stays within 2 SEM across all permutations with ranks preserved. M3 then holds in expectation, with a proof sketch.

   KILL: a named term breaks the symmetry (index-ordered tie-breaking, or a bias tied to a particular action), and some permutation moves a teacher's worth by more than 3 SEM. Then v(S) needs explicit symmetrization (averaging over a random relabeling committed in advance), and M3 stays open with that term named.

4. **Scale and interference on a brain that takes in content (stale item 4, never run on the transfer harness)**

   **Milestone:** M1 'robust across sizes' (currently unshown) and the stale NEXT item 4. Folds in EXP-07 (forgetting).

   **What:** Rung A, 1 fire. Extend the chamber from 4 to 6 stages, or add weathers. Run only the RUN GATE window pilot, with know-k and random teachers, on the best instrument from items 1 and 2.

   Rung B, 1 fire. Run the full know-k ladder and fakes at the chosen length, under item 1's pre-registered bars. Add a half-life arm: after the lesson, N attempts of unrelated life in a different chamber, then measure worth again.

   Optional if rung B has headroom: one non-label channel (per-step grades as in EXP-39).

   **Why now:** All of the content evidence on a chain comes from one chamber, one corrective schedule and 24 students per length (EXP-58's stated limits). The first step up from the bandit is what exposed the instrument problem (EXP-49), so the next step up must run only on a brain already shown to take in content.

   This is the only path to the 'robust across sizes' half of M1. It can kill: if content does not carry across tasks, Noesis would have to validate its instrument per task class.

   I placed it above the M5 curve because most of M5's new information can be derived at zero compute (see item 5).

   **Cost:** 2 fires (build and pilot, then run). Estimate.

   **Ready:** Needs design (the chamber extension). Blocked on EXP-62 passing at least its content and know-4 bars.

   **Kill or confirm:** CONFIRM: the know-k ranking and fakes <= 0 hold at 6 stages (Spearman >= .3), and worth keeps >= .5 of its lesson-end value after the unrelated life. KILL: ranking or fake pricing collapses as the chain gets longer, so the measure is valid only on short chains. Or worth decays to noise under ordinary continuing life, so transfer has to be measured immediately; that shapes the protocol's settlement window.

5. **M5 on the chain: a measured capture curve with an adversary that chooses which tasks it supplies**

   **Milestone:** M5 (exogenous anchor), restated as T + I + N.

   **What:** Rung 0, no compute; can ride in item 1's rung 0. Add a derived caveat to M5-EXOGENOUS-ANCHOR.md. In EXP-17's own linear model, genuine and fake differ only on contexts where R disagrees with T.
   - With a uniform adversary pool, both terms scale by (1 - a_R), so on a saturated learner q* = .5 for EVERY a_R. A bandit sweep over a_R alone therefore cannot move q*.
   - If the adversary supplies only states where R disagrees with T, the same model gives q* = (1 - a_R)/(2 - a_R): .33 at a_R .5 and .20 at a_R .75.
   This is derived, not measured. It applies only to an adversary that knows T well enough to find the states where its rule disagrees, which a deliberately built fake does (EXP-52's wrong-chain is built from c.right()).

   Rung 1, 1 fire. On item 1's harness and saved per-state logs, add consistent partial-rule teachers that agree with T on m of 4 stages (m = 1, 2, 3). Compute paired genuine-minus-adversary worth as a function of q under two pools: a uniform adversary pool, and a disagreement-selecting adversary pool. The only new compute is the partial-rule arms.

   **Why now:** EXP-17's own reflection admits q* = .500 is forced by the design. The derivation shows the stated boundary ('an honest majority of tasks') is an upper bound on q*. That changes the task-supply bond Noesis would need.

   The chain run checks whether the linear model survives learning that does not saturate. This is also Boardy's round-3 ask.

   It ranks below items 1-4 because answering it helps every approach equally, and most of its value is captured by the zero-compute rung.

   **Cost:** 0.1 day (rung 0) plus 1 fire (about 20 min of new compute plus analysis; estimate).

   **Ready:** Rung 0 is ready now. Rung 1 is blocked on EXP-62's per-state logs.

   **Kill or confirm:** CONFIRM (a useful boundary): measured q* tracks the derived curve. A disagreement-selecting adversary flips prices well below .5 (around .33 at a_R .5), and a uniform one at about .5. The honest task share Noesis must guarantee is then about 1/(2 - a_R), not one half. Write that into M5 as a design number.

   SURPRISE: q* on the chain sits far from both predictions. The linear model then does not describe a learner below saturation, and M5 must cite the measured curve only.

6. **Interior battery on the label streams, post hoc (makes M2's 'wash_sim adversary' literal)**

   **Milestone:** M2 (feature-matched fake). The program currently says 'ported from wash_sim.rs', which is not literally true.

   **What:** No new compute. Score every EXP-62 lesson on the interior features available from its logged label stream:
   - agreement with the student;
   - label entropy;
   - consistency within each stage;
   - coverage;
   - plus EXP-37's weight change dW where it can be computed.
   Report each feature's AUC for genuine vs each declared fake, next to transfer on the same rows. Then either make the M2 wording literal or delete 'ported'.

   **Why now:** This is the cheapest thing that moves M2. It replaces the 1-2 day port of novelty, synergy, cycle-energy and circulation onto EXP-10, whose interior is identical by construction, so that port would show little.

   It also answers, more cheaply, the key question a learned v(S) would raise: can label-stream features separate fakes? It polishes a rung that is already crossed, so it ranks below the open questions.

   **Cost:** About 0.3-0.5 day of analysis, 0 compute.

   **Ready:** Blocked on EXP-62 having run with label streams logged (change (e) in item 1).

   **Kill or confirm:** CONFIRM (the impossibility core on a second substrate): every interior feature ranks at least one fake at or above the genuine teachers, while transfer orders them correctly. For example, echo has total agreement and wrong-chain has perfect consistency.

   SURPRISE: some interior feature separates. That does not break the core, because these fakes were not built to match that feature. It does make 'a fake matched on that feature' the next adversary to build before claiming M2 against wash_sim's adversary.

7. **EXP-05: does a mid-lesson snapshot of the delayed-credit brain replay bit-identically in a fresh process, on main and on the #203 head?**

   **Milestone:** Instrument infrastructure. A precondition for committing I so that any validator can replay the twin.

   **What:** Snapshot a delayed-credit brain partway through a lesson and restore it in a fresh process. Check that it continues bit-identically and that the digests match. Do this on main (6499e56) and on the PR #203 worktree (~/_cadence_203, 9a2d422, checkpoint format cadence-generic/9).

   **Why now:** A verifiable v(S) needs any validator to replay the same twin and get the same delta. Same-process twins are shown: EXP-08 is bit-identical across versions and on the #203 head. Restoring the brain that carries content in a fresh process is not shown, and #203 changes the checkpoint format. The worktree already exists, so running both now covers the merge.

   **Cost:** 0.1-0.25. Filler for any fire whose main item is blocked or running in the background.

   **Ready:** Ready.

   **Kill or confirm:** CONFIRM: continuation is bit-identical on both, so the instrument can be committed and replayed. KILL: the runs diverge (RNG or replay state not captured). Measured transfer then cannot be verified independently until upstream fixes it; file an upstream issue with the minimal repro.

Dropped / parked (2026-10-16 re-rank):
- FOLD: standalone EXP-64 becomes instrument B in EXP-62b. Its #198 reading comes out of that run.
- DROP: the EXP-17 asymmetric sweep on the bandit, with only a_R varied. Under EXP-17's own linear model with a uniform adversary pool and saturated learning, q* = .5 for every a_R, so the run cannot move it. Replaced by the derived (1 - a_R)/(2 - a_R) caveat now, and by the chain capture curve (item 5).
- DROP: the 'self-sharpen' fake. On this schedule labels fire only after executed mistakes, so labelling the student's greedy action mostly reproduces echo. It would also need the student's policy, which the labeller signature (c, a) does not carry. Anti-echo replaces it.
- PARK: an 'eliminator' fake that remembers rejected actions per state. It learns the task from the student's own failures, which makes it a relay rather than a fake that never sees the task. Whether reprocessing the receiver's own feedback should be paid is a design decision to make before running it.
- PARK: learned v(S) trained on transfer labels. The labels come from the chamber's own oracle, not exogenous realized use, so this does not advance irreducible 2 as stated. The EXP-49/52 rows are labels of the jolt to the student, taken from a brain that does not take in content. Item 6 answers the fake question more cheaply. Revisit after items 1-2 pass, framed as a bound on distilling the live measure into a static scorer.
- PARK: the XOR wiring search (more columns, fan_in, parameter_prior): 2-3 days with a low prior. It would fix under-payment, not a wash hole. The boundary is written into M2's status instead. Keying on #203's recall codes would likely act as a lookup table and remove the synergy.
- DROP: the M1 size sweep on the bandit (K 8/16/32). The bandit is already a valid instrument; the scale question lives on the chain (item 4).
- PARK: porting wash_sim's novelty, synergy, cycle-energy and circulation scorers onto EXP-10. EXP-10's interior is identical by construction; item 6 does the same job on the chain for zero compute.
- PARK: M4 residuals (EXP-09 low-gamma rerun after the fix; peer prediction on brain behaviour with SEMs). These are filler for a fire whose main item is blocked, since M4's immunity to c holds by construction.
- PARK: M5 constructions (EXP-41 Sybil students vs network marginal value, commit-reveal sealed windows, priced-examiner noise sweep, realized-use task source). Stage them after item 5's curve says which one is needed. EXP-41 is out of scope while the protocol fixes the instrument. Also: cost-to-fake across 1/2/3 layers with independent vs correlated roots (design note 2026-10-16).
- PARK: EXP-51 gene-by-gene dissection. Run it only if EXP-62b's brain B is blind and upstream wants to know which gene blocks content.
- PARK: Shapley pricing extras (EXP-20b/21 free-rider game, paying an honest party on its best coalition, noise-twin ensemble) and Noesis-lite two-dimension finality vs a stake whale plus a ring, until item 1 shows pay rising with skill.
- OFF-PROGRAM: the memory track (EXP-66 and further #202 hold-rule work). The receiver that carries content has no episodic memory, and no program task needs hidden-progress chains. The #202 comment v2 is already posted (comment 6220420983, 2026-10-16), so nothing is waiting to be sent.
- OFF-PROGRAM: the text track (EXP-50; EXP-42-44 follow-ons) and pedigree/royalty economics (EXP-35b, EXP-38 follow-ons). They take v(S) as given.
- DROP: EXP-01b and EXP-02. Both rest on the retracted #164 eval bug.
- DROP: EXP-40 (brain size in the peer network). Will said abandon, and it covers only the teaching network.
- FOLD: EXP-07 (forgetting) into item 4's interference arm. PARK: EXP-06.
- DROP: the patch-world substrate plan inside the old M2-SYNERGY item. The snapshot twin exists, and the XOR wall belongs to the substrate.

DONE: M1-harden (iter2); M4 first pass (iter3); M1/M2/M4 rerun after the #164 fix (iter8); M4 matched PP (iter9); M3 empirical (iter10); M5 boundary statement (iter11); M2 data-channel synergy (iter12); M2 learned-composition synergy (iter13); content-channel prerequisite discharged (EXP-58/61, 10-14).
