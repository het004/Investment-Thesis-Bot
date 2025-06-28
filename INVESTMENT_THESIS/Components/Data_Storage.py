from pymongo import MongoClient
from INVESTMENT_THESIS.entity.config import DataStorageConfig
from datetime import datetime, timedelta
from INVESTMENT_THESIS.Logging.logger import logging
class DataStorage:
    def __init__(self, config: DataStorageConfig):
        logging.info("Initializing DataStorage")
        try:
            self.client = MongoClient(config.mongo_uri)
            self.db = self.client[config.mongo_db_name]
            self.config = config
            # Create indexes for performance
            self.db[self.config.mongo_collections["company_data"]].create_index([("ticker", 1)])
            self.db[self.config.mongo_collections["news"]].create_index([("ticker", 1), ("stored_at", -1)])
            self.db[self.config.mongo_collections["social_media"]].create_index([("ticker", 1), ("platform", 1)])
            self.db[self.config.mongo_collections["financials"]].create_index([("ticker", 1)])
            self.db[self.config.mongo_collections["recommendations"]].create_index([("ticker", 1)])
            self.db[self.config.mongo_collections["technicals"]].create_index([("ticker", 1), ("stored_at", -1)])
        except Exception as e:
            logging.error(f"Error connecting to MongoDB: {e}")
            raise

    def store_company_data(self, ticker, company_data):
        try:
            collection = self.db[self.config.mongo_collections["company_data"]]
            collection.update_one(
                {"ticker": ticker},
                {"$set": {"data": company_data, "updated_at": datetime.utcnow()}},
                upsert=True
            )
            logging.info(f"Stored company data for {ticker}")
        except Exception as e:
            logging.error(f"Error storing company data: {e}")

    def store_news(self, ticker, news_data):
        try:
            collection = self.db[self.config.mongo_collections["news"]]
            for news in news_data:
                news["ticker"] = ticker
                news["stored_at"] = datetime.utcnow()
                collection.insert_one(news)
            logging.info(f"Stored news for {ticker}")
        except Exception as e:
            logging.error(f"Error storing news: {e}")

    def store_social_media(self, ticker, social_data, platform):
        try:
            collection = self.db[self.config.mongo_collections["social_media"]]
            for item in social_data:
                item["ticker"] = ticker
                item["platform"] = platform
                item["stored_at"] = datetime.utcnow()
                collection.insert_one(item)
            logging.info(f"Stored {platform} data for {ticker}")
        except Exception as e:
            logging.error(f"Error storing social media data: {e}")

    def store_financials(self, ticker, financial_data):
        try:
            collection = self.db[self.config.mongo_collections["financials"]]
            financial_data["ticker"] = ticker
            financial_data["stored_at"] = datetime.utcnow()
            collection.insert_one(financial_data)
            logging.info(f"Stored financials for {ticker}")
        except Exception as e:
            logging.error(f"Error storing financials: {e}")

    def store_recommendation(self, ticker, recommendation):
        try:
            collection = self.db[self.config.mongo_collections["recommendations"]]
            recommendation["ticker"] = ticker
            recommendation["generated_at"] = datetime.utcnow()
            collection.insert_one(recommendation)
            logging.info(f"Stored recommendation for {ticker}")
        except Exception as e:
            logging.error(f"Error storing recommendation: {e}")

    def store_technicals(self, ticker, technical_data):
        try:
            collection = self.db[self.config.mongo_collections["technicals"]]
            technical_data["ticker"] = ticker
            technical_data["stored_at"] = datetime.utcnow()
            collection.insert_one(technical_data)
            logging.info(f"Stored technicals for {ticker}")
        except Exception as e:
            logging.error(f"Error storing technicals: {e}")

    def get_cached_technicals(self, ticker):
        try:
            collection = self.db[self.config.mongo_collections["technicals"]]
            one_hour_ago = datetime.utcnow() - timedelta(hours=1)
            cached = collection.find_one({"ticker": ticker, "stored_at": {"$gte": one_hour_ago}})
            return cached.get("data") if cached else None
        except Exception as e:
            logging.error(f"Error retrieving cached technicals: {e}")
            return None