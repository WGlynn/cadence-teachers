# EXP-57: confirm on fresh seeds that keeping misses out of the temporal context makes the greedy ambiguous chain clean

- Date: 2026-10-14 | Cadence version: 0.83.0 (`23dba71`, `~/_cadence_study`) | Program iter: none (memory track; confirmatory follow-up to EXP-56; the reading the group thread is waiting for)
- Script: `exp/EXP-57_confirm_hold_greedy.py` (reuses EXP-56's chamber, brain, trace rule and readings) | Evidence: `exp/EXP-57-full.json/.jsonl/.out`

## Summary
- Question: in EXP-56, holding decisions that left the observation unchanged out of Cadence's temporal context did not help recovery after a miss (the pre-registered hypothesis, refuted), but in a reading without a prediction it tripled clean greedy passes of Huncho's ambiguous chain (17 of 48 vs 5 of 48; McNemar 14 vs 2, p = .004). A clean greedy pass has no misses, so the hold rule never fires during that reading: any difference there comes from what training stored. Post-hoc hypothesis: without hold, each different run of misses at a stage is a different context path, so the stage's rewards and corrections are split across many keys (the split `docs/episodic.md` describes); with hold they all land on the first-try key.
- Setup: EXP-56 exactly, arms `ctx5` and `hold5` only, fresh seeds (57_000 + i, none used in EXP-56), both signals (natural, corrective). Horizon 120 attempts with 48 seeds per signal (primary), and 240 attempts with 24 seeds per signal (Huncho's V7.3 horizon, secondary).
- RUN GATE: (1) prediction below, written before any run. (2) Window: EXP-56 is the pilot (same chamber and arms; greedy exact rates 5/48 and 17/48, off floor and ceiling); no new pilot. (3) Variance: arms share each seed; paired exact McNemar for passes, paired SEM for rates. (4) Metric: greedy exact pass (all four stages in four greedy decisions). (5) Chain: hold at training time -> a stage's records concentrate on its first-try key -> the greedy first choice at each stage is right -> clean pass.
- Prediction (written before any run):
  - (P1, primary) At 120 attempts, greedy exact pass hold5 > ctx5 pooled over both signals: more hold-only than ctx5-only pairs, exact two-sided McNemar p < .05 (96 pairs).
  - (P2) At 120, first-try accuracy P(right | r = 0) is higher under hold5, pooled, by more than 2 SEM.
  - (P3) At 120, sampled success differs by less than .05 either way (recovery-dominated; EXP-56's +.019 replicates).
  - (P4) At 240 attempts, hold5 still has more clean greedy passes than ctx5 (more hold-only than ctx5-only pairs, 48 pairs).
- Decision rule (written before any run): P1 holds -> report to the group with these numbers: keeping only observation-changing decisions in the temporal context makes the greedy ambiguous chain clean far more often, and it acts through what training stores (the rule never fires in a clean pass); a non-learned instance of "which memories matter" and a concrete target for a learned write gate. P1 fails -> EXP-56's greedy result was a lucky contrast among several readings; report only the refuted erosion mechanism and the replication of V7.2's direction.
- Result (fresh seeds 57_000+; `exp/EXP-57-full.*`):

  | horizon, signal | pairs | clean greedy passes, hold5 vs ctx5 | hold-only / ctx5-only (exact McNemar p) | first-try accuracy, hold5 - ctx5 (SEM) | sampled success, hold5 vs ctx5 (diff, SEM) |
  |---|---|---|---|---|---|
  | 120, natural | 48 | 9 vs 2 | 9 / 2 (p .065) | +.129 (.040) | .604 vs .436 (+.168, .068) |
  | 120, corrective | 48 | 29 vs 2 | 27 / 0 (p < .0001) | +.219 (.026) | .898 vs .562 (+.336, .056) |
  | **120, pooled** | 96 | **38 vs 4** | **36 / 2 (p < .0001)** | **+.174 (.024)** | .751 vs .499 (+.252, .045) |
  | 240, natural | 24 | 12 vs 2 | 11 / 1 (p .006) | +.174 (.063) | .719 vs .505 (+.214, .112) |
  | 240, corrective | 24 | 11 vs 7 | 8 / 4 (p .39) | +.104 (.047) | .876 vs .775 (+.102, .097) |
  | **240, pooled** | 48 | **23 vs 9** | **19 / 5 (p .007)** | +.139 (.039) | .798 vs .640 (+.158, .074) |

  Accuracy after a miss (P(right | r >= 1)), hold5 - ctx5: +.130 (SEM .025) at 120, +.097 (.045) at 240; at the first try +.174 and +.139. So hold helps both, more at the first try; EXP-56's flat after-miss reading (+.009) was that seed set.
  P1 HELD (36 vs 2 discordant pairs, p < .0001). P2 HELD (+.174, 7 SEM). P3 FAILED: sampled success did not stay flat, it rose +.252 (5.6 SEM); EXP-56's +.019 on its 48 pairs now looks like that seed set's luck (pooled over both experiments, 144 pairs, the sampled gain is about +.17). P4 HELD (19 vs 5, p = .007 at 240).
- Verdict: SUPPORTIVE, 3 of 4. On fresh seeds, keeping decisions that left the observation unchanged out of the temporal context takes clean greedy passes of the ambiguous chain from 4% to 40% at 120 attempts (60% with corrections), raises first-try accuracy by .17, and keeps a lead at 240 attempts. A clean pass never fires the rule, so the gain is in what training stored. Decision rule: P1 held, so the reply to the group carries these numbers.

## Reflection
- What it means: Cadence already applies this rule to its replay path (`_extend_paths`: a decision taken on the observations of the previous decision replaces it, because it "left the situation as it was"), but not to the temporal context that keys its episodic records. Applying the same rule to the key, with no learning at all, is the largest single lift we have measured on the ambiguous chain. It is one concrete, non-learned answer to Bernhard's "which memories matter": here, the decisions that changed something. On Huncho's V7.3 question: with corrections, the plain context's clean passes grow with training (2 of 48 at 120 to 7 of 24 at 240), and from reward alone they barely move (2 of 48 to 2 of 24); the rule's lead holds at both horizons.
- Process: pre-registered before any run, fresh seeds, EXP-56 as the pilot; the primary was a post-hoc reading in EXP-56 and is now confirmed. P3 was a prediction of no change and failed; the record keeps it. Limits: our rebuild of the chamber (not Huncho's code), one composed brain, efference off, an instrument-level rule (a library gene would be the real test), and a task where the one memory that matters is the last observation change by construction; a task where an unchanged observation still carries information (a timer, a wait) would break this rule.
- Lesson: when an exploratory run turns up an effect in a reading you did not predict, the confirmatory run on fresh seeds is what lets you say it; here it was larger on fresh seeds, and the metric I predicted flat moved too.
- Next: report to the group (Will sends); the rule as an opt-in library gene is a judgment-class upstream proposal (draft, Will-gated); test the boundary (a chamber where an unchanged observation still matters).
