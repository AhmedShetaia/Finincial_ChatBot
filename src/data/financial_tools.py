import yfinance as yf
from langchain_core.tools import tool
from typing import Dict, Any
import pandas as pd

@tool
def fetch_stock_price(ticker: str) -> Dict[str, Any]:
    """Fetch current stock price for a given ticker symbol."""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1d")
        if not hist.empty:
            current_price = hist["Close"].iloc[-1]
            return {
                "ticker": ticker, 
                "current_price": float(current_price),
                "status": "success"
            }
        else:
            return {"ticker": ticker, "error": "No data found", "status": "error"}
    except Exception as e:
        return {"ticker": ticker, "error": str(e), "status": "error"}

@tool
def fetch_historical_data(ticker: str, start_date: str, end_date: str) -> Dict[str, Any]:
    """Fetch historical stock data for a given ticker and date range."""
    try:
        stock = yf.Ticker(ticker)
        historical_data = stock.history(start=start_date, end=end_date)
        if not historical_data.empty:
            return {
                "ticker": ticker,
                "data": historical_data.to_dict(),
                "status": "success"
            }
        else:
            return {"ticker": ticker, "error": "No data found", "status": "error"}
    except Exception as e:
        return {"ticker": ticker, "error": str(e), "status": "error"}

@tool
def fetch_dividends(ticker: str) -> Dict[str, Any]:
    """Fetch dividend information for a given ticker."""
    try:
        stock = yf.Ticker(ticker)
        dividends = stock.dividends
        if not dividends.empty:
            return {
                "ticker": ticker,
                "dividends": dividends.to_dict(),
                "status": "success"
            }
        else:
            return {"ticker": ticker, "error": "No dividend data found", "status": "error"}
    except Exception as e:
        return {"ticker": ticker, "error": str(e), "status": "error"}

@tool
def fetch_market_data(index: str) -> Dict[str, Any]:
    """Fetch market index data."""
    try:
        index_data = yf.Ticker(index)
        hist = index_data.history(period="1d")
        if not hist.empty:
            market_price = hist["Close"].iloc[-1]
            return {
                "index": index, 
                "market_data": float(market_price),
                "status": "success"
            }
        else:
            return {"index": index, "error": "No data found", "status": "error"}
    except Exception as e:
        return {"index": index, "error": str(e), "status": "error"}

@tool
def fetch_currency_conversion(from_currency: str, to_currency: str) -> Dict[str, Any]:
    """Fetch currency conversion rate."""
    try:
        pair = f"{from_currency}{to_currency}=X"
        conversion_data = yf.Ticker(pair)
        hist = conversion_data.history(period="1d")
        if not hist.empty:
            conversion_rate = hist["Close"].iloc[-1]
            return {
                "from_currency": from_currency,
                "to_currency": to_currency,
                "rate": float(conversion_rate),
                "status": "success"
            }
        else:
            return {
                "from_currency": from_currency,
                "to_currency": to_currency,
                "error": "No conversion data found",
                "status": "error"
            }
    except Exception as e:
        return {
            "from_currency": from_currency,
            "to_currency": to_currency,
            "error": str(e),
            "status": "error"
        }

@tool
def fetch_company_info(ticker: str) -> Dict[str, Any]:
    """Fetch company information for a given ticker."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        if info:
            return {
                "ticker": ticker,
                "company_info": info,
                "status": "success"
            }
        else:
            return {"ticker": ticker, "error": "No company info found", "status": "error"}
    except Exception as e:
        return {"ticker": ticker, "error": str(e), "status": "error"}
