#!/bin/bash

# --- 1. USER CREDENTIALS ---
APP_ID="G7F1FWV6NH-100"
SECRET_ID="K1BXM9A1BA"
CLIENT_ID="XB06976"
# This script will assume you have a 'token.txt' file in the directory.
# If not, it will prompt you once.

# --- 2. THE QUANTUM ENGINE (PYTHON) ---
cat << 'PY_EOF' > genie_engine.py
import time, datetime, socket, statistics, os, sys
from fyers_apiv3 import fyersModel

# Load Token
try:
    with open("token.txt", "r") as f: TOKEN = f.read().strip()
except:
    print("❌ Error: 'token.txt' not found. Create it first."); sys.exit()

fyers = fyersModel.FyersModel(client_id="$APP_ID", token=TOKEN, is_async=False)

class QuantumHFT:
    def __init__(self):
        self.pcr_window = []
        self.state = {"bal": 0, "pnl": 0, "nifty": 0, "z": 0.0, "status": "SCANNING", "trades": 0}

    def get_data(self):
        # Math: PCR + Velocity
        oc = fyers.optionchain(data={"symbol": "NSE:NIFTY50-INDEX", "strikecount": 10})['data']
        pcr = oc['putOi'] / oc['callOi'] if oc['callOi'] > 0 else 1
        self.pcr_window.append(pcr)
        if len(self.pcr_window) > 30: self.pcr_window.pop(0)
        
        # Z-Score Calculation
        z = (pcr - statistics.mean(self.pcr_window)) / statistics.stdev(self.pcr_window) if len(self.pcr_window) > 1 else 0
        
        # Market Price
        lp = fyers.quotes({"symbols": "NSE:NIFTY50-INDEX"})['d'][0]['v']
        funds = fyers.funds()
        bal = next(i['amt'] for i in funds['fund_limit'] if i['title'] == 'Total Equity Balance')
        
        return z, lp['lp'], bal, pcr

    def blast(self, side):
        try:
            msg = f"GENIE,{side},NIFTY_ATM,MARKET,0,0,50,NSE,QUANTUM"
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(('127.0.0.1', 56789))
                s.sendall(msg.encode())
            self.state["trades"] += 1
        except: pass

    def run(self):
        while True:
            z, lp, bal, pcr = self.get_data()
            move = lp - 22500 # Assume daily baseline
            
            # THE INTERFACE
            print("\033[2J\033[H") # Clear
            print(f"\033[1;34m================================================================\033[0m")
            print(f"🧞 \033[1;36mQUANTUM GENIE HFT\033[0m | ID: $CLIENT_ID | BAL: \033[1;32m₹{bal}\033[0m")
            print(f"\033[1;34m================================================================\033[0m")
            print(f"NIFTY SPOT: {lp} | SENTIMENT Z-SCORE: \033[1;33m{z:+.2f} σ\033[0m")
            print(f"TRADES TODAY: {self.state['trades']} | PCR: {pcr:.2f}")
            print(f"\033[1;34m----------------------------------------------------------------\033[0m")
            
            # AUTO-TRADE
            if z > 2.0 and self.state["status"] == "SCANNING":
                self.blast("LE")
                self.state["status"] = "LONG_ACTIVE"
            elif z < -2.0 and self.state["status"] == "SCANNING":
                self.blast("SE")
                self.state["status"] = "SHORT_ACTIVE"

            time.sleep(1)

genie = QuantumHFT()
genie.run()
PY_EOF

# --- 3. EXECUTION ---
chmod +x genie_engine.py
python3 genie_engine.py
