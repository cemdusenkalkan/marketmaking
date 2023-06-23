
from binance.client import Client
from binance.enums import *
import talib
import numpy as np
import pandas as pd
from datetime import datetime, time

api_key = 'y'
api_secret = 'x'

client = Client(api_key, api_secret)
client.API_URL = 'https://testnet.binancefuture.com/api'

def get_data():
    candles = client.futures_klines(symbol='BTCUSDT', interval=Client.KLINE_INTERVAL_1MINUTE)
    df = pd.DataFrame(candles, columns=['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time', 'Quote asset volume', 'Number of trades', 'Taker buy base asset volume', 'Taker buy quote asset volume', 'Ignore'])
    df = df.astype(float)
    return df

def calculate_GMMA(close_prices, short_periods, long_periods):
    short_emas = [talib.EMA(close_prices, timeperiod=period) for period in short_periods]
    long_emas = [talib.EMA(close_prices, timeperiod=period) for period in long_periods]
    return short_emas, long_emas

def calculate_ATR(high_prices, low_prices, close_prices, atr_period):
    atr = talib.ATR(high_prices, low_prices, close_prices, timeperiod=atr_period)
    return atr

def is_within_trading_hours(timestamp):
    utc_time = datetime.utcfromtimestamp(timestamp / 1000)
    trading_start = time(14, 0)  # 2 PM UTC
    trading_end = time(22, 0)  # 10 PM UTC
    trading_time = datetime.combine(utc_time.date(), trading_start)
    trading_start_timestamp = int(trading_time.timestamp() * 1000)
    trading_time = datetime.combine(utc_time.date(), trading_end)
    trading_end_timestamp = int(trading_time.timestamp() * 1000)
    return trading_start_timestamp <= timestamp <= trading_end_timestamp

def calculate_volume(risk, atr):
    return risk / atr

def execute_trade(symbol, side, quantity, stop_price, take_profit_price):
    try:
        order_params = {
            'symbol': symbol,
            'side': side,
            'type': ORDER_TYPE_LIMIT,
            'timeInForce': TIME_IN_FORCE_GTC,
            'quantity': quantity,
            'price': stop_price,
            'newOrderRespType': 'FULL',
            'stopPrice': stop_price,
            'takeProfitPrice': take_profit_price
        }
        response = client.futures_create_order(**order_params)
        print(response)
    except Exception as e:
        print(e)

def backtest_strategy(short_periods, long_periods, atr_period):
    df = get_data()
    close_prices = df['Close'].values
    high_prices = df['High'].values
    low_prices = df['Low'].values
    timestamps = df['Open time'].values

    short_emas, long_emas = calculate_GMMA(close_prices, short_periods, long_periods)
    atr = calculate_ATR(high_prices, low_prices, close_prices, atr_period)

    position = None
    stop_loss = None
    take_profit = None
    for i in range(len(df)):
        if not is_within_trading_hours(timestamps[i]):
            continue
        short_gmma = np.array([ema[i] for ema in short_emas])
        long_gmma = np.array([ema[i] for ema in long_emas])
        if position is None:
            if np.all(short_gmma > long_gmma):
                position = 'long'
                entry_price = close_prices[i]
                stop_loss = entry_price - 2 * atr[i]
                take_profit = entry_price + 7 * atr[i]
                volume = calculate_volume(0.1, atr[i])
                execute_trade('BTCUSDT', SIDE_BUY, volume, stop_loss, take_profit)
            elif np.all(short_gmma < long_gmma):
                position = 'short'
                entry_price = close_prices[i]
                stop_loss = entry_price + 2 * atr[i]
                take_profit = entry_price - 7 * atr[i]
                volume = calculate_volume(0.01, atr[i])
                execute_trade('BTCUSDT', SIDE_SELL, volume, stop_loss, take_profit)
        elif position == 'long' and close_prices[i] < stop_loss or close_prices[i] > take_profit:
            position = None
            execute_trade('BTCUSDT', SIDE_SELL, volume, close_prices[i], None)
        elif position == 'short' and close_prices[i] > stop_loss or close_prices[i] < take_profit:
            position = None
            execute_trade('BTCUSDT', SIDE_BUY, volume, close_prices[i], None)

backtest_strategy([2, 7, 11, 13, 14, 21], [29, 31, 37, 47, 53, 61], 14)
