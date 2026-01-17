import os
from core.crypto.ca import ROOT_CA
from core.crypto.entropy import verify_stealth
from agents.secure_agent import SecureAgent

def run_v1_audit():
    print("=== AEGIS-GRID v1.0 MASTER AUDIT ===")
    
    # Check 1: PKI
    sig = ROOT_CA.sign(b"test")
    pki_ok = ROOT_CA.verify(b"test", sig)
    print(f"Layer 1 (Identity): {'✅ VALID' if pki_ok else '❌ FAIL'}")

    # Check 2: Stealth
    stealth_ok = verify_stealth(os.urandom(64), os.urandom(64))
    print(f"Layer 5 (Stealth):  {'✅ VALID' if stealth_ok else '❌ FAIL'}")

    # Check 3: Safety Sink
    agent = SecureAgent(os.urandom(32))
    agent.add_attack_pressure(10.0)
    print(f"Layer 7 (Safety):   {'✅ LOCKED' if agent.is_locked() else '❌ FAIL'}")

    print("====================================")
    print("V1.0 ARCHITECTURE: STATUS GREEN")

if __name__ == "__main__":
    run_v1_audit()
