"""
Script to calculate and store technical indicators for all tickers.
"""
from config.settings import TICKERS
from utils.data_utils import get_stock_data, calculate_technical_indicators, store_technical_indicators

def calculate_all_indicators(days=60):
    """
    Calculate and store technical indicators for all tickers.
    
    Args:
        days (int): Number of days of data to use for calculations
        
    Returns:
        dict: Dictionary with results for each ticker
    """
    results = {}
    
    for ticker in TICKERS:
        print(f"Calculating technical indicators for {ticker}...")
        
        # Get stock data from primary source
        df = get_stock_data(ticker, days=days, source='yfinance')
        
        if df.empty:
            print(f"No data available for {ticker} from primary source, trying alternative sources...")
            df = get_stock_data(ticker, days=days, source='all')
        
        if df.empty:
            print(f"No data available for {ticker}")
            results[ticker] = {'status': 'error', 'message': 'No data available'}
            continue
        
        # Calculate technical indicators
        indicators_df = calculate_technical_indicators(df)
        
        # Store indicators in database
        records_inserted = store_technical_indicators(ticker, indicators_df)
        
        results[ticker] = {
            'status': 'success',
            'records_inserted': records_inserted,
            'indicators_calculated': len(indicators_df.columns) - len(df.columns)
        }
        
        print(f"Stored {records_inserted} records for {ticker}")
    
    return results

if __name__ == "__main__":
    calculate_all_indicators() 