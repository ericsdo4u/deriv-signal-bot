import os
import csv
from datetime import datetime

LOG_FILE = "signal_log.csv"

def init_log_file():
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Timestamp", "Price", "RSI", "EMA9", "EMA21", "Signal"])

def log_signal(price, rsi, ema9, ema21, signal):
    with open(LOG_FILE, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            price,
            rsi,
            ema9,
            ema21,
            signal
        ])
