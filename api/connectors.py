"""
API connector module for connecting to various financial data APIs.
"""
import requests
import datetime
from config.settings import (
    ALPHAVANTAGE_API_KEY,
    FINHUB_API_KEY,
    FMP_API_KEY,
    NEWS_API_KEY,
    ALPHAVANTAGE_BASE_URL,
    FINHUB_BASE_URL,
    FMP_BASE_URL,
    NEWS_API_BASE_URL
)

def connect_to_alphavantage(symbol, function="TIME_SERIES_DAILY"):
    """
    Connect to AlphaVantage API and retrieve data.
    
    Args:
        symbol (str): Stock ticker symbol
        function (str): API function to call
        
    Returns:
        dict: JSON response from the API
    """
    params = {
        "function": function,
        "symbol": symbol,
        "apikey": ALPHAVANTAGE_API_KEY
    }
    
    try:
        response = requests.get(ALPHAVANTAGE_BASE_URL, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to AlphaVantage API: {e}")
        return {}

def connect_to_finhub(symbol):
    """
    Connect to Finhub API and retrieve quote data.
    
    Args:
        symbol (str): Stock ticker symbol
        
    Returns:
        dict: JSON response from the API
    """
    url = f"{FINHUB_BASE_URL}/quote"
    params = {
        "symbol": symbol,
        "token": FINHUB_API_KEY
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Finhub API: {e}")
        return {}

def connect_to_fmp(symbol, endpoint="profile"):
    """
    Connect to Financial Modeling Prep API and retrieve data.
    
    Args:
        symbol (str): Stock ticker symbol
        endpoint (str): API endpoint to call
        
    Returns:
        dict: JSON response from the API
    """
    url = f"{FMP_BASE_URL}/{endpoint}/{symbol}"
    params = {
        "apikey": FMP_API_KEY
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to FMP API: {e}")
        return {}

def connect_to_news_api(query):
    """
    Connect to News API and retrieve news articles.
    
    Args:
        query (str): Search query (typically a ticker symbol)
        
    Returns:
        dict: JSON response from the API
    """
    url = f"{NEWS_API_BASE_URL}/everything"
    params = {
        "q": query,
        "apiKey": NEWS_API_KEY
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to News API: {e}")
        return {} 