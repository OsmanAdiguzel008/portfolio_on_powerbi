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
    begin = dt.datetime.now()
    result = pd.DataFrame()
    ret_types = {"1day":["5d","1d","1D"],
                 "1week":["1mo","1d","1W"],
                 "1month":["3mo","1d","1M"],
                 "1year":["1y","1d","1M"]
                 }
    for key in ret_types.keys():
        ret_dict  = {}
        for i in range(1,26):
            if i in df.port_num.to_list():
                temp = df.loc[df.port_num == i]
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
                        ret_value = ret_value.sum().mean()
                    else:
                        #print("if-else")
                        ret_value = ret_value.mean(axis=1).iloc[-1]
                else:
                    #print("else")
                    ret_value = frame["Adj Close"].pct_change().iloc[-1]
                ret_dict[i] = ret_value
                print(f"Portfolio ---- {i} for {key} ---- return : {round(ret_value,4)}")
        temp2 = pd.DataFrame().from_dict(ret_dict, orient="index", columns=[key])
        if len(result) == 0:
            result = temp2
        else:
            result = result.merge(temp2, right_index=True, left_index=True)
                
    end = dt.datetime.now()
    print(end-begin)
    return result


if __name__ == "__main__":
    
    if dt.datetime.today().day == 1:
        runpy.run_module(mod_name="fundamental_momentum")
    if dt.date.today().weekday() == 0:
        runpy.run_module(mod_name="price_momentum")
    fun = pd.read_csv("C:/myml/powerbi/fundamental_momentum.csv", index_col = "ticker")
    prc = pd.read_csv("C:/myml/powerbi/price_momentum.csv", index_col = "ticker")
    
    predictions = split_portfolios(fun, prc)
    result = get_returns(predictions)
    map_ = predictions[["port_num","fun_queue","prc_queue","pred"]].reset_index()
    twin_matrix = result.merge(map_.set_index("port_num")[["fun_queue","prc_queue"]].drop_duplicates(), 
                               left_index=True, right_index=True)    
    twin_matrix.index.name = "port_num"
    twin_matrix = twin_matrix.reset_index()    
    result.to_csv("C:/myml/powerbi/twin_returns_equal_weight.csv")
    map_.to_csv("C:/myml/powerbi/twin_momentum_portfolios.csv")