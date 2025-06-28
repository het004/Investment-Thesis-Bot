from INVESTMENT_THESIS.entity.config import ReportConfig
from INVESTMENT_THESIS.Logging.logger import logging

class ReportGenerator:
    def __init__(self, config: ReportConfig):
        logging.info("Initializing ReportGenerator")

    def generate_report(self, ticker, company_data, news, social_sentiment, financials, technicals, recommendation):
        logging.info(f"Generating report for {ticker}")
        try:
            # Header with current time
            from datetime import datetime
            from pytz import timezone
            ist = timezone("Asia/Kolkata")
            current_time = datetime.now(ist).strftime("%I:%M %p IST on %B %d, %Y")  # 04:16 PM IST on June 28, 2025
            report = f"# Investment Thesis Report for {ticker}\nGenerated on {current_time}\n\n"

            # Company Overview
            report += "## Company Overview\n"
            if company_data:
                for key, value in company_data.items():
                    if value is not None:
                        # Handle numeric values with proper formatting (avoiding ',' with 's' conflict)
                        if isinstance(value, (int, float)):
                            report += f"- {key.replace('_', ' ').title()}: {value:,.2f}\n"
                        else:
                            report += f"- {key.replace('_', ' ').title()}: {value}\n"
            else:
                report += "- No company data available\n"

            # News Summary
            report += "## News Summary\n"
            if news:
                report += "- Recent news highlights:\n"
                for article in news[:3]:  # Top 3 news items
                    report += f"  - {article['title']} ({article['source']})\n"
            else:
                report += "- No news data available\n"

            # Social Sentiment
            report += "## Social Sentiment\n"
            if social_sentiment:
                avg_sentiment = sum(s["vader_compound"] for s in social_sentiment) / len(social_sentiment)
                report += f"- Average sentiment score: {avg_sentiment:.2f}\n"
            else:
                report += "- No social sentiment data available\n"

            # Financials
            report += "## Financial Overview\n"
            if financials:
                report += "- Latest 10-K filing data available\n"
            else:
                report += "- No financial data available\n"

            # Technical Indicators
            report += "## Technical Indicators\n"
            if technicals and technicals.get("rsi") is not None:
                report += f"- RSI (14-day): {technicals['rsi']:.2f}\n"
            else:
                report += "- No technical data available\n"

            # Recommendation
            report += "## Recommendation\n"
            report += f"- {recommendation}\n"

            logging.info(f"Report generated successfully for {ticker}")
            return report
        except Exception as e:
            logging.error(f"Error generating report: {e}")
            return f"# Error Generating Report for {ticker}\n- Error: {str(e)}"
