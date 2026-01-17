from core.fragmentation import fragment_message

def generate_traffic(agent, message, dummy_ratio):
    return fragment_message(
        message,
        agent.fragment_count,
        dummy_ratio,
        agent.master_key
    )
