from datetime import datetime
from INVESTMENT_THESIS.entity.config import ReportConfig
from INVESTMENT_THESIS.Logging.logger import logging

class ReportGenerator:
    def __init__(self, config: ReportConfig):
        logging.info("Initializing ReportGenerator")

    def generate_report(self, ticker, company_data, news, social_media, financials, technicals, recommendation):
        logging.info(f"Generating report for {ticker}")
        try:
            report = f"# Investment Thesis Report for {ticker}\n\n"
            report += f"**Generated on**: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n"
            
            report += "## Company Overview\n"
            report += f"- **Market Cap**: ${company_data.get('market_cap', 'N/A'):,}\n"
            report += f"- **P/E Ratio**: {company_data.get('pe_ratio', 'N/A')}\n"
            report += f"- **Dividend Yield**: {company_data.get('dividend_yield', 'N/A')}\n"
            report += f"- **52-Week High/Low**: ${company_data.get('52_week_high', 'N/A')} / ${company_data.get('52_week_low', 'N/A')}\n\n"
            
            report += "## Recent News\n"
            for article in news[:3]:
                report += f"- **{article['title']}** ({article['source']}): {article['description'][:100]}...\n"
            
            report += "\n## Social Media Sentiment\n"
            for item in social_media[:3]:
                report += f"- **{item['platform']}**: {item['text'][:50]}... (Sentiment: {item['vader_compound']:.2f})\n"
            
            report += "\n## Technical Indicators\n"
            report += f"- **RSI (14-day)**: {technicals.get('rsi', 'N/A')}\n"
            
            report += "\n## Recommendation\n"
            report += f"**{recommendation}**\n"
            
            logging.info(f"Report generated successfully for {ticker}")
            return report
        except Exception as e:
            logging.error(f"Error generating report: {e}")
            return f"Error generating report for {ticker}"