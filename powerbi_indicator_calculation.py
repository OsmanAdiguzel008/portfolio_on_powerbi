# -*- coding: utf-8 -*-
"""
Created on Tue Sep  6 16:51:57 2022

@author: oadiguzel
"""

#'dataset' holds the input data for this script

import pandas as pd
import numpy as np
import talib as ta
from scipy import stats

columns = [ "Date","Ticker","RSI", 
            "Keltner_Upper", "Keltner_Lower", "Keltner_Middle", 
            "slowk", "slowd"]
df = pd.DataFrame()

# dataset comes from powerbi pricedata tables
for t in dataset.Ticker.unique():
    temp = dataset[dataset.Ticker == t]

    slowk, slowd  = ta.STOCH(temp.High, temp.Low, temp.Close)
    slowk = slowk.dropna()[(np.abs(stats.zscore(slowk.dropna())) < 3)]
    slowd = slowd.dropna()[(np.abs(stats.zscore(slowd.dropna())) < 3)]
    temp["slowk"], temp["slowd"] = slowk, slowd

    atr   = ta.ATR(temp.High, temp.Low, temp.Close)
    ema   = ta.EMA(dataset.Close, 20)
    upper = ema + 2*atr
    lower = ema - 2*atr
    temp["Keltner_Middle"] = ema
    temp["Keltner_Upper"]  = upper
    temp["Keltner_Lower"]  = lower
    
    temp["RSI"] = ta.RSI(temp.Close, 14)
    df = df.append(temp)

dateset = dataset.merge(df[columns], left_on=["Date","Ticker"], right_on=["Date","Ticker"])
