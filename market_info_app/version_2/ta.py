import talib
import numpy as np

data = np.genfromtxt('btc_day.csv', delimiter=',')

close = data[:,4]

rsi = talib.RSI(close)
print(rsi)