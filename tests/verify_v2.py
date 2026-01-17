import time
import os
from core.crypto.ca import ROOT_CA
from agents.secure_agent import SecureAgentV2

def run_v2_audit():
    print("\n=== AEGIS-GRID V2: POST-QUANTUM MASTER AUDIT ===")
    
    node_id = "SUBSTATION_PQ_01"
    cert = ROOT_CA.issue_node_certificate(node_id)
    pq_ok = ROOT_CA.verify_certificate(node_id, cert)
    print(f"Layer 1 (PQ-Identity):     {'✅ RESILIENT' if pq_ok else '❌ FAIL'}")

    agent = SecureAgentV2(os.urandom(32))
    valid_ts = time.time() - 0.5
    print(f"Layer 7 (Time-Freshness):  {'✅ VALID' if agent.is_time_valid(valid_ts) else '❌ FAIL'}")

    agent.add_attack_pressure(6.0)
    print(f"Layer 7 (Safety Sink):     {'✅ LOCKED' if agent.is_locked() else '❌ FAIL'}")
    print("================================================\n")

if __name__ == "__main__":
    run_v2_audit()
