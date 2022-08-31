# -*- coding: utf-8 -*-
"""
Created on Mon Aug 29 10:26:09 2022

@author: oadiguzel
"""


import pandas as pd
import numpy as np
import yfinance as yf
import datetime as dt
from bs4 import BeautifulSoup
import requests
import sklearn.linear_model as skl_lm
import statsmodels.api as sm


def get_financials_annual(ticker):
    df = pd.DataFrame()
    obj = yf.Ticker(ticker)
    tables = [obj.financials, obj.balancesheet, obj.cashflow]
    for t in tables:
        t.index.name   = "name"
        t.columns.name = "date"
        t = t.unstack().to_frame(name="value")
        t["ticker"]    = ticker
        t = t.reset_index().set_index(["date","ticker"])
        if len(df) == 0:
            df = t
        else:
            df = df.append(t)
    df = df.reset_index().set_index(["name","date","ticker"])
    df = df[~df.index.duplicated(keep='first')]
    return df.unstack(0)["value"]
    

def get_financials_quarterly(ticker):
    df = pd.DataFrame()
    obj = yf.Ticker(ticker)
    tables = [obj.quarterly_financials, obj.quarterly_balancesheet, 
              obj.quarterly_cashflow]
    for t in tables:
        t.index.name   = "name"
        t.columns.name = "date"
        t = t.unstack().to_frame(name="value")
        t["ticker"]    = ticker
        t = t.reset_index().set_index(["date","ticker"])
        if len(df) == 0:
            df = t
        else:
            df = df.append(t)
    df = df.reset_index().set_index(["name","date","ticker"])
    df = df[~df.index.duplicated(keep='first')]
    return df.unstack(0)["value"]

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

def calculate_fundamental(fund, *args, **kwargs):
    global ret
    b_e  = fund["Total Assets"] - fund["Total Liab"]
    earn = (fund["Net Income"] - fund["Retained Earnings"]) / fund["Net Income"]
    roe  = fund["Net Income"] / fund["Total Stockholder Equity"]
    roa  = fund["Net Income"] /  fund["Total Assets"]
    ape  = ((fund["Total Revenue"] - fund["Cost Of Revenue"]
            )-(fund["Selling General Administrative"] + fund["Interest Expense"]
               )) / b_e
    cpa  = (fund["Total Cash From Operating Activities"] - fund["Ebit"]
            ) / annual["Total Assets"]
    gpa  = (fund["Total Revenue"] + fund["Cost Of Revenue"]) / fund["Net Income"]
    #npy  = (""" NO DATA FOR CALCULATION """) / annual["Net Income"]
    
    fundamentals = earn.to_frame(name="earn")
    fundamentals["roe"] = roa
    fundamentals["roa"] = roa
    fundamentals["ape"] = ape
    fundamentals["cpa"] = cpa
    fundamentals["gpa"] = gpa
    #fundamentals = fundamentals.shift(1) # the shift is need for forecast for return,
                                         # please disregard dates after this
    dates = fundamentals.reset_index().date.to_list()
    ret = price_ret(*args, **kwargs)
    ret = ret[ret.index.isin(dates)]
    fundamentals["ret"] = ret.to_list()
    return fundamentals

def price_ret(ticker, ret,  period="5y", interval="1mo"):
    df = yf.download(
                       tickers = ticker,
                       period = period,
                       interval = interval
                     )
    if (ret == "q") | (ret == "quarterly"):
        df = df.resample("3M").last().Close.pct_change().dropna()
    elif (ret == "a") | (ret == "annual"):
        df = df.resample("A").last().Close.pct_change().dropna()
    else:
        raise ValueError(f"Please enter correct value not like {ret}")
    pd.options.display.float_format = '{:,.2f}'.format
    return df.round(3)

def get_prediction(df, fund1):
    lm = skl_lm.LinearRegression()
    df = df.fillna(0).reset_index()
    fund1 = fund1.reset_index()
    for number,tic in enumerate(df.ticker.unique()):
        df.loc[df.ticker == tic, "ticker_num"] = number
        fund1.loc[fund1.ticker == tic, "ticker_num"] = number
    X_train = df[["ticker_num","earn","roe","roa","ape","cpa","gpa"]]
    X_test  = fund1.groupby("ticker_num").last().fillna(0).reset_index()
    index   = X_test.ticker
    X_test  = X_test[["ticker_num","earn","roe","roa","ape","cpa","gpa"]]
    X_test  = X_test.values.reshape((len(X_test.index),len(X_test.columns)))
    y_train = df["Y"].fillna(0)
    #y_test  = fundamentals1["ret"].iloc[-1:,].fillna(0)
    model = lm.fit(X_train, y_train)
    pred = model.predict(X_test)
    pred = pd.DataFrame(data=pred,index=index,columns=["pred"])
    results = sm.OLS(y_train,X_train).fit()
    print(results.summary())
    return pred, results
   
def get_last_step(tickers):
    df = pd.DataFrame()
    fund1 = pd.DataFrame()
    for ticker in tickers:
        print(ticker)
        #ticker     = "ADESE.IS"
        try:
            quarterly  = get_financials_quarterly(ticker)
            annual     = get_financials_annual(ticker)
            
            fundamentals1 = calculate_fundamental(quarterly,ticker,"q")
            fundamentals2 = calculate_fundamental(annual,ticker,"a")
            fund1 = fund1.append(fundamentals1)
            
            ret1 = fundamentals1["ret"].tail(2)
            ret2 = fundamentals2["ret"].tail(2)
            ret  = ret1.append(ret2)
            data = fundamentals1.iloc[-3:-1,:].append(fundamentals2.iloc[-3:-1,:])
            data["Y"] = ret.to_list()
            df = df.append(data)
        except Exception as e:
            print(f"ERROR on the ticker: {ticker}")
    return df,fund1


if __name__ == "__main__":
    
    tickers    = get_bist100_ticker()
 
    df, fund1    = get_last_step(tickers)
    pred, result = get_prediction(df,fund1)
    pred.to_csv("fundamental_momentum.csv")
    