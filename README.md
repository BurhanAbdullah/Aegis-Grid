By Burhan 
# Agentic Secure Grid Communication

This repository provides a reference implementation for a time-bounded,
agent-mediated, post-quantum-resilient secure communication architecture
for intelligent power systems.

The framework integrates:
- Constant-entropy traffic shaping
- Multilayer packet fragmentation with dummy payloads
- Time-bounded correctness guarantees
- Adaptive agent-based security control
- Resilience to traffic analysis, packet loss, delay, and DDoS attacks

The implementation is aligned with the accompanying research paper and
is intended for reproducible simulation and artifact evaluation.

## Repository Structure
- core/: cryptographic abstraction, packet and timing primitives
- agents/: adaptive security agents
- network/: traffic shaping and adversarial models
- protocol/: sender and receiver pipelines
- simulation/: experiments and evaluation logic
- paper/: LaTeX source of the manuscript

## Running the Simulation

```bash
pip install -r requirements.txt
python main.py
# agentic-secure-grid-communication
