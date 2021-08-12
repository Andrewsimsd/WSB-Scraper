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
from iexfinance.stocks import get_historical_data
from nltk.sentiment import SentimentIntensityAnalyzer

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
    sia = SentimentIntensityAnalyzer()
    reddit = praw.Reddit(client_id = "REDACTED",
                         client_secret = "REDACTED",
                         user_agent = "windows:scraper:0.1 (by uREDACTED)",
                         check_for_async = False)
    
    # People may use use words that happen to be real ticker names
    flagged_words = ("YOLO", "PUMP", "RH", "EOD", "IPO", "ATH", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", 
        "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z")
    positive_disposition = ('buy', 'buying', 'leap', 'soar', 'long', 'skyrocket', 'good', 'awesome', 'genius', 'smart', 'rich', 'gain', 'gains', 'leap', 'leaps', 'potential', 'jump', 'jump', 'hold', 'invest', 'investing', 'push', 'call', '🚀', 'moon', 'green', 'running', 'run', 'up', 'strong')
    negative_disposition = ('sell', 'selling', 'crash', 'short', 'bad', 'awful', 'horrible', 'stupid', 'retarded', 'drop', 'dropped', 'rip', 'put', 'red', 'dumping', 'dump', 'down', 'weak')
    ticker_set = get_nasdaq_tickers()
    tickers = pd.DataFrame(columns = ('mentions', 'disposition', 'vader_positive', 'vader_negative', 'vader_neutral'))
    # Enter the url of daily discussion post
    submission = reddit.submission(url=url)
    print(submission.title)
    counter = 0
    for comment in iter_top_level(submission.comments): 
        # set how many comments you want to search
        if counter == 1000:
            tickers = tickers.sort_values('mentions', ascending = False)
            #adjust vader scores to percent
            tickers.vader_positive = tickers.vader_positive/tickers.mentions
            tickers.vader_negative = tickers.vader_negative/tickers.mentions
            tickers.vader_neutral = tickers.vader_neutral/tickers.mentions
            return tickers
        tickers_present = []
        #see if comment contains a ticker
        for word in comment.body.split():
            #if word is a valid ticker
            if word == word.upper() and word in ticker_set and word not in flagged_words:
                tickers_present.append(word)
                #if ticker not seen before
                if word not in tickers.index.values:
                    #create new index for ticker
                    tickers = tickers.append(pd.Series(name=word, dtype = object))
                    tickers.loc[word]['mentions'] = 1
                else:
                    tickers.loc[word]['mentions'] += 1     
        for ticker in tickers_present:
            #grade disposition
            disposition = 0
            for _word in comment.body.split():
                if _word.lower() in positive_disposition:
                    disposition += 1
                elif _word.lower() in negative_disposition:
                    disposition -= 1
            #if disposition not initialized
            if tickers.loc[ticker]['disposition'] is np.nan:
                tickers.loc[ticker]['disposition'] = disposition
            else:
                tickers.loc[ticker]['disposition'] += disposition
            #vader disposition
            scores = sia.polarity_scores(comment.body)
            #if disposition not initialized
            if tickers.loc[ticker]['vader_positive'] is np.nan:
                tickers.loc[ticker]['vader_positive'] = scores['pos']
            else:
                tickers.loc[ticker]['vader_positive'] += scores['pos']
                
            if tickers.loc[ticker]['vader_negative'] is np.nan:
                tickers.loc[ticker]['vader_negative'] = scores['neg']
            else:
                tickers.loc[ticker]['vader_negative'] += scores['neg']    
                
            if tickers.loc[ticker]['vader_neutral'] is np.nan:
                tickers.loc[ticker]['vader_neutral'] = scores['neu']
            else:
                tickers.loc[ticker]['vader_neutral'] += scores['neu'] 

        counter += 1
    tickers = tickers.sort_values('mentions', ascending = False)
    #adjust vader scores to percent
    tickers.vader_positive = tickers.vader_positive/tickers.mentions
    tickers.vader_negative = tickers.vader_negative/tickers.mentions
    tickers.vader_neutral = tickers.vader_neutral/tickers.mentions

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
    
    x = np.arange(len(tickers.index.values))  # the label locations
    width = 0.35  # the width of the bars
    
    # fig, ax = plt.subplots()
    rects1 = axs[1].bar(x - width/2, tickers['vader_positive'].values, width, label='VADER Positive', zorder = 3)
    rects2 = axs[1].bar(x + width/2, tickers['vader_negative'].values, width, label='VADER Negative', zorder = 3)
    
    axs[1].set_xticks(x)
    axs[1].set_xticklabels(tickers.index.values)
    axs[1].legend()
    axs[1].set_xticklabels(tickers.index.values, rotation = 90)
    axs[1].set_xlabel('Ticker')
    axs[1].set_ylabel('Disposition')
    axs[1].set_xlim(xmin, xmax)
    axs[1].grid(zorder = 0)
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
    pages = {20210222: r'https://www.reddit.com/r/wallstreetbets/comments/lplby9/daily_discussion_thread_for_february_22_2021/',
             20210220: r'https://www.reddit.com/r/wallstreetbets/comments/lnqdke/weekend_discussion_thread_for_the_weekend_of/',
             20210219: r'https://www.reddit.com/r/wallstreetbets/comments/lnd8jo/daily_discussion_thread_for_february_19_2021/',
             20210218: r'https://www.reddit.com/r/wallstreetbets/comments/lmk8bq/daily_discussion_thread_for_february_18_2021/',
             20210217: r'https://www.reddit.com/r/wallstreetbets/comments/llrzit/daily_discussion_thread_for_february_17_2021/',
             20210216: r'https://www.reddit.com/r/wallstreetbets/comments/ll1ir4/daily_discussion_thread_for_february_16_2021/',
             20210212: r'https://www.reddit.com/r/wallstreetbets/comments/li8ul6/daily_discussion_thread_for_february_12_2021/',
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
