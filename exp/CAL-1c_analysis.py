"""
CAL-1c analysis: every number the pre-registration names, computed on the saved rows (no compute on brains).
PRE-REGISTRATION: experiments/CAL-1c.md (Will's go 2026-11-18). Written before any CAL-1c data existed, from
CAL-1b_analysis.py: blocks of 224 teachers in groups of 28, criterion 6 and K1 cover seven fake classes (nowait-map and
mixed-map added), the forms table (L refitted without nowait-map, without wait, without both) replaces CAL-1b's cause
table, with the registered readings for the novel form, the near-the-bar classes and the honest classes. Reported, not
decisive: two-sided calibration per fake class, consensus (S2) overpricing per class, mixed-map by WAIT count.

    PYTHONPATH=~/_cadence_v0940/src python -u CAL-1c_analysis.py > CAL-1c-full-analysis.out

Primary (verdict) uses the composite zero Z = per-student mean of {null, untaught, random}. Amendment (a), exploratory:
the whole primary analysis is repeated with each single zero (null, untaught, random) and reported beside Z; the verdict
still uses Z. Seeds: permutations default_rng(1), bootstraps default_rng(0).
"""
import importlib.util, json, os, sys

import numpy as np
from scipy.stats import rankdata
from sklearn.isotonic import IsotonicRegression

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("cal1ch", os.path.join(HERE, "CAL-1c_calibration_vs.py"))
H = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(H)
KNOW, FAKES, ZERO, RIGHTS, G, WAIT = H.KNOW, H.FAKES, H.ZERO, H.RIGHTS, H.G, H.WAIT
NT = 8 * G                                              # teachers per block (224)
HONEST = ["graded"] + KNOW
CLASSES = ["graded"] + KNOW + FAKES
LAMS = 10 ** np.arange(-3, 3.0001, 0.5)                 # 13 penalties, half-decade steps
N_PERM, N_BOOT, MARGIN6, B_BAR = 1000, 2000, 1 / 16, 1 / 32
PREFIX = os.environ.get("PREFIX", "CAL-1c-full")


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
    acc, mism, v5_bad = {}, 0, 0
    for r in rows:
        ver, path = (r.get("cadence") or ["?", "?"])
        v5_bad += ver != H.PIN_VERSION or H.PIN_DIR not in str(path).replace("\\", "/").split("/")
        acc[H.key(r)] = r["acc"]
        if r["arm"] == "teacher" and [list(x) for x in P[(r["tblock"], r["t"])]["probe"]] != [list(x) for x in r["probe"]]:
            mism += 1
    n_held = len({r["s"] for r in rows if r["sblock"] == "held"})
    assert n_held in (48, 64), n_held
    m = n_held // 8
    blocks = {}
    for b in ("train", "held", "probe-only"):
        ps = [P[(b, t)] for t in range(NT if b != "probe-only" else 80)]
        blocks[b] = dict(kinds=np.array([p["kind"] for p in ps]),
                         groups=np.array([p["group"] if p["group"] is not None else -1 for p in ps]),
                         probes=[[tuple(x) for x in p["probe"]] for p in ps],
                         identity=[p["identity"] for p in ps])
    return rows, acc, blocks, m, mism, v5_bad


