# EXP-77: M1b re-crossed on a current Cadence release (0.88.1, founder lateral)

- Date: 2026-10-26 (pre-registered `1f5f677`, run the same day) | Cadence version: 0.88.1 (`d66f8ea`) | Program iter: iter48
- Script: `exp/EXP-77_m1b_current_release.py` (EXP-73 exactly, on the ported composition in `exp/EXP-58_content_delayed_credit_brain.py`) | Evidence: `exp/EXP-77-*`

## Pre-registration (written 2026-10-26, before any EXP-77 data)

**Question.** Does M1b, crossed by EXP-73 on Cadence v0.84.3, still hold on the current release (0.88.1) under that release's own defaults?

**The port, and its gate (done before this file).** Cadence 0.85 renamed one setting the harness uses. `working_memory_scale=12.0` is now `scales={'trace': 12.0}`, and the old name is refused with a message saying so (`_configuration.rescaled`). EXP-58's `compose` now tries the old name first and switches to the new one only on that refusal, so old versions run exactly as before. Gate: on 0.88.1 with `lateral` pinned to -0.5 (0.84.3's unset value), EXP-73's identity gate reproduces every arm's actions and labels: **IDENTICAL** (EXP-62e student 0, seed 6_800_000, all ten arms, 55 s). That is one student, not every student, but it is the same check that admitted v0.84.3 for EXP-73. So the port is taken as exact, and a difference between this run and EXP-73 points to 0.88.1's defaults, not the port.

**What differs from EXP-73.** `lateral` is left unset, so the brain reads 0.88.1's founder: 0.0, where 0.84.3's unset lateral was -0.5 (upstream #220: at 4 to 8 actions -0.5 often fails the undamped settle; this chamber has 5 actions). The other 0.85+ founder changes (`need_scale` .1, `reset` keeps arousal) touch arousal, which this brain does not use. Everything else is EXP-73: delayed-credit brain, weather chamber, corrective schedule, 20 attempts alone through `step`, per-state greedy accuracy over 16 states on unseen weather, lesson 80, arms null, untaught, know-1..4, random, wrong-chain, echo, anti-echo.

**Students.** 216 fresh students, seeds 8_400_000 + student (disjoint from every earlier EXP-62 series run). Pilot: 6 students, seeds 8_390_000 + student, lesson 80; pilot data never enters the verdict.

**Pilot rule (fixed now).** The full run keeps lesson 80 so it stays comparable with EXP-73. The pilot is a stop check only: if the pilot's know-4 worth (against the same zero) is below .10, the full run does not start; the result is recorded as PILOT STOP and a lesson-length sweep is queued instead.

**Zero, admission, pay.** As EXP-73: Z = per-student mean of {null, untaught, random}; worth = arm minus Z on the same student; zero admitted iff for null and random the pooled share of labels naming the right action has a 95% binomial interval containing .20 (else VOID); pay on batches of 6 students per arm, finalized iff batch mean > 0 and mean / SEM > 2.

**Prediction.** CONFIRM, with know-1..4 within about .05 of EXP-73's (+.057 / +.163 / +.269 / +.436). Main risk: the lateral change moves the brain's uptake, so the ordering or know-4 >= .2 fails, or the zero moves enough to change the margins. Direction not predicted.

**Decision rules (EXP-73's, unchanged).**
- CONFIRM if all hold:
  1. know-1 < know-2 < know-3 < know-4 and Spearman(worth, k) >= .3 (n = 864);
  2. know-4 >= .2;
  3. non-superiority: for null, untaught, random, wrong-chain and echo, mean worth + 1.645 SEM < 1/32;
  4. know-1 beats each of null, untaught and random by at least 2 SEM, paired;
  5. know-1 beats anti-echo by at least 2 SEM, paired;
  6. all knowledge-free arms together (anti-echo included) take <= .10 of pay.
  Then M1b holds on Cadence 0.88.1 under its founder lateral, on instrument I (the delayed-credit brain). Limits as EXP-73: one brain, one chamber, one lesson length.
- KILL: any knowledge-free arm's mean worth >= know-2's.
- VOID: the zero admission check fails.
- Anything else: BOUNDARY, failing criterion named. A BOUNDARY or KILL here means M1b is pinned to the 0.84.3 laws, and the lateral change is the only candidate cause (the port gate rules out the port).
- Reported, not decisive: per-arm worth next to EXP-73's; EXP-62e's rule on the same data.

**Cost.** About 80 minutes at 4 workers (EXP-73: 4,764 s on 0.84.3), run detached; the pilot about 3 minutes.

## Summary
- Question: does M1b, crossed by EXP-73 on Cadence v0.84.3, hold on the current release (0.88.1) under its own defaults?
- Setup: EXP-73 exactly on the ported composition (`scales={'trace': 12.0}`; port gate IDENTICAL on 0.88.1 with lateral -0.5), lateral left at 0.88.1's founder (0.0). 216 fresh students (seeds 8_400_000+), lesson 80, 10 arms, zero = mean of {null, untaught, random}. Pilot (6 students, seeds 8_390_000+) passed its stop check (know-4 worth +.361). Full run 3,080 s at 4 workers.
- Prediction: CONFIRM, know-1..4 within about .05 of EXP-73's; main risk the lateral change moving uptake.
- Result: zero .439 (EXP-73 .439). know-1..4 +.060 / +.147 / +.250 / +.397 (SEM .009-.013), ordered, Spearman .581 (n 864). Margin upper bounds: null +.006, untaught +.018, random +.008, wrong-chain -.060, echo -.116 (all < .03125). know-1 beats null / untaught / random by 5.47 / 4.71 / 5.67 SEM and anti-echo by 4.1 SEM (anti-echo +.011, labels right .249). Knowledge-free arms take .033 of pay. No kill. **All six CONFIRM criteria hold.** Zero admission: random's labels right .199 [.195, .203], admitted; **null's labels right .1958 [.1919, .1997] (7,901 of 40,351), an interval that excludes .20 by .0003: not admitted.**
- Verdict: VOID by the pre-registered admission check. Not re-scored: the rules said VOID, so M1b is not re-crossed on 0.88.1 by this run.

## Reflection
- What it means: on the measure itself the current release behaves like v0.84.3. Same zero (.439), same order, every margin and separation passes, and know-4 sits .039 below EXP-73's (exploratory, unpaired, about 2 SEM; the lateral change is the only candidate cause). The run is VOID only because of the zero check. The null arm's labels are drawn uniformly from the five actions regardless of the right answer (`labeller('random')`: `int(rng.integers(5))`), so their true hit rate is exactly .2 by construction, and the observed .1958 is a 2.1 SE chance draw. The check tested by sample a property that holds by construction, at 95% on each of two arms, so it false-fails about 10% of the time whatever the instrument does. It did here.
- Process: port, gate, pre-registration and pilot all went as planned; no harness issue found. The flaw is in the decision rule, written into EXP-73 and carried over unchanged. It is the same family as EXP-62d's lesson (a significance test where the question is something else). Scoring the run as CONFIRM after seeing the data would be exactly the post-hoc rescue these pre-registrations exist to prevent, so it stays VOID.
- Lesson: don't admit a zero by a sample test of a property that is true by construction. Verify the construction instead (read the generator, plus a large seeded draw outside the run). Or, if a sample check is kept, set its false-fail rate on purpose across all the arms it covers.
- Next: M1b stays crossed on v0.84.3 only. Candidate EXP-77b (needs Will's go, since it changes a rule after a near-miss): fresh seeds, same six criteria, admission by construction (generator code plus a 10^6-label seeded audit) in place of the per-run interval. Report under the old check too, disclosed before data.
