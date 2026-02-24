# v2.0 Binary Reconstruction Rule
validity_window = 0.005 # 5ms window

def evaluate_reconstruction(packets_received, total_expected):
    # Binary Result: Must have all fragments to succeed
    reconstruction_result = 1 if packets_received == total_expected else 0
    return reconstruction_result

def generate_v2_csv(packet_loss, n_fragments):
    # Deterministic piecewise definition
    success = 1 if packet_loss == 0 else 0
    return [packet_loss, n_fragments, success]
