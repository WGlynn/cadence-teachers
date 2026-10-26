"""EXP-76: a taught/held split of the 729 (role0, role1, role2) triples for the three-fact task
action = (role0 + role1 + role2) % 3, nine value symbols shared by every role.

A held triple tests generalization only if the taught triples determine its answer under a declared
hypothesis class. The class (as in V0.5B's split check, extended to three facts): each of the nine
value symbols carries a hidden residue in Z3, the SAME residue in every role (the value inputs are
shared across roles), and the action is a fixed map Z3 -> {0, 1, 2} of the residue sum.

Checks (all by exhaustive enumeration over the 729 triples):
  1. identifiable: all 3^9 residue assignments x all 27 maps; count the explanations that fit every
     taught triple and the held triples on which they all agree with the rule.
     Cross-checked against a GF(3) rank computation of the same class.
  2. single-fact chance: in both panels, each relevant role's value alone predicts each action
     equally often.
  3. pair chance: in both panels, each value PAIR of any two relevant roles predicts each action
     equally often, so a learner using two of the three facts is at chance.
  4. memorizer: no held triple is taught (exact lookup is at chance); also a nearest-neighbour
     memorizer (plurality of the taught triples at the least Hamming distance, ties split evenly).
  5. size: at least 81 held triples, and the taught triples identify the residues (check 1).
Extra (reported; used to choose among passing candidates, never to relax 1-5):
  E1. role-specific Z3 codes: each (role, value) carries its own residue (GF(3) rank).
  E2. shared affine Z9 codes: residue alpha * v + beta in Z9, any map Z9 -> {0, 1, 2} of the sum.
      This catches a split defined by a symmetric form (r0 + r1 + r2) mod 9, whose held sums would
      never be seen in taught. Affine codes only; all 9^9 shared Z9 codes are not enumerated.
  E3. every value pair of any two relevant roles occurs in BOTH panels, so a held triple is new
      only as a triple (no held failure can come from an untaught pair).

The search family: held iff (r0 + b*r1 + c*r2) mod 9 in S, for b, c in 0..8 and S a 3-subset of
Z9 (scaling the form by a unit gives the same family, so the role0 coefficient is fixed at 1).
The chosen split is the first candidate, in (b, c, S) order, that passes 1-5 and E1-E3.

    python EXP-76_split_check.py                  # search (about 2.5 min), then the chosen split's report
    python EXP-76_split_check.py --chosen-only    # the chosen split's report only
"""

from __future__ import annotations

import itertools
import json
from collections import Counter

import numpy as np

VALUES, M = 9, 3
TRIPLES = list(itertools.product(range(VALUES), repeat=3))


def rule(t) -> int:
    return (t[0] + t[1] + t[2]) % M


def split(form=(1, 1, 2), held_sums=(0, 1, 2)):
    """Held iff (form . triple) mod 9 lies in held_sums; taught is the rest."""
    held = [t for t in TRIPLES if sum(f * x for f, x in zip(form, t)) % VALUES in held_sums]
    held_set = set(held)
    return [t for t in TRIPLES if t not in held_set], held


# ============ 2-3: chance for one fact and for any two facts ============

def chance(panel, roles) -> bool:
    """Every value combination of ``roles`` that occurs in the panel predicts each action equally
    often (all three actions present, equal counts)."""
    P = np.array(panel)
    key = np.zeros(len(P), dtype=np.int64)
    for r in roles:
        key = key * VALUES + P[:, r]
    counts = np.zeros((VALUES ** len(roles), M), dtype=np.int64)
    np.add.at(counts, (key, P.sum(axis=1) % M), 1)
    seen = counts.sum(axis=1) > 0
    return bool(((counts[seen] == counts[seen][:, :1]) & (counts[seen] > 0)).all())


def chance_report(panel) -> dict:
    return {"single": all(chance(panel, (r,)) for r in range(3)),
            "pair": all(chance(panel, rs) for rs in itertools.combinations(range(3), 2))}


def every_pair_present(panel) -> bool:
    return all(len({(t[i], t[j]) for t in panel}) == VALUES ** 2
               for i, j in itertools.combinations(range(3), 2))


# ============ 1: the declared class, exhaustively ============

def identifiable(taught, held) -> dict:
    """All 3^9 shared residue assignments x all 27 maps Z3 -> {0,1,2}."""
    codes = np.array(list(itertools.product(range(M), repeat=VALUES)), dtype=np.int8)
    maps = np.array(list(itertools.product(range(M), repeat=M)), dtype=np.int8)
    T, H = np.array(taught), np.array(held)
    target = T.sum(axis=1) % M
    sums = (codes[:, T[:, 0]] + codes[:, T[:, 1]] + codes[:, T[:, 2]]) % M
    fits = np.stack([(g[sums] == target).all(axis=1) for g in maps], axis=1)
    code_index, map_index = np.nonzero(fits)
    hs = (codes[code_index][:, H[:, 0]] + codes[code_index][:, H[:, 1]]
          + codes[code_index][:, H[:, 2]]) % M
    predicted = maps[map_index][np.arange(len(map_index))[:, None], hs]
    truth = H.sum(axis=1) % M
    fixed = (predicted == predicted[:1]).all(axis=0)
    right = (predicted == truth).all(axis=1)
    return {"explanations_enumerated": int(len(codes) * len(maps)),
            "consistent_explanations": int(len(code_index)),
            "consistent_explanations_right_on_every_held": int(right.sum()),
            "held_triples_determined": int(fixed.sum()),
            "determined_answers_match_rule": bool((predicted[0][fixed] == truth[fixed]).all()),
            "worst_consistent_held_accuracy": float((predicted == truth).mean(axis=1).min())}


