from INVESTMENT_THESIS.entity.config import PipelineConfig, DataIngestionConfig, DataStorageConfig, SentimentAnalysisConfig, RecommendationConfig, ReportConfig
from INVESTMENT_THESIS.Components.Data_Fetcher import DataFetcher
from INVESTMENT_THESIS.Components.Data_Storage import DataStorage
from INVESTMENT_THESIS.Components.Sentiment_Analyzer import SentimentAnalyzer
from INVESTMENT_THESIS.Components.Recommendation_Engine import RecommendationEngine
from INVESTMENT_THESIS.Components.Report_Genrator import ReportGenerator

from INVESTMENT_THESIS.Logging.logger import logging


def main():
    try:
        # Initialize pipeline configuration
        pipeline_config = PipelineConfig()
        data_ingestion_config = DataIngestionConfig(pipeline_config)
        data_storage_config = DataStorageConfig(pipeline_config)
        sentiment_analysis_config = SentimentAnalysisConfig(pipeline_config)
        recommendation_config = RecommendationConfig(pipeline_config)
        report_config = ReportConfig(pipeline_config)

        # Initialize modules
        logging.info("Initializing pipeline components")
        data_fetcher = DataFetcher(data_ingestion_config)
        data_storage = DataStorage(data_storage_config)
        sentiment_analyzer = SentimentAnalyzer(sentiment_analysis_config)
        recommendation_engine = RecommendationEngine(recommendation_config)
        report_generator = ReportGenerator(report_config)


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


        # Sentiment analysis
        logging.info("Performing sentiment analysis")
        news_sentiment = sentiment_analyzer.analyze_news(news)
        social_sentiment = sentiment_analyzer.analyze_social_media(reddit_posts + twitter_posts)


        # Data storage
        logging.info("Storing data in MongoDB")
        data_storage.store_company_data(ticker, company_data)
        data_storage.store_news(ticker, news)
        data_storage.store_social_media(ticker, reddit_posts, "Reddit")
        data_storage.store_social_media(ticker, twitter_posts, "Twitter")
        data_storage.store_financials(ticker, financials)

        # Generate recommendation
        logging.info("Generating recommendation")
        recommendation = recommendation_engine.generate_recommendation(company_data, technicals, news_sentiment, social_sentiment)
        data_storage.store_recommendation(ticker, {"recommendation": recommendation})

        # Generate report
        logging.info("Generating final report")
        report = report_generator.generate_report(ticker, company_data, news, social_sentiment, financials, technicals, recommendation)
        print(report)


    except Exception as e:
        logging.error(f"Pipeline error: {e}")
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()