import talib
import numpy as np
import pandas as pd
from datetime import datetime, time
import pandas as pd
import plotly.graph_objects as go

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

def backtest_strategy(csv_file, short_periods, long_periods, atr_period):
    df = pd.read_csv(csv_file)
    close_prices = df['Close'].values
    high_prices = df['High'].values
    low_prices = df['Low'].values
    timestamps = df['Timestamp'].values

    short_emas, long_emas = calculate_GMMA(close_prices, short_periods, long_periods)
    atr = calculate_ATR(high_prices, low_prices, close_prices, atr_period)

    position = None
    stop_loss = None
    take_profit = None
    entry_price = None

    total_trades = 0
    winning_trades = 0
    losing_trades = 0
    breakeven_trades = 0
    pnl = []

    trade_entries = []
    trade_exits = []

    for i in range(len(close_prices)):
        if i < max(long_periods):
            continue

        timestamp = timestamps[i]
        if not is_within_trading_hours(timestamp):
            continue

        if all(short_emas[j][i] > long_emas[j][i] for j in range(len(short_emas))):
            if position is None or position < 0:
                print(f"Open long position at price {close_prices[i]}")
                position = 1
                entry_price = close_prices[i]
                stop_loss = entry_price - 3 * atr[i]
                take_profit = entry_price + atr[i] + 24
                trade_entries.append((timestamps[i], entry_price))

        elif all(short_emas[j][i] < long_emas[j][i] for j in range(len(short_emas))):
            if position is None or position > 0:
                print(f"Open short position at price {close_prices[i]}")
                position = -1
                entry_price = close_prices[i]
                stop_loss = entry_price + 3 * atr[i]
                take_profit = entry_price - (atr[i] + 25)
                trade_entries.append((timestamps[i], entry_price))

        # Update stop loss
        if position == 1:  # Long position
            new_stop_loss = max(stop_loss, close_prices[i] - 2 * atr[i])
        elif position == -1:  # Short position
            new_stop_loss = min(stop_loss, close_prices[i] + 2 * atr[i])

        if new_stop_loss != stop_loss:  # Check if stop loss got updated
            if position == 1 and close_prices[i] <= new_stop_loss:
                print(f"Break even trade at price {close_prices[i]}")
                position = None
                stop_loss = None
                take_profit = None
                breakeven_trades += 1
                pnl.append(0)
            elif position == -1 and close_prices[i] >= new_stop_loss:
                print(f"Break even trade at price {close_prices[i]}")
                position = None
                stop_loss = None
                take_profit = None
                breakeven_trades += 1
                pnl.append(0)
            stop_loss = new_stop_loss

        if position == 1 and close_prices[i] <= stop_loss:
            print(f"Stop loss hit for long position at price {close_prices[i]}")
            position = None
            stop_loss = None
            take_profit = None
            losing_trades += 1
            pnl.append(entry_price - close_prices[i])
            trade_exits.append((timestamps[i], close_prices[i]))
        elif position == -1 and close_prices[i] >= stop_loss:
            print(f"Stop loss hit for short position at price {close_prices[i]}")
            position = None
            stop_loss = None
            take_profit = None
            losing_trades += 1
            pnl.append(close_prices[i] - entry_price)
            trade_exits.append((timestamps[i], close_prices[i]))

        if position == 1 and close_prices[i] >= take_profit:
            print(f"Take profit hit for long position at price {close_prices[i]}")
            position = None
            stop_loss = None
            take_profit = None
            winning_trades += 1
            pnl.append(close_prices[i] - entry_price)
            trade_exits.append((timestamps[i], close_prices[i]))
        elif position == -1 and close_prices[i] <= take_profit:
            print(f"Take profit hit for short position at price {close_prices[i]}")
            position = None
            stop_loss = None
            take_profit = None
            winning_trades += 1
            pnl.append(entry_price - close_prices[i])
            trade_exits.append((timestamps[i], close_prices[i]))

    pnl = np.array(pnl)  # Convert pnl list to numpy array

    total_trades = winning_trades + losing_trades + breakeven_trades
    average_pnl = np.mean(pnl) if pnl.size > 0 else 0
    win_rate = winning_trades / total_trades * 100 if total_trades > 0 else 0
    risk_to_reward_ratio = abs(np.mean(pnl[pnl > 0]) / np.mean(pnl[pnl < 0])) if pnl.size > 0 else 0

    print(f"Total Trades: {total_trades}")
    print(f"Winning Trades: {winning_trades}")
    print(f"Losing Trades: {losing_trades}")
    print(f"Breakeven Trades: {breakeven_trades}")
    print(f"Average P/L per trade: {average_pnl}")
    print(f"Win Rate: {win_rate}%")
    print(f"Risk-to-Reward Ratio: {risk_to_reward_ratio}")

    # ...

    # Plotting the chart
    fig = go.Figure(data=[go.Candlestick(x=timestamps,
                                         open=df['Open'],
                                         high=df['High'],
                                         low=df['Low'],
                                         close=close_prices,
                                         name='BTC/USDT')])

    fig.add_trace(go.Scatter(x=[entry[0] for entry in trade_entries],
                             y=[entry[1] for entry in trade_entries],
                             mode='markers',
                             marker=dict(color='green', symbol='triangle-up'),
                             name='Entry'))

    fig.add_trace(go.Scatter(x=[exit[0] for exit in trade_exits],
                             y=[exit[1] for exit in trade_exits],
                             mode='markers',
                             marker=dict(color='red', symbol='triangle-down'),
                             name='Exit'))

    fig.update_layout(title='BTC/USDT Trades',
                      xaxis_title='Timestamp',
                      yaxis_title='Price')

    # Save the chart as an HTML file
    fig.write_html('trades_chart.html')

    


csv_file = '/Users/cem/Desktop/btcltf20212022.csv'
short_periods = [2, 7, 11, 13, 21, 14]
long_periods = [29, 31, 37, 47, 53, 61]
atr_period = 14

backtest_strategy(csv_file, short_periods, long_periods, atr_period)
