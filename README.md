Aegis-Grid — v3.0 (Agentic Elastic Defense)

Aegis-Grid is a bash-first, agent-controlled security simulation framework.
It models security as a dynamic control system rather than a static protocol.

This version focuses on agentic decision-making under uncertainty, cost-aware
defense, and adversarial stress testing.

------------------------------------------------------------
Overview
------------------------------------------------------------

Aegis-Grid treats security like a control loop:

observe system signals
decide adaptively
apply mitigation
pay operational cost
fail safely when limits are exceeded

The system is fully deterministic, auditable, and implemented in bash to keep
all logic transparent.

------------------------------------------------------------
Core Signals
------------------------------------------------------------

attack pressure
  cumulative packet loss over time

entropy / noise
  signal degradation and uncertainty, including spoofed noise

adaptive threshold
  thresholds shift based on history, not fixed constants

elastic mitigation
  defense strength scales instead of switching on/off

computational cost
  mitigation consumes resources and introduces overhead

fail-secure
  irreversible lockdown when safety margins are exceeded

------------------------------------------------------------
What Changed in v3.0
------------------------------------------------------------

agentic elastic mitigation
  defense effort scales with observed risk

false-positive resistance
  jitter and near-trigger tests where agent must not react

fog-of-war adversary
  decoy entropy spikes without real loss

ramp-up (boil-the-frog) attacks
  slow attack intensity increase to evade naive thresholds

cost-aware decision logic
  mitigation increases computational cost

fail-secure boundary discovery
  hard safety cutoff under sustained attack

sensitivity sweeps
  automatic exploration of attack intensity vs survivability

------------------------------------------------------------
Experiments Implemented
------------------------------------------------------------

baseline attack simulation
agent-controlled mitigation
stress tests with entropy noise
jitter and near-trigger false positives
fog-of-war spoofing
computational cost accounting
fail-secure triggering
sensitivity matrix sweep

------------------------------------------------------------
Repository Structure
------------------------------------------------------------

experiments/
  simulate_attack.sh
  simulate_attack_with_agent.sh
  simulate_attack_agent_stress.sh
  sensitivity_sweep.sh

results/
  attack_data.dat
  attack_agent_data.dat
  attack_agent_stress.dat
  sensitivity_matrix.csv

.novelty_state/
  baseline.txt
  current.txt
  counts.csv

VERSION

------------------------------------------------------------
How to Run
------------------------------------------------------------

cd experiments
chmod +x *.sh
./simulate_attack.sh
./simulate_attack_with_agent.sh
./simulate_attack_agent_stress.sh
./sensitivity_sweep.sh

Results are written to the results directory.

------------------------------------------------------------
Design Philosophy
------------------------------------------------------------

security is treated as a system property, not a configuration
agents reason over history, cost, and uncertainty
defense is elastic, not binary
false positives are as dangerous as missed attacks
fail-safe behavior is mandatory

Aegis-Grid is designed for research, teaching, and systems thinking where
interpretability and control matter more than opaque automation.

------------------------------------------------------------
Status
------------------------------------------------------------

bash-only core
no external dependencies
fully auditable logic
deterministic experiments
research-grade prototype

Version: v3.0-agentic-elastic-defense

------------------------------------------------------------
