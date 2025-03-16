"""
Utility functions for processing and analyzing financial data.
"""
import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime, timedelta

def get_stock_data(ticker, days=30, source='yfinance'):
    """
    Get stock data for a specific ticker from the database.
    
    Args:
        ticker (str): Stock ticker symbol
        days (int): Number of days of data to retrieve
        source (str): Data source ('yfinance', 'polygon', etc.)
        
    Returns:
        pandas.DataFrame: DataFrame containing stock data
    """
    conn = sqlite3.connect('financial_data.db')
    
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    
    query = f"""
    SELECT date, open, high, low, close, volume
    FROM stock_daily_data
    WHERE ticker = '{ticker}'
    AND date BETWEEN '{start_date}' AND '{end_date}'
    """
    
    if source != 'all':
        query += f" AND source = '{source}'"
    
    query += " ORDER BY date"
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    if not df.empty:
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
    
    return df

def calculate_technical_indicators(df):
    """
    Calculate technical indicators for a DataFrame of stock data.
    
    Args:
        df (pandas.DataFrame): DataFrame with OHLCV data
        
    Returns:
        pandas.DataFrame: DataFrame with technical indicators
    """
    if df.empty:
        return df
    
    # Make a copy to avoid modifying the original
    result = df.copy()
    
    # Simple Moving Averages
    result['sma_20'] = result['close'].rolling(window=20).mean()
    result['sma_50'] = result['close'].rolling(window=50).mean()
    result['sma_200'] = result['close'].rolling(window=200).mean()
    
    # Exponential Moving Averages
    result['ema_12'] = result['close'].ewm(span=12, adjust=False).mean()
    result['ema_26'] = result['close'].ewm(span=26, adjust=False).mean()
    
    # MACD
    result['macd'] = result['ema_12'] - result['ema_26']
    result['macd_signal'] = result['macd'].ewm(span=9, adjust=False).mean()
    result['macd_histogram'] = result['macd'] - result['macd_signal']
    
    # RSI
    delta = result['close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    result['rsi_14'] = 100 - (100 / (1 + rs))
    
    # Bollinger Bands
    result['bollinger_middle'] = result['close'].rolling(window=20).mean()
    result['bollinger_std'] = result['close'].rolling(window=20).std()
    result['bollinger_upper'] = result['bollinger_middle'] + (result['bollinger_std'] * 2)
    result['bollinger_lower'] = result['bollinger_middle'] - (result['bollinger_std'] * 2)
    
    # Average True Range
    high_low = result['high'] - result['low']
    high_close = (result['high'] - result['close'].shift()).abs()
    low_close = (result['low'] - result['close'].shift()).abs()
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = ranges.max(axis=1)
    result['atr_14'] = true_range.rolling(window=14).mean()
    
    return result

def store_technical_indicators(ticker, indicators_df):
    """
    Store technical indicators in the database.
    
    Args:
        ticker (str): Stock ticker symbol
        indicators_df (pandas.DataFrame): DataFrame with technical indicators
        
    Returns:
        int: Number of records inserted
    """
    if indicators_df.empty:
        return 0
    
    conn = sqlite3.connect('financial_data.db')
    cursor = conn.cursor()
    records_inserted = 0
    
    for date, row in indicators_df.iterrows():
        try:
            date_str = date.strftime('%Y-%m-%d')
            cursor.execute('''
            INSERT OR REPLACE INTO technical_indicators 
            (ticker, date, sma_20, sma_50, sma_200, ema_12, ema_26, 
            macd, macd_signal, macd_histogram, rsi_14, 
            bollinger_upper, bollinger_middle, bollinger_lower, atr_14)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                ticker,
                date_str,
                row.get('sma_20'),
                row.get('sma_50'),
                row.get('sma_200'),
                row.get('ema_12'),
                row.get('ema_26'),
                row.get('macd'),
                row.get('macd_signal'),
                row.get('macd_histogram'),
                row.get('rsi_14'),
                row.get('bollinger_upper'),
                row.get('bollinger_middle'),
                row.get('bollinger_lower'),
                row.get('atr_14')
            ))
            records_inserted += 1
        except Exception as e:
            print(f"Error inserting technical indicators for {ticker} on {date_str}: {e}")
    
    conn.commit()
    conn.close()
    
    return records_inserted

def get_company_profile(ticker):
    """
    Get company profile for a specific ticker from the database.
    
    Args:
        ticker (str): Stock ticker symbol
        
    Returns:
        dict: Company profile data
    """
    conn = sqlite3.connect('financial_data.db')
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT * FROM company_profiles
    WHERE ticker = ?
    ORDER BY timestamp DESC
    LIMIT 1
    """, (ticker,))
    
    profile = cursor.fetchone()
    
    if profile:
        # Convert to dictionary
        columns = [desc[0] for desc in cursor.description]
        profile_dict = {columns[i]: profile[i] for i in range(len(columns))}
    else:
        profile_dict = {}
    
    conn.close()
    return profile_dict

def get_latest_news(ticker, limit=5):
    """
    Get latest news for a specific ticker from the database.
    
    Args:
        ticker (str): Stock ticker symbol
        limit (int): Maximum number of news articles to retrieve
        
    Returns:
        pandas.DataFrame: DataFrame with news articles
    """
    conn = sqlite3.connect('financial_data.db')
    
    query = f"""
    SELECT title, source, url, published_at, content
    FROM news_articles
    WHERE ticker = '{ticker}'
    ORDER BY published_at DESC
    LIMIT {limit}
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    return df

def get_market_quotes(ticker):
    """
    Get latest market quotes for a specific ticker from the database.
    
    Args:
        ticker (str): Stock ticker symbol
        
    Returns:
        dict: Market quote data
    """
    conn = sqlite3.connect('financial_data.db')
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT * FROM market_quotes
    WHERE ticker = ?
    ORDER BY timestamp DESC
    LIMIT 1
    """, (ticker,))
    
    quote = cursor.fetchone()
    
    if quote:
        # Convert to dictionary
        columns = [desc[0] for desc in cursor.description]
        quote_dict = {columns[i]: quote[i] for i in range(len(columns))}
    else:
        quote_dict = {}
    
    conn.close()
    return quote_dict

def get_fundamental_data(ticker, periods=4):
    """
    Get fundamental financial data for a specific ticker from the database.
    
    Args:
        ticker (str): Stock ticker symbol
        periods (int): Number of periods to retrieve
        
    Returns:
        pandas.DataFrame: DataFrame with fundamental data
    """
    conn = sqlite3.connect('financial_data.db')
    
    query = f"""
    SELECT *
    FROM fundamental_data
    WHERE ticker = '{ticker}'
    ORDER BY period_end_date DESC
    LIMIT {periods}
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    return df

def update_technical_indicators_for_all_stocks():
    """
    Update technical indicators for all stocks with data since 2024.
    
    Returns:
        int: Number of records inserted
    """
    conn = sqlite3.connect('financial_data.db')
    cursor = conn.cursor()
    
    # Get all unique tickers from stock_daily_data
    cursor.execute("SELECT DISTINCT ticker FROM stock_daily_data WHERE source = 'yfinance'")
    tickers = [row[0] for row in cursor.fetchall()]
    
    total_records = 0
    
    for ticker in tickers:
        print(f"Calculating technical indicators for {ticker}...")
        
        # Get all data since 2024 for this ticker
        df = get_stock_data(ticker, days=500, source='yfinance')  # Using a large number to get all data since 2024
        
        if not df.empty:
            # Calculate technical indicators
            indicators_df = calculate_technical_indicators(df)
            
            # Store in database
            records = store_technical_indicators(ticker, indicators_df)
            total_records += records
            
            print(f"Inserted {records} technical indicator records for {ticker}")
        else:
            print(f"No data available for {ticker}")
    
    conn.close()
    return total_records 