import os
from agents.secure_agent import SecureAgent
from core.crypto.pki import generate_authority_keys, GridIdentity
from simulation.run_experiments import run_all
from protocol.sender import generate_traffic
from protocol.receiver import receive_and_reconstruct

if __name__ == "__main__":
    # Identity Handshake Phase
    priv, pub = generate_authority_keys()
    challenge = os.urandom(16)
    from Crypto.Hash import SHA256
    from Crypto.Signature import pkcs1_15
    sig = pkcs1_15.new(priv).sign(SHA256.new(challenge))
    
    print("=== Aegis-Grid: v1.3 Master Release (7-Layer) ===")
    if GridIdentity.verify_node(challenge, sig, pub):
        print("[AUTH] RSA-2048 Identity Verified via Grid Root.")
        master_key = os.urandom(32)
        agent = SecureAgent(master_key)
        run_all(agent, generate_traffic, receive_and_reconstruct)
