# -*- coding: utf-8 -*-
"""
Created on Wed Aug 31 16:28:22 2022

@author: oadiguzel
"""


import pandas as pd
import numpy as np
import yfinance as yf
import datetime as dt
from bs4 import BeautifulSoup
import requests

def get_bist100_ticker():
    wl = {"components":"https://tr.wikipedia.org/wiki/Borsa_İstanbul"}
    page = requests.get(wl["components"])
    print(page)
    soup = BeautifulSoup(page.text, "html.parser")
    value = soup.find_all("table",class_="wikitable")
    print(value)
    text = value[0].text
    list_ = []
    for i in text.split("\n\n"):
        list_.append(i)
    list_ = list_[2:]
    t_list = []
    temp = []
    for i in list_:
        if len(temp)==6:
            t_list.append(temp)
            temp = []
            temp.append(i)
        else:
            temp.append(i)
    col = ["ticker","name","sector","sub_sector","city","founding"]
    components = pd.DataFrame(t_list[1:], columns=col)
    a = components["ticker"].str.split("\n",expand=True)
    return (a[1] + ".IS").to_list()

def get_returns(tickers):
    dic = {}
    for ticker in tickers:
        df = yf.download(
                           tickers = ticker,
                           period = "3mo",
                           interval = "1d"
                         )
        if len(df) > 0:
            df = df.resample("W").last()
        
            ret = df["Adj Close"].pct_change().fillna(0)
            if df.index.max() > pd.to_datetime(dt.datetime.today().date()):
                ret = ret.iloc[:-1]
            ret_ind = 100
            for i in ret.values:
                ret_ind = ret_ind * (i + 1)
            ret_val = ret_ind / 100 - 1
            print(ticker, "=", ret_val*4)
            dic[ticker] = ret_val*4
    return dic

if (__name__ == "__main__") | (__name__ != "__main__"):

    tickers    = get_bist100_ticker()
    pd.Series(tickers).to_csv("C:/myml/powerbi/tickers.csv",index=False)
    dic        = get_returns(tickers)
    df = pd.DataFrame.from_dict(dic, orient="index", columns=["returns"])
    df.index.name = "ticker"
    df.to_csv("price_momentum.csv")
