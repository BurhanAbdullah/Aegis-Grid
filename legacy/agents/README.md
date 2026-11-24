# agents/

Autonomous security agents for Aegis-Grid v3+.

## Purpose

Each agent makes **local security decisions** without access to a global oracle.
Agents observe their local communication channel, evaluate incoming messages
against fail-secure criteria, and act independently.

## Agent Types

| Script | Role |
|--------|------|
| `freq_agent.sh` | Baseline frequency-monitoring agent |
| `freq_agent_A/B/C.sh` | Named agents for multi-agent coordination scenarios |
| `freq_agent_byzantine.sh` | Byzantine fault injection agent (adversarial testing) |

## Design Principle

Agents are intentionally **non-cooperative by default**.
Coordination is limited; disagreement between agents is treated as a signal,
not an error. See v3 README for the theoretical grounding.

## Usage

```bash
bash agents/freq_agent.sh        # single agent
bash agents/freq_agent_A.sh &    # multi-agent (run concurrently)
bash agents/freq_agent_B.sh &
bash agents/freq_agent_C.sh &
```

## Relationship to Versions

- Introduced in **v3** (agent-based autonomous security)
- Extended in **v3.3** (agents operate under physical deadline constraints)
- Grid-state-aware variant in **v4**
