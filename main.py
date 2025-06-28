from INVESTMENT_THESIS.entity.config import PipelineConfig, DataIngestionConfig, DataStorageConfig, SentimentAnalysisConfig, RecommendationConfig, ReportConfig
from INVESTMENT_THESIS.Components.Data_Fetcher import DataFetcher


from INVESTMENT_THESIS.Logging.logger import logging


def main():
    try:
        # Initialize pipeline configuration
        pipeline_config = PipelineConfig()
        data_ingestion_config = DataIngestionConfig(pipeline_config)
        data_storage_config = DataStorageConfig(pipeline_config)

        # Initialize modules
        logging.info("Initializing pipeline components")
        data_fetcher = DataFetcher(data_ingestion_config)
    


        # Get user input
        ticker = input("Enter company ticker or name: ").upper()
        logging.info(f"Starting analysis for {ticker}")

        # Data ingestion
        logging.info("Initiating data ingestion")
        company_data = data_fetcher.fetch_yahoo_finance_data(ticker)
        news = data_fetcher.fetch_news(ticker)
        reddit_posts = data_fetcher.fetch_reddit_posts(ticker)
        twitter_posts = data_fetcher.fetch_twitter_posts(ticker)
        financials = data_fetcher.fetch_sec_filings(ticker)
        technicals = data_fetcher.fetch_technical_indicators(ticker)





    except Exception as e:
        logging.error(f"Pipeline error: {e}")
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()