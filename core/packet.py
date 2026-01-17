class Packet:
    def __init__(self, msg_id, frag_id, total_frags, payload, is_dummy=False, signature=None):
        self.msg_id = msg_id
        self.frag_id = frag_id
        self.total_frags = total_frags
        self.payload = payload
        self.is_dummy = is_dummy
        self.signature = signature

    def signable(self):
        if self.is_dummy:
            return self.msg_id + b"DUMMY"
        return self.msg_id + self.frag_id.to_bytes(4, "big") + self.payload

    @staticmethod
    def create(msg_id, frag_id, total_frags, payload, is_dummy=False, signature=None):
        return Packet(msg_id, frag_id, total_frags, payload, is_dummy, signature)