def worth_tables(acc, m, zero):
    """Per-teacher, per-student worth (taught acc minus the zero on the same student)."""
    def z(sb, s):
        arms = ZERO if zero == "Z" else [zero]
        return float(np.mean([acc[(sb, s, a)] for a in arms]))
    wtr = np.array([[acc[("train", 3 * (t // G) + k, t)] - z("train", 3 * (t // G) + k) for k in range(3)]
                    for t in range(NT)])
    whe = np.array([[acc[("held", m * (t // G) + k, t)] - z("held", m * (t // G) + k) for k in range(m)]
                    for t in range(NT)])
    aud = np.array([acc[("audition", t // G, t)] - z("audition", t // G) for t in range(NT)])
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

def analyse(acc, blocks, m, zero, extras=False, v5_bad=0):
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

    allidx = np.arange(NT)
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
        yp = Wtr[rng1.permutation(NT)]
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
    void = dict(V3_reliability_below_5=rel < 0.5, V4_know4_W_below_10=k4 < 0.10, V5_other_cadence=v5_bad > 0)
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
                           wait_share_at_stage=[float(beta[5 * i + 4]) for i in range(4)],
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
    # L-archive is not repeated (CAL-1c.md, as CAL-1b)
    # two-sided calibration per fake class: |mean(L - W)| + 1.645 SE < 1/16 ("priced within one state both ways")
    ex["two_sided"] = {c: dict(over=res["classes"][c]["over_L"], se=res["classes"][c]["over_L_se"],
                               bound=abs(res["classes"][c]["over_L"]) + 1.645 * res["classes"][c]["over_L_se"],
                               passes=bool(abs(res["classes"][c]["over_L"]) + 1.645 * res["classes"][c]["over_L_se"] < MARGIN6))
                       for c in FAKES}
    # consensus (S2, through its own isotonic map) overpricing per fake class, as criterion 6 reads L
    ex["S2_over"] = {}
    for c in FAKES:
        d = fc["S2"][cls == c] - Whe[cls == c]
        se = float(d.std(ddof=1) / np.sqrt(len(d)))
        ex["S2_over"][c] = dict(over=float(d.mean()), se=se, bound=float(d.mean()) + 1.645 * se,
                                passes=bool(float(d.mean()) + 1.645 * se < MARGIN6))
    # mixed-map by its number of WAIT stages
    ix_mm = np.where(cls == "mixed-map")[0]
    nw = np.array([he["identity"][t]["map"].count(WAIT) for t in ix_mm])
    ex["mixed_by_wait"] = {int(k): dict(n=int((nw == k).sum()), W=float(Whe[ix_mm][nw == k].mean()),
                                        fc_L=float(fc["L"][ix_mm][nw == k].mean()),
                                        over_L=float((fc["L"][ix_mm] - Whe[ix_mm])[nw == k].mean()))
                           for k in sorted(set(nw.tolist()))}
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
        Wb = np.array([whe_s[t, pick[t // G]].mean() for t in range(NT)])
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


# ============ CAL-1c: the registered forms table (composite Z) ============

VARIANTS = (("primary", ()), ("L-nomap", ("nowait-map",)), ("L-nowait", ("wait",)), ("L-cal1", ("wait", "nowait-map")))


def forms_table(acc, blocks, m):
    """L's whole procedure (penalty by leave-one-group-out CV, isotonic map on the out-of-fold scores, clipped) refitted with
    training instances of the named classes dropped: primary (all 224), L-nomap (no nowait-map, 208), L-nowait (no wait,
    208), L-cal1 (neither, 192: CAL-1's training classes and graded share on fresh seeds). Per cell: criterion 6 for every
    fake class, the floor, rho and MSE on all held-out teachers and on the honest classes (graded and know-k). Plus the
    primary's raw ridge output on mixed-map (reported), and the paired bootstrap of MSE primary minus L-cal1."""
    tr, he = blocks["train"], blocks["held"]
    wtr_s, whe_s, _ = worth_tables(acc, m, "Z")
    Wtr, Whe = wtr_s.mean(1), whe_s.mean(1)
    cls, ghe = he["kinds"], he["groups"]
    honest = np.isin(cls, HONEST)
    Ftr_all, Fhe = feats(tr["probes"]), feats(he["probes"])
    out, fcs = {}, {}
    for name, drop in VARIANTS:
        keep = ~np.isin(tr["kinds"], drop)
        Ftr, ytr, gtr = Ftr_all[keep], Wtr[keep], tr["groups"][keep]
        std, mu, sd = standardizer(Ftr)
        L = L_procedure(std(Ftr), ytr, gtr, [std(Fhe)])
        sgn = sign_of(L["oof"], ytr)
        imap = iso(sgn * L["oof"], ytr)
        f = imap.predict(sgn * L["te"][0])
        fcs[name] = f
        cell = dict(n_train=int(keep.sum()), dropped=list(drop), lam=L["lam"], sign=sgn,
                    floor=float(np.min(imap.predict(sgn * L["oof"]))),
                    rho=spearman(sgn * L["te"][0], Whe), mse=float(np.mean((f - Whe) ** 2)),
                    mse_honest=float(np.mean((f[honest] - Whe[honest]) ** 2)), c6={})
        for c in FAKES:
            ix = cls == c
            d = f[ix] - Whe[ix]
            over, se = float(d.mean()), float(d.std(ddof=1) / np.sqrt(ix.sum()))
            cell["c6"][c] = dict(fc=float(f[ix].mean()), W=float(Whe[ix].mean()), over=over, se=se,
                                 bound=over + 1.645 * se, passes=bool(over + 1.645 * se < MARGIN6))
        if name == "primary":
            raw = L["te"][0]
            ix = cls == "mixed-map"
            d = raw[ix] - Whe[ix]
            cell["raw_mixed_map"] = dict(fc=float(raw[ix].mean()), over=float(d.mean()),
                                         bound=float(d.mean()) + 1.645 * float(d.std(ddof=1) / np.sqrt(ix.sum())))
        out[name] = cell
    # honest classes: MSE primary minus L-cal1, paired bootstrap over held-out teachers stratified by group, models fixed
    rng = np.random.default_rng(0)
    gidx = [np.where(ghe == g)[0] for g in range(8)]
    sq = {k: (fcs[k] - Whe) ** 2 for k in ("primary", "L-cal1")}
    diffs_h, diffs_a = [], []
    for _ in range(N_BOOT):
        idx = np.concatenate([rng.choice(ix, size=len(ix), replace=True) for ix in gidx])
        h = idx[honest[idx]]
        diffs_h.append(float(sq["primary"][h].mean() - sq["L-cal1"][h].mean()))
        diffs_a.append(float(sq["primary"][idx].mean() - sq["L-cal1"][idx].mean()))
    out["honest_mse_primary_minus_cal1"] = dict(
        point=float(sq["primary"][honest].mean() - sq["L-cal1"][honest].mean()), ci=ci(diffs_h), n=int(honest.sum()))
    out["all_mse_primary_minus_cal1"] = dict(point=float(sq["primary"].mean() - sq["L-cal1"].mean()), ci=ci(diffs_a))

    # ---- the registered readings (CAL-1c.md), fixed before any data
    P = lambda v, c: out[v]["c6"][c]["passes"]
    rd = []
    if P("primary", "mixed-map") and not P("L-nomap", "mixed-map"):
        rd.append("R1: primary passes and L-nomap fails on mixed-map: the non-WAIT maps in training are what priced the "
                  "novel form (spanning the kind worked where one pure harm did not)")
    if P("primary", "mixed-map") and P("L-nomap", "mixed-map"):
        rd.append("R2: primary and L-nomap both pass on mixed-map: on these rows the non-WAIT maps were not needed; the pass "
                  "comes with the rest of the design (CAL-1's 96 graded teachers, the wait class, fresh seeds)")
    if not P("primary", "mixed-map"):
        rd.append("R3: primary fails on mixed-map: training on several consistent-wrong forms did not make the procedure "
                  "price the novel form within one state")
    if P("L-cal1", "mixed-map"):
        rd.append("R4: L-cal1 passes on mixed-map: the CAL-1 / CAL-1b failure on the novel class did not replicate on these "
                  "seeds (the novel class here is mixed maps only); R1 to R3 are read with that caveat")
    if not P("primary", "nowait-map"):
        rd.append("R5: primary fails on nowait-map (a trained form, new maps): the procedure does not price new instances "
                  "of a trained consistent-wrong form within one state, so the binding limit is the forecaster's form "
                  "(additive in per-stage label shares), not only which forms training covers")
    near = ("random", "anti-echo")
    fail_p = [c for c in near if not P("primary", c)]
    if not fail_p:
        rd.append("N1: primary passes random and anti-echo: adding wait and nowait-map to CAL-1's training pool, its 96 "
                  "graded teachers kept, does not cost calibration near the bar on these rows; CAL-1b's failures there go "
                  "with its smaller graded pool or its draw, not with the range stretch alone")
    elif all(P("L-cal1", c) for c in fail_p):
        rd.append(f"N2: primary fails {fail_p} and L-cal1 passes them: on these rows adding the consistent-wrong forms to "
                  f"training costs calibration near the bar (L-nomap, CAL-1's pool plus wait, passes "
                  f"{[c for c in fail_p if P('L-nomap', c)]}; L-nowait passes {[c for c in fail_p if P('L-nowait', c)]})")
    else:
        rd.append(f"N3: primary fails {fail_p} and L-cal1 fails {[c for c in fail_p if not P('L-cal1', c)]} too: these "
                  f"classes fail near the bar on these seeds even with CAL-1's exact training pool; the stretch is not shown "
                  f"to be the cause" + (f" (L-cal1 passes {[c for c in fail_p if P('L-cal1', c)]})"
                                         if any(P("L-cal1", c) for c in fail_p) else ""))
    hci = out["honest_mse_primary_minus_cal1"]["ci"]
    rd.append("H1: the honest-class MSE interval is above 0: training on the consistent-wrong forms cost calibration on "
              "honest teachers" if hci[0] > 0 else
              "H2: the honest-class MSE interval is below 0: training on the consistent-wrong forms improved calibration "
              "on honest teachers" if hci[1] < 0 else
              "H3: the honest-class MSE interval spans 0: no change on honest teachers shown")
    out["readings"] = rd
    out["primary_forecasts"] = np.round(fcs["primary"], 6).tolist()
    return out


def report_forms(ft):
    p = lambda *a: print(*a, flush=True)
    p("\n=== CAL-1c forms table (registered, reported beside the verdict, not part of it; composite Z) ===")
    for name, _ in VARIANTS:
        c = ft[name]
        p(f"  {name:9s} ({c['n_train']} training teachers, dropped {c['dropped']}): penalty {c['lam']:g}, isotonic floor "
          f"{c['floor']:+.4f}, rho {c['rho']:+.3f}, MSE {c['mse']:.5f}, MSE on honest classes {c['mse_honest']:.5f}")
        p("     criterion 6 (over, bound): " + " | ".join(
            f"{k} {v['over']:+.3f} ({v['bound']:+.3f}) {'pass' if v['passes'] else 'FAIL'}" for k, v in c["c6"].items()))
    r = ft["primary"]["raw_mixed_map"]
    p(f"  primary raw ridge output on mixed-map (reported): fc {r['fc']:+.3f}, over {r['over']:+.3f}, bound {r['bound']:+.3f}")
    h, a = ft["honest_mse_primary_minus_cal1"], ft["all_mse_primary_minus_cal1"]
    p(f"  MSE primary minus L-cal1: honest classes (n {h['n']}) {h['point']:+.5f} [{h['ci'][0]:+.5f}, {h['ci'][1]:+.5f}]; "
      f"all held-out {a['point']:+.5f} [{a['ci'][0]:+.5f}, {a['ci'][1]:+.5f}]")
    for x in ft["readings"]:
        p(f"  reading: {x}")


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
      f"on WAIT {[round(x, 3) for x in w['wait_share_at_stage']]}; echo share {w['echo_share']:+.3f}")
    p(f"  L weights stage x labelled action (raw units): {w['stage_by_action']}")
    c = ex["S2_coordinated"]
    p(f"  S2 coordinated (64 wrong-chain clones in the pool): rho {c['rho']:+.3f}, MSE {c['mse']:.5f}; top class {c['top_class']}")
    p(f"    class mean S2 coordinated: {{{', '.join(f'{k}: {v:.3f}' for k, v in c['class_mean_S2'].items())}}}")
    p(f"    class mean S2 honest:      {{{', '.join(f'{k}: {v:.3f}' for k, v in c['class_mean_S2_honest'].items())}}}")
    g = ex["probe_gamer"]
    p(f"  probe-gamer (16): L forecast {g['forecast']:+.3f} vs W {g['W']:+.3f}: overpriced {g['over']:+.3f} (se {g['over_se']:.3f}); "
      f"know-4 W {g['know4_W']:+.3f}")
    p("  L on R probe labels per context: " + "  ".join(f"R={R}: rho {v['rho']:.3f} MSE {v['mse']:.5f}" for R, v in ex["L_R"].items()))
    p("  two-sided, |mean(L - W)| + 1.645 SE < 1/16: " + " | ".join(
        f"{k} {v['over']:+.3f} ({v['bound']:.3f}) {'pass' if v['passes'] else 'FAIL'}" for k, v in ex["two_sided"].items()))
    p("  consensus S2 overpricing (over, upper bound): " + " | ".join(
        f"{k} {v['over']:+.3f} ({v['bound']:+.3f}) {'pass' if v['passes'] else 'FAIL'}" for k, v in ex["S2_over"].items()))
    p("  mixed-map by WAIT stages: " + " | ".join(
        f"{k} WAIT (n {v['n']}): W {v['W']:+.3f} fc_L {v['fc_L']:+.3f} over {v['over_L']:+.3f}"
        for k, v in ex["mixed_by_wait"].items()))
    sbt = ex["student_bootstrap"]
    p("  student-level bootstrap (95%): " + "  ".join(f"{k} [{v[0]:+.5f}, {v[1]:+.5f}]" for k, v in sbt.items()
                                                    if k.startswith(("rho_L", "drho", "dmse"))))


def main():
    rows, acc, blocks, m, mism, v5_bad = load()
    print(f"CAL-1c analysis: {len(rows)} twins, m = {m}, probe mismatches between rows and the pre-teaching file: {mism}; "
          f"rows on a Cadence other than {H.PIN_VERSION} from ~/{H.PIN_DIR}: {v5_bad}")
    out = {}
    for zero in ["Z", "null", "untaught", "random"]:
        out[zero] = analyse(acc, blocks, m, zero, extras=(zero == "Z"), v5_bad=v5_bad)
        report(out[zero], full=(zero == "Z"))
        if zero == "Z":
            ft = forms_table(acc, blocks, m)
            assert np.allclose(ft["primary_forecasts"], out["Z"]["forecasts"]["L"], atol=1e-4), "forms primary != verdict L"
            report_forms(ft)
            out["forms_table"] = ft
    print("\n=== exploratory per-zero summary (amendment a; the verdict uses Z) ===")
    for zero, r in out.items():
        if zero == "forms_table":
            continue
        print(f"  {zero:8s} rho_L {r['rho']['L']:.3f} rho_S1 {r['rho']['S1']:+.3f} rho_S2 {r['rho']['S2']:.3f} "
              f"MSE_L {r['mse']['L']:.5f} MSE_S2 {r['mse']['S2']:.5f} know-4 W {r['classes']['know-4']['W']:+.3f} "
              f"rel {r['reliability']['spearman_brown']:.3f} failing {[k for k, v in r['criteria'].items() if not v]} -> {r['verdict']}")
    import cadence
    json.dump(dict(analysis=out, m=m, n_rows=len(rows), probe_mismatch=mism, v5_bad=v5_bad, version=cadence.__version__),
              open(os.path.join(HERE, f"{PREFIX}-analysis.json"), "w"), default=float)


if __name__ == "__main__":
    main()
