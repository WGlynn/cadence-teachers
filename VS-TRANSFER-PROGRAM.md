# V(S) TRANSFER PROGRAM — the standing north star of the Cadence experiment loop

> Will, 2026-10-07: *"continue spending computing power to try solving the problem until we get
> there ... this is the Cadence loop from now on."* The daily Cadence experiment loop
> (`cadence-experiment-loop`) advances THIS program first, every fire, until the solved-criteria
> below are met or a hard wall is proven. Generic queue items are secondary.

Keep every claim honest-floor-first ([F·teammate-not-salesman]). Numbers, not hopes. Version-stamp
against the live clone (`~/_cadence_study`, kept at HEAD by the monitor loop).

---

## THE PROBLEM (grounded — do not re-derive from memory)

Canonical statement: `~/Desktop/vs-value-measurement-problem-paper-2026-10-07.md`.
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

---

## SOLVED-CRITERIA (when does the loop stop / ping Will)

A chain of increasingly hard bars. Each is a real milestone; ping Will on each crossing.

- **M1 — separation exists.** Measured transfer separates genuine from a surface-matched fake on an
  exogenous task (genuine transfers, fakes ~0), robust across seeds/sizes.  [STATUS: CROSSED iter2 —
  genuine +0.219 (~3.6 SEM) vs fake_random +0.008, fake_wrong -0.242, clean chance baseline, own-task
  diagnostic confirms task-specificity. Still only SURFACE-matched; interior-matched fake = M2.]
- **M2 — feature-matched fake.** Separation survives a fake matched on ALL interior features the
  paper's impossibility uses (novelty, synergy, acyclic topology, content-stats), not just surface
  stats. This is the real adversary from wash_sim.rs, ported to learning agents.  [STATUS: ADDITIVE
  half CROSSED iter5 (EXP-10) — multi-mind collaboration, interior-identical genuine vs fake minds;
  transfer localizes worth PER-MIND (+0.250 vs -0.292, gap +0.542) and scales ~linearly with genuine
  fraction. SYNERGY half OPEN — super-additive (combination-only, XOR-style) worth NOT representable
  in a small bandit; needs a different substrate/task design. This is the remaining M2 bar.]
