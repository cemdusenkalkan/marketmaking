import csv
from binance.client import Client

api_key = 'YOUR_API_KEY'
api_secret = 'YOUR_API_SECRET'
client = Client(api_key, api_secret)

symbol = 'ETHUSDT'
interval = Client.KLINE_INTERVAL_1DAY
start_str = '5 years ago UTC'

klines = client.get_historical_klines(symbol, interval, start_str)

data = []
for kline in klines:
    timestamp = kline[0]
    open_price = kline[1]
    high_price = kline[2]
    low_price = kline[3]
    close_price = kline[4]
    volume = kline[5]
    data.append([timestamp, open_price, high_price, low_price, close_price, volume])


csv_file = 'binance_historical_data.csv'


with open(csv_file, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])  # Write header
    writer.writerows(data)

print(f"Historical price data saved to: {csv_file}")
