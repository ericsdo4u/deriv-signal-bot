# main.py (multi-timeframe support: 5m + 1m)
import asyncio
import json
import os
import time
from collections import deque
from dotenv import load_dotenv
import websockets
import aiohttp

from indicators import calculate_rsi, calculate_ema, calculate_macd
from log_utils import init_log_file, log_signal
from telegram_utils import send_telegram_alert

load_dotenv()

ASSET = os.getenv("ASSET", "R_75")
RSI_PERIOD = int(os.getenv("RSI_PERIOD", 14))
EMA_FAST = int(os.getenv("EMA_FAST", 9))
EMA_SLOW = int(os.getenv("EMA_SLOW", 21))
MACD_FAST = int(os.getenv("MACD_FAST", 12))
MACD_SLOW = int(os.getenv("MACD_SLOW", 26))
MACD_SIGNAL = int(os.getenv("MACD_SIGNAL", 9))
RSI_JUMP_THRESHOLD = float(os.getenv("RSI_JUMP_THRESHOLD", 5))
COOLDOWN_SECONDS = int(os.getenv("COOLDOWN", 180))
CANDLE_COUNT = int(os.getenv("CANDLE_COUNT", 30))

price_history_5m = deque(maxlen=100)
price_history_1m = deque(maxlen=100)
last_alert_time = 0

async def fetch_candle_data(interval_seconds):
    url = "https://api.deriv.com/api/v1/ohlc"
    params = {
        "ticks_history": ASSET,
        "style": "candles",
        "granularity": interval_seconds,
        "count": CANDLE_COUNT
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            data = await resp.json()
            if "candles" in data:
                candles = data["candles"]
                prices = [c["close"] for c in candles if "close" in c]
                volumes = [c["volume"] for c in candles if "volume" in c]
                return prices, volumes[-1], sum(volumes) / len(volumes)
    return [], 0, 0

async def deriv_price_stream():
    uri = "wss://ws.deriv.com/websockets/v3"
    async with websockets.connect(uri) as ws:
        await ws.send(json.dumps({"ticks": ASSET, "subscribe": 1}))
        print(f"✅ Subscribed to {ASSET} live stream")

        init_log_file()
        last_rsi = 50

        while True:
            msg = await ws.recv()
            data = json.loads(msg)

            if "tick" not in data:
                continue

            price = float(data["tick"]["quote"])
            price_history_5m.append(price)

            if len(price_history_5m) >= max(RSI_PERIOD, EMA_SLOW, MACD_SLOW):
                prices_5m, volume_5m, avg_vol_5m = await fetch_candle_data(300)
                prices_1m, volume_1m, avg_vol_1m = await fetch_candle_data(60)

                price_history_1m.clear()
                price_history_1m.extend(prices_1m)

                rsi_5m = calculate_rsi(prices_5m, RSI_PERIOD)
                rsi_1m = calculate_rsi(prices_1m, RSI_PERIOD)
                ema_fast = calculate_ema(prices_5m, EMA_FAST)
                ema_slow = calculate_ema(prices_5m, EMA_SLOW)
                macd, signal_line = calculate_macd(prices_5m, MACD_FAST, MACD_SLOW, MACD_SIGNAL)

                rsi_jump = abs(rsi_5m - last_rsi)
                last_rsi = rsi_5m

                strong_volume = volume_5m > avg_vol_5m
                macd_cross = macd is not None and signal_line is not None and abs(macd - signal_line) < 0.5 and (macd > signal_line)
                cooldown_ok = time.time() - last_alert_time > COOLDOWN_SECONDS

                signal = "HOLD"
                should_alert = False
                alert_text = None

                if rsi_5m < 30 and ema_fast > ema_slow and rsi_jump >= RSI_JUMP_THRESHOLD and strong_volume and macd_cross and rsi_1m > rsi_5m:
                    signal = "BUY"
                    should_alert = True
                    alert_text = f"📈 BUY | {ASSET} | Price: {price:.2f} | RSI(5m): {rsi_5m:.2f} | RSI↑: {rsi_jump:.2f}% | Vol↑ | MACD✔ | RSI(1m): {rsi_1m:.2f}"
                elif rsi_5m > 70 and ema_fast < ema_slow and rsi_jump >= RSI_JUMP_THRESHOLD and strong_volume and not macd_cross and rsi_1m < rsi_5m:
                    signal = "SELL"
                    should_alert = True
                    alert_text = f"📉 SELL | {ASSET} | Price: {price:.2f} | RSI(5m): {rsi_5m:.2f} | RSI↓: {rsi_jump:.2f}% | Vol↑ | MACD✘ | RSI(1m): {rsi_1m:.2f}"

                print(f"Price: {price:.2f} | RSI(5m): {rsi_5m:.2f} | RSI(1m): {rsi_1m:.2f} | Jump: {rsi_jump:.2f} | EMA{EMA_FAST}: {ema_fast:.2f} | EMA{EMA_SLOW}: {ema_slow:.2f} | MACD: {macd:.2f if macd else 0} | Signal: {signal}")

                if should_alert and cooldown_ok:
                    global last_alert_time
                    send_telegram_alert(alert_text)
                    last_alert_time = time.time()

                log_signal(price, rsi_5m, ema_fast, ema_slow, signal, macd, signal_line, volume_5m)

if __name__ == "__main__":
    asyncio.run(deriv_price_stream())
