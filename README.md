### WallStreetBets Sentiment Dashboard

Derives market sentiment from reddit posts and comments using VADER sentiment model to assess bullish/bearish sentiment.


## Tools

Python 3.9.2  
Django  
Chart.js  
SQLite  
[Vader Sentiment](https://github.com/cjhutto/vaderSentiment)  
[get_all_tickers](https://github.com/shilewenuw/get_all_tickers)  
[praw](https://praw.readthedocs.io/en/latest/#)  
[psaw](https://psaw.readthedocs.io/en/latest/)  

## How it works

1. Iterates through reddit posts and comments
2. Extracts ticker symbols from reddit text submissions
3. VADER analyzes text submsision and assigns a sentiment value to the ticker [Bullish, Bearish, Neutral]
4. Data is inserted into sqlite database and outputted onto the dashboard

## Roadmap