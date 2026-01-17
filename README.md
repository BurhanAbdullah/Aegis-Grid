# 🛡️ Aegis-Grid  
### Agentic, Attack-Resilient Communication for Critical Infrastructure

> **Status:** Research Prototype  
> **Audience:** Researchers, security engineers, infrastructure operators  
> **License:** Restricted (contact author before reuse)

---

## ⚠️ IMPORTANT NOTICE

This repository implements **active defense mechanisms** for critical infrastructure communication.

**Do NOT:**
- Deploy in production without review
- Copy or reuse code without contacting the author
- Treat this as a cryptographic library

📩 **Contact required before use or citation:**  
**Author:** Burhan Abdullah  
**Email / GitHub:** Contact via GitHub profile  

---

## 📌 Overview

**Aegis-Grid** is a research framework for **secure, adaptive, and irreversible-safe communication** in adversarial environments such as:

- Power grids
- Industrial control systems (ICS)
- Emergency command networks
- Military / disaster-response coordination

Unlike traditional systems, Aegis-Grid assumes:
- Persistent packet loss
- Active DDoS
- Traffic analysis
- Signature forgery
- Timing attacks

and **responds autonomously**.

---

## 🧠 Core Contributions (What’s Novel)

### ✅ Agentic Security Model
- Autonomous agent observes attack pressure
- Adapts thresholds dynamically
- Makes irreversible safety decisions

### ✅ Multilayer Encryption
- Key superposition
- Layered derivation per session
- Forward secrecy by design

### ✅ Dummy Traffic Indistinguishability
- Real and idle traffic are statistically identical
- KL divergence ≈ **0**
- Traffic analysis resistance

### ✅ Fragmentation with Adaptive Threshold
- Message split into fragments
- Reconstruction threshold adapts to attack severity
- Never drops below safety minimum

### ✅ Cryptographic Signatures
- Each fragment signed
- Forgery → **immediate irreversible lock**

### ✅ Time-Lock Irreversible Failure (Key Novelty)
- Sustained attack over time triggers permanent shutdown
- System does **not recover**
- Models real-world safety systems

---

## 🧪 Experiments Included

### 1️⃣ Latency vs Dummy Ratio
Measures overhead of obfuscation.

### 2️⃣ Fragment Loss Resilience
Evaluates reconstruction probability under packet loss.

### 3️⃣ Traffic Indistinguishability
KL divergence between idle and active traffic.

### 4️⃣ Adaptive Threshold under DDoS
Threshold shifts based on attack pressure.

### 5️⃣ Time-Based Irreversible Lock
System permanently disables under sustained attack.

---

## 📊 Example Output


cat << 'EOF' > agents/secure_agent.py
import math
import time

class SecureAgent:
    def __init__(self, master_key):
        self.master_key = master_key

        # Attack state
        self.attack_score = 0.0
        self.attack_start = None

        # Fragment parameters
        self.base_fragments = 12
        self.fragment_count = self.base_fragments
        self.threshold = self.base_fragments

        # Protocol state
        self.expected_real_fragments = 0
        self.last_nonce = None

        # Irreversible lock
        self.locked = False
        self.lock_reason = None

    def observe(self, loss_rate: float, now=None):
        if self.locked:
            return

        if now is None:
            now = time.time()

        if self.attack_start is None:
            self.attack_start = now

        # Accumulate pressure
        self.attack_score = min(1.0, self.attack_score + loss_rate)

        # === SIGMOID THRESHOLD ===
        k = 8.0
        x = self.attack_score
        sigmoid = 1.0 / (1.0 + math.exp(k * (x - 0.5)))

        min_threshold = int(0.6 * self.fragment_count)
        adaptive = int(self.fragment_count * sigmoid)
        self.threshold = max(min_threshold, adaptive)

        # === TIME-LOCK (PHASE 3 – NOT ENABLED) ===
        if now - self.attack_start > 5.0 and self.attack_score > 0.6:
            self.locked = True
            self.lock_reason = "TIME_LOCK_IRREVERSIBLE_FAILURE"

    def is_locked(self):
        return self.locked