- **M3 — isomorphism-invariance.** The transfer measure provably satisfies v(S)=v(phi(S)) for any
  structure-preserving relabeling phi of everything v may see. (The paper's formal success criterion.)
- **M4 — coordinated-prior robustness.** Separation holds against a coordinated-but-wrong prior past
  the peer-prediction crossover (paper reports gamma*=0.70 for correlated-agreement). Transfer should
  beat that because it reads a causal delta, not agreement.  [STATUS: SUPPORTIVE, clean curve (iter4) —
  monotonic, worth bar firmly at gamma=0.875-1.0, everything <=0.75 ~zero. Noise objection resolved.
  Still owes a MATCHED in-harness peer-prediction scorer before the >0.70 comparison is decision-grade.]
- **M5 — exogenous anchor honesty.** State precisely what exogenous ingredient the measure still
  assumes (the disjoint task / capital-independent reference set) and whether any part of it can be
  sourced from a cost-bearing real signal rather than assumed. This is the irreducible-1 anchor; may
  end as an honest boundary ("this is what still must come from outside"), which is itself a result.

"Solved" = M1-M4 crossed with measured robustness + M5 stated as either a construction or a proven
boundary. Realistically this is a long program; the loop's job is to advance it one honest rung per
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

2026-10-08 (iter11): M5 STATED AS BOUNDARY (EXP-17: task-pool capture flips at q*=0.5; see M5-EXOGENOUS-ANCHOR.md). Only M2-SYNERGY remains open.

2026-10-08 (iter8, post-#164 eval fix): **M1 CROSSED (stronger, +0.42 vs fakes <=-0.11) · M2 ADDITIVE CROSSED (gap +0.854) · M3 CROSSED EMPIRICALLY (EXP-16: paired transfer invariant in 95/96 cells; raw delta only in expectation) · M4 CROSSED on a matched PP baseline (EXP-15: PP flips at c~0.5 coordination, transfer unaffected given exogenous T; cost = M5) · M2 SYNERGY OPEN.** Numbers below this line are pre-fix.

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
  Reply draft: Desktop/maarten-reply-brain-gains-2026-10-09.md. Testable: weight-change vs measured transfer.

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
  the fake passed 2 seeds the same way. Kept as `exp/EXP-19-fedonly.out`.
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
  by up to 0.25 under phi; ensemble gap max_phi|v_n(phiS)-v_n(S)| at n=8 = 0.125 / 0.062 / 0.031 on the
  3 tasks (n=1 up to 0.25). Cause identified: the noise is the instrument's PRIOR (acc_base), which
  mirrors under action-swap (base -> 1-base) while acc_after saturates (genuine 1.0, fake 0.5).
- **Paired form v_pair = transfer(witness) - transfer(reference witness) on the same instrument cancels
  the prior: genuine-minus-fake = 0.500 in 95/96 cells** (one 0.625). So invariance holds per instance
  once the measure is defined RELATIVE to a reference on the same twin, not against the instrument's own
  baseline.
- **M3 VERDICT: CROSSED EMPIRICALLY for the paired measure, on this bandit; NOT a proof.** Caveats: the
  exactness leans on learning saturating (after = 1.0 / 0.5); with partial learning the paired form
  should still cancel the prior but will carry learning noise. Only context-perm + action-swap tested
  (the full symmetry group of this world), 3 tasks. Design consequence: the v(S) used in pricing should
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
  partly by construction, since it consumes an exogenous held-out T that PP does not have. What is shown:
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
  learning" (`~/Desktop/C__Users_dongy_reports_fast_cadence_method.md`). Will: extract the raw speed
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

1. **M2-SYNERGY** (TOP — the hard open core). Additive/per-node M2 is DONE (iter5: mapping-level
   fake_wrong priced to -0.24; multi-mind per-contributor attribution gap +0.542). What remains is
   SUPER-ADDITIVE synergy: worth that exists ONLY in the combination of minds (e.g. T=XOR(b1,b2);
   neither witness alone enables T, both together do). A small Cadence bandit cannot cleanly represent
   combination-only worth from separate bit-teachers. Needs a different design: either a brain whose
   input encodes both witnesses' learned reps and a held-out task that reads the joint, or a
   compositional-perception curriculum, or a richer substrate. Design carefully (do NOT fake the
   synergy with additive coverage — that is iter5, already done). This is where the measure either
   captures emergent collaborative worth or hits an honest boundary.
   **SUBSTRATE NAMED (Bernhard, 2026-10-07 TG, convergent):** `muellerberndt/cadence-demos/patch-world`
   — a multi-creature evolutionary world (survival/mass task = real held-out consequence, `speak`
   action = creature-to-creature contribution, private-imagination = twin-like rollout). Bernhard
   independently proposed our exact twin-brain-ablation edge ("byte-identical twin; a useless
   contribution leaves a settled learner unchanged") and suggested patch-world as the model. Minimal
   synergy probe: freeze creature b, fork a byte-identical twin, expose only one to a's output over a
   window, measure survival/reward gap on a held-out stretch; synergy = two signals that help only
   combined. GATING QUESTION RESOLVED (2026-10-08, read the code): the byte-identical twin EXISTS at
   the creature level. `cadence.experimental.equilibrium.Reinforcement.snapshot()` saves brain +
   replay + pending action + RNG state for exact continuation; `.from_snapshot(text)` reconstructs
   (schema `reinforcement/3`, strict-validated). patch-world's `library_brain.py` builds exactly a
   `Reinforcement` creature; the README "no saved continuation" is about the browser PAGE, not the
   creature API. => M2-synergy probe is buildable SOLO on the equilibrium Reinforcement substrate
   (richer than our bandit: multi-patch columns, 106-dim continuous senses, replay), no full JS world
   and no waiting on Bernhard. Build on current 0.78 (snapshot confirmed present); patch-world itself
   pins 0.70.0. Design care: construct a genuinely super-additive task (combination-only worth), NOT
   additive coverage (that was iter5).
2. **M4-harden**: rerun the gamma sweep at 16-32 seeds for a clean crossover AND implement a real
   peer-prediction/correlated-agreement scorer in the same harness, so "transfer's bar is higher than
   0.70" becomes a MATCHED measurement, not a conceptual comparison.
3. **M3 invariance test**: apply structure-preserving relabelings (permute contexts/actions/module
   seeds consistently) and confirm the transfer score is invariant; find any relabeling that moves it.
4. **scale/robustness**: larger brains/tasks, longer witnesses, transfer half-life, and whether the
   delta survives when b has its own ongoing life (interference). Also lift genuine mastery at K=8
   (more steps/bigger net) so absolute separation is not capped by partial learning.
5. **M5 anchor write-up**: once M1-M4 measured, state the residual exogenous assumption precisely;
   decide construction-vs-boundary. Feeds a paper section + Bernhard note (Will dispatches).

DONE: M1-harden (iter2, crossed) · M4 first pass (iter3, supportive).
