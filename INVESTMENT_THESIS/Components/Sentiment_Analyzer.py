from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from INVESTMENT_THESIS.entity.config import SentimentAnalysisConfig
from INVESTMENT_THESIS.Logging.logger import logging


class SentimentAnalyzer:
    def __init__(self, config: SentimentAnalysisConfig):
        logging.info("Initializing SentimentAnalyzer")
        self.vader = SentimentIntensityAnalyzer()

    def analyze_news(self, news_data):
        logging.info("Analyzing news sentiment")
        try:
            sentiments = []
            for news in news_data:
                text = f"{news['title']} {news['description']}"
                blob = TextBlob(text)
                vader_score = self.vader.polarity_scores(text)
                sentiments.append({
                    "title": news["title"],
                    "textblob_polarity": blob.sentiment.polarity,
                    "vader_compound": vader_score["compound"]
                })
            return sentiments
        except Exception as e:
            logging.error(f"Error analyzing news sentiment: {e}")
            return []

    def analyze_social_media(self, social_data):
        logging.info("Analyzing social media sentiment")
        try:
            sentiments = []
            for item in social_data:
                text = item.get("title", "") + " " + item.get("text", item.get("text", ""))
                blob = TextBlob(text)
                vader_score = self.vader.polarity_scores(text)
                sentiments.append({
                    "text": text[:50],
                    "textblob_polarity": blob.sentiment.polarity,
                    "vader_compound": vader_score["compound"]
                })
            return sentiments
        except Exception as e:
            logging.error(f"Error analyzing social media sentiment: {e}")
            return []