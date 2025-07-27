from fastapi import FastAPI, Form, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from INVESTMENT_THESIS.entity.config import PipelineConfig, DataIngestionConfig, DataStorageConfig, SentimentAnalysisConfig, RecommendationConfig, ReportConfig
from INVESTMENT_THESIS.Components.Data_Fetcher import DataFetcher
from INVESTMENT_THESIS.Components.Data_Storage import DataStorage
from INVESTMENT_THESIS.Components.Sentiment_Analyzer import SentimentAnalyzer
from INVESTMENT_THESIS.Components.Recommendation_Engine import RecommendationEngine
from INVESTMENT_THESIS.Components.Report_Genrator import ReportGenerator
from INVESTMENT_THESIS.Logging.logger import logging
from datetime import datetime
from pytz import timezone
from typing import Optional
import re
import pdfkit

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
ist = timezone("Asia/Kolkata")

# Helper to split the report into HTML chunks
def extract_sections(report: str) -> dict:
    def section(name):
        pattern = fr"<h2>{re.escape(name)}</h2>(.*?)(?=<h2>|</div>|$)"
        match = re.search(pattern, report, re.DOTALL)
        return match.group(1).strip() if match else "<p>No data available.</p>"
    return {
        "overview": section("Company Overview"),
        "news": section("News Summary"),
        "sentiment": section("Social Sentiment"),
        "financials": section("Financial Overview"),
        "technicals": section("Technical Indicators"),
        "recommendation": section("Final Recommendation")
    }

def run_pipeline(ticker: str) -> dict:
    try:
        current_time = datetime.now(ist).strftime("%I:%M %p IST on %B %d, %Y")
        pipeline_config = PipelineConfig()
        data_ingestion_config = DataIngestionConfig(pipeline_config)
        data_storage_config = DataStorageConfig(pipeline_config)
        sentiment_analysis_config = SentimentAnalysisConfig(pipeline_config)
        recommendation_config = RecommendationConfig(pipeline_config)
        report_config = ReportConfig(pipeline_config)

        logging.info("Initializing pipeline components")
        data_fetcher = DataFetcher(data_ingestion_config)
        data_storage = DataStorage(data_storage_config)
        sentiment_analyzer = SentimentAnalyzer(sentiment_analysis_config)
        recommendation_engine = RecommendationEngine(recommendation_config)
        report_generator = ReportGenerator(report_config)

        logging.info(f"Starting analysis for {ticker}")
        collection = data_storage.db[data_storage.config.mongo_collections["recommendations"]]
        today = datetime.now(ist).replace(hour=0, minute=0, second=0, microsecond=0)
        cached_recommendation = collection.find_one({"ticker": ticker, "generated_at": {"$gte": today}})
        if cached_recommendation:
            report = report_generator.generate_report(
                ticker, {}, [], [], {}, {"rsi": None}, cached_recommendation["recommendation"]
            )
            last_update = cached_recommendation["generated_at"].astimezone(ist).strftime("%I:%M %p IST")
            return {"status": "success", "report": report, "ticker": ticker, "last_update": last_update}

        logging.info("Initiating data ingestion")
        company_data = data_fetcher.fetch_yahoo_finance_data(ticker)
        news = data_fetcher.fetch_news(ticker)
        reddit_posts = data_fetcher.fetch_reddit_posts(ticker)
        twitter_posts = data_fetcher.fetch_twitter_posts(ticker)
        financials = data_fetcher.fetch_sec_filings(ticker)
        technicals = data_fetcher.fetch_technical_indicators(ticker, storage=data_storage)

        logging.info("Performing sentiment analysis")
        news_sentiment = sentiment_analyzer.analyze_news(news)
        social_sentiment = sentiment_analyzer.analyze_social_media(reddit_posts + twitter_posts)

        logging.info("Storing data in MongoDB")
        data_storage.store_company_data(ticker, company_data)
        data_storage.store_news(ticker, news)
        data_storage.store_social_media(ticker, reddit_posts, "Reddit")
        data_storage.store_social_media(ticker, twitter_posts, "Twitter")
        data_storage.store_financials(ticker, financials)
        data_storage.store_technicals(ticker, technicals)

        logging.info("Generating recommendation")
        recommendation = recommendation_engine.generate_recommendation(company_data, technicals, news_sentiment, social_sentiment)
        data_storage.store_recommendation(ticker, {"recommendation": recommendation})

        logging.info("Generating final report")
        report = report_generator.generate_report(
            ticker, company_data, news, social_sentiment, financials, technicals, recommendation
        ).replace("Generated on", f"Generated on {current_time}")
        return {"status": "success", "report": report, "ticker": ticker, "last_update": current_time}
    except Exception as e:
        logging.error(f"Pipeline error: {e}")
        return {"status": "error", "message": str(e), "ticker": ticker}

@app.get("/")
async def get_index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/generate-report")
async def generate_report(request: Request, ticker: str = Form(...)):
    if not re.match("^[A-Za-z0-9.-]+$", ticker):
        return templates.TemplateResponse("index.html", {"request": request, "error": "Invalid ticker format."})
    result = run_pipeline(ticker)
    if result["status"] == "success":
        sections = extract_sections(result["report"])
        return templates.TemplateResponse(
            "report.html",
            {
                "request": request,
                "ticker": result["ticker"],
                "last_update": result["last_update"],
                **sections
            }
        )
    else:
        return templates.TemplateResponse("report.html", {"request": request, "ticker": None})

@app.get("/api/report/{ticker}", summary="Get Investment Thesis Report", description="Returns a detailed investment report for the given ticker symbol.")
async def get_report(ticker: str):
    return run_pipeline(ticker)

@app.get("/download-report/{ticker}")
async def download_report(ticker: str):
    result = run_pipeline(ticker)
    if result["status"] != "success":
        raise HTTPException(status_code=500, detail=result["message"])
    report_html = result["report"]
    file_path = f"{ticker}_report.pdf"
    

    try:
        pdfkit.from_string(report_html, file_path)
        return FileResponse(file_path, media_type='application/pdf', filename=file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {e}")

if __name__ == "__main__":
    pass  # For deployment on Render 
    # import uvicorn
    # uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)