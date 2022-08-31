# -*- coding: utf-8 -*-
"""
Created on Fri Aug 26 21:37:11 2022

@author: oadiguzel
"""

# The following code to create a dataframe and remove duplicated rows is always executed and acts as a preamble for your script: 

# dataset = pandas.DataFrame(Open, High, Low, Close, Date, Volume, Ticker)
# dataset = dataset.drop_duplicates()

# Paste or type your script code here:

import matplotlib.pyplot as plt
import pandas as pd
import talib as ta
import numpy as np
from scipy import stats

    
dataset["rsi"] = ta.RSI(dataset.Close, 14)
slowk, slowd  = ta.STOCH(dataset.High, dataset.Low, dataset.Close)
slowk = slowk.dropna()[(np.abs(stats.zscore(slowk.dropna())) < 3)]
slowd = slowd.dropna()[(np.abs(stats.zscore(slowd.dropna())) < 3)]
dataset["slowk"], dataset["slowd"] = slowk, slowd
    
atr   = ta.ATR(dataset.High, dataset.Low, dataset.Close)
ema   = ta.EMA(dataset.Close, 20)
upper = ema + 2*atr
lower = ema - 2*atr
dataset["Middle"] = ema
dataset["Upper"]  = upper
dataset["Lower"]  = lower



fig = plt.figure(figsize=(24, 36))
fig.subplots_adjust(hspace=0.2, wspace=0.2, bottom=.02, left=.06,
                    right=.97, top=.94)

ax = fig.add_subplot(211)
ax.set_title("Keltner")
ax.plot(dataset.Date, dataset["bist100_usd"], "black", lw=2, label="Price")
ax.plot(dataset.Date, dataset["Middle"], "cyan", lw=1, label="Middle")
ax.plot(dataset.Date, dataset["Upper"], "blue", lw=1, label="Upper")
ax.plot(dataset.Date, dataset["Lower"], "blue", lw=1, label="Lower")
ax.fill_between(dataset.Date, dataset["Upper"], dataset["Lower"], facecolor='blue', alpha=0.1)
ax.legend(loc=2)

ax = fig.add_subplot(413)
ax.set_title("RSI")
ax.plot(dataset.Date, dataset["rsi"], "cyan", lw=1, label="RSI")
ax.axhline(y=70, color="black")
ax.axhline(y=30, color="black")
ax.legend(loc=2)
        
ax = fig.add_subplot(414)
ax.set_title("Stoch")
ax.plot(dataset.Date, dataset["slowk"], "green", lw=1, label="Slowk")
ax.plot(dataset.Date, dataset["slowd"], "red", lw=1, label="Slowd")
ax.legend(loc=2)
        
    
plt.show()