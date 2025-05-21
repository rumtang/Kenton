#!/usr/bin/env python3
"""
Financial Modeling Prep API Tools Module
Provides financial data tools using the new API integration framework.
"""

import os
import logging
import requests
import json
from typing import Dict, Any, Optional

# Import the utility functions from the template
from tools.api_tool_template import (
    with_retry, validate_api_key, format_response, 
    DEFAULT_TIMEOUT, AgentExecutionError, create_api_key_error
)

# Try to import agents SDK, but provide fallback if not available
try:
    from agents import function_tool
except ImportError:
    from tools.api_tool_template import function_tool

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Base URL for Financial Modeling Prep API
BASE_URL = "https://financialmodelingprep.com/api/v3"

@function_tool
@with_retry(max_retries=2)
def company_profile(symbol: str) -> Dict[str, Any]:
    """
    Get comprehensive company profile information.
    
    Args:
        symbol: The stock ticker symbol of the company (e.g., AAPL, MSFT)
        
    Returns:
        Formatted company profile data
    """
    return _make_fmp_request(
        endpoint=f"/profile/{symbol}",
        params={},
        description="Company profile information"
    )

@function_tool
@with_retry(max_retries=2)
def income_statement(symbol: str, period: str = "annual", limit: int = 5) -> Dict[str, Any]:
    """
    Get company income statements.
    
    Args:
        symbol: The stock ticker symbol of the company (e.g., AAPL, MSFT)
        period: Data period - 'annual' or 'quarter'
        limit: Number of statements to return
        
    Returns:
        Formatted income statement data
    """
    return _make_fmp_request(
        endpoint=f"/income-statement/{symbol}",
        params={"period": period, "limit": limit},
        description="Income statement data"
    )

@function_tool
@with_retry(max_retries=2)
def balance_sheet(symbol: str, period: str = "annual", limit: int = 5) -> Dict[str, Any]:
    """
    Get company balance sheets.
    
    Args:
        symbol: The stock ticker symbol of the company (e.g., AAPL, MSFT)
        period: Data period - 'annual' or 'quarter'
        limit: Number of statements to return
        
    Returns:
        Formatted balance sheet data
    """
    return _make_fmp_request(
        endpoint=f"/balance-sheet-statement/{symbol}",
        params={"period": period, "limit": limit},
        description="Balance sheet data"
    )

@function_tool
@with_retry(max_retries=2)
def cash_flow(symbol: str, period: str = "annual", limit: int = 5) -> Dict[str, Any]:
    """
    Get company cash flow statements.
    
    Args:
        symbol: The stock ticker symbol of the company (e.g., AAPL, MSFT)
        period: Data period - 'annual' or 'quarter'
        limit: Number of statements to return
        
    Returns:
        Formatted cash flow statement data
    """
    return _make_fmp_request(
        endpoint=f"/cash-flow-statement/{symbol}",
        params={"period": period, "limit": limit},
        description="Cash flow statement data"
    )

@function_tool
@with_retry(max_retries=2)
def key_metrics(symbol: str, period: str = "annual", limit: int = 5) -> Dict[str, Any]:
    """
    Get key financial metrics for a company.
    
    Args:
        symbol: The stock ticker symbol of the company (e.g., AAPL, MSFT)
        period: Data period - 'annual' or 'quarter'
        limit: Number of periods to return
        
    Returns:
        Formatted key metrics data
    """
    return _make_fmp_request(
        endpoint=f"/key-metrics/{symbol}",
        params={"period": period, "limit": limit},
        description="Key financial metrics"
    )

@function_tool
@with_retry(max_retries=2)
def financial_ratios(symbol: str, period: str = "annual", limit: int = 5) -> Dict[str, Any]:
    """
    Get financial ratios for a company.
    
    Args:
        symbol: The stock ticker symbol of the company (e.g., AAPL, MSFT)
        period: Data period - 'annual' or 'quarter'
        limit: Number of periods to return
        
    Returns:
        Formatted financial ratios data
    """
    return _make_fmp_request(
        endpoint=f"/ratios/{symbol}",
        params={"period": period, "limit": limit},
        description="Financial ratios"
    )

