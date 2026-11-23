def compare_static_vs_agentic(load_factor):
    # Deterministic adaptation: N increases only at specific thresholds
    n_fragments = 10 if load_factor < 0.5 else 20
    return n_fragments
