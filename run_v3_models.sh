#!/bin/bash
set -e

BASE="paper_results/2026"
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

confirm_save() {
  echo
  read -p "Save this dataset to CSV/PNG? (y/n): " ans
  if [ "$ans" != "y" ]; then
    echo -e "${RED}DISCARDED — Not saved${NC}"
    return 1
  fi
  return 0
}

mkdir -p "$BASE/v3.0-locked"
mkdir -p "$BASE/v3.0-agentic"

echo "=============================================="
echo "  v3 MODEL PIPELINE — DETERMINISTIC ONLY"
echo "=============================================="

############################
# v3.0-LOCKED — EXPOSURE
############################
echo
echo "=============================="
echo "v3.0-LOCKED — EXPOSURE MODEL"
echo "Invariant: leakage = 0"
echo "=============================="
echo "fragments,leakage"

for i in {1..10}; do
  echo "$i,0"
done

if confirm_save; then
  python3 << PY
import csv, matplotlib.pyplot as plt

base = "$BASE/v3.0-locked"

with open(f"{base}/exposure.csv","w",newline="") as f:
    w = csv.writer(f)
    w.writerow(["fragments","leakage"])
    for i in range(1,11):
        w.writerow([i,0])

x = list(range(1,11))
y = [0]*10

plt.figure(figsize=(6,4))
plt.plot(x,y,"o-")
plt.title("v3.0-locked — Leakage Invariant")
plt.xlabel("Intercepted Fragments")
plt.ylabel("Leakage Metric")
plt.ylim(-0.1,1)
plt.grid(True)
plt.savefig(f"{base}/exposure.png")
PY
fi

############################
# v3.0-LOCKED — EMISSION
############################
echo
echo "=============================="
echo "v3.0-LOCKED — TRAFFIC MODEL"
echo "Invariant: constant emission"
echo "=============================="
echo "time,rate"

for i in {0..9}; do
  echo "$i,100"
done

if confirm_save; then
  python3 << PY
import csv, matplotlib.pyplot as plt

base = "$BASE/v3.0-locked"

with open(f"{base}/emission.csv","w",newline="") as f:
    w = csv.writer(f)
    w.writerow(["time","rate"])
    for i in range(10):
        w.writerow([i,100])

x = list(range(10))
y = [100]*10

plt.figure(figsize=(6,4))
plt.step(x,y,where="post")
plt.title("v3.0-locked — Indistinguishable Traffic")
plt.xlabel("Time Index")
plt.ylabel("Packets/sec")
plt.ylim(0,150)
plt.grid(True)
plt.savefig(f"{base}/emission.png")
PY
fi

############################
# v3.0-AGENTIC — ADAPTATION
############################
echo
echo "=============================="
echo "v3.0-AGENTIC — ADAPTIVE MODEL"
echo "Deterministic Rule:"
echo "If threat_time >= 5 → N=16, dummy_ratio=0.30, latency=7"
echo "Else → N=10, dummy_ratio=0.10, latency=5"
echo "=============================="
echo "time,N,dummy_ratio,latency_ms"

for t in {0..9}; do
  if [ "$t" -lt 5 ]; then
    echo "$t,10,0.10,5"
  else
    echo "$t,16,0.30,7"
  fi
done

if confirm_save; then
  python3 << PY
import csv, matplotlib.pyplot as plt

base = "$BASE/v3.0-agentic"
import os
os.makedirs(base, exist_ok=True)

rows = []
for t in range(10):
    if t < 5:
        rows.append([t,10,0.10,5])
    else:
        rows.append([t,16,0.30,7])

with open(f"{base}/adaptation.csv","w",newline="") as f:
    w = csv.writer(f)
    w.writerow(["time","N","dummy_ratio","latency_ms"])
    w.writerows(rows)

t = [r[0] for r in rows]
lat = [r[3] for r in rows]

plt.figure(figsize=(6,4))
plt.plot(t,lat,"o-")
plt.title("v3.0-agentic — Latency Under Adaptation")
plt.xlabel("Time Index")
plt.ylabel("Latency (ms)")
plt.grid(True)
plt.savefig(f"{base}/adaptation.png")
PY
fi

echo
echo -e "${GREEN}v3 MODELS COMPLETE${NC}"
