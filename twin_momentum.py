# -*- coding: utf-8 -*-
"""
Created on Wed Aug 31 19:58:01 2022

@author: oadiguzel
"""

import pandas as pd
import numpy as np
import yfinance as yf
import datetime as dt
import importlib
import runpy


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

def get_returns(df):
    global wht_methods
    begin = dt.datetime.now()
    result = pd.DataFrame()
    ret_types = {"1day":["5d","1d","1D"],
                 "1week":["1mo","1d","1W"],
                 "1month":["3mo","1d","1M"],
                 "1year":["1y","1d","1M"]
                 }
    for wht_method in wht_methods:
        temp3 = pd.DataFrame()
        wht = get_weights(df, wht_method)
        
        for key in ret_types.keys():
            ret_dict  = {}
            for i in range(1,26):
                if i in df.port_num.to_list():
                    temp   = df.loc[df.port_num == i]
                    temp_w = wht.loc[wht.port_num == i]["weights"].T
                    
                    tic_list = ""
                    for k in temp.index:
                        tic_list += f"{k} "
                    frame = yf.download(tickers = tic_list,
                                        period = ret_types[key][0],
                                        interval = ret_types[key][1]
                                        ).dropna()
                    if len(frame.columns) > 6:
                        #print("if")
                        rs = ret_types[key][2]
                        ret_value = frame.resample(rs).last().pct_change(
                                                                )["Adj Close"]
                        if key == "1year":
                            #print("if-if")
                            ret_value = ret_value.sum().mul(temp_w).sum()
                        else:
                            #print("if-else")
                            ret_value = ret_value.mul(temp_w).sum(axis=1).iloc[-1]
                    else:
                        #print("else")
                        # weight hesaplammasi yapilmiyor cunku tek kagit var
                        ret_value = frame["Adj Close"].pct_change().iloc[-1]
                        
                    ret_dict[i] = ret_value
                    print(f"Portfolio ---- {i} for {key} & {wht_method} ---- return : {round(ret_value,4)}")
            temp2 = pd.DataFrame().from_dict(ret_dict, orient="index", columns=[key])
            if len(temp3) == 0:
                temp3 = temp2
            else:
                temp3 = temp3.merge(temp2, right_index=True, left_index=True)
        
        temp3["wht_method"] = wht_method
        temp3.index.name = "port_num"
        temp3 = temp3.reset_index()
        result = result.append(temp3)
    end = dt.datetime.now()
    print(end-begin)
    return result.set_index("port_num")

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

def get_all_weights(df):
    global wht_methods
    wht = pd.DataFrame()
    for i in wht_methods:
        temp = get_weights(predictions, i)["weights"].to_frame(name="wht")
        temp["wht_method"] = i
        wht = wht.append(temp)
    return wht
    
    

if __name__ == "__main__":
    wht_methods = ["tm","equal"]
    
    if dt.datetime.today().day == 1:
        runpy.run_path("C:/myml/powerbi/fundamental_momentum.py")
    if dt.date.today().weekday() == 0:
        runpy.run_path("C:/myml/powerbi/price_momentum.py")
    fun = pd.read_csv("C:/myml/powerbi/data/fundamental_momentum.csv", index_col = "ticker")
    prc = pd.read_csv("C:/myml/powerbi/data/price_momentum.csv", index_col = "ticker")
    
    predictions = split_portfolios(fun, prc)
    result      = get_returns(predictions)
    wht         = get_all_weights(predictions)
    map_        = predictions[["port_num","fun_queue","prc_queue","pred","weights"]].reset_index()
    map_        = map_.merge(wht, left_on="ticker", right_index=True)
    twin_matrix = result.merge(map_.set_index("port_num")[["fun_queue","prc_queue"]].drop_duplicates(), 
                               left_index=True, right_index=True)
    
    twin_matrix.index.name = "port_num"
    twin_matrix = twin_matrix.reset_index()    
    twin_matrix.to_csv("C:/myml/powerbi/data/twin_matrix.csv", index = False)
    map_.to_csv("C:/myml/powerbi/data/twin_momentum_portfolios.csv", index=False)
    