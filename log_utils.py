import os
import csv
from datetime import datetime

LOG_FILE = "signal_log_5min.csv"


def init_log_file():
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                "Timestamp", "Price", "RSI", "EMA_Fast", "EMA_Slow",
                "Signal", "MACD", "Signal_Line", "Volume"
            ])


def log_signal(price, rsi, ema_fast, ema_slow, signal, macd, signal_line, volume):
    with open(LOG_FILE, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            price, rsi, ema_fast, ema_slow,
            signal, macd, signal_line, volume
        ])