# ============ GF(3) linear algebra (cross-check of 1, and E1) ============

def _basis_mod3(rows: np.ndarray):
    """Row-reduce over GF(3); returns (basis rows with pivot 1, pivot columns)."""
    A = rows.copy() % M
    basis, pivots, r = [], [], 0
    for col in range(A.shape[1]):
        nz = np.nonzero(A[r:, col])[0] if r < len(A) else []
        if len(nz) == 0:
            continue
        i = r + nz[0]
        A[[r, i]] = A[[i, r]]
        A[r] = (A[r] * A[r, col]) % M  # 1 * 1 = 1, 2 * 2 = 4 = 1 (mod 3): scales the pivot to 1
        others = np.nonzero(A[:, col])[0]
        others = others[others != r]
        A[others] = (A[others] - A[others, col][:, None] * A[r]) % M
        basis.append(A[r].copy())
        pivots.append(col)
        r += 1
        if r == len(A):
            break
    return np.array(basis), pivots


def _in_span(rows: np.ndarray, basis: np.ndarray, pivots) -> np.ndarray:
    R = rows.copy() % M
    for b, p in zip(basis, pivots):
        R = (R - R[:, p][:, None] * b) % M
    return ~R.any(axis=1)


def shared_rank(taught, held) -> dict:
    """The declared class as a linear system: any bijection Z3 -> Z3 is s -> e*s + k, so a fitting
    explanation is (e, d, k) with d(t0) + d(t1) + d(t2) + k = 0 on every taught triple, where
    d(v) = e*c(v) - v. Non-bijective maps cannot fit (taught shows all three actions)."""
    def rows(panel):
        out = np.zeros((len(panel), VALUES + 1), dtype=np.int64)
        for i, t in enumerate(panel):
            for v in t:
                out[i, v] += 1
            out[i, VALUES] = 1
        return out
    basis, pivots = _basis_mod3(rows(taught))
    return {"rank": len(pivots), "consistent_explanations": 2 * M ** (VALUES + 1 - len(pivots)),
            "held_triples_determined": int(_in_span(rows(held), basis, pivots).sum())}


def role_specific(taught, held) -> dict:
    """E1: each (role, value) its own residue; d0(t0) + d1(t1) + d2(t2) = 0 on taught (the map's
    sign and offset absorbed). Full rank is 25 (two constant shifts that cancel)."""
    def rows(panel):
        out = np.zeros((len(panel), 3 * VALUES), dtype=np.int64)
        for i, t in enumerate(panel):
            for j, v in enumerate(t):
                out[i, j * VALUES + v] = 1
        return out
    basis, pivots = _basis_mod3(rows(taught))
    return {"rank": len(pivots), "full_rank": 3 * VALUES - 2,
            "held_triples_determined": int(_in_span(rows(held), basis, pivots).sum())}


def affine_z9(taught, held) -> dict:
    """E2: shared residue alpha * v + beta in Z9 (81 codes), any map Z9 -> {0,1,2} of the sum mod 9.
    A map is fixed on the sums taught shows and free elsewhere."""
    T, H = np.array(taught), np.array(held)
    tt, ht = T.sum(axis=1) % M, H.sum(axis=1) % M
    fit = right = 0
    for alpha, beta in itertools.product(range(VALUES), repeat=2):
        ts = (alpha * T.sum(axis=1) + 3 * beta) % VALUES
        hs = (alpha * H.sum(axis=1) + 3 * beta) % VALUES
        counts = np.zeros((VALUES, M), dtype=np.int64)
        np.add.at(counts, (ts, tt), 1)
        if ((counts > 0).sum(axis=1) > 1).any():  # one sum, two answers: no map fits
            continue
        free = int((counts.sum(axis=1) == 0).sum())
        fit += M ** free
        if (counts[hs, ht] > 0).all():  # every held sum was taught, with the rule's answer
            right += M ** free
    return {"consistent_explanations": fit, "consistent_explanations_right_on_every_held": right}


# ============ 4: memorizers ============

