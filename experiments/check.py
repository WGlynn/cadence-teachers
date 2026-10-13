"""Every experiment needs experiments/EXP-XX.md with a filled Summary and Reflection (Will 2026-10-10).
Pre-registration is encouraged: write Question / Setup / Prediction BEFORE running and mark Result, Verdict and
Reflection "PENDING"; a pending write-up passes (it is listed, not failed) so a running experiment does not break CI.
Run: python experiments/check.py   -> exit 1 and a list if any EXP is missing or incomplete."""
import os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ids = sorted({m.group(1) for f in os.listdir(os.path.join(ROOT, "exp"))
              if (m := re.match(r"(EXP-\d+[a-z]?)_.*\.py$", f))}, key=lambda s: (int(re.findall(r"\d+", s)[0]), s))
bad = []
for i in ids:
    p = os.path.join(ROOT, "experiments", f"{i}.md")
    if not os.path.exists(p):
        bad.append(f"{i}: missing"); continue
    t = open(p, encoding="utf-8").read()
    for sec in ("## Summary", "## Reflection"):
        if sec not in t:
            bad.append(f"{i}: no {sec}")
    if re.search(r"<one-line name>|YYYY-MM-DD|<EXP|<file>", t):
        bad.append(f"{i}: template placeholders left")
pending = [i for i in ids if os.path.exists(os.path.join(ROOT, "experiments", f"{i}.md"))
           and "PENDING" in open(os.path.join(ROOT, "experiments", f"{i}.md"), encoding="utf-8").read()]

# ---- Coherence gate (Will 2026-10-13): derived facts must agree with the data they derive from.
import json
atlas = json.load(open(os.path.join(ROOT, "experiments", "atlas.json"), encoding="utf-8"))
in_atlas = {x["id"] for x in atlas}
done = [i for i in ids if os.path.exists(os.path.join(ROOT, "experiments", f"{i}.md")) and i not in pending
        and not any(b.startswith(i + ":") for b in bad)]
for i in done:
    if i not in in_atlas and not re.fullmatch(r"EXP-0?[1-7]", i):
        bad.append(f"{i}: finished write-up has no atlas.json entry")
sys.path.insert(0, os.path.join(ROOT, "experiments"))
from build_atlas import readme_counts_sentence  # noqa: E402
want = readme_counts_sentence(atlas)
readme = open(os.path.join(ROOT, "README.md"), encoding="utf-8").read()
m = re.search(r"<!-- counts:start -->(.*?)<!-- counts:end -->", readme, re.S)
if not m or m.group(1).strip() != want:
    bad.append(f"README counts out of date: run python experiments/build_atlas.py (want: {want})")
for dp, _, fns in os.walk(os.path.join(ROOT, "site", "src")):
    for fn in fns:
        if fn.endswith((".jsx", ".js")) and fn != "atlas.json":
            t = open(os.path.join(dp, fn), encoding="utf-8").read()
            if re.search(r"(Thirty|Forty|Fifty|Sixty)[- ]?\w*\s+(runs|experiments)", t):
                bad.append(f"site/src/{fn}: a typed experiment count; derive it from the data")

print(f"{len(ids)} experiments, {len(ids) - len({b.split(':')[0] for b in bad}) - len(pending)} complete"
      + (f", {len(pending)} pre-registered / running: {', '.join(pending)}" if pending else ""))
for b in bad:
    print("  " + b)
sys.exit(1 if bad else 0)
