"""Check that results/paper_values.json is exactly what the committed result
directories produce. On failure, print each differing key and both values so
provenance drift can be diagnosed from CI logs."""
import json
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
        check=True,
        cwd=ROOT,
        env=dict(os.environ, PAPER_VALUES_OUT=generated),
        stdout=subprocess.DEVNULL,
    )
    with open(committed) as stream:
        expected = json.load(stream)
    with open(generated) as stream:
        actual = json.load(stream)

diff = sorted(
    key for key in set(expected) | set(actual)
    if json.dumps(expected.get(key), sort_keys=True)
    != json.dumps(actual.get(key), sort_keys=True)
)
if diff:
    print(f"MISMATCH: {len(diff)} keys")
    for key in diff:
        print(
            f"  {key}: committed={expected.get(key)!r}; "
            f"derived={actual.get(key)!r}"
        )
    print("Committed sources:", json.dumps(expected.get("_sources"), sort_keys=True))
    print("Derived sources:  ", json.dumps(actual.get("_sources"), sort_keys=True))
    sys.exit(1)

print(
    f"{len(expected)} manuscript values reproduced from "
    f"{len(expected['_sources'])} result runs"
)
