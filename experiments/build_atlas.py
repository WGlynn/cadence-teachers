"""Build ATLAS.html, the Cadence Lab Atlas, from atlas.json + experiments/EXP-*.md.

Python stdlib only. Run from anywhere:
    python experiments/build_atlas.py
Output: experiments/ATLAS.html (self-contained: inline CSS, inline SVG, a little vanilla JS).
"""

import glob
import html
import json
import os
import re
from collections import Counter, OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "atlas.json")
OUT = os.path.join(HERE, "ATLAS.html")
GENERATED = "2026-10-10"

# ============ Verdict palette ============
# Categorical slots 1-7 of the dataviz reference palette in its validated order
# (adjacent CVD and normal-vision gates pass in light and dark). Assigned to verdicts
# in fixed stack order; the verdict word always appears next to the colour.
VERDICTS = ["CROSSED", "SUPPORTIVE", "BOUNDARY", "NULL", "SUPERSEDED", "VOID", "RETRACTED"]
# Verdicts with no standing positive result: drawn as hollow marks so the split
# never rests on colour alone (several light-mode slots sit below 3:1 contrast).
HOLLOW = {"NULL", "SUPERSEDED", "VOID", "RETRACTED"}
VERDICT_BLURB = {
    "CROSSED": "milestone claim met on corrected numbers",
    "SUPPORTIVE": "points the right way, not a milestone",
    "BOUNDARY": "a limit, stated with a number",
    "NULL": "no effect, or the effect could not be seen",
    "SUPERSEDED": "replaced by a later, better experiment",
    "VOID": "never produced usable data",
    "RETRACTED": "the original claim was our bug",
}

ISSUE_RULES = OrderedDict([
    ("under-powered", ("Power the run for the pilot's effect size; one run per arm shows direction, not rank.",
                       "lesson (EXP-27), part of RUN GATE line 2 (seeds are a window knob)", "EXP-27")),
    ("at ceiling", ("Pilot finds the effect window: sweep the key knob under the exact run conditions; "
                    "the chosen value must sit away from 0% and 100%.", "RUN GATE line 2: WINDOW", "EXP-24")),
    ("bug in script", ("When a result looks better (or worse) than expected, audit the eval and accounting path "
                       "first; dump raw actions before theorising.", "lesson (EXP-01, EXP-12e, EXP-36)", "EXP-36")),
    ("stale records", ("Every experiment gets a reflection: experiments/EXP-XX.md with Summary + Reflection, "
                       "nulls, voids and reruns included; check.py must pass.", "rule, Will 2026-10-10", "EXP-20")),
    ("metric gameable", ("The score must not be passable by a degenerate policy (do-nothing twin, "
                         "None scored as wrong, identities by construction).", "RUN GATE line 4: METRIC", "EXP-19")),
    ("nothing varied", ("Confirm the thing being selected or compared actually varies before running.",
                        "RUN GATE line 3: VARIANCE", "EXP-23")),
    ("pilot != run conditions", ("A smoke test (does it run) is not the pilot. Name the chain knob -> signal -> "
                                 "estimate -> choice -> outcome and print every link per arm.",
                                 "RUN GATE line 5: CHAIN", "EXP-35")),
    ("effect window too small", ("Size the sweep to the time available; order cells so a timeout still leaves "
                                 "the decisive number.", "RUN GATE line 2: WINDOW", "EXP-12d")),
    ("version drift", ("Keep each run's output instead of overwriting it, and stamp the library version.",
                       "lesson (EXP-09, EXP-36), not yet a gate line", "EXP-09")),
])


def esc(s):
    return html.escape(str(s if s is not None else ""), quote=True)


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def fmt(v):
    if abs(v) >= 10 or v == int(v) and abs(v) >= 2:
        return ("%.3f" % v).rstrip("0").rstrip(".") if v != int(v) else str(int(v))
    return ("%.3f" % v).rstrip("0").rstrip(".") if v != 0 else "0"


# ============ Markdown extraction ============

def read_md():
    out = {}
    for path in sorted(glob.glob(os.path.join(HERE, "EXP-*.md"))):
        eid = os.path.splitext(os.path.basename(path))[0]
        with open(path, encoding="utf-8") as f:
            lines = f.read().splitlines()
        title = lines[0].lstrip("# ").strip() if lines else eid
        meaning, grab = [], False
        script = ""
        for ln in lines:
            if ln.startswith("- Script:"):
                script = ln[2:].strip()
            if ln.startswith("- What it means:"):
                grab = True
                meaning.append(ln[len("- What it means:"):].strip())
                continue
            if grab:
                if ln.startswith("  ") and not ln.lstrip().startswith("- "):
                    meaning.append(ln.strip())
                else:
                    grab = False
        out[eid] = {"title": title, "meaning": " ".join(meaning), "script": script.replace("`", "")}
    return out


# ============ SVG: horizontal bar chart (polarity aware) ============