def nearest_neighbour(taught, held) -> float:
    """Expected held accuracy of a plurality vote over the taught triples at the least Hamming
    distance, ties split evenly."""
    T, H = np.array(taught), np.array(held)
    D = (H[:, None, :] != T[None, :, :]).sum(axis=2)
    nearest = D == D.min(axis=1, keepdims=True)
    tt = T.sum(axis=1) % M
    votes = np.stack([(nearest & (tt == a)[None, :]).sum(axis=1) for a in range(M)], axis=1)
    best = votes == votes.max(axis=1, keepdims=True)
    truth = H.sum(axis=1) % M
    return float((best[np.arange(len(H)), truth] / best.sum(axis=1)).mean())


# ============ report and search ============

def report(name: str, taught, held, exhaustive: bool = True) -> dict:
    out = {"split": name, "values": VALUES, "taught_triples": len(taught), "held_triples": len(held),
           "chance_taught": chance_report(taught), "chance_held": chance_report(held),
           "held_also_taught": len(set(held) & set(taught)),
           "lookup_memorizer_held_accuracy": 1 / M,  # no held triple was taught: a uniform guess
           "nearest_neighbour_memorizer_held_accuracy": nearest_neighbour(taught, held),
           "shared_gf3": shared_rank(taught, held),
           "E1_role_specific_gf3": role_specific(taught, held),
           "E2_shared_affine_z9": affine_z9(taught, held)}
    if exhaustive:
        out["shared_exhaustive"] = identifiable(taught, held)
        ex, gf = out["shared_exhaustive"], out["shared_gf3"]
        assert ex["consistent_explanations"] == gf["consistent_explanations"], (ex, gf)
        assert ex["held_triples_determined"] == gf["held_triples_determined"], (ex, gf)
    ident = out["shared_exhaustive"] if exhaustive else out["shared_gf3"]
    checks = {
        "1_held_determined": ident["held_triples_determined"] == len(held)
        and ident.get("determined_answers_match_rule", True),
        "2_single_fact_chance": out["chance_taught"]["single"] and out["chance_held"]["single"],
        "3_pair_chance": out["chance_taught"]["pair"] and out["chance_held"]["pair"],
        "4_memorizer_chance": out["held_also_taught"] == 0
        and abs(out["nearest_neighbour_memorizer_held_accuracy"] - 1 / M) < 1e-9,
        "5_size": len(held) >= 81 and len(taught) >= 81,
        "E1_role_specific_determined": out["E1_role_specific_gf3"]["held_triples_determined"] == len(held),
        "E2_affine_z9_determined": out["E2_shared_affine_z9"]["consistent_explanations"]
        == out["E2_shared_affine_z9"]["consistent_explanations_right_on_every_held"],
        "E3_every_pair_in_both_panels": every_pair_present(taught) and every_pair_present(held),
    }
    out["checks"] = checks
    out["passes_required"] = all(v for k, v in checks.items() if k[0].isdigit())
    out["passes_all"] = all(checks.values())
    return out


def search(verbose: bool = False):
    """Every (1, b, c) form and 3-subset S of Z9, fast checks (GF(3) for check 1)."""
    rows, chosen = [], None
    for b, c in itertools.product(range(VALUES), repeat=2):
        for S in itertools.combinations(range(VALUES), 3):
            taught, held = split((1, b, c), S)
            r = report(f"(r0+{b}r1+{c}r2)%9 in {S}", taught, held, exhaustive=False)
            rows.append(((1, b, c), S, r["checks"]))
            if chosen is None and r["passes_all"]:
                chosen = ((1, b, c), S)
    return rows, chosen


CHOSEN_FORM, CHOSEN_SUMS = (1, 1, 2), (0, 1, 2)  # the search's first full pass; __main__ re-derives it


def split_v05c():
    return split(CHOSEN_FORM, CHOSEN_SUMS)


if __name__ == "__main__":
    import sys

    taught, held = split_v05c()
    if "--chosen-only" not in sys.argv:
        rows, chosen = search()
        req = [r for r in rows if all(v for k, v in r[2].items() if k[0].isdigit())]
        full = [r for r in rows if all(r[2].values())]
        fail_counts = Counter(k for r in rows for k, v in r[2].items() if not v)
        print(json.dumps({"candidates": len(rows), "pass_required_1_to_5": len(req),
                          "pass_all_incl_E1_E3": len(full),
                          "candidates_failing_each_check": dict(sorted(fail_counts.items())),
                          "first_passing_all": chosen}))
        assert chosen == (CHOSEN_FORM, CHOSEN_SUMS), chosen
        # contrasts: the symmetric form, a cross-role-transfer split, a non-unit coefficient
        for form, S in (((1, 1, 1), (0, 1, 2)), ((1, 0, 0), (0, 1, 2)), ((1, 1, 3), (0, 1, 2))):
            r = report(f"(r0+{form[1]}r1+{form[2]}r2)%9 in {S}", *split(form, S), exhaustive=False)
            print("contrast", r["split"], "fails:", [k for k, v in r["checks"].items() if not v])
    print(json.dumps(report(f"V0.5C: held iff (r0+{CHOSEN_FORM[1]}r1+{CHOSEN_FORM[2]}r2)%9 in {CHOSEN_SUMS}",
                            taught, held), indent=1))
