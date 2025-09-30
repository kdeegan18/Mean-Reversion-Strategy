# Mean-Reversion-Strategy
This is a program for the King's Quant Society Taster Session 
import numpy as np
import pandas as pd
import yfinance as yf

# -------------------------------
# Step 1: Load data from CSV
# -------------------------------
ticker = 'AAPL'
file_path = f'{ticker}.csv'  # make sure the CSV file exists
data = pd.read_csv(file_path)

# Ensure 'Date' is datetime
data['Date'] = pd.to_datetime(data['Date'])

# -------------------------------
# Step 2: Extract the last 20 days up to yesterday
# -------------------------------
end_date = pd.Timestamp('2025-09-22')
last_20_days = data[data['Date'] <= end_date].sort_values('Date').tail(20)
closing_prices_20 = last_20_days['Close'].values

# -------------------------------
# Step 3: Calculate mean and std
# -------------------------------
mean_price = np.mean(closing_prices_20)
std_price = np.std(closing_prices_20, ddof=1)  # sample std

# -------------------------------
# Step 4: Define today's price and bounds
# -------------------------------
today_price = data[data['Date'] == '2025-09-23']['Close'].values[0]
upper_bound = mean_price + 2 * std_price
lower_bound = mean_price - 2 * std_price

# -------------------------------
# Step 5: Generate trading signal
# -------------------------------
z_score = (today_price - mean_price) / std_price
signal = "Hold"
likelihood = 0.0

if today_price > upper_bound:
    signal = "Sell (price likely to drop)"
    likelihood = min((today_price - upper_bound) / std_price, 1)
elif today_price < lower_bound:
    signal = "Buy (price likely to rise)"
    likelihood = min((lower_bound - today_price) / std_price, 1)

# -------------------------------
# Step 6: Display results
# -------------------------------
print(f"Last 20 closing prices: {closing_prices_20}")
print(f"Mean price: {mean_price:.2f}")
print(f"Standard deviation: {std_price:.2f}")
print(f"Today's price: {today_price:.2f}")
print(f"Price bounds: [{lower_bound:.2f}, {upper_bound:.2f}]")
print(f"Trading signal: {signal}")
print(f"Likelihood (0 to 1 scale): {likelihood:.2f}")