def bar_path(x0, x1, y, h, r=4):
    """Bar from baseline x0 to x1 with only the data end rounded."""
    if abs(x1 - x0) < 0.5:
        return "M%.1f,%.1f h1 v%.1f h-1 Z" % (min(x0, x1), y, h)
    r = min(r, abs(x1 - x0), h / 2)
    if x1 >= x0:
        return ("M%.1f,%.1f H%.1f A%.1f,%.1f 0 0 1 %.1f,%.1f V%.1f A%.1f,%.1f 0 0 1 %.1f,%.1f H%.1f Z"
                % (x0, y, x1 - r, r, r, x1, y + r, y + h - r, r, r, x1 - r, y + h, x0))
    return ("M%.1f,%.1f H%.1f A%.1f,%.1f 0 0 0 %.1f,%.1f V%.1f A%.1f,%.1f 0 0 0 %.1f,%.1f H%.1f Z"
            % (x0, y, x1 + r, r, r, x1, y + r, y + h - r, r, r, x1 + r, y + h, x0))


def hbar(chart, exp_id=""):
    bars = chart.get("bars") or []
    if not bars:
        return '<p class="nochart">No chart: this experiment produced no usable numbers.</p>'
    W, PAD, ROW, BH, TOP = 460, 46, 26, 14, 6
    # Label column sized to the longest (truncated) label at ~6px/char for 11px text, so nothing clips.
    longest = max(min(len(b["label"]), 34) for b in bars)
    LABEL = int(min(230, max(90, 14 + longest * 6.2)))
    lo = min([0.0] + [b["value"] - b.get("sem", 0) for b in bars])
    hi = max([0.0] + [b["value"] + b.get("sem", 0) for b in bars])
    if hi == lo:
        hi = lo + 1
    px0, px1 = LABEL + (PAD if lo < 0 else 6), W - PAD

    def sx(v):
        return px0 + (v - lo) / (hi - lo) * (px1 - px0)

    H = TOP + ROW * len(bars) + 4
    zx = sx(0)
    parts = ['<svg class="bars" viewBox="0 0 %d %d" role="img" aria-label="%s">' % (W, H, esc(chart.get("title", "")))]
    parts.append('<line class="zero" x1="%.1f" x2="%.1f" y1="2" y2="%d"/>' % (zx, zx, H - 2))
    for i, b in enumerate(bars):
        v = b["value"]
        y = TOP + i * ROW
        x1 = sx(v)
        cls = "neg" if v < 0 else "pos"
        sem = b.get("sem")
        tip = "%s: %s%s" % (b["label"], fmt(v), (" +/- %s SEM" % fmt(sem)) if sem else "")
        parts.append('<g class="hit" data-tip="%s">' % esc(tip))
        parts.append('<rect class="hitbox" x="0" y="%d" width="%d" height="%d"/>' % (y - 5, W, ROW))
        lab = b["label"] if len(b["label"]) <= 34 else b["label"][:32] + "..."
        parts.append('<text class="lab" x="%d" y="%.1f">%s</text>' % (LABEL - 8, y + BH - 3, esc(lab)))
        parts.append('<path class="%s" d="%s"/>' % (cls, bar_path(zx, x1, y, BH)))
        end = x1
        if sem:
            a, c = sx(v - sem), sx(v + sem)
            parts.append('<line class="err" x1="%.1f" x2="%.1f" y1="%.1f" y2="%.1f"/>' % (a, c, y + BH / 2, y + BH / 2))
            for xx in (a, c):
                parts.append('<line class="err" x1="%.1f" x2="%.1f" y1="%.1f" y2="%.1f"/>' % (xx, xx, y + 3, y + BH - 3))
            end = c if v >= 0 else a
        if v >= 0:
            parts.append('<text class="val" x="%.1f" y="%.1f">%s</text>' % (end + 5, y + BH - 3, esc(fmt(v))))
        else:
            parts.append('<text class="val" text-anchor="end" x="%.1f" y="%.1f">%s</text>' % (end - 5, y + BH - 3, esc(fmt(v))))
        parts.append("</g>")
    parts.append("</svg>")
    unit = chart.get("unit", "")
    return ('<figure class="chart"><figcaption><b>%s</b>%s</figcaption>%s</figure>'
            % (esc(chart.get("title", "")), (" <span>&middot; %s</span>" % esc(unit)) if unit else "", "".join(parts)))


# ============ SVG: timeline ============

