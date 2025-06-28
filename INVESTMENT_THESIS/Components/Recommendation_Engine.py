from INVESTMENT_THESIS.entity.config import RecommendationConfig
from INVESTMENT_THESIS.Logging.logger import logging

class RecommendationEngine:
    def __init__(self, config: RecommendationConfig):
        logging.info("Initializing RecommendationEngine")

    def generate_recommendation(self, financials, technicals, news_sentiment, social_sentiment):
        logging.info("Generating recommendation")
        try:
            score = 0

            # Financials: Low P/E and high dividend yield are positive
            if financials.get("pe_ratio") and financials["pe_ratio"] < 15:
                score += 1
            if financials.get("dividend_yield") and financials["dividend_yield"] > 0.03:
                score += 1

            # Technicals: RSI < 30 (oversold) is positive, RSI > 70 (overbought) is negative
            if technicals.get("rsi") and technicals["rsi"] < 30:
                score += 1
            elif technicals.get("rsi") and technicals["rsi"] > 70:
                score -= 1

            # Sentiment: Positive news and social media sentiment are positive
            avg_news_sentiment = sum(s["vader_compound"] for s in news_sentiment) / len(news_sentiment) if news_sentiment else 0
            avg_social_sentiment = sum(s["vader_compound"] for s in social_sentiment) / len(social_sentiment) if social_sentiment else 0
            if avg_news_sentiment > 0.2:
                score += 1
            elif avg_news_sentiment < -0.2:
                score -= 1
            if avg_social_sentiment > 0.2:
                score += 1
            elif avg_social_sentiment < -0.2:
                score -= 1

            # Recommendation logic
            if score >= 2:
                recommendation = "Buy"
            elif score <= -2:
                recommendation = "Sell"
            else:
                recommendation = "Hold"
            logging.info(f"Recommendation: {recommendation}")
            return recommendation
        except Exception as e:
            logging.error(f"Error generating recommendation: {e}")
            return "Hold"