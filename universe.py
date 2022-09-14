# -*- coding: utf-8 -*-
"""
Created on Thu Sep  8 13:58:58 2022

@author: oadiguzel
"""

import pandas as pd
import yfinance as yf

def get_price_data(tickers, period="1y", interval="1d"):
    df = yf.download(tickers = tickers,
                    period = period,
                    interval = interval)
    return df

if __name__ == "__main__":
    df = get_price_data(["XU100.IS","USDTRY=X"])
    df = df["Adj Close"]
    df = df.rename(columns= {"USDTRY=X":"usd","XU100.IS":"bist100"})
    df["bist100_usd"] = df.bist100.div(df.usd)
    #df = df.resample("1W").last().pct_change().dropna()
    df.to_csv("c:/myml/powerbi/data/universe.csv")
    
    """
    # it's for PowerBI extra transaction
    # 'dataset' holds the input data for this script
    import pandas as pd
    dataset  = pd.read_csv("C:/mymll/powerbi/data/dataset.csv")
    dataset1 = dataset[["date","pred","p_ret","w_ret","port_num","wht_method"]].dropna()
    dataset2 = dataset[["universe.Date","universe.usd","universe.bist100","universe.bist100_usd"]].dropna()
    
    
    dataset1["date"] = dataset1.date.astype('datetime64[ns]')
    date_min = dataset1.date.min()
    dataset2["universe.Date"] = dataset2["universe.Date"].astype('datetime64[ns]')
    dataset2 = dataset2.set_index("universe.Date")
    dataset2 = dataset2.pct_change()
    dataset2 = dataset2.loc[dataset2.index > date_min]
    dataset2["date"] = dataset2.index
    dataset2["usd"] = dataset2["universe.usd"]
    dataset2["bist100"] = dataset2["universe.bist100"]
    dataset2["bist100_usd"] = dataset2["universe.bist100_usd"]
    dataset2 = dataset2.set_index("date")
    dataset2 = dataset2[["usd","bist100","bist100_usd"]]
    dataset2 = (1+dataset2[["usd","bist100","bist100_usd"]]).cumprod().mul(100)
    dataset2 = dataset2.reset_index()
    begin = dataset2.date.min() - pd.DateOffset(7)
    first_row = {"date":begin, "usd":100, "bist100":100, "bist100_usd":100}
    dataset2 = dataset2.append(first_row,ignore_index=True).sort_values("date")
    
    ds = dataset1.merge(dataset2, right_on="date", left_on="date")

    
    """