Aegis-Grid: Evolutionary Research Repository
Aegis-Grid is a comprehensive research framework dealing with Agentic Security for Cyber-Physical Systems (CPS). It explores how autonomous digital agents can protect critical infrastructure (like power grids) from high-sophistication attacks (Quantum Adversaries, Infinite Compute, Physical Compromise).

This repository contains the complete evolutionary history of the project, from initial Python prototypes to the final Bash-based auditing tools and future quantum concepts.

📂 Repository Structure & Version Guide
The codebase is organized by evolutionary stage. Choose the version that matches your research intent:

🟢 The "Core" (Stable & Published)
Use these versions for reproducing paper results or understanding the core theory.

v3.0-final (The Paper Artifact)

Focus: Agentic Elastic Defense
Tech: Bash / Awk / Gnuplot (No External Dependencies)
Description: This is the pure simulation core used for the published results. It is designed for maximum transparency and auditability. It treats security as a control loop (Pressure vs. Mitigation costs) rather than just cryptography.
Key Files: 
experiments/simulate_attack_fog_of_war.sh
, agents/secure_agent.sh
v3.0-agentic (The Implementation)

Focus: Python Integration
Tech: Python 3.9+
Description: The "Productized" version of v3.0 logic. Ideally used if you want to inspect how these agents would be written in a standard object-oriented language.

🟡 Early Prototypes (Historical)
Useful for seeing how the cryptographic stack evolved.

v1.0.0

Focus: Basic 7-Layer Stack
Description: The original proof-of-concept. Implements a static cryptographic stack with simple decision rules.
v2.0

Focus: Cryptographic Stealth
Description: Introduced "Indistinguishable Dummies" and traffic analysis resistance.
🔴 Experimental & Future (Active Research)
These versions are volatile, conceptual, or focused on specific sub-domains.

v4.0-cyberphysical

Focus: Hardware & Physics
Description: Moves beyond network packets to model the actual physics of the grid. Contains control-room and substation models.

v5-concept

Focus: Post-Cryptography / Information Theoretic
Description: A "Sci-Fi" exploration of security against an adversary with infinite compute. Abandoning encryption in favor of "Time-Bounded Secrecy" (data that self-destructs or becomes irrelevant before it can be cracked).
🚀 Quick Start (Reproduction)
To run the standard "Fog of War" simulation (v3.0):

cd v3.0-final/experiments
chmod +x simulate_attack_fog_of_war.sh
./simulate_attack_fog_of_war.sh
This will generate attack_data.dat which models how the agent adapts its security threshold in response to entropy noise and simulated packet loss.

🤝 Citation & Usage
Primary Author: Burhan Abdullah
License: Proprietary / Research Use Only (See 
LICENSE
 in specific folders
