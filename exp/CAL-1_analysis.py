"""
CAL-1 analysis: every number the pre-registration names, computed on the saved rows (no compute on brains).
PRE-REGISTRATION: experiments/CAL-1.md (committed b70748c, 2026-11-13). Written before any full-run data existed.

    python -u CAL-1_analysis.py > CAL-1-full-analysis.out      # reads CAL-1-full.jsonl + CAL-1-full-probes.json

Primary (verdict) uses the composite zero Z = per-student mean of {null, untaught, random}. Amendment (a), exploratory:
the whole primary analysis is repeated with each single zero (null, untaught, random) and reported beside Z; the verdict
still uses Z. Seeds: permutations default_rng(1), bootstraps default_rng(0).
"""
import importlib.util, json, os, sys

import numpy as np
from scipy.stats import rankdata
from sklearn.isotonic import IsotonicRegression

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("cal1h", os.path.join(HERE, "CAL-1_calibration_vs.py"))
H = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(H)
KNOW, FAKES, ZERO, RIGHTS = H.KNOW, H.FAKES, H.ZERO, H.RIGHTS
CLASSES = ["graded"] + KNOW + FAKES
LAMS = 10 ** np.arange(-3, 3.0001, 0.5)                 # 13 penalties, half-decade steps
N_PERM, N_BOOT, MARGIN6, B_BAR = 1000, 2000, 1 / 16, 1 / 32
PREFIX = os.environ.get("PREFIX", "CAL-1-full")


# ============ Small tools ============

