import talib
import numpy as np


def calculate_GMMA(close_prices, short_periods, long_periods):
    short_emas = [talib.EMA(close_prices, timeperiod=period) for period in short_periods]
    long_emas = [talib.EMA(close_prices, timeperiod=period) for period in long_periods]
    return short_emas, long_emas


def calculate_ATR(high_prices, low_prices, close_prices, atr_period):
    atr = talib.ATR(high_prices, low_prices, close_prices, timeperiod=atr_period)
    return atr


# Custom price data for backtesting
close_prices = np.array([100, 102, 105, 101, 98, 105, 110, 108, 112, 115, 110, 105])
high_prices = np.array([105, 108, 110, 105, 102, 110, 115, 112, 116, 118, 112, 108])
low_prices = np.array([95, 98, 100, 96, 94, 100, 105, 102, 106, 110, 105, 100])

short_periods = [2, 7, 11, 13, 21, 14]
long_periods = [29, 31, 37, 47, 53, 61]

short_emas, long_emas = calculate_GMMA(close_prices, short_periods, long_periods)

atr = calculate_ATR(high_prices, low_prices, close_prices, atr_period=14)

position = None
stop_loss = None

for i in range(len(close_prices)):
    if i < max(long_periods):
        continue

    # long position
    if short_emas[0][i] > long_emas[0][i] and short_emas[1][i] > long_emas[1][i] and short_emas[2][i] > long_emas[2][i]:
        if position is None or position < 0:
            print(f"Open long position at price {close_prices[i]}")
            position = 1
            stop_loss = close_prices[i] - 2 * atr[i]

    # short position
    elif short_emas[0][i] < long_emas[0][i] and short_emas[1][i] < long_emas[1][i] and short_emas[2][i] < long_emas[2][i]:
        if position is None or position > 0:
            print(f"Open short position at price {close_prices[i]}")
            position = -1
            stop_loss = close_prices[i] + 2 * atr[i]

    # update stoploss
    if position == 1:  # long position
        stop_loss = max(stop_loss, close_prices[i] - 2 * atr[i])
    elif position == -1:  # short position
        stop_loss = min(stop_loss, close_prices[i] + 2 * atr[i])

    # to check for sl
    if position == 1 and close_prices[i] <= stop_loss:
        print(f"Stop loss hit for long position at price {close_prices[i]}")
        position = None
        stop_loss = None
    elif position == -1 and close_prices[i] >= stop_loss:
        print(f"Stop loss hit for short position at price {close_prices[i]}")
        position = None
        stop_loss = None