def timeline(recs, tracks):
    n = len(recs)
    LEFT, STEP, ROWH, TOP = 190, 22, 40, 26
    W = LEFT + STEP * n + 20
    H = TOP + ROWH * len(tracks) + 10
    idx = {r["id"]: i for i, r in enumerate(recs)}
    p = ['<svg class="timeline" viewBox="0 0 %d %d" role="img" aria-label="Experiments in run order by track">' % (W, H)]
    # day bands from first date in record
    days = [r["date"][:10] for r in recs]
    start = 0
    for i in range(1, n + 1):
        if i == n or days[i] != days[start]:
            x0 = LEFT + STEP * start
            p.append('<text class="day" x="%.1f" y="14">%s</text>' % (x0 + 2, esc(days[start][5:])))
            p.append('<line class="dayline" x1="%.1f" x2="%.1f" y1="18" y2="%d"/>' % (x0 - 2, x0 - 2, H - 4))
            start = i
    for t, track in enumerate(tracks):
        y = TOP + t * ROWH + ROWH / 2
        p.append('<text class="trk" x="%d" y="%.1f">%s</text>' % (LEFT - 12, y + 4, esc(track)))
        p.append('<line class="rail" x1="%d" x2="%d" y1="%.1f" y2="%.1f"/>' % (LEFT, W - 14, y, y))
        for r in recs:
            if r["track"] != track:
                continue
            x = LEFT + STEP * idx[r["id"]] + STEP / 2
            vi = VERDICTS.index(r["verdict"]) + 1
            hol = " hollow" if r["verdict"] in HOLLOW else ""
            tip = "%s %s [%s]: %s" % (r["id"], r["name"], r["verdict"], r["headline"])
            p.append('<g class="dot hit" tabindex="0" data-id="%s" data-tip="%s"><circle class="halo" cx="%.1f" cy="%.1f" r="11"/>'
                     '<circle class="v%d%s" cx="%.1f" cy="%.1f" r="7"/></g>' % (esc(r["id"]), esc(tip), x, y, vi, hol, x, y))
    p.append("</svg>")
    return "".join(p)


# ============ SVG: stacked verdicts per track ============

def stacked(recs, tracks):
    W, LABEL, ROW, BH = 640, 190, 30, 18
    maxn = max(sum(1 for r in recs if r["track"] == t) for t in tracks)
    unit = (W - LABEL - 40) / maxn
    H = ROW * len(tracks) + 6
    p = ['<svg class="stack" viewBox="0 0 %d %d" role="img" aria-label="Verdicts per track">' % (W, H)]
    for t, track in enumerate(tracks):
        y = 4 + t * ROW
        rs = [r for r in recs if r["track"] == track]
        c = Counter(r["verdict"] for r in rs)
        p.append('<text class="lab" x="%d" y="%.1f">%s</text>' % (LABEL - 8, y + BH - 4, esc(track)))
        x = LABEL
        segs = [(v, c[v]) for v in VERDICTS if c[v]]
        for k, (v, cnt) in enumerate(segs):
            w = cnt * unit - 2
            last = k == len(segs) - 1
            ids = ", ".join(r["id"] for r in rs if r["verdict"] == v)
            tip = "%s / %s: %d (%s)" % (track, v, cnt, ids)
            p.append('<g class="hit" data-tip="%s">' % esc(tip))
            if last:
                p.append('<path class="v%d" d="%s"/>' % (VERDICTS.index(v) + 1, bar_path(x, x + w, y, BH)))
            else:
                p.append('<rect class="v%d" x="%.1f" y="%d" width="%.1f" height="%d"/>' % (VERDICTS.index(v) + 1, x, y, w, BH))
            p.append("</g>")
            x += cnt * unit
        p.append('<text class="val" x="%.1f" y="%.1f">%d</text>' % (x + 4, y + BH - 4, len(rs)))
    p.append("</svg>")
    return "".join(p)


def legend():
    return '<ul class="legend">' + "".join(
        '<li><span class="sw v%d%s"></span><b>%s</b> <span class="muted">%s</span></li>'
        % (i + 1, " hollow" if v in HOLLOW else "", v, esc(VERDICT_BLURB[v]))
        for i, v in enumerate(VERDICTS)) + "</ul>" + (
        '<p class="note" style="margin:-6px 0 14px">In the storyline and verdict chips, filled dot: a result that currently stands. '
        "Hollow ring: no standing positive result (null, void, retracted, or replaced by a later run).</p>")


# ============ Page ============

