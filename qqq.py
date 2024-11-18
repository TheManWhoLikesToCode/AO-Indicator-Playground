import yfinance as yf
import pandas as pd
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import matplotlib.pyplot as plt

# Parameters
ticker = 'QQQ'
start_date = '2000-01-01'
end_date = '2023-01-01'  # Adjust as needed
ao_fast = 5
ao_slow = 34
cash = 10000
commission = 0.002  # 0.2%

# Define the Awesome Oscillator calculation function
def calculate_ao(data, fast_period, slow_period):
    median_price = (data['High'] + data['Low']) / 2
    fast_sma = median_price.rolling(window=fast_period).mean()
    slow_sma = median_price.rolling(window=slow_period).mean()
    ao = fast_sma - slow_sma
    return ao

# Define the trading strategy using the AO indicator
class AO_Strategy(Strategy):
    fast_period = ao_fast
    slow_period = ao_slow

    def init(self):
        # Calculate AO and store it
        self.ao = self.I(calculate_ao, self.data.df, self.fast_period, self.slow_period)

    def next(self):
        # Entry condition: AO crosses above zero
        if crossover(self.ao, 0):
            self.buy()
        # Exit condition: AO crosses below zero
        elif crossover(0, self.ao):
            self.position.close()

# Download historical data for QQQ
data = yf.download(ticker, start=start_date, end=end_date)
data.index.name = 'Date'
data = data[['Open', 'High', 'Low', 'Close', 'Volume']]

# Run the backtest
bt = Backtest(data, AO_Strategy, cash=cash, commission=commission)
stats = bt.run()
print(stats)
bt.plot()

# Visualize the most recent AO to assess current momentum
# Note: yfinance data may have a delay and might not be real-time
latest_data = yf.download(ticker, period='6mo', interval='1d')
latest_data.index.name = 'Date'
latest_data = latest_data[['High', 'Low']]

# Calculate the AO for the latest data
latest_data['AO'] = calculate_ao(latest_data, ao_fast, ao_slow)

# Plot the AO indicator
plt.figure(figsize=(12, 6))
plt.plot(latest_data.index, latest_data['AO'], label='Awesome Oscillator')
plt.axhline(0, color='red', linestyle='--', label='Zero Line')
plt.title('Awesome Oscillator for QQQ - Last 6 Months')
plt.xlabel('Date')
plt.ylabel('AO Value')
plt.legend()
plt.show()
