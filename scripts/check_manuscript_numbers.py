"""Compare manuscript values with values derived from committed experiment runs."""
import json
import math
import os
import subprocess
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
committed = os.path.join(ROOT, "results", "paper_values.json")
if not os.path.exists(committed):
    print("NOT RUN: results/paper_values.json absent")
    sys.exit(2)

with tempfile.TemporaryDirectory() as directory:
    generated = os.path.join(directory, "paper_values.json")
    subprocess.run(
        [sys.executable, os.path.join(ROOT, "scripts", "paper_values.py")],
        check=True, cwd=ROOT,
        env=dict(os.environ, PAPER_VALUES_OUT=generated),
        stdout=subprocess.DEVNULL,
    )
    with open(committed) as stream:
        expected = json.load(stream)
    with open(generated) as stream:
        actual = json.load(stream)

def equivalent(left, right):
    # JSON has one numeric domain; 75 and 75.0 represent the same value.
    if isinstance(left, bool) or isinstance(right, bool):
        return type(left) is type(right) and left == right
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return math.isfinite(left) and math.isfinite(right) and left == right
    if isinstance(left, dict) and isinstance(right, dict):
        return (left.keys() == right.keys()
                and all(equivalent(left[k], right[k]) for k in left))
    if isinstance(left, list) and isinstance(right, list):
        return len(left) == len(right) and all(
            equivalent(x, y) for x, y in zip(left, right)
        )
    return type(left) is type(right) and left == right

diff = sorted(
    key for key in set(expected) | set(actual)
    if key not in expected or key not in actual
    or not equivalent(expected[key], actual[key])
)
if diff:
    print(f"MISMATCH: {len(diff)} keys")
    for key in diff:
        print(f"  {key}: committed={expected.get(key)!r}; derived={actual.get(key)!r}")
    print("Committed sources:", json.dumps(expected.get("_sources"), sort_keys=True))
    print("Derived sources:  ", json.dumps(actual.get("_sources"), sort_keys=True))
    sys.exit(1)
print(f"{len(expected)} manuscript values reproduced from {len(expected['_sources'])} result runs")
