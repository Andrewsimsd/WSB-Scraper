# -*- coding: utf-8 -*-

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


def get_ticker_count(date, url):
    reddit = praw.Reddit(client_id = "bbHD9kqIv2nmLQ",
                         client_secret = "vijXx26W5qgMyx2BbWA4tihwHjdIWg",
                         user_agent = "windows:scraper:0.1 (by u/0x00000194)",
                         check_for_async = False)
    
    # People may use use words that happen to be real ticker names
    flagged_words = ("YOLO", "PUMP", "RH", "EOD", "IPO", "ATH", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", 
        "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z")
    positive_disposition = ('buy', 'leap', 'soar', 'long', 'skyrocket', 'good', 'awesome', 'genius', 'smart', 'rich')
    negative_disposition = ('sell', 'crash', 'short', 'bad', 'awful', 'horrible', 'stupid', 'retarded')
    ticker_set = get_nasdaq_tickers()
    tickers = pd.DataFrame(columns = ('mentions', 'disposition'))
    # Enter the url of daily discussion post
    submission = reddit.submission(url=url)
    print(submission.title)
    counter = 0
    for comment in iter_top_level(submission.comments): 
        # set how many comments you want to search
        if counter == 100:
            tickers = tickers.sort_values('mentions', ascending = False)
            return tickers
        #see if comment contains a ticker
        for word in comment.body.split():
            #if word is a valid ticker
            if word == word.upper() and word in ticker_set and word not in flagged_words:
                #if ticker not seen before
                if word not in tickers.index.values:
                    #create new index for ticker
                    tickers = tickers.append(pd.Series(name=word, dtype = object))
                    tickers.loc[word]['mentions'] = 1
                else:
                    tickers.loc[word]['mentions'] += 1     
                #grade disposition
                disposition = 0
                for _word in comment.body.split():
                    if _word.lower() in positive_disposition:
                        disposition += 1
                    elif _word.lower() in negative_disposition:
                        disposition -= 1
                #if disposition not initialized
                if tickers.loc[word]['disposition'] is np.nan:
                    tickers.loc[word]['disposition'] = disposition
                else:
                    tickers.loc[word]['disposition'] += disposition
        counter += 1
    tickers = tickers.sort_values('mentions', ascending = False)
    return tickers

def plot_ticker_count(tickers, date, save_file_dir):
    fig, axs = plt.subplots(2, figsize = (10, 10))
    xmin = -0.5
    xmax = len(tickers.index.values) - 0.5
    fig.suptitle(f'Ticker Mention Count and Disposition\nDate: {date}')
    axs[0].grid(zorder = 0)
    axs[0].bar(tickers.index.values, tickers['mentions'].values, zorder = 3)
    axs[0].set_xticklabels(tickers.index.values, rotation = 90)
    # axs[0].set_xlabel('Ticker')
    axs[0].set_ylabel('Times Mentioned')
    axs[0].set_xlim(xmin, xmax)
    
    axs[1].grid(zorder = 0)
    axs[1].bar(tickers.index.values, tickers['disposition'].values, zorder = 3)
    axs[1].set_xticklabels(tickers.index.values, rotation = 90)
    axs[1].set_xlabel('Ticker')
    axs[1].set_ylabel('Disposition')
    axs[1].hlines(0, xmin, xmax, color = 'k', lw = 3)
    axs[1].set_xlim(xmin, xmax)
    
    save_path = save_file_dir / 'plots'
    save_path.mkdir(parents=True, exist_ok=True)
    plt.savefig(save_path / f'{date}_ticker_mentions.png', bbox_inches = 'tight')
    plt.close()
    return fig


def plot_ticker_change(tickers):
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
    save_file_dir = pathlib.Path(os.getcwd(), 'Artifacts')
    save_file_dir.mkdir(parents=True, exist_ok=True)
    pages = {20210212: r'https://www.reddit.com/r/wallstreetbets/comments/li8ul6/daily_discussion_thread_for_february_12_2021/',
             20210211: r'https://www.reddit.com/r/wallstreetbets/comments/lhifig/daily_discussion_thread_for_february_11_2021/',
             20210210: r'https://www.reddit.com/r/wallstreetbets/comments/lgrc39/daily_discussion_thread_for_february_10_2021/',
             20210209: r'https://www.reddit.com/r/wallstreetbets/comments/lg0h70/daily_discussion_thread_for_february_09_2021/',
             20210208: r'https://www.reddit.com/r/wallstreetbets/comments/lf9huy/daily_discussion_thread_for_february_08_2021/'
             }
    for date, url in pages.items(): 
        tickers = get_ticker_count(date, url)
        # tickers = calc_change(tickers)
        save_path = save_file_dir / 'csv files'
        save_path.mkdir(parents=True, exist_ok=True)
        tickers.to_csv(save_path / f'{date}_ticker_mentions.csv')
        plot_ticker_count(tickers, date, save_file_dir)
        # plot_ticker_change(tickers)
    
    
if __name__ == "__main__":
    main()
