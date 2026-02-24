def process_signal(status):
    # Binary control semantics: No degraded state
    control_action = 'execute' if status else 'drop'
    return control_action
