# -*- coding: utf-8 -*-
"""
Created on Sun Feb 14 21:19:08 2021

@author: andre
"""
import matplotlib.pyplot as plt
import pickle
import pathlib
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
import scipy.stats

def main():
    save_path = pathlib.Path(os.getcwd()) / 'Artifacts' / 'exchange data'
    save_path.mkdir(parents=True, exist_ok=True)
    exchange_data_path = pathlib.Path(os.getcwd()) / 'historical data' / 'AIJJBGFG.csv'
    exchange_data = pd.read_csv(exchange_data_path, index_col = 'Date')
    reddit_data_dir = pathlib.Path(os.getcwd()) / 'Artifacts' / 'csv files'
    reddit_files = os.listdir(reddit_data_dir)
    reddit_data = {}
    for file in reddit_files:
        date = file.split('_')[0]
        data = pd.read_csv(reddit_data_dir / file, index_col=0)
        reddit_data[date] = data
        
    #calculate rank change
    dates = list(reddit_data.keys())
    for i, (date, tickers) in enumerate(reddit_data.items()):
        tickers['rank'] = pd.Series()
        tickers['rank change'] = pd.Series()
        for idx, ticker in enumerate(tickers.index.values):
            tickers.loc[ticker, 'rank'] = idx + 1
        #no rank chaneg available on first day
        if i > 0:
            for idx, ticker in enumerate(tickers.index.values):
                #if ticker seen yesterday
                if ticker in reddit_data[dates[i-1]].index.values:
                    previous_rank = reddit_data[dates[i-1]].loc[ticker, 'rank']
                    tickers.loc[ticker, 'rank change'] = previous_rank - tickers.loc[ticker, 'rank']
                else:  #ticker not seen yesterday
                #cant decide which is best. both valid
                    # tickers.loc[ticker, 'rank change'] = len(tickers.index.values) - tickers.loc[ticker, 'rank']
                    tickers.loc[ticker, 'rank change'] = np.nan
    #calc custom feature
    for i, (date, tickers) in enumerate(reddit_data.items()):
        tickers['custom'] = pd.Series()
        tickers.loc[:, 'custom'] = (tickers.loc[:, 'mentions'] * tickers.loc[:, 'vader_positive']) - (tickers.loc[:, 'mentions'] * tickers.loc[:, 'vader_negative'])
       
    #calc perceng change in price       
    for date, tickers in reddit_data.items():
        tickers['percent change'] = pd.Series()
        for ticker in tickers.index.values:
            current_day = datetime(int(date[0:4]), int(date[4:6]), int(date[6:8]))
            previous_day = current_day - timedelta(days = 1)
            if current_day == datetime(2021, 2, 16):
                #holiday
                previous_day = previous_day - timedelta(days = 3)
            #if weekend
            if previous_day.weekday() > 4:
                #move to previous friday,
                previous_day = previous_day - timedelta(days = 2)
            if ticker in exchange_data.columns:
                previous_day_close = exchange_data[ticker][previous_day.strftime("%Y-%m-%d")]
                current_day_close = exchange_data[ticker][current_day.strftime("%Y-%m-%d")]
                percent_change = (current_day_close - previous_day_close)/previous_day_close
                tickers.loc[ticker, 'percent change'] = percent_change
         
        # fig = plt.figure(figsize = (10, 6))
        # xmin = -0.5
        # xmax = len(tickers.index.values) - 0.5
        # plt.grid(zorder = 0)
        # plt.bar(tickers.index.values, tickers['percent change'].values, zorder = 3)
        # plt.xticks(rotation = 'vertical')
        # plt.title(f'Ticker Percent Chance\nDate: {date}')
        # plt.xlabel('Ticker')
        # plt.ylabel('Percent Change (%)')
        # plt.hlines(0, xmin, xmax, color = 'k', lw = 3)
        # plt.xlim(xmin, xmax)
        # save_path.mkdir(parents=True, exist_ok=True)
        # plt.savefig(save_path / f'{date}_price_change.png', bbox_inches = 'tight')
        # plt.close()
        ################################plot rank change and price change###############################################
        # fig, axs = plt.subplots(2, figsize = (10, 10))
        # xmin = -0.5
        # xmax = len(tickers.index.values) - 0.5
        # fig.suptitle(f'Ticker Mention Rank Change & Price Change\nDate: {date}')
        # axs[0].grid(zorder = 0)
        # axs[0].bar(tickers.index.values, tickers['rank change'].values, zorder = 3)
        # axs[0].set_xticklabels(tickers.index.values, rotation = 90)
        # # axs[0].set_xlabel('Ticker')
        # axs[0].set_ylabel('Mention Rank Change')
        # axs[0].set_xlim(xmin, xmax)
        # axs[0].hlines(0, xmin, xmax, color = 'k', lw = 3)
        
        # axs[1].grid(zorder = 0)
        # axs[1].bar(tickers.index.values, tickers['percent change'].values, zorder = 3)
        # axs[1].set_xticklabels(tickers.index.values, rotation = 90)
        # axs[1].set_xlabel('Ticker')
        # axs[1].set_ylabel('Price Change (%)')
        # axs[1].hlines(0, xmin, xmax, color = 'k', lw = 3)
        # axs[1].set_xlim(xmin, xmax)
        
        # save_path.mkdir(parents=True, exist_ok=True)
        # plt.savefig(save_path / f'{date}_price_change.png', bbox_inches = 'tight')
        # plt.close()
    
    
    #####################plot custom vs price change same day#########################
    figure = plt.figure(figsize = (10, 10))
    plt.title('Custom Vs. Price change for same day')
    plt.xlabel('Custom')
    plt.ylabel('Price Change (%)')
    
    for date, tickers in reddit_data.items():
       plt.scatter(tickers['custom'], tickers['percent change'], label = date, zorder = 3)
    plt.xscale('log')
    plt.legend()
    plt.grid(which="both", zorder = 0)
    save_path.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path / f'custom_vs_price_change_same_day.png', bbox_inches = 'tight')
    plt.close()
    ###################plot custom vs price change next day#################
    figure = plt.figure(figsize = (10, 10))
    plt.title('custom Vs. Price change for next day')
    plt.xlabel('Rank change')
    plt.ylabel('Price Change (%)')
    for i, (date, tickers) in enumerate(reddit_data.items()):
        #no future data for last day
        if i < len(dates) - 1:
            intersecting_tickers = set(tickers.index.values) & set(reddit_data[dates[i+1]].index.values)
            #reduce current ticker to intersecting only
            current_tickers = pd.DataFrame(columns = ('mentions', 'disposition', 'rank', 'rank change', 'percent change', 'custom'))
            for row in tickers.iterrows():
                if row[0] in intersecting_tickers:
                    current_tickers.loc[row[0]] = row[1]
            #reduce future tickers to intersecting only
            future_tickers = pd.DataFrame(columns = ('mentions', 'disposition', 'rank', 'rank change', 'percent change', 'custom'))   
            for row in reddit_data[dates[i+1]].iterrows():
                if row[0] in intersecting_tickers:
                    future_tickers.loc[row[0]] = row[1]
            plt.scatter(current_tickers['custom'], future_tickers['percent change'], label = date, zorder = 3)
    plt.xscale('log')
    plt.legend()
    plt.grid(which="both", zorder = 0)
    save_path.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path / f'custom_vs_price_change_next_day.png', bbox_inches = 'tight')
    plt.close()
    #####################plot rank change vs price change same day#######################
    figure = plt.figure(figsize = (10, 10))
    plt.title('Rank change Vs. Price change for same day')
    plt.xlabel('Rank change')
    plt.ylabel('Price Change (%)')
    
    for date, tickers in reddit_data.items():
       plt.scatter(tickers['rank change'], tickers['percent change'], label = date, zorder = 3) 
    plt.legend()
    plt.grid(zorder = 0)
    save_path.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path / f'rank_change_vs_price_change_same_day.png', bbox_inches = 'tight')
    plt.close()
    ######################plot rank change vs price change next day##############
    figure = plt.figure(figsize = (10, 10))
    plt.title('Rank change Vs. Price change for next day')
    plt.xlabel('Rank change')
    plt.ylabel('Price Change (%)')
    for i, (date, tickers) in enumerate(reddit_data.items()):
        #no future data for last day
        if i < len(dates) - 1:
            intersecting_tickers = set(tickers.index.values) & set(reddit_data[dates[i+1]].index.values)
            #reduce current ticker to intersecting only
            current_tickers = pd.DataFrame(columns = ('mentions', 'disposition', 'rank', 'rank change', 'percent change'))
            for row in tickers.iterrows():
                if row[0] in intersecting_tickers:
                    current_tickers.loc[row[0]] = row[1]
            #reduce future tickers to intersecting only
            future_tickers = pd.DataFrame(columns = ('mentions', 'disposition', 'rank', 'rank change', 'percent change'))   
            for row in reddit_data[dates[i+1]].iterrows():
                if row[0] in intersecting_tickers:
                    future_tickers.loc[row[0]] = row[1]
            plt.scatter(current_tickers['rank change'], future_tickers['percent change'], label = date, zorder = 3) 
    plt.legend()
    plt.grid(zorder = 0)
    save_path.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path / f'rank_change_vs_price_change_next_day.png', bbox_inches = 'tight')
    plt.close()
    ################## plot corr matrix################################
    corr = tickers.corr()
    figure = plt.figure(figsize = (15, 15))
    plt.matshow(corr, fignum=1)
    plt.title('Correlation Matrix')
    plt.xticks(range(tickers.select_dtypes(['number']).shape[1]), tickers.select_dtypes(['number']).columns, fontsize=14, rotation=45)
    plt.yticks(range(tickers.select_dtypes(['number']).shape[1]), tickers.select_dtypes(['number']).columns, fontsize=14)
    cb = plt.colorbar()
    save_path.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path / f'corr_matrix.png', bbox_inches = 'tight')
    plt.close()
    #calculate correlation and p value of price
    # corr, p = scipy.stats.pearsonr(tickers., y)
    breakpoint()
    
if __name__ == "__main__":
    main()
