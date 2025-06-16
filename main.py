# main.py
import asyncio
import json
import os
from collections import deque
from dotenv import load_dotenv
import websockets

from indicators import calculate_rsi, calculate_ema
from log_utils import init_log_file, log_signal
from telegram_utils import send_telegram_alert

load_dotenv()

ASSET = os.getenv("ASSET", "R_75")
RSI_PERIOD = int(os.getenv("RSI_PERIOD", 14))
EMA_FAST = int(os.getenv("EMA_FAST", 9))
EMA_SLOW = int(os.getenv("EMA_SLOW", 21))
price_history = deque(maxlen=100)

async def deriv_price_stream():
    uri = "wss://ws.deriv.com/websockets/v3"
    async with websockets.connect(uri) as ws:
        await ws.send(json.dumps({ "ticks": ASSET, "subscribe": 1 }))
        print(f"✅ Subscribed to {ASSET} live stream")

        init_log_file()

        while True:
            msg = await ws.recv()
            data = json.loads(msg)

            if "tick" not in data:
                continue

            price = float(data["tick"]["quote"])
            price_history.append(price)

            if len(price_history) >= max(RSI_PERIOD, EMA_SLOW):
                rsi = calculate_rsi(price_history, RSI_PERIOD)
                ema_fast = calculate_ema(price_history, EMA_FAST)
                ema_slow = calculate_ema(price_history, EMA_SLOW)

                signal = "HOLD"
                if rsi < 30 and ema_fast > ema_slow:
                    signal = "BUY"
                    send_telegram_alert(f"📈 BUY | {ASSET} | Price: {price:.2f} | RSI: {rsi:.2f}")
                elif rsi > 70 and ema_fast < ema_slow:
                    signal = "SELL"
                    send_telegram_alert(f"📉 SELL | {ASSET} | Price: {price:.2f} | RSI: {rsi:.2f}")

                print(f"Price: {price:.2f} | RSI: {rsi:.2f} | EMA{EMA_FAST}: {ema_fast:.2f} | EMA{EMA_SLOW}: {ema_slow:.2f} | Signal: {signal}")
                log_signal(price, rsi, ema_fast, ema_slow, signal)

if __name__ == "__main__":
    asyncio.run(deriv_price_stream())
