import asyncio
import websockets
import json
import os
from dotenv import load_dotenv
from collections import deque
from indicators import calculate_rsi, calculate_ema
from log_utils import init_log_file, log_signal
from telegram_utils import send_telegram_alert

load_dotenv()

price_history = deque(maxlen=100)
ASSET = os.getenv("DERIV_ASSET", "R_75")

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

            if len(price_history) >= 50:
                rsi = calculate_rsi(price_history, 14)
                ema9 = calculate_ema(price_history, 9)
                ema21 = calculate_ema(price_history, 21)

                signal = "HOLD"
                if rsi is not None:
                    if rsi < 30 and ema9 > ema21:
                        signal = "BUY"
                        send_telegram_alert(f"📈 BUY | Price: {price:.2f} | RSI: {rsi:.2f}")
                    elif rsi > 70 and ema9 < ema21:
                        signal = "SELL"
                        send_telegram_alert(f"📉 SELL | Price: {price:.2f} | RSI: {rsi:.2f}")

                print(f"Price: {price:.2f} | RSI: {rsi:.2f} | EMA9: {ema9:.2f} | EMA21: {ema21:.2f} | Signal: {signal}")
                log_signal(price, rsi, ema9, ema21, signal)

asyncio.run(deriv_price_stream())
