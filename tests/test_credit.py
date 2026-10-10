"""Credit rules (teachers/credit.py): the Shapley axioms on random games, the experiments' two-player formulas
(EXP-19, EXP-20b) bit for bit, and payout ratios. Fast; no Cadence."""
import itertools
import math

import numpy as np
import pytest

from teachers.credit import MAX_PLAYERS, equal_split, leave_one_out, payout_ratio, shapley

TOL = 1e-12


def close(a, b):
    return math.isclose(a, b, rel_tol=0.0, abs_tol=TOL)


def random_game(players, rng, empty=0.0):
    """A random coalition value table: v(S) ~ N(0, 1) for every non-empty S, v(empty) = `empty`."""
    v = {frozenset(): float(empty)}
    for k in range(1, len(players) + 1):
        for s in itertools.combinations(players, k):
            v[frozenset(s)] = float(rng.normal())
    return v


GAMES = [(n, seed) for n in range(1, 8) for seed in range(3)]


# ---------------- Shapley axioms on random games ----------------
@pytest.mark.parametrize("n,seed", GAMES)
def test_efficiency(n, seed):
    """Credits sum to v(all) - v(empty), also when v(empty) is not 0."""
    rng = np.random.default_rng(seed)
    players = [f"p{i}" for i in range(n)]
    for empty in (0.0, float(rng.normal())):
        v = random_game(players, rng, empty)
        phi = shapley(players, v)
        assert close(sum(phi.values()), v[frozenset(players)] - v[frozenset()])


@pytest.mark.parametrize("n,seed", [(n, s) for n in range(2, 8) for s in range(3)])
def test_symmetry(n, seed):
    """Two interchangeable players (v depends only on how many of them S holds) get identical credit."""
    rng = np.random.default_rng(100 + seed)
    players = [f"p{i}" for i in range(n)]
    a, b = players[0], players[-1]
    rest = random_game(players[1:-1], rng)                      # v by (the other members, count of a and b)
    table = {(s, k): float(rng.normal()) for s in rest for k in (0, 1, 2)}
    table[(frozenset(), 0)] = 0.0

    def v(s):
        return table[(s - {a, b}, len(s & {a, b}))]

    phi = shapley(players, v)
    assert phi[a] == phi[b]


@pytest.mark.parametrize("n,seed", GAMES)
def test_null_player(n, seed):
    """A player who never changes v gets exactly 0, and adding it leaves everyone else's credit unchanged."""
    rng = np.random.default_rng(200 + seed)
    players = [f"p{i}" for i in range(n)]
    base = random_game(players, rng)

    def v(s):
        return base[s - {"null"}]

    phi = shapley(players + ["null"], v)
    assert phi["null"] == 0.0
    without = shapley(players, base)
    assert all(close(phi[p], without[p]) for p in players)


@pytest.mark.parametrize("n,seed", GAMES)
def test_additivity(n, seed):
    """phi(v + w) = phi(v) + phi(w)."""
    rng = np.random.default_rng(300 + seed)
    players = [f"p{i}" for i in range(n)]
    v, w = random_game(players, rng), random_game(players, rng)
    vw = {s: v[s] + w[s] for s in v}
    pv, pw, pvw = shapley(players, v), shapley(players, w), shapley(players, vw)
    assert all(close(pvw[p], pv[p] + pw[p]) for p in players)


@pytest.mark.parametrize("n,seed", GAMES)
def test_listing_order_does_not_change_credit(n, seed):
    rng = np.random.default_rng(400 + seed)
    players = [f"p{i}" for i in range(n)]
    v = random_game(players, rng)
    fwd, rev = shapley(players, v), shapley(players[::-1], v)
    assert all(fwd[p] == rev[p] for p in players)
    assert list(fwd) == players and list(rev) == players[::-1]


def test_shapley_calls_v_once_per_coalition_in_bitmask_order():
    players = ["a", "b", "c"]
    calls = []

    def v(s):
        calls.append(s)
        return float(len(s))

    shapley(players, v)
    expected = [frozenset(p for j, p in enumerate(players) if m >> j & 1) for m in range(8)]
    assert calls == expected                                    # empty first, grand coalition last


def test_shapley_size_limit_and_inputs():
    v = lambda s: float(len(s))                                 # noqa: E731
    phi = shapley(range(MAX_PLAYERS), v)                        # 4096 coalitions is fine
    assert all(close(x, 1.0) for x in phi.values())
    with pytest.raises(ValueError):
        shapley(range(MAX_PLAYERS + 1), v)
    with pytest.raises(ValueError):
        shapley(["a", "a"], v)
    assert shapley([], v) == {}
    with pytest.raises(KeyError):                               # a dict that misses a coalition fails loud
        shapley(["a", "b"], {frozenset(): 0.0, frozenset("a"): 1.0})


