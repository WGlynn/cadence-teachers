"""Credit rules: how to split what a group of teachers created among them.

`v` is a coalition value: v(S) = what the lessons of the players in S are worth together, for every subset S of
the players (worth.coalition_values measures one on real brains, relative to the empty coalition). The rules are
the ones the experiments compared (EXP-18, EXP-19, EXP-20b):

  shapley        phi_i = sum over S without i of |S|! (n-|S|-1)! / n! * (v(S + i) - v(S))
                 budget-balanced: the credits sum to v(all) - v(empty)
  leave_one_out  phi_i = v(all) - v(all - i)
                 over-pays complements: on EXP-19's numbers it pays 1.30 for v(AB) = 0.58 (2.24x); EXP-20b's
                 teachers were paid 1.83x the value they created
  equal_split    phi_i = (v(all) - v(empty)) / n
                 budget-balanced, but pays the group result whatever a player's own lesson did

For two players and v(empty) = 0 these are exactly the experiments' formulas, e.g. Shapley
phi_A = 1/2 v(A) + 1/2 (v(AB) - v(B)), and they return bit-identical floats (tests/test_credit.py).

`v` may be a callable on frozensets or a dict keyed by frozensets (what worth.coalition_values returns). v(empty)
is the zero point of every rule; every rule asks for v(empty), so v must accept the empty frozenset.
"""
from __future__ import annotations

import math
from collections.abc import Callable, Hashable, Iterable, Mapping

MAX_PLAYERS = 12  # exact Shapley enumerates all 2^n coalitions: 12 players = 4096 values of v


def _value(v) -> Callable[[frozenset], float]:
    """A dict of coalition values (worth.coalition_values) or a callable, as a callable."""
    return v.__getitem__ if isinstance(v, Mapping) else v


def _distinct(players: Iterable[Hashable]) -> list:
    players = list(players)
    if len(set(players)) != len(players):
        raise ValueError(f"players must be distinct, got {players!r}")
    return players


def shapley(players: Iterable[Hashable], v) -> dict:
    """Exact Shapley credit by subset enumeration (n <= MAX_PLAYERS; raises beyond).

    v is called exactly once per coalition, in increasing bitmask order of `players` (bit j = players[j]; the
    empty set first, the grand coalition last), so a v that measures brains runs in a fixed order. Each credit is a
    math.fsum of its weighted marginal contributions, so a player's credit does not depend on how the players are
    listed and symmetric players get identical credits."""
    players = _distinct(players)
    n = len(players)
    if n > MAX_PLAYERS:
        raise ValueError(f"exact Shapley enumerates 2^n coalitions; n={n} > MAX_PLAYERS={MAX_PLAYERS}")
    if n == 0:
        return {}
    v = _value(v)
    val = [float(v(frozenset(p for j, p in enumerate(players) if m >> j & 1))) for m in range(1 << n)]
    w = [math.factorial(k) * math.factorial(n - k - 1) / math.factorial(n) for k in range(n)]
    out = {}
    for i, p in enumerate(players):
        bit = 1 << i
        out[p] = math.fsum(w[m.bit_count()] * (val[m | bit] - val[m]) for m in range(1 << n) if not m & bit)
    return out


def leave_one_out(players: Iterable[Hashable], v) -> dict:
    """phi_i = v(all) - v(all - i): what the group loses without player i (twin ablation of one lesson).
    Calls v(all) first, then v(all - i) in player order."""
    players = _distinct(players)
    if not players:
        return {}
    v = _value(v)
    grand = frozenset(players)
    vg = float(v(grand))
    return {p: vg - float(v(grand - {p})) for p in players}


def equal_split(players: Iterable[Hashable], v) -> dict:
    """phi_i = (v(all) - v(empty)) / n for every player. Calls v(all), then v(empty)."""
    players = _distinct(players)
    if not players:
        return {}
    v = _value(v)
    share = (float(v(frozenset(players))) - float(v(frozenset()))) / len(players)
    return {p: share for p in players}


def payout_ratio(credits, v_grand: float) -> float:
    """Total credit paid over the value created: sum(credits) / v_grand, with v_grand = v(all) - v(empty).

    1.0 = budget-balanced (shapley, equal_split); above 1 the rule mints more than the lessons created
    (leave_one_out on complements; EXP-20b: 1.83). `credits` is a dict from a rule above, or any iterable of
    amounts (e.g. every payment over a run, against the summed value, as EXP-20b reports it)."""
    total = math.fsum(credits.values() if isinstance(credits, Mapping) else credits)
    if v_grand == 0:
        raise ZeroDivisionError("payout ratio is undefined when v_grand == 0 (the coalition created nothing)")
    return total / v_grand
