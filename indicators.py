import numpy as np

def calculate_rsi(prices, period=14):
    prices = np.array(prices)
    deltas = np.diff(prices)
    seed = deltas[:period]
    up = seed[seed > 0].sum() / period
    down = -seed[seed < 0].sum() / period
    rs = up / down if down != 0 else 0
    rsi = 100 - (100 / (1 + rs))

    for i in range(period, len(prices)):
        delta = deltas[i - 1]
        upval = max(delta, 0)
        downval = -min(delta, 0)
        up = (up * (period - 1) + upval) / period
        down = (down * (period - 1) + downval) / period
        rs = up / down if down != 0 else 0
        rsi = 100 - (100 / (1 + rs))

    return round(rsi, 2)

def calculate_ema(prices, period=9):
    prices = np.array(prices)
    if len(prices) < period:
        return None
    weights = np.exp(np.linspace(-1., 0., period))
    weights /= weights.sum()
    a = np.convolve(prices, weights, mode='valid')
    return round(a[-1], 2)

def calculate_macd(prices, fast=12, slow=26, signal=9):
    if len(prices) < slow:
        return None, None

    prices = np.array(prices)
    ema_fast = np.convolve(prices, np.exp(np.linspace(-1., 0., fast)) / sum(np.exp(np.linspace(-1., 0., fast))), mode='valid')
    ema_slow = np.convolve(prices, np.exp(np.linspace(-1., 0., slow)) / sum(np.exp(np.linspace(-1., 0., slow))), mode='valid')

    if len(ema_fast) < len(ema_slow):
        ema_fast = ema_fast[-len(ema_slow):]
    elif len(ema_slow) < len(ema_fast):
        ema_slow = ema_slow[-len(ema_fast):]

    macd_line = ema_fast - ema_slow
    signal_line = np.convolve(macd_line, np.ones(signal) / signal, mode='valid')
    
    if len(signal_line) == 0:
        return None, None

    return round(macd_line[-1], 2), round(signal_line[-1], 2)
