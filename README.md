# WSB-Scraper
# Abstract  
This was a quick effort to try to draw some correlation between conversations on Reddit and security price changes.  
Given a set of Reddit threads to analyze, the program reads and analyzes all messages that contain a valid ticker symbol.
A number of features are analyzed including the following:
* sentiment (by the way of an NLP ML algorithm, VADER).
* The populatiry of each ticker symbol. 
* The rate of change of popularity of each ticker symbol.

No conclusive results were obtained.

# Directions for use
1. update pages dict in wsb_scraper.py main()
2. update get_ticker_count() to contian your reddit account info
3. run wsb_scraper.py
4. run ticker_test_file_maker.py
5. use resulting fiel to pull stock data from http://finance.jasonstrimpel.com/bulk-stock-download/
6. update exchange_price_analysis.py to reference the data downloaded from http://finance.jasonstrimpel.com/bulk-stock-download/ in main()
7. run exchange_price_analysis.py
8. ??????
9. profit

# Plots
An example of a plot displaying popularity and sentiment using the VADER algorithm.  
![20210208_ticker_mentions](https://user-images.githubusercontent.com/23323883/129273003-87544e4e-7ac2-4a75-be3e-c198af77dce3.png)  
An example of a plot displaying ticker popularity and price change.  
![20210219_price_change](https://user-images.githubusercontent.com/23323883/129273693-15d628d1-5afa-41c7-8bb7-21c94f75e541.png)  
An example of a plot displaying a correlation matrix of features of interest.  
![corr_matrix](https://user-images.githubusercontent.com/23323883/129273942-06d3c612-0bac-4b50-aa7e-1eccd824b6e4.png)  
An example of a plot displaying ticker popularity change vs. the next days price change.  
![rank_change_vs_price_change_next_day](https://user-images.githubusercontent.com/23323883/129274007-3bbb913e-d42f-42aa-a50e-fa69cb375164.png)  
An example of a plot displaying a scatter matrix of features of interest.  
![scatter_matrix](https://user-images.githubusercontent.com/23323883/129274050-fd97d3e4-982f-4b25-9603-048e90612e5a.png)  

