# -*- coding: utf-8 -*-
"""
Created on Sun Feb 14 16:49:27 2021

@author: andre
"""
import matplotlib.pyplot as plt
import pickle
import pathlib
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
from iexfinance.stocks import get_historical_data


def divide_chunks(l, n): 
    # looping till length l 
    for i in range(0, len(l), n):  
        yield l[i:i + n] 
        
def main():
    save_path = pathlib.Path(os.getcwd()) / 'Artifacts' / 'exchange data'
    save_path.mkdir(parents=True, exist_ok=True)
    # YYYY, M, D
    start_date = datetime(2021, 2, 8)
    end_date = datetime(2021, 2, 12)
    
    reddit_data_dir = pathlib.Path(os.getcwd()) / 'Artifacts' / 'csv files'
    reddit_files = os.listdir(reddit_data_dir)
    reddit_data = {}
    for file in reddit_files:
        date = file.split('_')[0]
        data = pd.read_csv(reddit_data_dir / file, index_col=0)
        reddit_data[date] = data
    
    all_tickers = set()
    for date, tickers in reddit_data.items():  
        all_tickers = all_tickers | set(tickers.index.values)
    # for date, tickers in reddit_data.items():
    #     for ticker in tickers.index.values:
    #         _date = datetime(int(date[0:4]), int(date[4:6]), int(date[6:8]))
    #         start_date = _date - timedelta(days = 1)
    #         end_date = _date 
            # historical_data = get_historical_data(ticker, start_date, end_date, close_only=True, token = "pk_d91e674c5901468c83b3bd5abd16426f")
    
    #sort elxically for the iex call
    all_tickers = sorted(all_tickers)
    # chunked_tickers = list(divide_chunks(all_tickers, 100))
    # data_elements = []
    # for chunk in chunked_tickers:
    #     historical_data = get_historical_data(chunk, start_date, end_date, token = "pk_d91e674c5901468c83b3bd5abd16426f")
    #     data_elements.append(historical_data)
    # all_data = pd.concat(data_elements)
    # all_data.to_csv(save_path / 'exchange_data.csv')
    tickers_file_path = save_path / 'tickers.csv'
    with open(tickers_file_path, 'w') as fh:
        for ticker in all_tickers:
            fh.write(ticker + '\n')
    print('break')


if __name__ == "__main__":
    main()