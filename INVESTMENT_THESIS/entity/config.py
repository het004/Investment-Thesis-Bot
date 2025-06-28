import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class PipelineConfig:
    def __init__(self):
        self.mongo_db_name = os.getenv("MONGO_DB_NAME", "investment_bot")
        self.mongo_collections = {
            "company_data": "company_data",
            "news": "news",
            "social_media": "social_media",
            "financials": "financials",
            "recommendations": "recommendations"
        }

class DataIngestionConfig:
    def __init__(self, pipeline_config: PipelineConfig):
        self.newsapi_key = os.getenv("NEWSAPI_KEY")
        self.reddit_client_id = os.getenv("REDDIT_CLIENT_ID")
        self.reddit_client_secret = os.getenv("REDDIT_CLIENT_SECRET")
        self.reddit_user_agent = os.getenv("REDDIT_USER_AGENT")
        self.twitter_bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
        self.alpha_vantage_key = os.getenv("ALPHA_VANTAGE_KEY")
        self.sec_api_key = os.getenv("SEC_API_KEY")
        self.mongo_uri = os.getenv("MONGO_URI")

class DataStorageConfig:
    def __init__(self, pipeline_config: PipelineConfig):
        self.mongo_uri = os.getenv("MONGO_URI")
        self.mongo_db_name = pipeline_config.mongo_db_name
        self.mongo_collections = pipeline_config.mongo_collections

class SentimentAnalysisConfig:
    def __init__(self, pipeline_config: PipelineConfig):
        pass  # No specific config needed for sentiment analysis

class RecommendationConfig:
    def __init__(self, pipeline_config: PipelineConfig):
        pass  # No specific config needed for recommendation

class ReportConfig:
    def __init__(self, pipeline_config: PipelineConfig):
        pass  # No specific config needed for report generation