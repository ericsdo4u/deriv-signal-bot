import os
import csv
from datetime import datetime

LOG_FILE = "signal_log.csv"

def log_signal(price, rsi, ema_fast, ema_slow, signal, macd, signal_line, volume):
    file_exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(["timestamp", "price", "rsi", "ema_fast", "ema_slow", "signal", "macd", "signal_line", "volume"])
        writer.writerow([
            datetime.utcnow().isoformat(),
            round(price, 4),
            round(rsi, 2),
            round(ema_fast, 2),
            round(ema_slow, 2),
            signal,
            round(macd, 4) if macd else "",
            round(signal_line, 4) if signal_line else "",
            round(volume, 2)
        ])

def read_last_logged_signal():
    if not os.path.exists(LOG_FILE):
        return None
    try:
        with open(LOG_FILE, "r") as csvfile:
            rows = list(csv.reader(csvfile))
            if len(rows) < 2:
                return None
            last_row = rows[-1]
            return last_row[5]  # signal column
    except Exception as e:
        print(f"⚠️ Error reading log file: {e}")
        return None
