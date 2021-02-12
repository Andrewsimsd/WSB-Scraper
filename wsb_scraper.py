# -*- coding: utf-8 -*-
"""
Created on Fri Feb 12 14:49:09 2021

@author: andre
"""

import praw
from praw.models import MoreComments
import matplotlib.pyplot as plt
import pickle
import pathlib
import pandas as pd
import numpy as np
import os
from iexfinance.stocks import Stock

# Creates a set of stock tickers in NASDAQ
def get_nasdaq_tickers():
    fin = open("nasdaqtraded.txt", 'r')
    tickers = set()
    fin.readline()
    for line in fin.readlines():
        line = line[2:]
        tickers.add(line[:line.index("|")])
    return tickers

# Iterates through only head comments 
def iter_top_level(comments):
    for top_level_comment in comments:
        if isinstance(top_level_comment, MoreComments):
            yield from iter_top_level(top_level_comment.comments())
        else:
            yield top_level_comment

def get_ticker_count():
    reddit = praw.Reddit(client_id = "bbHD9kqIv2nmLQ",
                         client_secret = "vijXx26W5qgMyx2BbWA4tihwHjdIWg",
                         user_agent = "windows:scraper:0.1 (by u/0x00000194)",
                         check_for_async = False)
    counter = 0
    
    # People may use use words that happen to be real ticker names
    flagged_words = ["YOLO", "PUMP", "RH", "EOD", "IPO", "ATH", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", 
        "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
    ticker_set = get_nasdaq_tickers()
    # tickers = {}
    tickers = pd.DataFrame(columns = ('ticker', 'mentions'))
    # Enter the url of daily discussion post
    url = "https://www.reddit.com/r/wallstreetbets/comments/li8ul6/daily_discussion_thread_for_february_12_2021/"
    submission = reddit.submission(url=url)
    print(submission.title)
    for comment in iter_top_level(submission.comments): 
        # set how many comments you want to search
        if counter == 1000:
            return tickers
        for word in comment.body.split():
            if word == word.upper() and word in ticker_set and word not in flagged_words:
                if word not in tickers.index.values:
                    tickers.loc[word] = 1
                else:
                    tickers.loc[word] += 1
        counter += 1
    return tickers

def plot_ticker_count(tickers):
    tickers = tickers.sort_values('mentions', ascending = False)
    fig = plt.figure()
    plt.bar(tickers.index.values, tickers['mentions'].values)
    plt.xticks(rotation = 'vertical')
    plt.title('Ticker mention count')
    plt.xlabel('Ticker')
    plt.ylabel('Times Mentioned')
    return fig


def plot_ticker_change(tickers):
    tickers = tickers.sort_values('mentions', ascending = False)
    fig = plt.figure()
    plt.bar(tickers.index.values, tickers['percent change'].values)
    plt.xticks(rotation = 'vertical')
    plt.title('value change per ticker')
    plt.xlabel('Ticker')
    plt.ylabel('value change (%)')
    return fig


def close_price(ticker):
    a = Stock(ticker, token = "pk_d91e674c5901468c83b3bd5abd16426f")
    previousClose = a.get_quote()['previousClose']
    currentClose = a.get_quote()['iexClose']
    return previousClose, currentClose


def calc_change(tickers):
    tickers['previous close'] = pd.Series()
    tickers['current close'] = pd.Series()
    tickers['change'] = pd.Series()
    tickers['percent change'] = pd.Series()
    for ticker, row in tickers.iterrows():
        previous_close, current_close = close_price(ticker)
        tickers['previous close'][ticker] = previous_close
        tickers['current close'][ticker] = current_close
        tickers['change'][ticker] = current_close - previous_close
        tickers['percent change'][ticker] = (current_close - previous_close) / previous_close
    return tickers
        
        
def main():
    save_file_dir = os.path.join(os.getcwd(), 'Artifacts')
    pathlib.Path(save_file_dir).mkdir(parents=True, exist_ok=True)
    tickers = get_ticker_count()
    tickers = calc_change(tickers)
    plot_ticker_count(tickers)
    plot_ticker_change(tickers)
    
    
if __name__ == "__main__":
    main()
