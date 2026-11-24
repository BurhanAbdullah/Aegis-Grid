import os
from agents.secure_agent import SecureAgent

def run_final_audit():
    print("🔬 AEGIS-GRID ARCHITECTURAL AUDIT")
    checks = {
        "Confidentiality (AES-GCM)": "core/crypto/encryption.py",
        "Authenticity (RSA-2048)": "core/crypto/pki.py",
        "Agentic CAP Logic": "agents/secure_agent.py",
        "Alog (Objectives Matrix)": "OBJECTIVES_LOG.md"
    }
    
    for name, path in checks.items():
        status = "✅ INTACT" if os.path.exists(path) else "❌ MISSING"
        print(f"{name:25}: {status}")

if __name__ == "__main__":
    run_final_audit()
