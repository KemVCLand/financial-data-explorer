"""
Configuration settings for the financial data application.
"""
import os
import json

# API Keys - Load from environment variables with fallback to default values
ALPHAVANTAGE_API_KEY = os.environ.get("ALPHAVANTAGE_API_KEY", "IVTDDERCMU1QF611")
FINANCIAL_DATA_SET_API_KEY = os.environ.get("FINANCIAL_DATA_SET_API_KEY", "2fb9d403-06dd-4a02-88da-88a10dd51241")
FINHUB_API_KEY = os.environ.get("FINHUB_API_KEY", "cv5fmgpr01qn849vjaqgcv5fmgpr01qn849vjar0")
FMP_API_KEY = os.environ.get("FMP_API_KEY", "KHT2UTcUslPkMfzfLWxdaORWjV7hG6Pn")
NEWS_API_KEY = os.environ.get("NEWS_API_KEY", "68da47963b2f4ca79b7e397abf680d60")

# Database settings
DB_NAME = 'financial_data.db'

# Tickers file path
TICKERS_FILE = 'tickers.json'

# Default tickers (used if tickers file doesn't exist)
DEFAULT_TICKERS = ["AMZN", "AAPL", "NVDA"]

# Function to load tickers from JSON file
def load_tickers_from_json(file_path=TICKERS_FILE, filter_type=None):
    """
    Load tickers from a JSON file.
    
    Args:
        file_path (str): Path to the JSON file
        filter_type (str, optional): Filter tickers by type (e.g., "Stock", "Crypto", etc.)
        
    Returns:
        list: List of ticker symbols
        dict: Dictionary mapping ticker symbols to their metadata
    """
    if not os.path.exists(file_path):
        print(f"Tickers file '{file_path}' not found. Using default tickers.")
        return DEFAULT_TICKERS, {}
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        ticker_data = {}
        ticker_symbols = []
        filtered_symbols = []
        
        if 'tickers' in data and isinstance(data['tickers'], list) and data['tickers']:
            for ticker_info in data['tickers']:
                # Check if ticker_info is a dictionary with a 'symbol' key
                if isinstance(ticker_info, dict) and 'symbol' in ticker_info:
                    symbol = ticker_info['symbol'].strip().upper()
                    ticker_data[symbol] = ticker_info
                    
                    # If filter_type is specified, only include tickers of that type in filtered list
                    if filter_type:
                        if 'tipo' in ticker_info and ticker_info['tipo'] == filter_type:
                            filtered_symbols.append(symbol)
                            print(f"Incluyendo ticker {symbol} de tipo {ticker_info['tipo']}")
                        else:
                            tipo = ticker_info.get('tipo', 'No especificado')
                            print(f"Excluyendo ticker {symbol} de tipo {tipo}")
                    else:
                        ticker_symbols.append(symbol)
                # Handle the case where ticker_info is just a string (old format)
                elif isinstance(ticker_info, str) and ticker_info.strip():
                    symbol = ticker_info.strip().upper()
                    ticker_symbols.append(symbol)
                    ticker_data[symbol] = {'symbol': symbol}
                    
                    # Can't filter by type if ticker_info is just a string
                    if filter_type:
                        print(f"No se puede filtrar ticker {symbol} por tipo (formato antiguo)")
            
            if filter_type and filtered_symbols:
                print(f"Se han filtrado {len(filtered_symbols)} tickers de tipo '{filter_type}' de un total de {len(ticker_data)}")
                return filtered_symbols, ticker_data
            elif not ticker_symbols and not filtered_symbols:
                print(f"No valid tickers found in '{file_path}'. Using default tickers.")
                return DEFAULT_TICKERS, {}
            else:
                return ticker_symbols, ticker_data
        else:
            print(f"No valid tickers found in '{file_path}'. Using default tickers.")
            return DEFAULT_TICKERS, {}
    except Exception as e:
        print(f"Error loading tickers from '{file_path}': {e}. Using default tickers.")
        return DEFAULT_TICKERS, {}

# Load tickers (only stocks)
TICKERS, TICKER_DATA = load_tickers_from_json(filter_type="Stock")
print(f"Loaded {len(TICKERS)} tickers of type 'Stock'")

# API endpoints
ALPHAVANTAGE_BASE_URL = "https://www.alphavantage.co/query"
FINHUB_BASE_URL = "https://finnhub.io/api/v1"
FMP_BASE_URL = "https://financialmodelingprep.com/api/v3"
NEWS_API_BASE_URL = "https://newsapi.org/v2"

# Data fetch settings
NEWS_ARTICLE_LIMIT = 10  # Number of news articles to fetch per ticker 