CSS = """
:root{color-scheme:light;--bg:#f4f3ef;--surface:#fcfcfb;--line:#e3e1db;--text:#0b0b0b;--text2:#52514e;--muted:#7a7974;
--v1:#2a78d6;--v2:#eb6834;--v3:#1baf7a;--v4:#eda100;--v5:#e87ba4;--v6:#008300;--v7:#4a3aa7;--pos:#2a78d6;--neg:#e34948;--accent:#2a78d6}
@media (prefers-color-scheme:dark){:root:where(:not([data-theme="light"])){color-scheme:dark;--bg:#111110;--surface:#1a1a19;--line:#33332f;
--text:#ffffff;--text2:#c3c2b7;--muted:#8f8e86;--v1:#3987e5;--v2:#d95926;--v3:#199e70;--v4:#c98500;--v5:#d55181;--v6:#008300;--v7:#9085e9;--pos:#3987e5;--neg:#e66767;--accent:#6da7ec}}
:root[data-theme="dark"]{color-scheme:dark;--bg:#111110;--surface:#1a1a19;--line:#33332f;
--text:#ffffff;--text2:#c3c2b7;--muted:#8f8e86;--v1:#3987e5;--v2:#d95926;--v3:#199e70;--v4:#c98500;--v5:#d55181;--v6:#008300;--v7:#9085e9;--pos:#3987e5;--neg:#e66767;--accent:#6da7ec}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);font:16px/1.55 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
.wrap{max-width:1120px;margin:0 auto;padding:0 20px}
header.hero{padding:56px 0 28px}
.kicker{font-size:13px;letter-spacing:.12em;text-transform:uppercase;color:var(--text2)}
h1{font-size:clamp(34px,6vw,58px);line-height:1.05;margin:.2em 0 .35em;letter-spacing:-.02em}
h2{font-size:28px;margin:0 0 6px;letter-spacing:-.01em}
h3{font-size:18px;margin:0 0 6px}
.lede{font-size:19px;max-width:760px;color:var(--text2)}
.lede b{color:var(--text)}
section{padding:40px 0;border-top:1px solid var(--line)}
.sub{color:var(--text2);max-width:780px;margin:0 0 22px}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin-top:28px}
.tile{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:16px 18px}
.tile .n{font-size:44px;font-weight:700;line-height:1;font-variant-numeric:tabular-nums}
.tile .l{color:var(--text2);font-size:14px;margin-top:6px}
.tile .mk{display:inline-block;width:10px;height:10px;border-radius:50%;margin-right:6px;vertical-align:1px}
.card{background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:18px 20px}
.grid2{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,480px),1fr));gap:16px}
.scrollx{overflow-x:auto;background:var(--surface);border:1px solid var(--line);border-radius:12px;padding:12px}
svg{display:block;width:100%;height:auto;font-family:inherit}
svg.timeline{min-width:980px}
svg.stack{max-width:820px}
svg text{fill:var(--text2);font-size:11px}
svg .lab,svg .trk{text-anchor:end;fill:var(--text2)}
svg .trk{font-size:12px;fill:var(--text)}
svg .val{fill:var(--text);font-size:11px;font-variant-numeric:tabular-nums}
svg .day{font-size:10px;fill:var(--muted)}
svg .dayline{stroke:var(--line);stroke-dasharray:2 3}
svg .rail{stroke:var(--line);stroke-width:2}
svg .zero{stroke:var(--muted);stroke-width:1}
svg .err{stroke:var(--text);stroke-width:1.2}
svg .pos{fill:var(--pos)} svg .neg{fill:var(--neg)}
svg .hitbox{fill:transparent}
svg .halo{fill:transparent}
svg .dot{cursor:pointer;outline:none}
svg .dot circle:not(.halo){stroke:var(--surface);stroke-width:2}
svg .dot:hover .halo,svg .dot:focus .halo,svg .dot.sel .halo{fill:none;stroke:var(--text);stroke-width:1.5}
svg .hit:hover .pos,svg .hit:hover .neg{opacity:.8}
.v1{fill:var(--v1);background:var(--v1)}.v2{fill:var(--v2);background:var(--v2)}.v3{fill:var(--v3);background:var(--v3)}
.v4{fill:var(--v4);background:var(--v4)}.v5{fill:var(--v5);background:var(--v5)}.v6{fill:var(--v6);background:var(--v6)}.v7{fill:var(--v7);background:var(--v7)}
.v1{color:var(--v1)}.v2{color:var(--v2)}.v3{color:var(--v3)}.v4{color:var(--v4)}.v5{color:var(--v5)}.v6{color:var(--v6)}.v7{color:var(--v7)}
svg .dot circle.hollow{fill:var(--surface);stroke:currentColor;stroke-width:3}
.sw.hollow,.mk.hollow{background:transparent!important;border:2.5px solid currentColor}
svg rect.v1,svg rect.v2,svg rect.v3,svg rect.v4,svg rect.v5,svg rect.v6,svg rect.v7{stroke:none}
.legend{list-style:none;padding:0;margin:0 0 14px;display:flex;flex-wrap:wrap;gap:6px 18px;font-size:14px}
.legend .sw,.vchip .sw{display:inline-block;width:11px;height:11px;border-radius:50%;margin-right:6px;vertical-align:-1px}
.muted{color:var(--muted)}
#detail{margin-top:14px;min-height:84px}
#detail .id{font-weight:700}
figure.chart{margin:12px 0 0}
figure.chart figcaption{font-size:13px;color:var(--text2);margin-bottom:4px}
figure.chart figcaption b{color:var(--text);font-weight:600}
.vchip{display:inline-flex;align-items:center;font-size:12px;font-weight:600;letter-spacing:.04em;border:1px solid var(--line);border-radius:999px;padding:1px 9px 1px 7px;color:var(--text)}
.head{display:flex;gap:10px;align-items:baseline;flex-wrap:wrap}
.head .id{font-weight:700;font-variant-numeric:tabular-nums}
.note{font-size:13px;color:var(--text2);margin-top:10px}
blockquote{margin:0;padding:16px 18px;background:var(--surface);border:1px solid var(--line);border-left:4px solid var(--accent);border-radius:10px;font-size:17px;line-height:1.45}
blockquote cite{display:block;margin-top:8px;font-style:normal;font-size:13px;color:var(--text2)}
.quotes{columns:3 300px;column-gap:16px}
.quotes blockquote{break-inside:avoid;margin:0 0 16px}
details.more>summary{cursor:pointer;color:var(--accent);font-weight:600;margin-top:4px}
table{border-collapse:collapse;width:100%;font-size:14px}
th,td{text-align:left;padding:8px 10px;border-bottom:1px solid var(--line);vertical-align:top}
th{color:var(--text2);font-weight:600}
td.num{text-align:right;font-variant-numeric:tabular-nums}
.filters{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 14px;align-items:center}
.filters button,.toggle{font:inherit;font-size:13px;background:var(--surface);color:var(--text);border:1px solid var(--line);border-radius:999px;padding:4px 12px;cursor:pointer}
.filters button[aria-pressed="true"]{border-color:var(--text);font-weight:600}
details.exp{background:var(--surface);border:1px solid var(--line);border-radius:10px;margin:0 0 8px}
details.exp>summary{cursor:pointer;padding:12px 16px;list-style:none}
details.exp>summary::-webkit-details-marker{display:none}
details.exp>summary .hl{display:block;color:var(--text2);font-size:14px;margin-top:2px}
details.exp .body{padding:0 16px 16px}
details.exp dl{display:grid;grid-template-columns:120px 1fr;gap:6px 14px;margin:10px 0;font-size:14px}
details.exp dt{color:var(--muted)} details.exp dd{margin:0}
a{color:var(--accent)}
.lessons td:first-child{white-space:nowrap;font-weight:600}
.pile td:first-child,.pile td:nth-child(2){white-space:nowrap}
.pill{font-size:12px;color:var(--text2)}
footer{padding:36px 0 60px;border-top:1px solid var(--line);color:var(--text2);font-size:14px}
code{font-size:.92em;background:var(--surface);border:1px solid var(--line);border-radius:5px;padding:0 5px}
#tip{position:fixed;pointer-events:none;z-index:9;max-width:360px;background:var(--text);color:var(--bg);font-size:13px;line-height:1.4;padding:8px 10px;border-radius:8px;opacity:0;transition:opacity .08s}
.toggle{position:absolute;top:16px;right:20px}
.topbar{position:relative}
.scrollhint{display:none;margin:0 0 6px}
@media (max-width:1020px){.scrollhint{display:block}}
@media (max-width:640px){details.exp dl{grid-template-columns:1fr}.tile .n{font-size:36px}}
@media print{.filters,.toggle{display:none}details.exp{break-inside:avoid}}
"""

