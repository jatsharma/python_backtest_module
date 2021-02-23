# Import required Libraries
import pandas as pd
import os
import pandas as pd
import numpy as np
import talib as tl
import backtesting as bt
from backtesting import Backtest, Strategy

# Get required files
from os import walk

f = []
for (dirpath, dirnames, filenames) in walk('../5min1/'):
    f.extend(filenames)
    break
    
files = [ fi for fi in f if fi.endswith(".csv") ]

class twel_breakout(Strategy):
    """Buy if first 5 min vwap candle close above vwap and sell if closes below vwap"""
    multiplier_sl = 1
    multiplier_tp = 1

    def init(self):
        self.atr = self.I(tl.ATR, high=self.data.High, low=self.data.Low, close=self.data.Close, timeperiod=14)

    def next(self):
        if self.data.Close.size > 12:
            if self.data.index[-1].hour == 11 and self.data.index[-1].minute == 45:
                global pm_price
                pm_price = self.data.Close[-1]
                global am_price
                am_price = self.data.Open[-33]
                global day_type
                day_type = "buy" if am_price < pm_price else "sell"
                global date

        if not self.position:
            if date != self.data.index[-1].day:
                if 15 > self.data.index[-1].hour >= 12:

                    sell_sl = self.data.Close[-1] + (self.atr[-1] * self.multiplier_sl)
                    sell_tp = self.data.Close[-1] - (self.atr[-1] * self.multiplier_tp)

                    buy_sl = self.data.Close[-1] - (self.atr[-1] * self.multiplier_sl)
                    buy_tp = self.data.Close[-1] + (self.atr[-1] * self.multiplier_tp)

                    # Define buy rules
                    if day_type == "buy":
                        if self.data.Close[-1] > pm_price:
                            date = self.data.index[-1].day
                            self.buy(sl=buy_sl, tp=buy_tp)
                        elif self.data.Close[-1] < am_price:
                            date = self.data.index[-1].day
                            self.sell(sl=sell_sl, tp=sell_tp)

                    elif day_type == "sell":
                        if self.data.Close[-1] < pm_price:
                            date = self.data.index[-1].day
                            self.sell(sl=(sell_sl), tp=(sell_tp))
                        elif self.data.Close[-1] > am_price:
                            date = self.data.index[-1].day
                            self.buy(sl=buy_sl, tp=buy_tp)

        elif self.data.index[-1].hour ==15 and self.data.index[-1].minute == 15:
            # Close any open position at 3:15 pm.
            self.position.close()

for i in range(len(files)):
	# Loop through each file to get backtest results.
    if os.path.exists(files[i][:-4]):
        continue
    data = pd.read_csv('../5min1/' + +files[i])
    data['timestamp'] = pd.to_datetime(data['timestamp'])
    data.set_index('timestamp', inplace=True)
    data = data.groupby(data.index.date, group_keys=False).apply(vwap)
    
    data = data.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close'})

    pm_price = 0
    am_price = 0
    day_type = ""
    date = ""

    bt = Backtest(data, twel_breakout, margin=0.2, cash = 60000, exclusive_orders=True)

    try:
        stats = bt.optimize(multiplier_sl = range(1,10),
                    multiplier_tp = range(1,10),
                   maximize = 'Equity Final [$]')
    except:
        continue

    os.mkdir(files[i][:-4])
    
    stats._trades.to_csv(files[i][:-4]+'/trades_'+files[i])
    stats.to_csv(files[i][:-4]+'/stats_'+files[i])
    print(i)
    print(files[i][:-4])