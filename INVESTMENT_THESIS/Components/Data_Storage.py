from pymongo import MongoClient
from INVESTMENT_THESIS.entity.config import DataStorageConfig
from datetime import datetime
from INVESTMENT_THESIS.Logging.logger import logging


class DataStorage:
    def __init__(self, config: DataStorageConfig):
        logging.info("Initializing DataStorage")
        try:
            self.client = MongoClient(config.mongo_uri)
            self.db = self.client[config.mongo_db_name]
            self.config = config  # Store config for use in methods
        except Exception as e:
            logging.error(f"Error connecting to MongoDB: {e}")
            raise

    def store_company_data(self, ticker, company_data):
        try:
            collection = self.db[self.config.mongo_collections["company_data"]]  # Fixed: config -> self.config
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
            collection = self.db[self.config.mongo_collections["news"]]  # Fixed: config -> self.config
            for news in news_data:
                news["ticker"] = ticker
                news["stored_at"] = datetime.utcnow()
                collection.insert_one(news)
            logging.info(f"Stored news for {ticker}")
        except Exception as e:
            logging.error(f"Error storing news: {e}")

    def store_social_media(self, ticker, social_data, platform):
        try:
            collection = self.db[self.config.mongo_collections["social_media"]]  # Fixed: config -> self.config
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
            collection = self.db[self.config.mongo_collections["financials"]]  # Fixed: config -> self.config
            financial_data["ticker"] = ticker
            financial_data["stored_at"] = datetime.utcnow()
            collection.insert_one(financial_data)
            logging.info(f"Stored financials for {ticker}")
        except Exception as e:
            logging.error(f"Error storing financials: {e}")

    def store_recommendation(self, ticker, recommendation):
        try:
            collection = self.db[self.config.mongo_collections["recommendations"]]  # Fixed: config -> self.config
            recommendation["ticker"] = ticker
            recommendation["generated_at"] = datetime.utcnow()
            collection.insert_one(recommendation)
            logging.info(f"Stored recommendation for {ticker}")
        except Exception as e:
            logging.error(f"Error storing recommendation: {e}")