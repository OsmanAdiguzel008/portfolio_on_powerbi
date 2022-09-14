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

dataset = pd.read_csv("C:\myml\powerbi\data\price_data.csv")

#'dataset' holds the input data for this script

df = pd.DataFrame()
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
    temp["ATR"]            = atr
    temp["Keltner_Middle"] = ema
    temp["Keltner_Upper"]  = upper
    temp["Keltner_Lower"]  = lower
    temp["PC_Upper"]       = temp.Close.rolling(20,1).max()
    temp["PC_Lower"]       = temp.Close.rolling(20,1).min()
    temp["PC_Middle"]      = (temp.PC_Upper + temp.PC_Lower) / 2
    
    temp["RSI"] = ta.RSI(temp.Close, 14)
    df = df.append(temp)

df.to_csv("C:\myml\powerbi\data\price_data.csv",index=False)