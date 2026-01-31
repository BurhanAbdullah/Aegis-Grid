def role_allows(packet):
    role = packet["role"]
    msg_type = packet["msg_type"]

    if msg_type == "MEASUREMENT" and role == "PMU":
        return True

    if msg_type == "CONTROL" and role == "SCADA":
        return True

    return False