# ---------------- the experiments' formulas ----------------
# EXP-19 run 3 pooled (experiments/EXP-19.md): v(A) -0.06, v(B) -0.08, v(AB) +0.58, v relative to the null twin.
VA, VB, VAB = -0.06, -0.08, 0.58
EXP19 = {frozenset(): 0.0, frozenset("A"): VA, frozenset("B"): VB, frozenset("AB"): VAB}


def test_exp19_shapley_formula():
    phi = shapley(["A", "B"], EXP19)
    # exp/EXP-19_keydoor_teamwork.py: shap key .5*m[a]+.5*(m[ab]-m[b]), door .5*m[b]+.5*(m[ab]-m[a])
    assert phi["A"] == .5 * VA + .5 * (VAB - VB)
    assert phi["B"] == .5 * VB + .5 * (VAB - VA)
    assert close(phi["A"], 0.30) and close(phi["B"], 0.28)
    assert close(phi["A"] + phi["B"], VAB)


def test_exp19_leave_one_out_formula():
    phi = leave_one_out(["A", "B"], EXP19)
    assert phi["A"] == VAB - VB and phi["B"] == VAB - VA      # EXP-19: LOO key m[ab]-m[b], door m[ab]-m[a]
    assert close(sum(phi.values()), 2 * VAB - VA - VB)        # EXP-19: sum 2*m[ab]-m[a]-m[b] = 1.30
    assert close(sum(phi.values()), 1.30)


def test_exp19_equal_split_and_payout():
    eq = equal_split(["A", "B"], EXP19)
    assert eq == {"A": VAB / 2, "B": VAB / 2}
    assert close(payout_ratio(shapley(["A", "B"], EXP19), VAB), 1.0)
    assert close(payout_ratio(eq, VAB), 1.0)
    assert close(payout_ratio(leave_one_out(["A", "B"], EXP19), VAB), (2 * VAB - VA - VB) / VAB)  # 2.24x


def exp20b_credits(v1, v2, v12, rule):
    """exp/EXP-20b_teachers_on_table.py credits(), after its base subtraction (verbatim)."""
    if rule == "shapley":
        return .5 * v1 + .5 * (v12 - v2), .5 * v2 + .5 * (v12 - v1), v12
    if rule == "loo":
        return v12 - v2, v12 - v1, v12
    return v12 / 2, v12 / 2, v12


@pytest.mark.parametrize("rule,fn", [("shapley", shapley), ("loo", leave_one_out), ("equal", equal_split)])
def test_exp20b_credits_bit_identical(rule, fn):
    """On random EXP-21-like rows (raw scores with a null-twin base), the library pays EXP-20b's floats exactly."""
    rng = np.random.default_rng(2020)
    for _ in range(500):
        base, r1, r2, r12 = rng.random(4)
        v1, v2, v12 = r1 - base, r2 - base, r12 - base
        game = {frozenset(): base - base, frozenset({1}): v1, frozenset({2}): v2, frozenset({1, 2}): v12}
        phi = fn([1, 2], game)
        p1, p2, _ = exp20b_credits(v1, v2, v12, rule)
        assert (phi[1], phi[2]) == (p1, p2)


# ---------------- what the rules reward ----------------
def test_loo_overpays_complements():
    """Pure complements (each lesson worthless alone, the pair worth 1): LOO pays 2x, Shapley and equal 1x."""
    v = {frozenset(): 0.0, frozenset("A"): 0.0, frozenset("B"): 0.0, frozenset("AB"): 1.0}
    assert payout_ratio(leave_one_out("AB", v), 1.0) == 2.0
    assert payout_ratio(shapley("AB", v), 1.0) == 1.0
    assert payout_ratio(equal_split("AB", v), 1.0) == 1.0


def test_equal_split_pays_a_free_rider():
    """A teaches the whole task alone, B adds nothing (EXP-20b's suggested free-rider table): Shapley and LOO pay B
    nothing, equal split pays B half."""
    v = {frozenset(): 0.0, frozenset("A"): 1.0, frozenset("B"): 0.0, frozenset("AB"): 1.0}
    assert shapley("AB", v) == {"A": 1.0, "B": 0.0}
    assert leave_one_out("AB", v) == {"A": 1.0, "B": 0.0}
    assert equal_split("AB", v) == {"A": 0.5, "B": 0.5}


def test_payout_ratio_inputs():
    assert payout_ratio({"a": 0.6, "b": 0.6}, 0.6) == 2.0
    assert close(payout_ratio([0.1] * 10, 0.5), 2.0)            # e.g. every payment over a run vs value made
    with pytest.raises(ZeroDivisionError):
        payout_ratio({"a": 1.0}, 0.0)
