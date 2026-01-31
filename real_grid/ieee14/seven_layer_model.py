import time
from key_manager import GridKeyManager
from pmu_fusion import consensus
from rocof import rocof
from gps_guard import gps_valid
from pressure_feedback import update_pressure
from agc_guard import agc_valid
from trust_model import role_allows
from islanding import islanded

class SevenLayer:
    def __init__(self):
        self.keys = GridKeyManager(120)
        self.prev = {}

    def eval(self, packet, grid_meas, grid_time):
        L = {}

        # L1 Identity
        L[1] = self.keys.valid(packet["node"])

        # L2 Structure
        L[2] = packet["size"] <= 256

        # L3 Crypto
        L[3] = self.keys.verify(
            self.keys.keys[packet["node"]][0],
            packet["payload"],
            packet["sig"]
        )

        # L4 Timing
        if packet["role"] == "PMU":
            L[4] = gps_valid(packet["ts"], grid_time)
        else:
            L[4] = abs(packet["ts"] - grid_time) <= 2.0

        # L5 Pressure
        L[5] = packet["pressure"] < 5.0

        # L6 Physics
        meas = grid_meas[packet["node"]]
        consensus_ok = consensus(grid_meas.values())
        rocof_ok = rocof(self.prev.get(packet["node"]), meas, 0.02)
        phys_ok = consensus_ok and rocof_ok
        L[6] = phys_ok

        # Islanding
        is_islanded = islanded(consensus_ok, rocof_ok)

        # L7 Authorization
        L[7] = role_allows(packet)

        # L7b Control (AGC)
        if packet.get("msg_type") == "CONTROL":
            L["7b"] = agc_valid(
                packet["command"],
                {"stable": not is_islanded}
            )
        else:
            L["7b"] = True

        # Feedback loop
        packet["pressure"] = update_pressure(packet["pressure"], phys_ok)

        self.prev[packet["node"]] = meas

        decision = all(v for v in L.values() if isinstance(v, bool))
        return decision, L
