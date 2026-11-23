"""Check that results/paper_values.json (the only source of numbers in the
manuscript) is exactly what scripts/paper_values.py derives from the committed
result directories. Exit 1 on any difference."""
import json, os, subprocess, sys, tempfile
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
committed = os.path.join(ROOT, "results", "paper_values.json")
if not os.path.exists(committed):
    print("NOT RUN: results/paper_values.json absent"); sys.exit(2)
with tempfile.TemporaryDirectory() as d:
    out = os.path.join(d, "pv.json")
    subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "paper_values.py")], check=True, cwd=ROOT,
                   env=dict(os.environ, PAPER_VALUES_OUT=out), stdout=subprocess.DEVNULL)
    a, b = json.load(open(committed)), json.load(open(out))
diff = sorted(k for k in set(a) | set(b) if json.dumps(a.get(k)) != json.dumps(b.get(k)))
if diff:
    print("MISMATCH:", diff[:20]); sys.exit(1)
print(f"{len(a)} manuscript values reproduced from {len(a['_sources'])} result runs")
