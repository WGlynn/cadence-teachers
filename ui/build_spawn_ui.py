"""Build a self-contained $SPAWN simulation viewer from exp/EXP-32.json -> ui/spawn-sim.html."""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
data = json.load(open(os.path.join(HERE, "..", "exp", "EXP-32.json")))
runs = [dict(label=f"{r['arm']} seed {r['seed']}", arm=r["arm"], acc=r["acc"], brain_acc=r["brain_acc"],
             events=r["events"], slices=r["slices"], paid=r["paid"], gain=r["gain"]) for r in data]
html = open(os.path.join(HERE, "spawn-sim.template.html"), encoding="utf-8").read()
out = os.path.join(HERE, "spawn-sim.html")
open(out, "w", encoding="utf-8").write(html.replace("/*DATA*/null", json.dumps(runs)))
print("wrote", out, len(runs), "runs")
