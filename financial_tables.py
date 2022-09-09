# -*- coding: utf-8 -*-
"""
Created on Wed Sep  7 14:19:46 2022

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

def get_financials_annual():
    tickers = get_bist100_ticker()
    if "CANTE.IS" in tickers:
        tickers.remove("CANTE.IS")
    if "ALKIM.IS" not in tickers:
        tickers.append("ALKIM.IS")
    df = pd.DataFrame()
    for ticker in tickers:
        print(ticker)
        try:
            df2 = pd.DataFrame()
            obj = yf.Ticker(ticker)
            tables = [obj.financials, obj.balancesheet, obj.cashflow]
            for t in tables:
                t.index.name   = "name"
                t.columns.name = "date"
                t = t.unstack().to_frame(name="value")
                t["ticker"]    = ticker
                t = t.reset_index().set_index(["date","ticker"])
                if len(df2) == 0:
                    df2 = t
                else:
                    df2 = df2.append(t)
            df2 = df2.reset_index().set_index(["name","date","ticker"])
            df2 = df2[~df2.index.duplicated(keep='first')]
            df2 = df2.unstack(0)["value"]
            print(f"{ticker} downloads --------------- DONE!")
        except Exception as e:
            print(f"ERROR on the ticker: {ticker}")
            print(traceback.print_exc())
        if len(df) == 0:
            df = df2
        else:
            df = df.append(df2)
    return df


if __name__ == "__main__":
   # if dt.date.today().weekday() == 0:
    financials = get_financials_annual().reset_index()
    financials.to_csv("C:/myml/powerbi/data/financials.csv", index=False)