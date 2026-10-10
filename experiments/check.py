"""Every experiment needs experiments/EXP-XX.md with a filled Summary and Reflection (Will 2026-10-10).
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
print(f"{len(ids)} experiments, {len(ids) - len({b.split(':')[0] for b in bad})} complete")
for b in bad:
    print("  " + b)
sys.exit(1 if bad else 0)
