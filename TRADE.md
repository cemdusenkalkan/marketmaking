# README

## Binance Futures GMMA and ATR Based Trading Bot

This repository contains Python scripts for a simple trading bot based on the Binance Futures API, using Guppy Multiple Moving Average (GMMA) and Average True Range (ATR) technical indicators for trade decisions. The bot retrieves market data, processes the data to generate trading signals, and executes trades according to these signals.

The bot primarily uses Binance Python SDK and TA-Lib for technical analysis.

### Dependencies:

The bot uses the following Python packages:

- `binance-client`: Binance Python SDK, used to interact with Binance Futures API
- `talib`: Technical Analysis Library, used to calculate technical indicators
- `numpy`: Used for array and numerical operations
- `pandas`: Used for data manipulation and analysis
- `datetime`: Used for timestamp conversion and trading time range check

### Setup:

Before you run the script, please make sure you have the necessary Python packages installed. If not, you can install them with pip:

```bash
pip install python-binance pandas numpy talib
```

### How to Run:

First, you need to obtain your Binance Futures API Key and Secret Key from your Binance account. Replace the placeholders in the following lines in the code with your actual keys:

```python
api_key = 'y'
api_secret = 'x'
```

After that, you can run the script with a Python interpreter. For example, if you're using Python 3:

```bash
python3 script.py
```

### Algorithm Explanation:

The script first fetches the latest minute candlestick data for the BTCUSDT pair and calculates the GMMA and ATR indicators.

GMMA is used to identify the trend and market sentiment. When short-term EMA group is above the long-term EMA group, it's a bullish signal, and vice versa.

ATR is used to calculate the stop loss and take profit levels, which are 2 times and 7 times the ATR value from the entry price respectively.

If the current time is within the defined trading hours (2 PM UTC to 10 PM UTC), and there's no active trade, the bot will check the GMMA condition and place a BUY/SELL order based on the trend. If there's an active trade, it checks if the price hits the stop loss or take profit level, and if it does, it will close the position.

### Note:

This bot is meant for educational purposes only and is not intended to provide financial advice. Always do your own research and consider the risks before running the bot in a live environment.