def spearman(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    ra, rb = rankdata(a), rankdata(b)
    if ra.std() == 0 or rb.std() == 0:
        return 0.0
    return float(np.corrcoef(ra, rb)[0, 1])


def sign_of(score_tr, w_tr):
    r = spearman(score_tr, w_tr)
    return 1.0 if r >= 0 else -1.0


def iso(x, y):
    return IsotonicRegression(increasing=True, out_of_bounds="clip").fit(np.asarray(x, float), np.asarray(y, float))


def ci(x):
    return [float(np.percentile(x, 2.5)), float(np.percentile(x, 97.5))]


def ridge_fit(X, y, lam):
    xm, ym = X.mean(0), y.mean()
    Xc = X - xm
    beta = np.linalg.solve(Xc.T @ Xc + lam * np.eye(X.shape[1]), Xc.T @ (y - ym))
    return xm, ym, beta


def ridge_pred(model, X):
    xm, ym, beta = model
    return (X - xm) @ beta + ym


def standardizer(X):
    mu, sd = X.mean(0), X.std(0)
    sd = np.where(sd > 0, sd, 1.0)
    return lambda Z: (Z - mu) / sd, mu, sd


def L_procedure(Xtr, ytr, groups, Xte_list):
    """Penalty by leave-one-group-out CV (a fold never splits a student), out-of-fold training scores, final fit on all.
    Returns OOF scores, the final model, and its scores on each matrix in Xte_list."""
    ug = np.unique(groups)
    oofs, mses = [], []
    for lam in LAMS:
        oof = np.zeros(len(ytr))
        for g in ug:
            tr, te = groups != g, groups == g
            oof[te] = ridge_pred(ridge_fit(Xtr[tr], ytr[tr], lam), Xtr[te])
        oofs.append(oof)
        mses.append(float(np.mean((oof - ytr) ** 2)))
    k = int(np.argmin(mses))
    final = ridge_fit(Xtr, ytr, LAMS[k])
    return dict(lam=float(LAMS[k]), cv_mse=mses, oof=oofs[k], model=final, te=[ridge_pred(final, X) for X in Xte_list])


def mapped(score_tr, y_tr, score_te_list):
    """Orientation by the sign of the training Spearman, then the isotonic map fitted on training, applied to held-out."""
    s = sign_of(score_tr, y_tr)
    m = iso(s * np.asarray(score_tr), y_tr)
    return s, [m.predict(s * np.asarray(x)) for x in score_te_list]


# ============ Data ============

def load():
    rows = [json.loads(l) for l in open(os.path.join(HERE, f"{PREFIX}.jsonl"))]
    probes = json.load(open(os.path.join(HERE, f"{PREFIX}-probes.json")))
    P = {(p["block"], p["t"]): p for p in probes}
    acc, mism = {}, 0
    for r in rows:
        acc[H.key(r)] = r["acc"]
        if r["arm"] == "teacher" and [list(x) for x in P[(r["tblock"], r["t"])]["probe"]] != [list(x) for x in r["probe"]]:
            mism += 1
    n_held = len({r["s"] for r in rows if r["sblock"] == "held"})
    assert n_held in (48, 64), n_held
    m = n_held // 8
    blocks = {}
    for b in ("train", "held", "probe-only"):
        ps = [P[(b, t)] for t in range(192 if b != "probe-only" else 80)]
        blocks[b] = dict(kinds=np.array([p["kind"] for p in ps]),
                         groups=np.array([p["group"] if p["group"] is not None else -1 for p in ps]),
                         probes=[[tuple(x) for x in p["probe"]] for p in ps],
                         identity=[p["identity"] for p in ps])
    return rows, acc, blocks, m, mism


def worth_tables(acc, m, zero):
    """Per-teacher, per-student worth (taught acc minus the zero on the same student)."""
    def z(sb, s):
        arms = ZERO if zero == "Z" else [zero]
        return float(np.mean([acc[(sb, s, a)] for a in arms]))
    wtr = np.array([[acc[("train", 3 * (t // 24) + k, t)] - z("train", 3 * (t // 24) + k) for k in range(3)]
                    for t in range(192)])
    whe = np.array([[acc[("held", m * (t // 24) + k, t)] - z("held", m * (t // 24) + k) for k in range(m)]
                    for t in range(192)])
    aud = np.array([acc[("audition", t // 24, t)] - z("audition", t // 24) for t in range(192)])
    return wtr, whe, aud


def feats(probes, R=12):
    """features() on the first R labels of each probe context (R = 12 is the full probe)."""
    out = []
    for pr in probes:
        cnt, sub = {}, []
        for i, a, t in pr:
            c = cnt.get((i, a), 0)
            if c < R:
                sub.append((i, a, t))
            cnt[(i, a)] = c + 1
        out.append(H.features(sub))
    return np.array(out)


# ============ One full primary analysis under a given zero ============

def analyse(acc, blocks, m, zero, extras=False):
    tr, he = blocks["train"], blocks["held"]
    wtr_s, whe_s, aud = worth_tables(acc, m, zero)
    Wtr, Whe = wtr_s.mean(1), whe_s.mean(1)
    clim = float(Wtr.mean())
    gtr, ghe, cls = tr["groups"], he["groups"], he["kinds"]

    # ---- scores
    Ftr, Fhe, Fpo = feats(tr["probes"]), feats(he["probes"]), feats(blocks["probe-only"]["probes"])
    std, mu, sd = standardizer(Ftr)
    L = L_procedure(std(Ftr), Wtr, gtr, [std(Fhe), std(Fpo)])
    sc_tr = dict(L=L["oof"], S1=np.array([H.s1(p) for p in tr["probes"]]), S2=np.array(H.s2_all(tr["probes"])),
                 K=np.array([H.k_key(p) for p in tr["probes"]]))
    sc_he = dict(L=L["te"][0], S1=np.array([H.s1(p) for p in he["probes"]]), S2=np.array(H.s2_all(he["probes"])),
                 K=np.array([H.k_key(p) for p in he["probes"]]))
    sgn, fc = {}, {}
    for k in sc_tr:
        sgn[k], (fc[k],) = mapped(sc_tr[k], Wtr, [sc_he[k]])
    osc = {k: sgn[k] * sc_he[k] for k in sc_he}            # oriented held-out scores
    osc["A"], fc["A"], sgn["A"] = aud, aud, 1.0            # audition: raw W on one student, no map
    preds = ["L", "S1", "S2", "K", "A"]

    def stats(idx, W):
        out = {}
        for k in preds:
            out[k] = (spearman(osc[k][idx], W[idx]), float(np.mean((fc[k][idx] - W[idx]) ** 2)))
        out["clim"] = float(np.mean((clim - W[idx]) ** 2))
        return out

    allidx = np.arange(192)
    base = stats(allidx, Whe)
    res = dict(zero=zero, m=m, clim=clim, lam=L["lam"], signs=sgn,
               rho={k: base[k][0] for k in preds}, mse={k: base[k][1] for k in preds}, mse_clim=base["clim"])
    res["skill"] = {k: 1 - res["mse"][k] / base["clim"] for k in preds}

    # ---- paired bootstrap over held-out teachers, stratified by group, maps and models fixed
    rng = np.random.default_rng(0)
    gidx = [np.where(ghe == g)[0] for g in range(8)]
    bs = {f"drho_{k}": [] for k in ("S1", "S2", "K", "A")}
    bs.update({f"dmse_{k}": [] for k in ("S1", "S2", "K", "A")})
    bs["skill_L"] = []
    for _ in range(N_BOOT):
        idx = np.concatenate([rng.choice(ix, size=len(ix), replace=True) for ix in gidx])
        st = stats(idx, Whe)
        for k in ("S1", "S2", "K", "A"):
            bs[f"drho_{k}"].append(st["L"][0] - st[k][0])
            bs[f"dmse_{k}"].append(st["L"][1] - st[k][1])
        bs["skill_L"].append(1 - st["L"][1] / st["clim"])
    res["boot"] = {k: dict(point=None, ci=ci(v)) for k, v in bs.items()}
    for k in ("S1", "S2", "K", "A"):
        res["boot"][f"drho_{k}"]["point"] = res["rho"]["L"] - res["rho"][k]
        res["boot"][f"dmse_{k}"]["point"] = res["mse"]["L"] - res["mse"][k]
    res["boot"]["skill_L"]["point"] = res["skill"]["L"]

    # ---- N0: L's whole procedure refitted on permuted training W, 1,000 times
    rng1 = np.random.default_rng(1)
    n0_rho, n0_mse = [], []
    Xtr, Xhe = std(Ftr), std(Fhe)
    for _ in range(N_PERM):
        yp = Wtr[rng1.permutation(192)]
        Lp = L_procedure(Xtr, yp, gtr, [Xhe])
        s, (f,) = mapped(Lp["oof"], yp, [Lp["te"][0]])
        n0_rho.append(spearman(s * Lp["te"][0], Whe))
        n0_mse.append(float(np.mean((f - Whe) ** 2)))
    res["N0"] = dict(rho_p99=float(np.percentile(n0_rho, 99)), mse_p1=float(np.percentile(n0_mse, 1)),
                     rho_mean=float(np.mean(n0_rho)), mse_mean=float(np.mean(n0_mse)),
                     rho_max=float(np.max(n0_rho)), mse_min=float(np.min(n0_mse)))

    # ---- per class: mean W, mean forecast per predictor, overpricing of L
    res["classes"] = {}
    for c in CLASSES:
        ix = cls == c
        d = fc["L"][ix] - Whe[ix]
        res["classes"][c] = dict(n=int(ix.sum()), W=float(Whe[ix].mean()), W_sem=float(Whe[ix].std(ddof=1) / np.sqrt(ix.sum())),
                                 fc={k: float(fc[k][ix].mean()) for k in preds},
                                 over_L=float(d.mean()), over_L_se=float(d.std(ddof=1) / np.sqrt(ix.sum())))
    # ---- noise ceiling: split-half reliability of held-out W (first half of each group's students vs second half)
    h = m // 2
    r_half = spearman(whe_s[:, :h].mean(1), whe_s[:, h:].mean(1))
    res["reliability"] = dict(split_half_r=r_half, spearman_brown=2 * r_half / (1 + r_half),
                              ceiling=float(np.sqrt(max(0.0, 2 * r_half / (1 + r_half)))), halves=f"0-{h - 1} vs {h}-{m - 1}")

    # ---- decision rules
    rel = res["reliability"]["spearman_brown"]
    k4 = res["classes"]["know-4"]["W"]
    void = dict(V3_reliability_below_5=rel < 0.5, V4_know4_W_below_10=k4 < 0.10)
    crit = {
        "1_rho_L_ge_.5": res["rho"]["L"] >= 0.5,
        "2_rank_beats_S1": res["boot"]["drho_S1"]["ci"][0] > 0,
        "2_rank_beats_S2": res["boot"]["drho_S2"]["ci"][0] > 0,
        "3_mse_beats_S1": res["boot"]["dmse_S1"]["ci"][1] < 0,
        "3_mse_beats_S2": res["boot"]["dmse_S2"]["ci"][1] < 0,
        "4_beats_N0": res["rho"]["L"] > res["N0"]["rho_p99"] and res["mse"]["L"] < res["N0"]["mse_p1"],
        "5_skill_above_0": res["boot"]["skill_L"]["ci"][0] > 0,
    }
    for c in FAKES:
        v = res["classes"][c]
        crit[f"6_not_overpriced_{c}"] = v["over_L"] + 1.645 * v["over_L_se"] < MARGIN6
    k2fc = res["classes"]["know-2"]["fc"]["L"]
    kill = dict(K1_fake_ge_know2=any(res["classes"][c]["fc"]["L"] >= k2fc for c in FAKES),
                K2_reversed=any(res["boot"][f"drho_{s}"]["ci"][1] < 0 and res["boot"][f"dmse_{s}"]["ci"][0] > 0
                                for s in ("S1", "S2")))
    verdict = ("VOID (" + ", ".join(k for k, v in void.items() if v) + ")" if any(void.values()) else
               "KILL (" + ", ".join(k for k, v in kill.items() if v) + ")" if any(kill.values()) else
               "CONFIRM" if all(crit.values()) else
               "BOUNDARY (failing: " + ", ".join(k for k, v in crit.items() if not v) + ")")
    res.update(void=void, criteria=crit, kill=kill, verdict=verdict)

    if not extras:
        return res

    # ============ Reported, not decisive (composite Z only) ============
    ex = {}
    sub = lambda c: np.isin(cls, c)
    ex["rho_within"] = {name: {k: spearman(osc[k][sub(c)], Whe[sub(c)]) for k in preds}
                        for name, c in (("graded", ["graded"]), ("know-k", KNOW))}
    ex["L_orders_know"] = bool(all(res["classes"][KNOW[i]]["fc"]["L"] < res["classes"][KNOW[i + 1]]["fc"]["L"] for i in range(3)))
    # hindsight MSE and the out-of-sample to hindsight ratio
    ex["hindsight"] = {}
    for k in ("L", "S1", "S2", "K"):
        hm = float(np.mean((iso(osc[k], Whe).predict(osc[k]) - Whe) ** 2))
        ex["hindsight"][k] = dict(mse=hm, ratio=res["mse"][k] / hm if hm > 0 else float("inf"))
    # Brier for B = [W >= 1/32] under the same isotonic procedure
    Btr, Bhe = (Wtr >= B_BAR).astype(float), (Whe >= B_BAR).astype(float)
    ex["brier"] = dict(base_rate_train=float(Btr.mean()), base_rate_held=float(Bhe.mean()),
                       clim=float(np.mean((Btr.mean() - Bhe) ** 2)))
    for k in ("L", "S1", "S2", "K"):
        s, (f,) = mapped(sc_tr[k], Btr, [sc_he[k]])
        ex["brier"][k] = float(np.mean((f - Bhe) ** 2))
    ex["brier"]["A"] = float(np.mean(((aud >= B_BAR).astype(float) - Bhe) ** 2))
    # L's weights in raw feature units (per stage x labelled action, then the echo share)
    beta = L["model"][2] / sd
    ex["L_weights"] = dict(stage_by_action=np.round(beta[:20].reshape(4, 5), 4).tolist(), echo_share=float(beta[20]),
                           right_action_at_stage=[float(beta[5 * i + i]) for i in range(4)],
                           standardized=np.round(L["model"][2], 4).tolist(), lam=L["lam"])
    # S2 coordinated: 64 probe-only wrong-chain clones added to the held-out reference pool; training map unchanged
    po = blocks["probe-only"]
    clones = [po["probes"][t] for t in range(16, 80)]
    s2c = np.array(H.s2_all(he["probes"], extra=clones))
    s, tr_map = sgn["S2"], iso(sgn["S2"] * sc_tr["S2"], Wtr)
    f2c = tr_map.predict(s * s2c)
    ex["S2_coordinated"] = dict(rho=spearman(s * s2c, Whe), mse=float(np.mean((f2c - Whe) ** 2)),
                                class_mean_S2={c: float(s2c[cls == c].mean()) for c in CLASSES},
                                class_mean_S2_honest={c: float(sc_he["S2"][cls == c].mean()) for c in CLASSES},
                                top_class=max(CLASSES, key=lambda c: s2c[cls == c].mean()))
    # probe-gamer: probe-only know-4 probes priced by L, paired with the held-out random instances' measured W
    s, (fpg,) = mapped(L["oof"], Wtr, [L["te"][1][:16]])
    w_rand = Whe[cls == "random"]
    d = fpg - w_rand
    ex["probe_gamer"] = dict(forecast=float(fpg.mean()), W=float(w_rand.mean()), over=float(d.mean()),
                             over_se=float(d.std(ddof=1) / 4), know4_W=res["classes"]["know-4"]["W"])
    # L-archive: L's procedure fitted on EXP-77b's logged lessons, applied to the held-out probes
    ex["L_archive"] = l_archive(std_he=Fhe, Whe=Whe, cls=cls, clim=clim)
    # L refitted on 1, 3 or 6 probe labels per context
    ex["L_R"] = {}
    for R in (1, 3, 6):
        a_tr, a_he = feats(tr["probes"], R), feats(he["probes"], R)
        sR = standardizer(a_tr)[0]
        LR = L_procedure(sR(a_tr), Wtr, gtr, [sR(a_he)])
        s, (f,) = mapped(LR["oof"], Wtr, [LR["te"][0]])
        ex["L_R"][R] = dict(rho=spearman(s * LR["te"][0], Whe), mse=float(np.mean((f - Whe) ** 2)), lam=LR["lam"])
    # student-level bootstrap of W (resample held-out students within group; forecasts fixed)
    rng = np.random.default_rng(0)
    sb = {f"{a}_{k}": [] for a in ("rho", "mse") for k in preds}
    sb.update({"drho_S2": [], "dmse_S2": [], "drho_S1": [], "dmse_S1": []})
    for _ in range(N_BOOT):
        pick = rng.integers(0, m, size=(8, m))
        Wb = np.array([whe_s[t, pick[t // 24]].mean() for t in range(192)])
        for k in preds:
            sb[f"rho_{k}"].append(spearman(osc[k], Wb))
            sb[f"mse_{k}"].append(float(np.mean((fc[k] - Wb) ** 2)))
        for k in ("S1", "S2"):
            sb[f"drho_{k}"].append(sb["rho_L"][-1] - sb[f"rho_{k}"][-1])
            sb[f"dmse_{k}"].append(sb["mse_L"][-1] - sb[f"mse_{k}"][-1])
    ex["student_bootstrap"] = {k: ci(v) for k, v in sb.items()}
    ex["probe_mismatch_note"] = "probes in rows equal the pre-teaching probe file (checked in load)"
    res["extras"] = ex
    res["forecasts"] = {k: np.round(fc[k], 5).tolist() for k in preds}
    res["W_held"] = np.round(Whe, 5).tolist()
    res["W_train"] = np.round(Wtr, 5).tolist()
    return res


def l_archive(std_he, Whe, cls, clim):
    """Training rows: EXP-77b's 216 students x 8 teacher arms, features from each lesson's label stream (a stage with no
    labels in a lesson gets the uniform 0.2 shares; disclosed), W = arm minus the composite zero on that student.
    Folds: 8 blocks of 27 students, so a fold never splits a student. Applied to the CAL-1 held-out probe features."""
    rows = [json.loads(l) for l in open(os.path.join(HERE, "EXP-77b-full.jsonl"))]
    arms = KNOW + ["random", "wrong-chain", "echo", "anti-echo"]
    X, y, g = [], [], []
    for r in rows:
        if r["lesson"] != 80:
            continue
        z = np.mean([r["arms"][a]["acc"] for a in ZERO])
        for a in arms:
            f, same = np.zeros((4, 5)), 0
            st = r["arms"][a]["labels"]
            for right, act, t in st:
                f[right, t] += 1
                same += t == act
            tot = f.sum(1, keepdims=True)
            sh = np.where(tot > 0, f / np.where(tot > 0, tot, 1), 0.2)
            X.append(np.r_[sh.ravel(), same / len(st) if st else 0.2])
            y.append(r["arms"][a]["acc"] - z)
            g.append(r["student"] // 27)
    X, y, g = np.array(X), np.array(y), np.array(g)
    std = standardizer(X)[0]
    La = L_procedure(std(X), y, g, [std(std_he)])
    s, (f,) = mapped(La["oof"], y, [La["te"][0]])
    mse = float(np.mean((f - Whe) ** 2))
    return dict(n_train=len(y), lam=La["lam"], rho=spearman(s * La["te"][0], Whe), mse=mse,
                skill=1 - mse / float(np.mean((clim - Whe) ** 2)),
                class_fc={c: float(f[cls == c].mean()) for c in CLASSES})


# ============ Report ============

def report(r, full=True):
    p = lambda *a: print(*a, flush=True)
    p(f"\n=== zero = {r['zero']}  (m = {r['m']}; climatology = training mean W {r['clim']:+.4f}; L penalty {r['lam']:g}; "
      f"orientation signs {r['signs']}) ===")
    p(f"  {'pred':4s} {'rho':>7s} {'MSE':>8s} {'skill':>7s}")
    for k in ("L", "S1", "S2", "K", "A"):
        p(f"  {k:4s} {r['rho'][k]:7.3f} {r['mse'][k]:8.5f} {r['skill'][k]:+7.3f}")
    p(f"  climatology MSE {r['mse_clim']:.5f}")
    for k in ("S1", "S2", "K", "A"):
        a, b = r["boot"][f"drho_{k}"], r["boot"][f"dmse_{k}"]
        p(f"  L minus {k:2s}: rho {a['point']:+.3f} [{a['ci'][0]:+.3f}, {a['ci'][1]:+.3f}]   "
          f"MSE {b['point']:+.5f} [{b['ci'][0]:+.5f}, {b['ci'][1]:+.5f}]")
    s = r["boot"]["skill_L"]
    p(f"  skill_L {s['point']:+.3f} [{s['ci'][0]:+.3f}, {s['ci'][1]:+.3f}]")
    n0 = r["N0"]
    p(f"  N0 ({N_PERM} refits): rho 99th pct {n0['rho_p99']:.3f} (mean {n0['rho_mean']:+.3f}, max {n0['rho_max']:.3f}); "
      f"MSE 1st pct {n0['mse_p1']:.5f} (mean {n0['mse_mean']:.5f}, min {n0['mse_min']:.5f})")
    rel = r["reliability"]
    p(f"  reliability of held-out W: split-half r {rel['split_half_r']:.3f} ({rel['halves']}), Spearman-Brown "
      f"{rel['spearman_brown']:.3f}, ceiling {rel['ceiling']:.3f}")
    p(f"  {'class':11s} {'n':>3s} {'W':>7s} {'sem':>6s} | " + " ".join(f"{'fc_' + k:>7s}" for k in ("L", "S1", "S2", "K", "A"))
      + f" | {'L-W':>7s} {'se':>6s} {'+1.645se':>8s}")
    for c, v in r["classes"].items():
        p(f"  {c:11s} {v['n']:3d} {v['W']:+7.3f} {v['W_sem']:6.3f} | "
          + " ".join(f"{v['fc'][k]:+7.3f}" for k in ("L", "S1", "S2", "K", "A"))
          + f" | {v['over_L']:+7.3f} {v['over_L_se']:6.3f} {v['over_L'] + 1.645 * v['over_L_se']:+8.3f}")
    p(f"  VOID checks {r['void']}")
    p(f"  criteria {r['criteria']}")
    p(f"  kill {r['kill']}")
    p(f"  -> {'VERDICT' if r['zero'] == 'Z' else 'exploratory reading'}: {r['verdict']}")
    if not full:
        return
    ex = r["extras"]
    p("\n  --- reported, not decisive (composite Z) ---")
    p(f"  rho within graded: {ex['rho_within']['graded']}")
    p(f"  rho within know-k: {ex['rho_within']['know-k']}")
    p(f"  L orders know-1 < know-2 < know-3 < know-4: {ex['L_orders_know']}")
    p(f"  hindsight: " + "  ".join(f"{k} MSE {v['mse']:.5f} ratio {v['ratio']:.2f}" for k, v in ex["hindsight"].items()))
    p(f"  Brier [W >= 1/32]: " + "  ".join(f"{k} {v:.4f}" if isinstance(v, float) else f"{k} {v}" for k, v in ex["brier"].items()))
    w = ex["L_weights"]
    p(f"  L weight on the right action at stages 0-3 (raw units): {[round(x, 3) for x in w['right_action_at_stage']]}; "
      f"echo share {w['echo_share']:+.3f}")
    p(f"  L weights stage x labelled action (raw units): {w['stage_by_action']}")
    c = ex["S2_coordinated"]
    p(f"  S2 coordinated (64 wrong-chain clones in the pool): rho {c['rho']:+.3f}, MSE {c['mse']:.5f}; top class {c['top_class']}")
    p(f"    class mean S2 coordinated: {{{', '.join(f'{k}: {v:.3f}' for k, v in c['class_mean_S2'].items())}}}")
    p(f"    class mean S2 honest:      {{{', '.join(f'{k}: {v:.3f}' for k, v in c['class_mean_S2_honest'].items())}}}")
    g = ex["probe_gamer"]
    p(f"  probe-gamer (16): L forecast {g['forecast']:+.3f} vs W {g['W']:+.3f}: overpriced {g['over']:+.3f} (se {g['over_se']:.3f}); "
      f"know-4 W {g['know4_W']:+.3f}")
    a = ex["L_archive"]
    p(f"  L-archive (EXP-77b lessons, {a['n_train']} rows, penalty {a['lam']:g}): rho {a['rho']:+.3f}, MSE {a['mse']:.5f}, "
      f"skill {a['skill']:+.3f}")
    p(f"    class forecasts: {{{', '.join(f'{k}: {v:+.3f}' for k, v in a['class_fc'].items())}}}")
    p("  L on R probe labels per context: " + "  ".join(f"R={R}: rho {v['rho']:.3f} MSE {v['mse']:.5f}" for R, v in ex["L_R"].items()))
    sbt = ex["student_bootstrap"]
    p("  student-level bootstrap (95%): " + "  ".join(f"{k} [{v[0]:+.5f}, {v[1]:+.5f}]" for k, v in sbt.items()
                                                    if k.startswith(("rho_L", "drho", "dmse"))))


def main():
    rows, acc, blocks, m, mism = load()
    print(f"CAL-1 analysis: {len(rows)} twins, m = {m}, probe mismatches between rows and the pre-teaching file: {mism}")
    out = {}
    for zero in ["Z", "null", "untaught", "random"]:
        out[zero] = analyse(acc, blocks, m, zero, extras=(zero == "Z"))
        report(out[zero], full=(zero == "Z"))
    print("\n=== exploratory per-zero summary (amendment a; the verdict uses Z) ===")
    for zero, r in out.items():
        print(f"  {zero:8s} rho_L {r['rho']['L']:.3f} rho_S1 {r['rho']['S1']:+.3f} rho_S2 {r['rho']['S2']:.3f} "
              f"MSE_L {r['mse']['L']:.5f} MSE_S2 {r['mse']['S2']:.5f} know-4 W {r['classes']['know-4']['W']:+.3f} "
              f"rel {r['reliability']['spearman_brown']:.3f} failing {[k for k, v in r['criteria'].items() if not v]} -> {r['verdict']}")
    import cadence
    json.dump(dict(analysis=out, m=m, n_rows=len(rows), probe_mismatch=mism, version=cadence.__version__),
              open(os.path.join(HERE, f"{PREFIX}-analysis.json"), "w"), default=float)


if __name__ == "__main__":
    main()
