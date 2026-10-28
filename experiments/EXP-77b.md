# EXP-77b: M1b on Cadence 0.89.0, zero admitted by construction

- Date: 2026-10-27 (pre-registered `4eb09f6`, run the same day) | Cadence version: 0.89.0 (`81345d8`) | Program iter: iter49
- Script: `exp/EXP-77b_m1b_construction_zero.py` (EXP-77 exactly, one rule changed); admission: `exp/EXP-77b_construction_audit.py` | Evidence: `exp/EXP-77b-*`

## Pre-registration (written 2026-10-27, before any EXP-77b data)

**Question.** Does M1b, crossed by EXP-73 on Cadence v0.84.3, hold on the current release (0.89.0) under its own defaults, when the zero is admitted by construction instead of by a per-run sample test?

**Why this run exists, disclosed.** EXP-77 (0.88.1) passed all six CONFIRM criteria. It was VOID only because the null arm's label hit rate (.1958, interval [.1919, .1997]) excluded .20 by .0003. Those labels are drawn uniformly from five actions, so their true hit rate is exactly .20. A 95% check on each of two such arms therefore fails about 10% of runs by chance alone (EXP-77 Reflection). Changing a rule after a near-miss is exactly what pre-registration exists to police. So the safeguards are: EXP-77 stays VOID and is not re-scored. This run uses fresh seeds. The new rule is fixed here, before any of its data. The old check is still computed and reported. Will gave the go for this change on 2026-10-27.

**The one rule that changes (admission).** The zero is admitted iff `exp/EXP-77b_construction_audit.py` prints ADMITTED BY CONSTRUCTION, run once before the pilot. Its checks, all deterministic:
1. code: the labeller entry point both labelled zero-class arms use (null and random) routes `random` to EXP-52's branch `return lambda c, a: int(rng.integers(5))`;
2. blindness: 1,000 labels produced with a chamber whose `right()` raises and an action whose `int()` raises (a label that read either would crash);
3. a seeded draw of 10^6 labels (seeds 77_000_002 / 77_000_003): every action's share within .002 of .2 (5 SE), the hit rate against a seeded right-answer stream within .002 of .2, and the hit rate per right answer within .004 (5 SE at about 250k each).
If any check fails, EXP-77b is VOID before any run. The per-run binomial interval is reported next to the verdict, not decisive.

**Everything else is EXP-77.** Delayed-credit brain on the ported composition (`scales={'trace': 12.0}`), founder lateral (0.0), weather chamber, corrective schedule, 20 attempts through `step`, per-state greedy accuracy over 16 states on unseen weather, lesson 80, arms null, untaught, know-1..4, random, wrong-chain, echo, anti-echo. Zero Z = per-student mean of {null, untaught, random}; worth = arm minus Z on the same student; pay on batches of 6 students per arm, finalized iff batch mean > 0 and mean / SEM > 2.

