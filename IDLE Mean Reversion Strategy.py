import yfinance as yf
import pandas as pd
import numpy as np

# PARAMETERS
symbol = "AAPL"           # replace with your ticker
start = "2018-01-01"
end = "2024-12-31"
lookback = 20             # rolling window for mean/std
entry_z = 2.0             # enter when z-score > entry_z or < -entry_z
exit_z = 0.5              # exit when z-score reverts below this
position_size = 1.0       # fraction of capital per trade (simple)

# 1) load price
df = yf.download(symbol, start=start, end=end, progress=False)
df = df[['Adj Close']].rename(columns={'Adj Close':'price'})

# 2) choose series for mean reversion: here use log price differences (or price - rolling mean)
df['logp'] = np.log(df['price'])
df['rolling_mean'] = df['logp'].rolling(lookback).mean()
df['rolling_std']  = df['logp'].rolling(lookback).std()
df['z'] = (df['logp'] - df['rolling_mean']) / df['rolling_std']

# 3) signals
df['long']  = (df['z'] < -entry_z).astype(int)
df['short'] = (df['z'] >  entry_z).astype(int)

# simple position logic: hold until z crosses exit threshold
position = 0
positions = []
for z_long, z_short, z in zip(df['long'], df['short'], df['z']):
    # enter long
    if position == 0 and z_long:
        position = 1
    # enter short
    elif position == 0 and z_short:
        position = -1
    # exit long
    elif position == 1 and abs(z) < exit_z:
        position = 0
    # exit short
    elif position == -1 and abs(z) < exit_z:
        position = 0
    positions.append(position)
df['position'] = positions

# 4) compute P&L (returns)
df['returns'] = df['price'].pct_change().fillna(0)
df['strategy_ret'] = df['position'].shift(1) * df['returns']    # assume daily rebalancing, no costs

# 5) equity curve
initial_capital = 100000
df['strategy_eq'] = initial_capital * (1 + df['strategy_ret']).cumprod()
df['buy_and_hold'] = initial_capital * (1 + df['returns']).cumprod()

# 6) performance summary
total_ret = df['strategy_eq'].iloc[-1] / initial_capital - 1
ann_ret = (1 + total_ret) ** (252 / len(df.dropna())) - 1   # crude annualization
sharpe = (df['strategy_ret'].mean() / df['strategy_ret'].std()) * np.sqrt(252)

print("Total return:", total_ret)
print("Approx annual return:", ann_ret)
print("Sharpe (ann):", sharpe)
