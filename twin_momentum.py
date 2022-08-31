# -*- coding: utf-8 -*-
"""
Created on Wed Aug 31 19:58:01 2022

@author: oadiguzel
"""

import pandas as pd
import numpy as np



if __name__ == "__main__":
    
    fun = pd.read_csv("fundamental_momentum.csv", index_col = "ticker")
    prc = pd.read_csv("price_momentum.csv", index_col = "ticker")
    
    print(fun)
    print(prc)
    
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
            temp["port_num"] = f"portfolio{count}"
            df = df.append(temp)
            count = count + 1