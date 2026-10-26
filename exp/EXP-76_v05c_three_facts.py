"""EXP-76: on a THREE-fact conjunction, does a second or third held head help generalization once teaching is
stable?

Task (call it V0.5C): four witnessed roles, nine values per role, action = (role0 + role1 + role2) % 3, role3 a
distractor. Taught and held are complementary sets of (role0, role1, role2) triples chosen and checked by
exp/EXP-76_split_check.py (held answers determined by the taught triples under the declared residue class; one
fact alone and any two facts alone at chance in both panels; a memorizer at chance). The script refuses to run
if that check fails.

Built on Bernhard Mueller's V0.5B runner (exp/v05b/run_v05b.py, vendored, imported and NOT edited): its compose
settings (attention=True, learned_code=16, recall_heads=H, ...), warm, banks written by Recall itself for all
9^4 four-role patterns, install and answer are used as they are. The wrappers here supply the three-fact
label, the lesson and panel sampler over triples, the readings and the causal controls for three relevant
roles and up to three heads. Teaching is learning_surprise=True from lesson 0 (EXP-72; upstream d66f8ea docs).
Every reading is taken on a deepcopy, so readings never touch the training path. Pre-registration:
experiments/EXP-76.md.

    python -u EXP-76_v05c_three_facts.py --seed 76101 --heads 2 --out EXP-76-76101-H2.jsonl
    python -u EXP-76_v05c_three_facts.py --seed 76101 --heads 2 --lessons 256 --out smoke.jsonl  # smoke test
"""
import argparse
import importlib.util
import json
import pathlib
import sys
import time
from copy import deepcopy

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "v05b"))
import run_v05b as v  # noqa: E402  (Bernhard's runner, unchanged; its building blocks only)

import cadence as cd  # noqa: E402

_spec = importlib.util.spec_from_file_location("exp76_split_check", HERE / "EXP-76_split_check.py")
split_check = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(split_check)

CHECKPOINTS = (256, 512, 1024, 2048, 4096)
CONTROLS_AT = (1024, 4096)
RELEVANT, DISTRACTOR = (0, 1, 2), 3
LESSON_ROWS = 16
TAUGHT, HELD = (sorted(panel) for panel in split_check.split_v05c())
assert v.ROLES == 4 and v.VALUES == split_check.VALUES and v.ACTIONS == split_check.M


# ============ Three-fact wrappers ============

def labels(patterns) -> np.ndarray:
    return np.array([(p[0] + p[1] + p[2]) % v.ACTIONS for p in patterns], dtype=np.int64)


def sample(rng, n: int, triples: list) -> list:
    """n four-role patterns: a triple drawn uniformly from the panel, the distractor uniformly."""
    picks = rng.integers(len(triples), size=n)
    distractors = rng.integers(v.VALUES, size=n)
    return [(*triples[int(i)], int(d)) for i, d in zip(picks, distractors)]


def full_panel(rng, triples: list) -> list:
    """Every triple of the panel once, each with one distractor value."""
    distractors = rng.integers(v.VALUES, size=len(triples))
    return [(*t, int(d)) for t, d in zip(triples, distractors)]


# ============ Readings (on a copy) ============

def reading(brain, bank, patterns, erase=(), clone=False) -> dict:
    """Accuracy, choice histogram, modal share, per-class accuracy, and each head's top role record."""
    trial = deepcopy(brain)
    if clone:  # every further head reads with head 0's address
        for h in range(1, trial.recall.heads):
            trial.recall.head_maps[h - 1] = tuple(a.copy() for a in trial.recall.head_map(0))
    try:
        choice = np.asarray(v.answer(trial, bank, patterns, erase)).astype(np.int64)
    except RuntimeError as error:
        return {"refused": str(error)[:80]}
    truth = labels(patterns)
    counts = np.bincount(choice, minlength=v.ACTIONS)
    out = {"accuracy": float(np.mean(choice == truth)), "n": len(patterns),
           "choice_counts": counts.tolist(),
           "label_counts": np.bincount(truth, minlength=v.ACTIONS).tolist(),
           "modal_share": float(counts.max() / counts.sum()),
           "per_class": [float(np.mean(choice[truth == a] == a)) if np.any(truth == a) else None
                         for a in range(v.ACTIONS)]}
    role_slots = [v.RECORD[j][1] for j in range(v.ROLES)]
    tops = [np.asarray(p)[:, role_slots].argmax(axis=1)
            for p in (trial.recall.attended_heads or ()) if p is not None]
    out["top_role_counts"] = [np.bincount(t, minlength=v.ROLES).tolist() for t in tops]
    if len(tops) > 1:
        stacked = np.stack(tops)
        out["distinct_top"] = float(np.mean([len(set(col)) == len(tops) for col in stacked.T]))
        out["tops_all_relevant"] = float(np.mean((stacked != DISTRACTOR).all(axis=0)))
    return out


