# -*- coding: utf-8 -*-
"""
Created on Thu Sep  1 16:14:13 2022

@author: oadiguzel
"""

import pandas as pd
import datetime as dt
import yfinance as yf
from bs4 import BeautifulSoup
import requests
import traceback


def get_bist100_ticker():
    wl = {"components":"https://tr.wikipedia.org/wiki/Borsa_İstanbul"}
    page = requests.get(wl["components"])
    soup = BeautifulSoup(page.text, "html.parser")
    value = soup.find_all("table",class_="wikitable")
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

def get_info():
    tickers = get_bist100_ticker()
    if "CANTE.IS" in tickers:
        tickers.remove("CANTE.IS")
    if "ALKIM.IS" not in tickers:
        tickers.append("ALKIM.IS")
    if "XU100.IS" not in tickers:
        tickers.append("XU100.IS")
        
    all_ = {}
    for t in tickers:
        print(t)
        tic = yf.Ticker(t)
        # get stock info
        info = tic.info
        all_[t] = info
        
    info = pd.DataFrame().from_dict(all_, orient="index")
    info.index.name = "ticker"
    info = info.reset_index()
    return info

if __name__ == "__main__":
    hour = dt.datetime.today().hour
    #if (hour < 9) | (hour > 18):
    info = get_info()
    info.to_csv("C:/myml/powerbi/data/info.csv", index=False)