JS = r"""
(function(){
  var DATA = JSON.parse(document.getElementById('atlas-data').textContent);
  var byId = {}; DATA.forEach(function(r){ byId[r.id] = r; });
  var tip = document.getElementById('tip');
  document.addEventListener('mousemove', function(e){
    var g = e.target.closest ? e.target.closest('[data-tip]') : null;
    if(!g){ tip.style.opacity = 0; return; }
    tip.textContent = g.getAttribute('data-tip');
    var x = e.clientX + 14, y = e.clientY + 14;
    if (x + 370 > window.innerWidth) x = e.clientX - 370;
    tip.style.left = x + 'px'; tip.style.top = y + 'px'; tip.style.opacity = 1;
  });
  var detail = document.getElementById('detail');
  function show(id){
    var r = byId[id]; if(!r) return;
    document.querySelectorAll('.dot.sel').forEach(function(d){ d.classList.remove('sel'); });
    var d = document.querySelector('.dot[data-id="'+id+'"]'); if(d) d.classList.add('sel');
    detail.innerHTML = '';
    var h = document.createElement('div'); h.className = 'head';
    h.innerHTML = '<span class="id"></span> <span class="nm"></span> <span class="vchip"><span class="sw v'+(VERD.indexOf(r.verdict)+1)+(HOL.indexOf(r.verdict)>=0?' hollow':'')+'"></span>'+r.verdict+'</span>';
    h.querySelector('.id').textContent = r.id; h.querySelector('.nm').textContent = r.name;
    var p = document.createElement('p'); p.textContent = r.headline; p.style.margin = '6px 0';
    var a = document.createElement('a'); a.href = '#x-' + r.id; a.textContent = 'Open in the index';
    a.addEventListener('click', function(){ var el = document.getElementById('x-'+r.id); if(el) el.open = true; });
    detail.appendChild(h); detail.appendChild(p); detail.appendChild(a);
  }
  var VERD = %VERD%, HOL = %HOL%;
  document.querySelectorAll('.dot').forEach(function(d){
    d.addEventListener('click', function(){ show(d.getAttribute('data-id')); });
    d.addEventListener('keydown', function(e){ if(e.key==='Enter'||e.key===' '){ e.preventDefault(); show(d.getAttribute('data-id')); }});
  });
  // index filters
  var state = {verdict:'all', track:'all'};
  function apply(){
    document.querySelectorAll('details.exp').forEach(function(el){
      var ok = (state.verdict==='all'||el.dataset.verdict===state.verdict) && (state.track==='all'||el.dataset.track===state.track);
      el.hidden = !ok;
    });
  }
  document.querySelectorAll('.filters button').forEach(function(b){
    b.addEventListener('click', function(){
      var k = b.dataset.k; state[k] = b.dataset.v;
      document.querySelectorAll('.filters button[data-k="'+k+'"]').forEach(function(o){ o.setAttribute('aria-pressed', o===b ? 'true':'false'); });
      apply();
    });
  });
  document.getElementById('expandall').addEventListener('click', function(){
    var open = this.dataset.open !== '1';
    document.querySelectorAll('details.exp').forEach(function(el){ if(!el.hidden) el.open = open; });
    this.dataset.open = open ? '1' : '0'; this.textContent = open ? 'Collapse all' : 'Expand all';
  });
  // theme toggle
  var t = document.getElementById('theme');
  t.addEventListener('click', function(){
    var root = document.documentElement;
    var dark = root.dataset.theme ? root.dataset.theme === 'dark' : window.matchMedia('(prefers-color-scheme: dark)').matches;
    root.dataset.theme = dark ? 'light' : 'dark';
  });
})();
"""


