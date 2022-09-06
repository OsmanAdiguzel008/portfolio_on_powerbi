# -*- coding: utf-8 -*-
"""
Created on Sat Sep  3 00:01:39 2022

@author: oadiguzel
"""

import pandas as pd
import yfinance as yf
from bs4 import BeautifulSoup
import requests


def split_portfolios(fun,prc):
    all_frame = fun.merge(prc, left_index=True, right_index=True)
    
    per = [0, 0.2, 0.4, 0.6, 0.8, 1]
    queue = ["worst", "bad", "medium", "good", "perfect"]
    for p in range(5):
        min_ = all_frame.quantile(per[p]).T
        max_ = all_frame.quantile(per[p+1]).T
        all_frame.loc[(all_frame.pred >= min_.pred) & (all_frame.pred <= max_.pred), "fun_queue"] = queue[p]
        all_frame.loc[(all_frame.returns >= min_.returns) & (all_frame.returns <= max_.returns), "prc_queue"] = queue[p]


    df = pd.DataFrame()
    count = 1
    for funq in queue:
        for prcq in queue:
            temp = all_frame[(all_frame.fun_queue == funq) & (all_frame.prc_queue == prcq)]
            temp["port_num"] = count
            df = df.append(temp)
            count = count + 1
    return df

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

def historical_momentum():
    # the parts get historical price momentum for 3 months
    #tickers = pd.read_csv("tickers.csv")["0"].to_list() 
    tickers = get_bist100_ticker()
    t_s = ""
    for tic in tickers:
        t_s += f"{tic} "
    daily  = yf.download(t_s, period="1Y", interval="1d")
    weekly = daily.resample("W").last()
    wk_ret = weekly["Adj Close"].pct_change().fillna(0)
    past   = wk_ret.iloc[-25:-9]
    past_loop = wk_ret.iloc[-9:-1]
    momentum = pd.DataFrame()
    returns  = pd.DataFrame()
    for i in range(len(past_loop)):
        temp   =  past.iloc[i:].append(past_loop.iloc[:i+1])
        cumret = (1 + temp).cumprod() - 1
        column = cumret.index.max()
        momentum[column] = cumret.iloc[-1]
        returns[column] = temp.iloc[-1]
    return momentum, returns

def historical_return(fund, hist, returns):
    df = pd.DataFrame()
    for col in range(len(hist.columns)-1):
        prc  = hist.iloc[:,col].to_frame(name="returns")
        port = split_portfolios(fund, prc)
        ret  = returns.iloc[:,col+1].to_frame(name="n_ret") #ret olarak momentum kullanmisim onu normal hist olarak duzenle
        date = hist.iloc[:,col+1].name
        temp2 = pd.DataFrame()
        for i in port.port_num.unique():
            temp = port[port.port_num == i]
            temp = temp.merge(ret, right_index=True, left_index=True)
            temp = temp[["port_num","pred","n_ret"]]
            temp2 = temp2.append(temp)
        temp2 = temp2.reset_index()
        temp2["date"] = date
        df = df.append(temp2)
    return df

def portfolios_index_return(historical_returns):
    df = pd.DataFrame()
    for pn in historical_returns.port_num.unique():
        temp = historical_returns[historical_returns.port_num == pn].set_index("date")
        temp = (1+temp[["pred","n_ret"]]).cumprod().mul(100)
        temp["port_num"] = pn
        temp = temp.reset_index()
        begin = temp.date.min() - pd.DateOffset(7)
        first_row = {"date":begin, "pred":100, "n_ret":100, "port_num":pn}
        temp = temp.append(first_row,ignore_index=True).sort_values("date")
        df = df.append(temp)
    return df


if __name__ == "__main__":

    port = pd.read_csv("C:/myml/powerbi/twin_momentum_portfolios.csv")
    fund = pd.read_csv("C:/myml/powerbi/fundamental_momentum.csv").set_index("ticker")
    
    hist, returns = historical_momentum()
    historical_portfolios = historical_return(fund, hist, returns)
    historical_returns = historical_portfolios.groupby(["port_num","date"]).mean().reset_index()
    portfolio_index_returns = portfolios_index_return(historical_returns)
