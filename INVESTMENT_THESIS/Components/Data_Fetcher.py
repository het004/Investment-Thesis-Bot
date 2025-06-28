import requests
import praw
import tweepy
from sec_api import QueryApi
import yfinance as yf
from datetime import datetime, timedelta
import time
from INVESTMENT_THESIS.entity.config import DataIngestionConfig
from INVESTMENT_THESIS.Logging.logger import logging

class DataFetcher:
    def __init__(self, config: DataIngestionConfig):
        logging.info("Initializing DataFetcher")
        self.reddit = praw.Reddit(
            client_id=config.reddit_client_id,
            client_secret=config.reddit_client_secret,
            user_agent=config.reddit_user_agent
        )
        self.twitter = tweepy.Client(bearer_token=config.twitter_bearer_token)
        self.sec_query_api = QueryApi(api_key=config.sec_api_key)
        self.newsapi_key = config.newsapi_key
        self.alpha_vantage_key = config.alpha_vantage_key

    def fetch_news(self, company_name, limit=10):
        logging.info(f"Fetching news for {company_name}")
        try:
            url = f"https://newsapi.org/v2/everything?q={company_name}&apiKey={self.newsapi_key}&language=en&sortBy=publishedAt"
            response = requests.get(url)
            if response.status_code == 200:
                articles = response.json().get("articles", [])[:limit]
                return [
                    {
                        "title": article["title"],
                        "description": article["description"] or "",
                        "publishedAt": article["publishedAt"],
                        "source": article["source"]["name"]
                    }
                    for article in articles
                ]
            return []
        except Exception as e:
            logging.error(f"Error fetching news: {e}")
            return []

    def fetch_reddit_posts(self, company_name, subreddits=["wallstreetbets", "stocks", "investing"], limit=10):
        logging.info(f"Fetching Reddit posts for {company_name}")
        try:
            posts = []
            for subreddit in subreddits:
                subreddit_instance = self.reddit.subreddit(subreddit)
                for submission in subreddit_instance.search(company_name, limit=limit):
                    posts.append({
                        "title": submission.title,
                        "body": submission.selftext,
                        "score": submission.score,
                        "created_at": datetime.fromtimestamp(submission.created_utc)
                    })
            return posts
        except Exception as e:
            logging.error(f"Error fetching Reddit posts: {e}")
            return []

    def fetch_twitter_posts(self, company_name, limit=10):
        logging.info(f"Fetching Twitter posts for {company_name}")
        try:
            query = f"{company_name} lang:en"
            tweets = self.twitter.search_recent_tweets(query=query, max_results=limit)
            if tweets.data:
                return [
                    {
                        "text": tweet.text,
                        "created_at": tweet.created_at
                    }
                    for tweet in tweets.data
                ]
            return []
        except Exception as e:
            logging.error(f"Error fetching Twitter posts: {e}")
            return []

    def fetch_sec_filings(self, ticker):
        logging.info(f"Fetching SEC filings for {ticker}")
        try:
            query = {
                "query": f"ticker:{ticker} AND formType:\"10-K\"",
                "from": "0",
                "size": "1",
                "sort": [{"filedAt": {"order": "desc"}}]
            }
            filings = self.sec_query_api.get_filings(query)
            return filings.get("filings", [])[0] if filings.get("filings") else {}
        except Exception as e:
            logging.error(f"Error fetching SEC filings: {e}")
            return {}

    def fetch_yahoo_finance_data(self, ticker):
        logging.info(f"Fetching Yahoo Finance data for {ticker}")
        try:
            stock = yf.Ticker(ticker)
            return {
                "price": stock.info.get("regularMarketPrice"),
                "market_cap": stock.info.get("marketCap"),
                "pe_ratio": stock.info.get("trailingPE"),
                "dividend_yield": stock.info.get("dividendYield"),
                "52_week_high": stock.info.get("fiftyTwoWeekHigh"),
                "52_week_low": stock.info.get("fiftyTwoWeekLow")
            }
        except Exception as e:
            logging.error(f"Error fetching Yahoo Finance data: {e}")
            return {}

    def fetch_technical_indicators(self, ticker, storage=None):
        logging.info(f"Fetching technical indicators for {ticker}")
        try:
            # Check cache if storage is provided
            if storage:
                cached = storage.get_cached_technicals(ticker)
                if cached:
                    logging.info(f"Using cached technicals for {ticker}")
                    return cached

            url = f"https://www.alphavantage.co/query?function=RSI&symbol={ticker}&interval=daily&time_period=14&series_type=close&apikey={self.alpha_vantage_key}"
            response = requests.get(url)
            if response.status_code != 200:
                logging.error(f"Alpha Vantage API returned status code {response.status_code}: {response.text}")
                return {"rsi": None}

            data = response.json()
            logging.debug(f"Alpha Vantage response: {data}")

            # Check for API error messages
            if "Error Message" in data:
                logging.error(f"Alpha Vantage error: {data['Error Message']}")
                return {"rsi": None}
            if "Note" in data and "rate limit" in data["Note"].lower():
                logging.warning("Alpha Vantage rate limit reached. Waiting 60 seconds...")
                time.sleep(60)
                response = requests.get(url)
                data = response.json()

            rsi_data = data.get("Technical Analysis: RSI", {})
            if not rsi_data:
                logging.error("No RSI data returned by Alpha Vantage")
                return {"rsi": None}

            latest_date = max(rsi_data.keys())
            technical_data = {"rsi": float(rsi_data[latest_date]["RSI"])}

            # Store in cache if storage is provided
            if storage:
                storage.store_technicals(ticker, technical_data)
            return technical_data
        except Exception as e:
            logging.error(f"Error fetching technical indicators: {e}")
            return {"rsi": None}