import pandas as pd
import backtrader as bt
import matplotlib.pyplot as plt

file_path = '/Users/daiwangtao/Documents/Data/TL5Minutes.xlsx'
raw = pd.read_excel(file_path)
raw['datetime'] = pd.to_datetime(raw['datetime'])

#use TL2403 as training data
train_data = raw[raw['contract'] == 'TL2403']
train_data = train_data.set_index('datetime')
train_data.drop(columns=['contract'], inplace=True)

train_data = train_data.resample('15min').agg({
    'open': 'first',
    'high': 'max',
    'low': 'min',
    'close': 'last',
    'volume': 'sum'})

train_data['returns'] = train_data['close'].pct_change(fill_method=None)
train_data.dropna(inplace=True)

# Filter data between September 2023 and February 2024
start_date = pd.Timestamp('2023-09-01')
end_date = pd.Timestamp('2024-02-29')
train_data = train_data[(train_data.index >= start_date) 
                        & (train_data.index <= end_date)]

class KDJStrategy(bt.Strategy):
    params = (
        ('k_period', 14),
        ('d_period', 3),
    )

    def __init__(self):
        # Calculate KDJ indicators
        self.k = bt.indicators.StochasticFull(
            self.data,
            period=self.p.k_period,
            period_dfast=self.p.d_period
        )

    def next(self):
        if self.k.percK[-1] < 20 and self.k.percK[0] > 20:
            self.buy()
        elif self.k.percK[-1] > 80 and self.k.percK[0] < 80:
            self.sell()

# Prepare data for Backtrader
def prepare_backtest(train_data):
    # Convert index to datetime
    train_data = train_data.copy()
    train_data.index = pd.to_datetime(train_data.index)
    
    # Create Backtrader data feed
    data = bt.feeds.PandasData(
        dataname=train_data,
        datetime=None,  # Index is already datetime
        open='open',
        high='high',
        low='low',
        close='close',
        volume='volume',
        openinterest=-1
    )
    
    # Initialize Backtrader cerebro
    cerebro = bt.Cerebro()
    cerebro.adddata(data)
    cerebro.addstrategy(KDJStrategy)
    
    # Set initial cash and commission
    cerebro.broker.setcash(100000.0)
    cerebro.broker.setcommission(commission=0.000003)
    
    return cerebro

# Run backtest
cerebro = prepare_backtest(train_data)
initial_value = cerebro.broker.getvalue()
results = cerebro.run()
final_value = cerebro.broker.getvalue()
cerebro.plot(style='candlestick', iplot=False)

print(f'Initial Portfolio Value: {initial_value:,.2f}')
print(f'Final Portfolio Value: {final_value:,.2f}')
print(f'Return: {((final_value - initial_value) / initial_value * 100):.2f}%')
