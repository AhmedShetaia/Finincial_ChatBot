from typing import Dict, Any, List
from src.models.financial_model import FinancialState
from src.data.financial_tools import (
    fetch_stock_price, fetch_historical_data, fetch_dividends,
    fetch_market_data, fetch_currency_conversion, fetch_company_info
)
from langchain_core.messages import AIMessage, HumanMessage
import json

class FinancialService:
    @staticmethod
    def collect_financial_info(state: FinancialState) -> AIMessage:
        """Dynamically ask for the missing financial information"""
        missing_info = []
        
        if state.get("income") is None:
            missing_info.append("monthly income")
        if state.get("expenses") is None:
            missing_info.append("monthly expenses")
        if state.get("financial_goals") is None:
            missing_info.append("financial goals")
        if state.get("budgeting_details") is None:
            missing_info.append("budgeting details")
        
        return FinancialService.generate_ai_response(missing_info)
    
    @staticmethod
    def generate_ai_response(missing_info: List[str]) -> AIMessage:
        """Generate AI response based on missing information"""
        if missing_info:
            # Ask for missing financial information
            return AIMessage(content=f"I'd be happy to help you with your financial planning! To provide you with the best advice, I need some information about your: {', '.join(missing_info)}. Could you please share these details?")
        else:
            # If no missing info, proceed
            return AIMessage(content="Great! I have all the necessary information. Let me help you with your financial planning based on your profile.")
    
    @staticmethod
    async def get_stock_analysis(ticker: str) -> Dict[str, Any]:
        """Get comprehensive stock analysis"""
        try:
            # Get current price
            price_data = fetch_stock_price.invoke({"ticker": ticker})
            
            # Get company info
            company_data = fetch_company_info.invoke({"ticker": ticker})
            
            # Get dividend info
            dividend_data = fetch_dividends.invoke({"ticker": ticker})
            
            analysis = {
                "ticker": ticker,
                "current_price": price_data,
                "company_info": company_data,
                "dividends": dividend_data,
                "recommendation": FinancialService._generate_stock_recommendation(price_data, company_data, dividend_data)
            }
            
            return analysis
        except Exception as e:
            return {"error": str(e), "ticker": ticker}
    
    @staticmethod
    def _generate_stock_recommendation(price_data: Dict, company_data: Dict, dividend_data: Dict) -> str:
        """Generate basic stock recommendation based on available data"""
        if price_data.get("status") == "error":
            return "Unable to analyze - stock data unavailable"
        
        recommendation = f"Based on current data for {price_data.get('ticker', 'the stock')}:\n"
        recommendation += f"Current Price: ${price_data.get('current_price', 'N/A')}\n"
        
        if company_data.get("status") == "success":
            info = company_data.get("company_info", {})
            if "longBusinessSummary" in info:
                recommendation += f"Company: {info.get('longName', 'N/A')}\n"
                recommendation += f"Sector: {info.get('sector', 'N/A')}\n"
        
        if dividend_data.get("status") == "success":
            recommendation += "This stock pays dividends, which could provide regular income.\n"
        
        recommendation += "\nPlease consult with a financial advisor for personalized investment advice."
        
        return recommendation
    
    @staticmethod
    async def get_market_overview(indices: List[str] = None) -> Dict[str, Any]:
        """Get market overview for major indices"""
        if indices is None:
            indices = ["^GSPC", "^DJI", "^IXIC"]  # S&P 500, Dow Jones, NASDAQ
        
        market_data = {}
        for index in indices:
            try:
                data = fetch_market_data.invoke({"index": index})
                market_data[index] = data
            except Exception as e:
                market_data[index] = {"error": str(e)}
        
        return market_data
    
    @staticmethod
    async def get_currency_rates(base_currency: str = "USD", target_currencies: List[str] = None) -> Dict[str, Any]:
        """Get currency conversion rates"""
        if target_currencies is None:
            target_currencies = ["EUR", "GBP", "JPY", "CAD"]
        
        rates = {}
        for currency in target_currencies:
            try:
                rate_data = fetch_currency_conversion.invoke({
                    "from_currency": base_currency,
                    "to_currency": currency
                })
                rates[f"{base_currency}/{currency}"] = rate_data
            except Exception as e:
                rates[f"{base_currency}/{currency}"] = {"error": str(e)}
        
        return rates