def controls(brain, bank, held, heads: int) -> dict:
    c = {f"role{j}_erased": reading(brain, bank, held, v.RECORD[j]) for j in RELEVANT}
    c["distractor_erased"] = reading(brain, bank, held, v.RECORD[DISTRACTOR])
    c["memory_off"] = reading(brain, bank, held, sum(v.RECORD.values(), []))
    if heads > 1:
        c["clone_heads"] = reading(brain, bank, held, clone=True)
    return c


# ============ Run ============

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--seed", type=int, required=True)
    p.add_argument("--heads", type=int, choices=(1, 2, 3), required=True)
    p.add_argument("--lessons", type=int, default=CHECKPOINTS[-1])
    p.add_argument("--out", required=True)
    a = p.parse_args()
    t0 = time.time()
    taught_t, held_t = split_check.split_v05c()
    split = split_check.report("V0.5C", taught_t, held_t)
    assert split["passes_all"], split["checks"]  # the admission gate: an identifiable split or no run
    checkpoints = sorted({c for c in CHECKPOINTS if c <= a.lessons} | {a.lessons})
    controls_at = {c for c in CONTROLS_AT if c <= a.lessons} | {a.lessons}
    brain = v.compose(a.seed, a.heads)
    assert brain.recall.heads == a.heads, (brain.recall.heads, a.heads)
    v.warm(brain)
    bank = v.banks(brain)
    panels = np.random.default_rng(99)  # evaluation panels, drawn once: every taught and every held triple
    taught, held = full_panel(panels, TAUGHT), full_panel(panels, HELD)
    rng = np.random.default_rng(1000 + a.seed)
    brain.retune(learning_surprise=True)  # stable teaching: only the wrong rows, from lesson 0
    level, refused = 1.0, 0
    with open(a.out, "w") as f:
        f.write(json.dumps({"cadence": cd.__version__, "seed": a.seed, "heads": a.heads, "lessons": a.lessons,
                            "teach": "surprise", "runner": "cadence-stone-age 5f038a3 building blocks",
                            "split_form": split_check.CHOSEN_FORM, "split_held_sums": split_check.CHOSEN_SUMS,
                            "split": split, "setup_seconds": round(time.time() - t0, 1)}) + "\n")
        f.flush()
        for lesson in range(a.lessons):
            patterns = sample(rng, LESSON_ROWS, TAUGHT)
            try:
                wrong = v.answer(brain, bank, patterns) != labels(patterns)
                level = 0.95 * level + 0.05 * float(wrong.mean())
                n = len(patterns)
                v.install(brain, bank, patterns)
                brain.act(v.event(v.NEUTRAL, n), greedy=True)
                brain.lesson(v.event(v.ASK, n), labels(patterns))
            except RuntimeError:
                refused += 1
            done = lesson + 1
            if done in checkpoints:
                row = {"lessons": done, "refused": refused, "level": round(level, 4),
                       "seconds": round(time.time() - t0, 1),
                       "taught": reading(brain, bank, taught), "held": reading(brain, bank, held)}
                if done in controls_at:
                    row["held_controls"] = controls(brain, bank, held, a.heads)
                row["seconds_after_readings"] = round(time.time() - t0, 1)
                f.write(json.dumps(row) + "\n")
                f.flush()
                print(a.seed, f"H{a.heads}", done, row["taught"].get("accuracy"), row["held"].get("accuracy"),
                      row["taught"].get("modal_share"), row["seconds"], flush=True)


if __name__ == "__main__":
    main()
