# -*- coding: utf-8 -*-
"""
Created on Fri Aug 26 11:43:03 2022

@author: oadiguzel
"""

import pandas as pd
from bs4 import BeautifulSoup
import requests
import yfinance as yf

class bist100:
    def __init__(self):
        self.scrape_components()
        self.split()
        self.components_table()
        
    def split(self):
        self.list_ = []
        for i in self.text.split("\n\n"):
            self.list_.append(i)
        self.list_ = self.list_[2:]

    def scrape_components(self):
        wl = {"components":"https://tr.wikipedia.org/wiki/Borsa_İstanbul"}
        page = requests.get(wl["components"])
        soup = BeautifulSoup(page.text, "html.parser")
        value = soup.find_all("table",class_="wikitable")
        self.text = value[0].text
        
    def components_table(self):
        t_list = []
        temp = []
        for i in self.list_:
            if len(temp)==6:
                t_list.append(temp)
                temp = []
                temp.append(i)
            else:
                temp.append(i)
        col = ["ticker","name","sector","sub_sector","city","founding"]
        self.components = pd.DataFrame(t_list[1:], columns=col)
        a = self.components["ticker"].str.split("\n",expand=True)
        self.components["ticker"] = a[1]
        
    
    def get_price(self, ticker, period="1d", interval="1m", group_by="ticker", 
              auto_adjust=True, prepost=True, threads=True, proxy=None):
        if ticker == "all":
            ticker = self.components.ticker.to_list()
            ticker = ticker + ["ALKIM"]
            ticker = self.listToString(ticker)
        else:
            ticker = ticker + ".IS"
        df = yf.download(
                        tickers = ticker,
                        period = period,
                        interval = interval,
                        group_by = group_by,
                        auto_adjust = auto_adjust,
                        prepost = prepost,
                        threads = threads,
                        proxy = proxy
                    )
        pd.options.display.float_format = '{:,.2f}'.format
     #   self.price = df.round(3)
        return df.round(3)
    
    def listToString(self,liste):
        str1 = "" 
        for ele in liste: 
            str1 += ele+".IS "
        return str1 
    
    def info(self, which):
        info_ = {"periods": "1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max",
                 "intervals": "1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo",
                 "tickers": "inputs shoul be like; 'AGEEN.IS SARKY.IS ADESE.IS'"}
        info_["help"] = f"You may get an information about these; \n {list(info_.keys())}"
        if which in info_.keys():
            print(info_[which])
        else:
            raise Exception(f"Please enter one of these \n {list(info_.keys())}")
        
    def get_price_clear(self):
        df = self.get_price("all", "1y", "1d") 
        df = df.stack(0)
        df.index = df.index.rename(['Date', 'Ticker'])
        df = df.reset_index()
        return df
        
if __name__ == "__main__":
    # below code is for Power BI reports
    bist = bist100()
    components = bist.components
    price_data = bist.get_price_clear()
    price_data.to_csv("C:/myml/powerbi/data/price_data.csv", index=False)
    components.to_csv("C:/myml/powerbi/data/components.csv", index=False)
