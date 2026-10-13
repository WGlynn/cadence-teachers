# EXP-37: weight-change filter (can we read a brain's gain from how much its weights moved?)

- Date: 2026-10-09 | Cadence version: v0.78.0 (iter26 states iter24 ran on 0.78; not stamped in the output) | Program iter: iter24
- Script: `exp/EXP-37_weight_change_filter.py` | Evidence: `exp/EXP-37.out`, `exp/EXP-37.json`

## Summary
- Question (Maarten G): can a brain's gain be measured from the inside, by how far its weights moved, instead of by an
  outcome test?
- Setup: EXP-08 harness (K=8 bandit, plain Cadence Brain). Same founder snapshot, three lessons: genuine (teaches the
  held-out task T), fake_wrong (teaches the opposite rule), fake_random (reward unrelated to action). Per twin: dW = L2
  norm of the change in all saved parameter arrays vs the founder; v = measured transfer on T. 16 seeds.
- Prediction: "dW is similar for genuine and fake_wrong (both learn a rule) while v differs hugely, so dW is worth-blind;
  at best dW separates 'learned something' (genuine, wrong) from noise (random): a pre-filter, not a price."
- Result (16 seeds): genuine dW 2.585 (sd 0.234), worth +0.422; fake_wrong dW 2.443 (sd 0.206), worth -0.578;
  fake_random dW 1.439 (sd 0.670), worth +0.008. Correlation(dW, worth) over all lessons: -0.02. In one seed (14)
  fake_random moved weights 3.89, more than any genuine lesson.
- Verdict: CROSSED for the worth-blind claim (prediction confirmed: genuine and opposite-rule lessons move weights about
  equally while worth differs by 1.0). The pre-filter part is only SUPPORTIVE: noise moves weights less on average, but
  not reliably (seed 14). Still current; nothing later retracted it.

## Reflection
- What it means: how much a brain changed says nothing about whether the change was worth anything; an outcome test (or
  twin transfer) is required to price a lesson. Weight change can at most flag "nothing was learned" as a cheap first pass.
- Process: small and quick, 16 seeds with a large, consistent separation, so adequately powered for the main claim.
  Caveats: v is measured on 8 contexts, so it moves in steps of 0.125; the pooled correlation is dominated by the
  genuine vs fake_wrong split rather than variation within a lesson type; dW is a raw L2 norm over all parameter arrays
  with no per-layer normalisation; only one task and one brain size; the fake_random arm has one large outlier that
  breaks a clean threshold. SEM not reported (sd only). Version not stamped in the output.
- Lesson: interior change is not a price signal; use it only as a pre-filter, expect outliers, and never let it veto a
  lesson on its own.
- Next: answered Maarten (reply draft `Desktop/People/maarten-reply-brain-gains-2026-10-09.md`). HANDOFF lists a further
  "Maarten's weight-filter check" queued after EXP-35b; not run yet.
