def islanded(consensus_ok, rocof_ok):
    """
    Islanding if PMUs disagree OR frequency changes too fast
    """
    return not (consensus_ok and rocof_ok)
