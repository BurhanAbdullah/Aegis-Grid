#!/usr/bin/env bash
set +e

echo "[+] Cleaning and restructuring repository"

# -------------------------
# Core structure
# -------------------------
mkdir -p docs archive/legacy scripts

for v in v1 v2 v3 v4; do
    mkdir -p "$v/scripts" "$v/data" "$v/plots" "$v/logs"
done

# -------------------------
# Root README
# -------------------------
chmod u+w README.md 2>/dev/null

cat > README.md << 'EOR'
Aegis-Grid
==========

Aegis-Grid is a research framework for studying adaptive, agent-based
security mechanisms in cyber-physical power systems.

Each version represents a distinct modeling scope and threat surface.
Core logic is abstracted. Results and methodology are preserved.
EOR

# -------------------------
# Version READMEs
# -------------------------
cat > v1/README.md << 'EOR'
Aegis-Grid v1
Deterministic baseline without adaptive defense.
EOR

cat > v2/README.md << 'EOR'
Aegis-Grid v2
Adaptive agent-based defense without physical coupling.
EOR

cat > v3/README.md << 'EOR'
Aegis-Grid v3
Elastic, cost-aware defense with fail-secure boundaries.
EOR

cat > v4/README.md << 'EOR'
Aegis-Grid v4
Cyber-physical microgrid defense with control-room and substation models.
EOR

# -------------------------
# Archive legacy files
# -------------------------
for f in error_log.txt novelty_check.sh requirements.txt sensitivity_sweep_elastic.sh genie_pro.sh plot_fog_of_war.sh; do
    [ -f "$f" ] && mv "$f" archive/legacy/
done

# -------------------------
# Gitignore protection
# -------------------------
grep -q "protected logic" .gitignore 2>/dev/null || cat >> .gitignore << 'EOR'

# protected logic
core/
agents/
v2_model/
protected/
*.log
EOR

echo "[+] Done."
