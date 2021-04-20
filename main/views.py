from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponse
from django.views import View
from django.db.models import Count

from main.models import Ticker
import praw
from psaw import PushshiftAPI
import datetime as dt
from datetime import datetime, timedelta
import re
import sys
sys.path.insert(0, 'vaderSentiment-master/vaderSentiment') 
from vaderSentiment import SentimentIntensityAnalyzer
sys.path.insert(1, 'get_all_tickers-master/')
from get_all_tickers import get_tickers as gt

list_of_tickers = gt.get_tickers_filtered(mktcap_min = 1000)
lookup = set(list_of_tickers)
ticker_dict = {}

reddit = praw.Reddit(
    client_id="BtjxvWJ_zS-n2Q",
    client_secret="BS6RuPJqZ_kVJnln_vQlcLEowEzCSQ",
    password="gtf0mypassword",
    user_agent="testscript by u/ryancfl0",
    username="ryancfl0",
)

api = PushshiftAPI(reddit)

blacklist_words = [
   "YOLO", "TOS", "CEO", "CFO", "CTO", "DD","BRO", "ARE", "BTFD", "WSB", "OK", "RH",
   "KYS", "FD", "TYS", "US", "USA", "IT", "ATH", "RIP", "BMW", "GDP",
   "OTM", "ATM", "ITM", "IMO", "LOL", "DOJ", "BE", "HAS", "PR", "PC", "ICE",
   "TYS", "ISIS", "PRAY", "PT", "FBI", "SEC", "GOD", "NOT", "POS", "COD",
   "AYYMD", "FOMO", "TL;DR", "EDIT", "STILL", "LGMA", "WTF", "RAW", "PM",
   "LMAO", "LMFAO", "ROFL", "EZ", "RED", "BEZOS", "TICK", "IS", "DOW"
   "AM", "PM", "LPT", "GOAT", "FL", "CA", "IL", "PDFUA", "MACD", "HQ",
   "OP", "DJIA", "PS", "AH", "TL", "DR", "JAN", "FEB", "JUL", "AUG",
   "SEP", "SEPT", "OCT", "NOV", "DEC", "FDA", "IV", "ER", "IPO", "RISE"
   "IPA", "URL", "MILF", "BUT", "SSN", "FIFA", "USD", "CPU", "AT",
   "GG", "ELON"
]

def index(request):
    if request.GET.get("24H-submit") == "24H":
        print("24H")
        end_date = datetime.today() - timedelta(days = 1, microseconds=datetime.today().microsecond)
    elif request.GET.get("3D-submit") == "3_DAYS":
        print("3D")
        end_date = datetime.today() - timedelta(days = 3, microseconds=datetime.today().microsecond)
    else:
        print("Other")
    print(str(end_date))
    ticker_data = Ticker.objects.filter(date_posted = str(end_date))
    # .values('ticker').annotate(num_mentions=Count('ticker')).order_by('-num_mentions')[:10]
    print(ticker_data)
    return render(request, 'main/24hour.html', {'data' : ticker_data})
    
#Without Dollar Sign
def extract_ticker(post):
   reg_tickers = re.findall(r'[$][A-Z][\S]*', post)
   reg_tickers = [e[1:] for e in reg_tickers]
   other_tickers =  re.findall(r'\b[A-Z][a-zA-Z]{1,4}\b', post)
   all_tick = reg_tickers + other_tickers
   return all_tick

#Analyze post body
#Add - Incorporate score
def analyze(body):
   analyzer = SentimentIntensityAnalyzer()
   sentiment = analyzer.polarity_scores(body)
   if (sentiment["compound"] > .005) or (sentiment["pos"] > abs(sentiment["neg"])):
      return "Bullish"
   elif (sentiment["compound"] < -.005) or (abs(sentiment["neg"]) > sentiment["pos"]):
      return "Bearish"
   else:
      return "Neutral"

#Run
def run():
    d = datetime.today() - timedelta(days = days_back)
    start_epoch = int(d.timestamp())
    print(start_epoch)

    submission = api.search_submissions(after=start_epoch,
                                subreddit=['WallStreetBets'], limit = 10)

    for post in submission: #Loops thru reddit posts
        print(post.title)
        post_tickers = extract_ticker(post.title) #Returns list of tickers
        for tick in post_tickers: #Loops thru tickers in the returned list
            if tick.upper() in lookup and tick.upper() not in blacklist_words:
                t = Ticker(ticker = tick.upper(), date_posted = str(datetime.fromtimestamp(post.created_utc)), sentiment = analyze(post.title), sentence = post.title )
                t.save()
        post.comments.replace_more(limit=4) #Max 32 instances
        for top_level_comment in post.comments: #Loops thru comment in post
            comment_tickers = extract_ticker(top_level_comment.body)
            # print(top_level_comment.body)
            for tick in comment_tickers:
                if tick.upper() in lookup and tick.upper() not in blacklist_words:
                    t = Ticker(ticker = tick.upper(), date_posted = str(datetime.fromtimestamp(top_level_comment.created_utc)), sentiment = analyze(top_level_comment.body), sentence = top_level_comment.body )
                    t.save()
    return ticker_dict