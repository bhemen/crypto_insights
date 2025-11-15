import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

all_tokens = [
    "USDe",
    "USDC",
    "USDT"
]

all_dfs = {}
for symbol in all_tokens:
    df = pd.read_csv(f"data/{symbol}.csv" )
    df.columns = ['timestamp','price']
    df['date'] = df.timestamp.apply( lambda x: datetime.strptime(x, '%Y-%m-%d') )
    all_dfs[symbol] = df

variances = { symbol: df.price.var() for symbol, df in all_dfs.items() }
means = { symbol: df.price.mean() for symbol, df in all_dfs.items() }

#################################################

tokens = ["USDC"]
dfs = { symbol: all_dfs[symbol] for symbol in tokens }

plt.figure(figsize=(24, 6))  # Make plot wider

earliest_date = min( [ df['date'].min() for df in dfs.values() ] ).strftime('%Y-%m-%d')
latest_date = max( [ df['date'].max() for df in dfs.values() ] ).strftime('%Y-%m-%d')

events = {
    'SVB Collapse': pd.Timestamp('2023-03-10'),
    'Terra Collapse': pd.Timestamp('2022-05-09'),
    'FTX Collapse': pd.Timestamp('2022-11-08'),
    'Voyager Collapse': pd.Timestamp('2022-07-01'),
#    'Ethena Launch': pd.Timestamp('2023-11-14'),
#    '3AC Collapse': pd.Timestamp('2022-06-16'),
#    'Celsius Collapse': pd.Timestamp('2022-07-12'),
}

for symbol, df in dfs.items():
    plt.plot(df.date, df.price, label=f"{symbol} (mean: {means[symbol]:.6f}, var: {variances[symbol]:.2e})", linewidth=0.5)  # Thinner lines

for event, date in events.items():
    plt.axvline(date,linewidth=.5,linestyle='--',color='grey' )
    plt.text( date - pd.Timedelta(days=10), .98, event, rotation='vertical', color='grey')

plt.xticks(rotation=45, ha='right')
plt.title( f'Price data for {", ".join(tokens)} from {earliest_date} - {latest_date}')
plt.legend()
plt.savefig( f"figures/{'-'.join(tokens)}.png", dpi=1200)
plt.clf()

#################################################

tokens = all_tokens

dfs = { symbol: all_dfs[symbol] for symbol in tokens }
min_date = max([df['date'].min() for df in dfs.values()])  # Find the latest of all minimum dates
dfs = {symbol: df[df['date'] >= min_date] for symbol, df in dfs.items()}  # Truncate all dataframes

earliest_date = min([df['date'].min() for df in dfs.values()]).strftime('%Y-%m-%d')
latest_date = max([df['date'].max() for df in dfs.values()]).strftime('%Y-%m-%d')

for symbol, df in dfs.items():
    plt.plot(df.date, df.price, label=f"{symbol} (mean: {means[symbol]:.6f}, var: {variances[symbol]:.2e})", linewidth=0.5)  # Thinner lines

plt.xticks(rotation=45, ha='right')
plt.title( f'Price data for {", ".join(tokens)} from {earliest_date} - {latest_date}')
plt.legend()
plt.savefig( f"figures/{'-'.join(tokens)}.png", dpi=1200)
plt.clf()

#https://institutional.vanguard.com/investments/product-details/fund/0011
#https://www.nasdaq.com/market-activity/mutual-fund/vusxx/historical

nasdaq_df = pd.read_csv("data/NASDAQ-VUXX.csv")