**Version.** 0.89.0 adds a recall-memory position term on by default; this brain composes no recall memory, and the port gate (EXP-73's identity gate, lateral pinned to -0.5) on 0.89.0 reproduces every arm's actions and labels of EXP-62e student 0: IDENTICAL (`exp/EXP-77b-gate-81345d8.out`, 100 s).

**Students.** 216 fresh students, seeds 9_000_000 + student (disjoint from every earlier run). Pilot: 6 students, seeds 8_990_000 + student; pilot data never enters the verdict.

**Pilot rule.** If the pilot's know-4 worth is below .10, the full run does not start; record PILOT STOP.

**Prediction.** CONFIRM, with know-1..4 within about .05 of EXP-77's (+.060 / +.147 / +.250 / +.397). The old interval check passes with probability about .9; its outcome is not predicted and does not decide.

**Decision rules (EXP-73's six criteria and KILL, unchanged).**
- CONFIRM if all hold:
  1. know-1 < know-2 < know-3 < know-4 and Spearman(worth, k) >= .3 (n = 864);
  2. know-4 >= .2;
  3. non-superiority: for null, untaught, random, wrong-chain and echo, mean worth + 1.645 SEM < 1/32;
  4. know-1 beats each of null, untaught and random by at least 2 SEM, paired;
  5. know-1 beats anti-echo by at least 2 SEM, paired;
  6. all knowledge-free arms together (anti-echo included) take <= .10 of pay.
  Then M1b holds on Cadence 0.89.0 under its founder defaults, on instrument I (the delayed-credit brain). Limits as EXP-73: one brain, one chamber, one lesson length.
- KILL: any knowledge-free arm's mean worth >= know-2's.
- VOID: the construction audit fails.
- Anything else: BOUNDARY, failing criterion named.
- Reported, not decisive: the old interval check; per-arm worth next to EXP-73's and EXP-77's.

**Cost.** About 50 to 80 minutes at 4 workers (EXP-77: 3,080 s), run detached; audit and pilot a few minutes.

## Status (2026-10-27)
- Construction audit run before the pilot: ADMITTED BY CONSTRUCTION (all six checks pass; 10^6 labels, shares .1997-.2006, hit .1995; `exp/EXP-77b-audit.out`).
- Pilot (6 students, seeds 9_070_000 to 9_070_005, not the registered 8_990_000+; see Errata): stop check passed, know-4 worth +.431 (>= .10). Pilot data never enters the verdict (`exp/EXP-77b-pilot.log`).
- Full run (216 students, seeds 9_000_000+) NOT STARTED: held by Will on 2026-10-27 (token budget given to the ETM doc sweep). Start with `TAG=full WORKERS=4 python -u EXP-77b_m1b_construction_zero.py` from `exp/`; the rules above stand unchanged.
- Full run (216 students) started 16:47 after Will lifted the hold ("we must also continue cadence experiments"), finished about 17:40 in one pass: 216/216, 3,284 s at 4 workers, no restart; the Cadence clone stayed at 0.89.0 (`81345d8`) throughout (`exp/EXP-77b-full.out`, `.jsonl`, `.json`).

## Summary
- Question: does M1b, crossed by EXP-73 on Cadence v0.84.3, hold on the current release (0.89.0) under its own defaults, with the zero admitted by construction instead of by a per-run sample test?
- Setup: EXP-77 exactly (EXP-73's harness on the ported composition, `scales={'trace': 12.0}`, lateral left at the founder 0.0; port gate IDENTICAL on 0.89.0 with lateral -0.5), one rule changed: the zero is admitted by `exp/EXP-77b_construction_audit.py`, run once before the pilot. Audit: ADMITTED BY CONSTRUCTION (code route and branch, blindness, 10^6 seeded labels with action shares .1997 to .2006, hit rate .1995, hit rate per right answer .1985 to .2003). 216 fresh students (seeds 9_000_000+), lesson 80, 10 arms, zero = mean of {null, untaught, random}. Pilot (6 students, seeds 9_070_000 to 9_070_005; see Errata) passed its stop check (know-4 worth +.431). Full run 3,284 s at 4 workers.
- Prediction: CONFIRM, know-1..4 within about .05 of EXP-77's (+.060 / +.147 / +.250 / +.397); the old interval check passes with probability about .9, outcome not predicted.
- Result: zero .446 (EXP-77 .439, EXP-73 .439). know-1..4 +.075 / +.157 / +.249 / +.385 (SEM .010 to .013). The six criteria:
  1. ordered (+.075 < +.157 < +.249 < +.385) and Spearman .549 (n 864), bar .3: pass.
  2. know-4 +.385, bar .2: pass.
  3. margin upper bounds (worth + 1.645 SEM): null +.007, untaught +.021, random -.000 (-.0003), wrong-chain -.084, echo -.140, all < .03125 (untaught the tightest, .010 inside): pass.
  4. know-1 beats null / untaught / random by +.077 / +.064 / +.084, that is 6.54 / 5.70 / 8.10 SEM, paired: pass.
  5. know-1 beats anti-echo by +.060, 5.7 SEM, paired (anti-echo worth +.015, SEM .009; its labels right .247 [.242, .251]): pass.
  6. knowledge-free arms together take .005 of pay (untaught .003, anti-echo .002, null / random / wrong-chain / echo 0), bar .10: pass.
  No kill: the highest knowledge-free worth is anti-echo's +.015, against know-2's +.157. Zero admitted by construction. **All six CONFIRM criteria hold.**
- Per-arm worth, EXP-77b / EXP-77 / EXP-73 (reported, not decisive): know-1 +.075 / +.060 / +.057; know-2 +.157 / +.147 / +.163; know-3 +.249 / +.250 / +.269; know-4 +.385 / +.397 / +.436; null -.002 / -.005 / +.006; untaught +.011 / +.008 / +.003; random -.009 / -.003 / -.009; anti-echo +.015 / +.011 / +.014; wrong-chain -.099 / -.076 / -.079; echo -.155 / -.132 / -.135. Zero .446 / .439 / .439; Spearman .549 / .581 / .638; knowledge-free pay .005 / .033 / .023.
- Old interval check (EXP-73 and EXP-77's per-run rule; reported, not decisive): null labels right .1993 [.1954, .2032] (8,065 of 40,466), random .1987 [.1948, .2026] (8,040 of 40,458). Both intervals contain .20: **passed**, so the old rule would also have admitted the zero.
- Prediction vs outcome: know-1..4 differ from EXP-77's by +.015 / +.010 / -.001 / -.012, all inside .05, and the verdict is CONFIRM: as predicted.
- Verdict: **CONFIRM (CROSSED)** by the pre-registered rules. M1b holds on Cadence 0.89.0 under its founder defaults, on instrument I (the delayed-credit brain); one brain, one chamber, one lesson length. EXP-77 stays VOID and is not re-scored.

## Reflection
- What it means: M1b is no longer pinned to the old release. The run used Cadence 0.89.0 under its own defaults (founder lateral 0.0) and 216 fresh students. Transfer priced the four real teachers in order. No knowledge-free arm earned more than +.015 (anti-echo), and the two misleading arms lost (.099 and .155). The weakest real teacher beat the best knowledge-free one (anti-echo) by 5.7 SEM, and knowledge-free arms took .005 of pay. Every real teacher sits within .015 of EXP-77's number, so the two founder-lateral runs (one VOID, one CONFIRM) tell the same story about the measure. The rung is now crossed twice, on v0.84.3 (EXP-73) and on 0.89.0 (EXP-77b), with EXP-73's limits unchanged: instrument I only, the weather chamber, lesson 80.
- What it does not show: no other brain (the default memory brain still does not take in content, EXP-52 and EXP-61; instrument dependence is the open EXP-62b / 62h / 62i line), no other chamber or lesson length, no later release. It does not re-cross M1b on 0.88.1: EXP-77 stays VOID. The zero is measured chance, so as in EXP-73 this answers the market question (does any knowledge-free arm out-earn the weakest real teacher?), not a zero-worth question: anti-echo still earns +.015, in line with the information its labels carry (right .247 against .20). Exploratory, unpaired, not a test: know-4 sits .051 below EXP-73's (about 3.1 SE) and .012 below EXP-77's. Both founder-lateral runs sit below EXP-73 at know-4 (.039 and .051), which points to the lateral change (0.0 against -0.5) lowering the top teacher's uptake by about .04 to .05. wrong-chain and echo are about .02 more negative than in either earlier run (about 1.5 to 1.7 SE unpaired each), within sampling.
- Did the rule change matter: no, not on this data. The old per-run interval check also passes (null .1993, random .1987, both intervals containing .20), so EXP-77b scores CONFIRM under EXP-73's original rule too. Admission by construction removed a chance false-fail of about one run in ten before any data came in, but on this draw it did no work, and the crossing does not depend on it. The one thing the per-run check can catch that the audit cannot (a labeller at run time that differs from the audited one) was also clear here. Read together, two independent 216-student draws at the founder lateral both pass all six criteria, and one of them failed the sample check by .0003, which fits a check that false-fails about one run in ten. This run does not rescue EXP-77; it replaces it on fresh seeds.
- Process: audit, pilot and full run went as registered; one pass, no restart, no harness change after registration. We re-scored the raw jsonl with a separate script (216 records, seeds 9_000_000 to 9_000_215). It matched the run's own scoring on every result figure: the zero, each arm's worth and SEM, the margins, the separations, Spearman, pay, the kill test and the label rates. The audit figures come from `exp/EXP-77b-audit.out`, and the EXP-73 and EXP-77 figures from their own `-full.json` summaries. Two notes from that check, neither changing a criterion. (a) The harness's `spearman` breaks ties by position instead of averaging them; with tie-averaged ranks Spearman here is .563, so the registered .549 is the lower figure (the same function scored EXP-73 and EXP-77, so the three runs compare). (b) The log carries two Cadence RuntimeWarnings (a finite teaching free phase used its whole `free_steps` budget). EXP-73's and EXP-77's logs carry the same warning (4 and 1), and Python's default filter shows it once per worker process, so how many lessons it touched is not recorded.
- Lesson: when a rule is changed after a near-miss, score the new data under the old rule too (EXP-73's lesson, applied again). Here both pass, so the honest report is that the change removed a risk but did not make the result.
- Next: M1b holds on two releases on one instrument. The next rung on the current API is instrument dependence (the EXP-62b / 62h / 62i line), or the Will-gated calibration candidates CAL-1 / CAL-2 (VS-TRANSFER-PROGRAM.md NEXT ITERATIONS, 2026-10-27).

## Errata (2026-10-28, found while drafting CAL-1; the pre-registration above is left as written)
- Pilot seeds. The registration says the pilot used seeds 8_990_000 + student. It ran on 9_070_000 to 9_070_005 (`exp/EXP-77b-pilot.jsonl`): under `TAG=pilot` the harness adds 1000 x lesson (lesson 80) to the base. EXP-77's pilot has the same mismatch (8_470_000+). Those seeds do not overlap the full run's 9_000_000 to 9_000_215, and pilot data never enters the verdict, so nothing scored changes.
- "Disjoint from every earlier run" is false as written. It holds among the delayed-credit runs only. EXP-52's third seed block runs each lesson at `base` and `base + 5`, with `base = 3_000_000 x 3 + 1000 x teacher + 10 x student` (`exp/EXP-52_noesis_lite_null_counterfactual.py:67-68`), so 9_000_000 to 9_006_115. Its first teacher alone uses 24 of EXP-77b's student seeds (9_000_000, 9_000_005, 9_000_010, ... 9_000_115); this counts only the two bases, not any offsets inside its `twins`. EXP-52 ran a different brain in a different chamber, and no EXP-77b choice was tuned on its outcomes, so the overlap repeats random streams without leaking a result. The verdict stands.