def main():
    with open(DATA, encoding="utf-8") as f:
        recs = json.load(f)
    md = read_md()
    tracks = list(OrderedDict.fromkeys(r["track"] for r in recs))
    vc = Counter(r["verdict"] for r in recs)
    bugs = sum(1 for r in recs if "bug in script" in r["process_issues"])
    issues = Counter(i for r in recs for i in r["process_issues"] if i != "none")
    vcls = {v: "v%d" % (i + 1) for i, v in enumerate(VERDICTS)}

    def chip(v):
        return '<span class="vchip"><span class="sw %s%s"></span>%s</span>' % (vcls[v], " hollow" if v in HOLLOW else "", v)

    out = []
    w = out.append
    w('<!doctype html><html lang="en"><head><meta charset="utf-8">')
    w('<meta name="viewport" content="width=device-width,initial-scale=1">')
    w("<title>Cadence Lab Atlas</title><style>%s</style></head><body>" % CSS)

    # ---- Hero
    tiles = [
        (len(recs), "experiments logged", ""),
        (vc["CROSSED"], "CROSSED: claim met", "v1"),
        (vc["NULL"], "NULL: no visible effect", "v4 hollow"),
        (vc["VOID"] + vc["RETRACTED"], "VOID or RETRACTED", "v6 hollow|v7 hollow"),
        (bugs, "experiments where we caught our own bug", ""),
    ]
    w('<div class="wrap topbar"><button class="toggle" id="theme" type="button">Light / dark</button>')
    w('<header class="hero"><div class="kicker">Cadence Lab Atlas &middot; reflections %s to %s</div>' % (esc(recs[0]["id"]), esc(recs[-1]["id"])))
    w("<h1>Small brains, learning to teach each other</h1>")
    w('<p class="lede">We grow small <b>Cadence</b> brains and ask whether one can measurably teach another, '
      "and whether the worth of that teaching can be priced from outcomes instead of from what the brain looks like inside. "
      "The goal is a market that pays for <b>teaching ability passed down generations</b>, where credit follows the lineage of what was learned. "
      "This atlas collects every reflection so far, the wins and, just as proudly, the nulls, voids and our own retracted mistakes.</p>")
    w('<div class="tiles">')
    for n, l, c in tiles:
        mk = "".join('<span class="mk %s"></span>' % k for k in c.split("|")) if c else ""
        w('<div class="tile"><div class="n">%d</div><div class="l">%s%s</div></div>' % (n, mk, esc(l)))
    w("</div>")
    w('<p class="note">%d SUPPORTIVE, %d SUPERSEDED, %d BOUNDARY make up the rest. Verdicts are the current ones after reruns; '
      "several experiments changed verdict when we found bugs, and those stories are kept below.</p>"
      % (vc["SUPPORTIVE"], vc["SUPERSEDED"], vc["BOUNDARY"]))
    w("</header></div>")

    # ---- Timeline
    w('<section id="timeline"><div class="wrap"><h2>Storyline</h2>')
    d0, d1 = min(r["date"][:10] for r in recs), max(r["date"][:10] for r in recs)
    w('<p class="sub">Every experiment in run order (left to right, by first run date: %s to %s; several were rerun later), '
      "one row per research track. " % (esc(d0), esc(d1)) +
      "Hover a dot for its headline, click or press Enter to pin the details. The program moved from <i>can we price a witness</i> "
      "(attribution) through a long XOR dead end, into the teaching game, generations, networks and finally attacks on the market.</p>")
    w(legend())
    w('<p class="note scrollhint">Scroll the chart sideways to see all %d experiments.</p>' % len(recs))
    w('<div class="scrollx">%s</div>' % timeline(recs, tracks))
    w('<div id="detail" class="card"><span class="muted">Click a dot to see its headline here.</span></div>')
    w("</div></section>")

    # ---- What we know
    crossed = [r for r in recs if r["verdict"] == "CROSSED"]
    w('<section id="know"><div class="wrap"><h2>What we know</h2>')
    w('<p class="sub">The %d CROSSED findings: claims that met their milestone on corrected numbers. Each carries its scope note; '
      "none of them is a proof, and most were run on small bandits with a handful of seeds. Blue bars are positive, red negative; "
      "whiskers are one standard error where we have it.</p>" % len(crossed))
    w('<div class="grid2">')
    for r in crossed:
        w('<article class="card"><div class="head"><span class="id">%s</span>%s<span class="pill">%s</span></div>'
          % (esc(r["id"]), chip(r["verdict"]), esc(r["track"])))
        w("<h3>%s</h3><p>%s</p>%s" % (esc(r["name"]), esc(r["headline"]), hbar(r.get("chart") or {}, r["id"])))
        w('<p class="note"><b>Scope:</b> %s</p></article>' % esc(r["verdict_note"]))
    w("</div>")
    sup = [r for r in recs if r["verdict"] in ("SUPPORTIVE", "BOUNDARY")]
    w('<p class="note" style="margin-top:18px">Also standing, at lower confidence: %s. Open them in the index below.</p>'
      % ", ".join('<a href="#x-%s">%s</a>' % (r["id"], r["id"]) for r in sup))
    w("</div></section>")

    # ---- Hall of nulls and mistakes
    w('<section id="hall"><div class="wrap"><h2>Hall of nulls and mistakes</h2>')
    w('<p class="sub">Every reflection tags what went wrong in the process. These tags are how the lab learns: most recurring '
      "failures became a line of the RUN GATE we now check before any experiment (in <a href=\"../VS-TRANSFER-PROGRAM.md\">VS-TRANSFER-PROGRAM.md</a>); "
      "the Status column says which are still only lessons. "
      "Counts are experiments carrying the tag; one experiment can carry several. %s came back with no tag at all.</p>"
      % (" and ".join(r["id"] for r in recs if not [i for i in r["process_issues"] if i != "none"]) or "No experiment"))
    tally = {"title": "Process issues across %d experiments" % len(recs), "unit": "experiments with this tag",
             "bars": [{"label": k, "value": v} for k, v in issues.most_common()]}
    w('<div class="grid2"><div class="card">%s</div>' % hbar(tally))
    shame = [r for r in recs if r["verdict"] in ("NULL", "VOID", "RETRACTED")]
    w('<div class="card"><h3>The honest pile</h3><p class="note" style="margin-top:0">Nulls, voids and retractions. Each one narrowed the search.</p><table class="pile"><tbody>')
    for r in shame:
        w('<tr><td><a href="#x-%s">%s</a></td><td>%s</td><td>%s</td></tr>' % (r["id"], r["id"], chip(r["verdict"]), esc(r["name"])))
    w("</tbody></table></div></div>")
    w('<h3 style="margin-top:26px">From mistake to rule</h3>')
    w('<div class="card scrollx" style="padding:4px 8px"><table class="lessons"><thead><tr><th>Issue</th><th class="num">Count</th>'
      "<th>What we do now</th><th>Status</th><th>Learned in</th></tr></thead><tbody>")
    for k, v in issues.most_common():
        rule, status, src = ISSUE_RULES.get(k, ("", "", ""))
        w('<tr><td>%s</td><td class="num">%d</td><td>%s</td><td class="pill">%s</td><td><a href="#x-%s">%s</a></td></tr>'
          % (esc(k), v, esc(rule), esc(status), esc(src), esc(src)))
    w("</tbody></table></div>")
    w('<p class="note">The single most common failure (about a third of failed runs, per the program log) was an effect outside '
      "the visible window: too small to see over noise, or so easy every arm hit 100%. Hence the rule: the pilot finds the effect window.</p>")
    w("</div></section>")

    # ---- Verdicts per track
    w('<section id="tracks"><div class="wrap"><h2>Verdicts by track</h2>')
    w('<p class="sub">How each line of work has fared. The XOR track is mostly nulls and dead ends: from EXP-12 to EXP-14b '
      "the substrate never got off chance on XOR on any wiring tried, a clear negative for this substrate, not for XOR learning in general. "
      "Synergy was later shown by a different route (EXP-18, EXP-19, both SUPPORTIVE). Bar length is the number of experiments; "
      "hover a segment for the ones in it, or open the table view.</p>")
    w(legend())
    w('<div class="card">%s</div>' % stacked(recs, tracks))
    w('<details style="margin-top:10px"><summary>Table view</summary><div class="card scrollx"><table><thead><tr><th>Track</th>')
    w("".join("<th class=\"num\">%s</th>" % v for v in VERDICTS) + '<th class="num">Total</th></tr></thead><tbody>')
    for t in tracks:
        c = Counter(r["verdict"] for r in recs if r["track"] == t)
        w("<tr><td>%s</td>%s<td class=\"num\">%d</td></tr>" % (esc(t), "".join('<td class="num">%s</td>' % (c[v] or "") for v in VERDICTS), sum(c.values())))
    w("</tbody></table></div></details></div></section>")

    # ---- Surprises
    qs = [r for r in recs if r.get("quote_worthy")]
    # Lead with one line per track (first in run order) so the wall reads as a tour, rest folded.
    seen, lead = set(), []
    for r in qs:
        if r["track"] not in seen:
            seen.add(r["track"])
            lead.append(r)
    rest = [r for r in qs if r not in lead]

    def quote(r):
        return ('<blockquote>%s<cite><a href="#x-%s">%s</a> &middot; %s &middot; %s</cite></blockquote>'
                % (esc(r["quote_worthy"]), r["id"], r["id"], esc(r["name"]), esc(r["track"])))
    w('<section id="surprises"><div class="wrap"><h2>Surprises</h2>')
    w('<p class="sub">The lines from the reflections that changed how we think, one per track to start. '
      "Many are about our own instruments rather than about Cadence.</p><div class=\"quotes\">")
    w("".join(quote(r) for r in lead))
    w("</div>")
    if rest:
        w('<details class="more"><summary>%d more surprises</summary><div class="quotes" style="margin-top:14px">%s</div></details>'
          % (len(rest), "".join(quote(r) for r in rest)))
    w("</div></section>")

    # ---- Index
    w('<section id="index"><div class="wrap"><h2>Every experiment</h2>')
    w('<p class="sub">Expand any row for the question, verdict note, lesson, chart and a link to the full reflection file.</p>')
    w('<div class="filters"><span class="muted">Verdict:</span><button data-k="verdict" data-v="all" aria-pressed="true">All</button>')
    for v in VERDICTS:
        if vc[v]:
            w('<button data-k="verdict" data-v="%s" aria-pressed="false">%s (%d)</button>' % (v, v, vc[v]))
    w('</div><div class="filters"><span class="muted">Track:</span><button data-k="track" data-v="all" aria-pressed="true">All</button>')
    for t in tracks:
        w('<button data-k="track" data-v="%s" aria-pressed="false">%s</button>' % (esc(t), esc(t)))
    w('<button id="expandall" type="button" style="margin-left:auto">Expand all</button></div>')
    for r in recs:
        m = md.get(r["id"], {})
        link = "%s.md" % r["id"]
        has_md = r["id"] in md
        w('<details class="exp" id="x-%s" data-verdict="%s" data-track="%s"><summary><span class="head"><span class="id">%s</span>'
          "<span>%s</span>%s<span class=\"pill\">%s</span></span><span class=\"hl\">%s</span></summary><div class=\"body\">"
          % (r["id"], r["verdict"], esc(r["track"]), r["id"], esc(r["name"]), chip(r["verdict"]), esc(r["track"]), esc(r["headline"])))
        w("<dl><dt>Question</dt><dd>%s</dd><dt>Dates</dt><dd>%s (%s)</dd><dt>Verdict note</dt><dd>%s</dd>"
          % (esc(r["question"]), esc(r["date"]), esc(r["iter"]), esc(r["verdict_note"])))
        if m.get("meaning"):
            w("<dt>What it means</dt><dd>%s</dd>" % esc(m["meaning"]))
        w("<dt>Lesson</dt><dd>%s</dd>" % esc(r["lesson"]))
        iss = [i for i in r["process_issues"] if i != "none"]
        w("<dt>Process tags</dt><dd>%s</dd>" % (esc(", ".join(iss)) if iss else "none"))
        if m.get("script"):
            w("<dt>Evidence</dt><dd><code>%s</code></dd>" % esc(m["script"]))
        w("<dt>Reflection</dt><dd>%s</dd></dl>" % (('<a href="%s">%s</a>' % (link, link)) if has_md else "not found"))
        w(hbar(r.get("chart") or {}, r["id"]))
        w("</div></details>")
    w("</div></section>")

    # ---- Footer
    if not any(r["id"] == "EXP-35b" for r in recs):
        w('<footer><div class="wrap"><p><b>Not yet in the atlas:</b> EXP-35b (pedigree share at K=96). It ran VOID on 2026-10-09 '
          "(credit bug: the share never reached the move choice) and NULL on the patched rerun 2026-10-10: the share channel was "
          "starved, not refuted. Its reflection file is not written yet; the next step is to open the effect window before any rerun "
          "(see VS-TRANSFER-PROGRAM.md, iter25 and iter27).</p>")
    else:
        w('<footer><div class="wrap">')
    w("<p>Generated %s from <code>experiments/atlas.json</code> plus %d reflection files. "
      "Regenerate with <code>python experiments/build_atlas.py</code> (Python stdlib only; no network, no libraries). "
      "Colours are slots 1 to 7 of a palette validated for colour-vision deficiency; every colour is paired with its verdict word or a filled/hollow shape. "
      "Bar charts are direct-labelled with their values; no chart is drawn on a dual axis.</p></div></footer>"
      % (GENERATED, len(md)))
    w('<div id="tip" role="tooltip"></div>')
    w('<script type="application/json" id="atlas-data">%s</script>'
      % json.dumps([{k: r[k] for k in ("id", "name", "verdict", "headline")} for r in recs]).replace("</", "<\\/"))
    w("<script>%s</script></body></html>" % JS.replace("%VERD%", json.dumps(VERDICTS)).replace("%HOL%", json.dumps(sorted(HOLLOW))))

    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    print("wrote %s (%d bytes, %d experiments, %d reflections)" % (OUT, os.path.getsize(OUT), len(recs), len(md)))


if __name__ == "__main__":
    main()