@function_tool
@with_retry(max_retries=2)
def stock_price(symbol: str) -> Dict[str, Any]:
    """
    Get current stock price data.
    
    Args:
        symbol: The stock ticker symbol of the company (e.g., AAPL, MSFT)
        
    Returns:
        Formatted stock price data
    """
    return _make_fmp_request(
        endpoint=f"/quote/{symbol}",
        params={},
        description="Current stock price data"
    )

@function_tool
@with_retry(max_retries=2)
def historical_price(symbol: str, from_date: str = None, to_date: str = None, 
                    timeseries: int = None) -> Dict[str, Any]:
    """
    Get historical stock price data.
    
    Args:
        symbol: The stock ticker symbol of the company (e.g., AAPL, MSFT)
        from_date: Start date in YYYY-MM-DD format
        to_date: End date in YYYY-MM-DD format
        timeseries: Number of data points to return
        
    Returns:
        Formatted historical price data
    """
    params = {}
    if from_date:
        params["from"] = from_date
    if to_date:
        params["to"] = to_date
    if timeseries:
        params["timeseries"] = timeseries
        
    return _make_fmp_request(
        endpoint=f"/historical-price-full/{symbol}",
        params=params,
        description="Historical stock price data"
    )

@function_tool
@with_retry(max_retries=2)
def stock_news(tickers: str = None, limit: int = 10) -> Dict[str, Any]:
    """
    Get news articles related to specific stocks.
    
    Args:
        tickers: Comma-separated list of stock ticker symbols (e.g., "AAPL,MSFT")
        limit: Maximum number of news articles to return
        
    Returns:
        Formatted stock news data
    """
    params = {"limit": limit}
    if tickers:
        params["tickers"] = tickers
        
    return _make_fmp_request(
        endpoint="/stock_news",
        params=params,
        description="Stock-specific news articles"
    )

@function_tool
@with_retry(max_retries=2)
def market_news(limit: int = 10, page: int = 0) -> Dict[str, Any]:
    """
    Get general market news articles.
    
    Args:
        limit: Maximum number of news articles to return
        page: Page number for pagination
        
    Returns:
        Formatted market news data
    """
    return _make_fmp_request(
        endpoint="/stock_market/news",
        params={"limit": limit, "page": page},
        description="General market news articles"
    )

def _make_fmp_request(endpoint: str, params: Dict[str, Any], description: str) -> Dict[str, Any]:
    """
    Make a request to the Financial Modeling Prep API.
    
    Args:
        endpoint: API endpoint path
        params: Query parameters
        description: Description of the data being requested
        
    Returns:
        Formatted API response
    """
    # Get API key from environment
    api_key = os.environ.get("MARKET_DATA_KEY", "")
    
    # Validate API key
    try:
        validate_api_key(api_key, "Financial Modeling Prep")
    except AgentExecutionError as e:
        return {"error": str(e), "status": "error"}
    
    # Add API key to parameters
    params["apikey"] = api_key
    
    # Set up request
    url = f"{BASE_URL}{endpoint}"
    
    try:
        # Make the request
        logger.info(f"Making FMP API request to {url} with params: {params}")
        response = requests.get(url, params=params, timeout=DEFAULT_TIMEOUT)
        
        # Check response status
        response.raise_for_status()
        
        # Parse response
        try:
            data = response.json()
        except json.JSONDecodeError:
            return {
                "error": "Invalid JSON response",
                "status": "error",
                "response": response.text
            }
        
        # Check for empty response
        if not data:
            return {
                "status": "success",
                "message": f"No {description} found for the provided parameters",
                "data": []
            }
            
        # Format and return the response based on endpoint type
        if endpoint.startswith("/quote/"):
            return _format_stock_price_response(data)
        elif endpoint.startswith("/profile/"):
            return _format_company_profile_response(data)
        elif endpoint.startswith("/stock_news") or endpoint.startswith("/stock_market/news"):
            return _format_news_response(data)
        else:
            # Default formatting for financial statements and other data
            return format_response(data)
        
    except requests.exceptions.Timeout:
        # Let the retry decorator handle this
        raise
    except requests.exceptions.ConnectionError:
        # Let the retry decorator handle this
        raise
    except requests.exceptions.HTTPError as e:
        # Handle HTTP errors (4xx, 5xx)
        status_code = e.response.status_code
        try:
            error_data = e.response.json()
            error_message = str(error_data) if error_data else str(e)
        except:
            error_message = e.response.text or str(e)
        
        return {
            "error": f"Financial Modeling Prep API error: {error_message}",
            "status": "error",
            "status_code": status_code
        }
    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Unexpected error in Financial Modeling Prep API request: {str(e)}")
        return {
            "error": f"Unexpected error: {str(e)}",
            "status": "error"
        }

