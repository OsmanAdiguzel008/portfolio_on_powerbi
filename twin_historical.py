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
    tickers.remove("CANTE.IS")
    tickers = tickers + ["ALKIM.IS"]
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

def historical_twin_momentum(fund, hist, returns):
    global wht_methods
    df = pd.DataFrame()
    for col in range(len(hist.columns)-1):
        prc  = hist.iloc[:,col].to_frame(name="returns")
        port = split_portfolios(fund, prc)
        temp3 = pd.DataFrame()
        for wht_method in wht_methods:
            wht  = get_weights(port, wht_method)
            port = port.drop("weights",axis=1)
            ret  = returns.iloc[:,col+1].to_frame(name="p_ret") #ret olarak momentum kullanmisim onu normal hist olarak duzenle
            date = hist.iloc[:,col+1].name
            temp2 = pd.DataFrame()
            for i in port.port_num.unique():
                temp   = port[port.port_num == i]
                temp_w = wht[wht.port_num == i]
                
                temp = temp.merge(ret, right_index=True, left_index=True)
                temp = temp.merge(temp_w["weights"], right_index=True, left_index=True)
                temp = temp[["port_num","pred","p_ret","weights"]]
                temp2 = temp2.append(temp)
            temp2.index.name = "ticker"
            temp2 = temp2.reset_index()
            temp2["date"] = date
            temp2["wht_method"] = wht_method
            temp3 = temp3.append(temp2)
        df = df.append(temp3)
    return df

def portfolios_index_return(historical_returns):
    df = pd.DataFrame()
    for method in historical_returns.wht_method.unique():
        df2 = pd.DataFrame()
        temp =  historical_returns[historical_returns.wht_method == method]
        for pn in historical_returns.port_num.unique():
            temp2 = temp[temp.port_num == pn].set_index("date")
            temp2 = (1+temp2[["pred","p_ret","w_ret"]]).cumprod().mul(100)
            temp2["port_num"] = pn
            temp2 = temp2.reset_index()
            begin = temp2.date.min() - pd.DateOffset(7)
            first_row = {"date":begin, "pred":100, "p_ret":100, "w_ret":100, "port_num":pn}
            temp2 = temp2.append(first_row,ignore_index=True).sort_values("date")
            df2 = df2.append(temp2)
        df2["wht_method"] = method
        df = df.append(df2)
    return df

def get_weights(df, method=None):
    # calculate tm weights
    df["returns"] = df["returns"] + df["returns"].median()
    df["pred"]    = df["pred"] + df["pred"].median()
    df["weights"] = df["returns"] + df["pred"]
    wht  = pd.DataFrame()
    for i in df.port_num.unique():
        temp = df[df.port_num == i]
        if method == "tm":
            temp["weights"] = temp["weights"]/temp["weights"].sum()
        elif method == "equal":
            temp["weights"] = 1/temp.weights.count()
        else:
            raise Exception("Please enter weighted method")
        wht = wht.append(temp)
    return wht


if __name__ == "__main__":
    wht_methods = ["tm","equal"]

    port = pd.read_csv("C:/myml/powerbi/data/twin_momentum_portfolios.csv")
    fund = pd.read_csv("C:/myml/powerbi/data/fundamental_momentum.csv").set_index("ticker")
    
    hist, returns = historical_momentum()
    historical_portfolios = historical_twin_momentum(fund, hist, returns)
    historical_returns = historical_portfolios.groupby(["port_num","date","wht_method"]).mean().reset_index()
    historical_portfolios["w_ret"] = historical_portfolios["p_ret"] * historical_portfolios["weights"]
    w_ret = historical_portfolios[["port_num","date","w_ret","ticker","wht_method"]
                                  ].groupby(["port_num","date","wht_method"]
                                            ).sum().reset_index()
    historical_returns = historical_returns.merge(w_ret, 
                                                  left_on=["port_num","date","wht_method"], 
                                                  right_on=["port_num","date","wht_method"])
    portfolio_index_returns = portfolios_index_return(historical_returns)
    
    historical_portfolios.to_csv("C:/myml/powerbi/data/historical_portfolios.csv", index=False)
    historical_returns.to_csv("C:/myml/powerbi/data/historical_returns.csv", index=False)
    portfolio_index_returns.to_csv("C:/myml/powerbi/data/portfolio_index_returns.csv", index=False)