def _format_stock_price_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """Format stock price data for better readability."""
    result = format_response(data)
    
    try:
        if isinstance(data, list) and len(data) > 0:
            quote = data[0]
            result["display"] = f"""Stock Data for {quote['symbol']} ({quote.get('name', 'Unknown')}):
- Price: ${quote['price']:.2f}
- Change: ${quote['change']:.2f} ({quote['changesPercentage']:.2f}%)
- Previous Close: ${quote['previousClose']:.2f}
- Day Range: ${quote['dayLow']:.2f} - ${quote['dayHigh']:.2f}
- 52 Week Range: ${quote.get('yearLow', 0):.2f} - ${quote.get('yearHigh', 0):.2f}
- Market Cap: ${quote.get('marketCap', 0):,.0f}
- Volume: {quote.get('volume', 0):,}
- Average Volume: {quote.get('avgVolume', 0):,}
- Exchange: {quote.get('exchange', 'N/A')}"""
    except Exception as e:
        logger.warning(f"Error formatting stock price response: {e}")
    
    return result

def _format_company_profile_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """Format company profile data for better readability."""
    result = format_response(data)
    
    try:
        if isinstance(data, list) and len(data) > 0:
            profile = data[0]
            result["display"] = f"""Company Profile: {profile['companyName']} ({profile['symbol']})
- Industry: {profile.get('industry', 'N/A')}
- Sector: {profile.get('sector', 'N/A')}
- CEO: {profile.get('ceo', 'N/A')}
- Website: {profile.get('website', 'N/A')}
- Description: {profile.get('description', 'N/A')[:300]}...
- Employees: {profile.get('fullTimeEmployees', 'N/A')}
- Market Cap: ${profile.get('mktCap', 0):,.0f}
- Price: ${profile.get('price', 0):.2f}
- Exchange: {profile.get('exchange', 'N/A')}
- Currency: {profile.get('currency', 'USD')}
- Country: {profile.get('country', 'N/A')}
- Address: {profile.get('address', 'N/A')}, {profile.get('city', 'N/A')}, {profile.get('state', 'N/A')}
- IPO Date: {profile.get('ipoDate', 'N/A')}"""
    except Exception as e:
        logger.warning(f"Error formatting company profile response: {e}")
    
    return result

def _format_news_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """Format news data for better readability."""
    result = format_response(data)
    
    try:
        if isinstance(data, list):
            news_items = []
            for i, article in enumerate(data[:5], 1):
                news_items.append(f"{i}. {article.get('title', 'No Title')}")
                news_items.append(f"   Published: {article.get('publishedDate', 'Unknown date')}")
                news_items.append(f"   Symbol: {article.get('symbol', 'N/A')}")
                news_items.append(f"   Source: {article.get('site', 'Unknown source')}")
                news_items.append(f"   URL: {article.get('url', '#')}")
                news_items.append("")
            
            if news_items:
                result["display"] = "\n".join(news_items)
    except Exception as e:
        logger.warning(f"Error formatting news response: {e}")
    
    return result

def test_financial_api_connection() -> Dict[str, Any]:
    """
    Test the connection to the Financial Modeling Prep API.
    
    Returns:
        Dict with test results
    """
    try:
        # Try to get Apple's stock price as a test
        result = stock_price("AAPL")
        
        if "error" in result:
            return {
                "status": "error",
                "message": result["error"]
            }
            
        return {
            "status": "success",
            "message": "Successfully connected to Financial Modeling Prep API",
            "data": result
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error testing Financial Modeling Prep API: {str(e)}"
        }

if __name__ == "__main__":
    # Test the API connection when run directly
    print("Testing Financial Modeling Prep API connection...")
    test_result = test_financial_api_connection()
    print(f"Status: {test_result['status']}")
    print(f"Message: {test_result['message']}")
    
    if test_result['status'] == 'success':
        print("\nSample data:")
        print(json.dumps(test_result.get('data', {}), indent=2)[:500] + "...")