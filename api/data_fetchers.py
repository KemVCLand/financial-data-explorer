"""
Data fetcher module for retrieving and processing data from financial APIs.
"""
from api.connectors import (
    connect_to_finhub,
    connect_to_fmp,
    connect_to_news_api
)
from config.settings import NEWS_ARTICLE_LIMIT
import datetime
import yfinance as yf
import pandas as pd

def fetch_yfinance_data(conn, tickers):
    """
    Fetch data from Yahoo Finance API and store in database.
    
    Args:
        conn (sqlite3.Connection): Database connection
        tickers (list): List of ticker symbols to fetch data for
        
    Returns:
        int: Number of records inserted
    """
    cursor = conn.cursor()
    records_inserted = 0
    
    # Eliminar registros antiguos para evitar duplicados
    try:
        cursor.execute("DELETE FROM stock_daily_data WHERE source = 'yfinance'")
        print(f"Registros antiguos de yfinance eliminados.")
    except Exception as e:
        print(f"Error al eliminar registros antiguos: {e}")
    
    # Get current date for end date
    end_date = datetime.datetime.now().strftime('%Y-%m-%d')
    
    for ticker in tickers:
        print(f"Fetching Yahoo Finance data for {ticker}...")
        try:
            # Get data from Yahoo Finance desde el inicio de 2024
            ticker_data = yf.Ticker(ticker)
            hist = ticker_data.history(start="2024-01-01", end=end_date)
            
            if not hist.empty:
                # Process and store each day's data
                for date, row in hist.iterrows():
                    try:
                        date_str = date.strftime('%Y-%m-%d')
                        cursor.execute('''
                        INSERT OR REPLACE INTO stock_daily_data 
                        (ticker, date, open, high, low, close, volume, source)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            ticker,
                            date_str,
                            float(row['Open']),
                            float(row['High']),
                            float(row['Low']),
                            float(row['Close']),
                            int(row['Volume']),
                            'yfinance'
                        ))
                        records_inserted += 1
                    except Exception as e:
                        print(f"Error inserting data for {ticker} on {date_str}: {e}")
            else:
                print(f"No data available for {ticker}")
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
    
    conn.commit()
    return records_inserted

def fetch_finhub_data(conn, tickers):
    """
    Fetch data from Finhub API and store in database.
    
    Args:
        conn (sqlite3.Connection): Database connection
        tickers (list): List of ticker symbols to fetch data for
        
    Returns:
        int: Number of records inserted
    """
    cursor = conn.cursor()
    records_inserted = 0
    
    for ticker in tickers:
        print(f"Fetching Finhub data for {ticker}...")
        try:
            # Get data from Finhub
            quote_data = connect_to_finhub(ticker)
            
            if quote_data and 'c' in quote_data:
                # Store quote data
                cursor.execute('''
                INSERT OR REPLACE INTO market_quotes 
                (ticker, current_price, change, percent_change, high, low, open, previous_close, source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    ticker,
                    quote_data.get('c', 0),  # Current price
                    quote_data.get('d', 0),  # Change
                    quote_data.get('dp', 0),  # Percent change
                    quote_data.get('h', 0),  # High
                    quote_data.get('l', 0),  # Low
                    quote_data.get('o', 0),  # Open
                    quote_data.get('pc', 0),  # Previous close
                    'finhub'
                ))
                records_inserted += 1
            else:
                print(f"No quote data available for {ticker}")
        except Exception as e:
            print(f"Error fetching quote data for {ticker}: {e}")
    
    conn.commit()
    return records_inserted

def fetch_fmp_data(conn, tickers):
    """
    Fetch data from Financial Modeling Prep API and store in database.
    
    Args:
        conn (sqlite3.Connection): Database connection
        tickers (list): List of ticker symbols to fetch data for
        
    Returns:
        int: Number of records inserted
    """
    cursor = conn.cursor()
    records_inserted = 0
    
    for ticker in tickers:
        print(f"Fetching FMP data for {ticker}...")
        try:
            # Get company profile from FMP
            profile_data = connect_to_fmp(ticker, endpoint="profile")
            
            if profile_data and isinstance(profile_data, list) and len(profile_data) > 0:
                profile = profile_data[0]
                
                # Store company profile
                cursor.execute('''
                INSERT OR REPLACE INTO company_profiles 
                (ticker, company_name, industry, sector, market_cap, employees, description, ceo, website, exchange, ipo_date, source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    ticker,
                    profile.get('companyName', ''),
                    profile.get('industry', ''),
                    profile.get('sector', ''),
                    profile.get('mktCap', 0),
                    profile.get('fullTimeEmployees', 0),
                    profile.get('description', ''),
                    profile.get('ceo', ''),
                    profile.get('website', ''),
                    profile.get('exchange', ''),
                    profile.get('ipoDate', ''),
                    'fmp'
                ))
                records_inserted += 1
                
                # También podríamos obtener datos fundamentales aquí
                # fetch_fundamental_data(conn, ticker)
            else:
                print(f"No profile data available for {ticker}")
        except Exception as e:
            print(f"Error fetching profile data for {ticker}: {e}")
    
    conn.commit()
    return records_inserted

def fetch_news_data(conn, tickers):
    """
    Fetch news data for tickers and store in database.
    
    Args:
        conn (sqlite3.Connection): Database connection
        tickers (list): List of ticker symbols to fetch news for
        
    Returns:
        int: Number of records inserted
    """
    cursor = conn.cursor()
    records_inserted = 0
    
    for ticker in tickers:
        print(f"Fetching news for {ticker}...")
        try:
            # Get news from News API
            news_data = connect_to_news_api(ticker)
            
            if news_data and 'articles' in news_data:
                articles = news_data['articles'][:NEWS_ARTICLE_LIMIT]  # Limit number of articles
                
                for article in articles:
                    try:
                        # Store news article
                        cursor.execute('''
                        INSERT OR IGNORE INTO news_articles 
                        (ticker, title, source, url, published_at, content)
                        VALUES (?, ?, ?, ?, ?, ?)
                        ''', (
                            ticker,
                            article.get('title', ''),
                            article.get('source', {}).get('name', ''),
                            article.get('url', ''),
                            article.get('publishedAt', ''),
                            article.get('content', '')
                        ))
                        if cursor.rowcount > 0:
                            records_inserted += 1
                    except Exception as e:
                        print(f"Error inserting news article for {ticker}: {e}")
            else:
                print(f"No news available for {ticker}")
        except Exception as e:
            print(f"Error fetching news for {ticker}: {e}")
    
    conn.commit()
    return records_inserted

def fetch_fundamental_data(conn, ticker):
    """
    Fetch fundamental financial data for a ticker and store in database.
    
    Args:
        conn (sqlite3.Connection): Database connection
        ticker (str): Ticker symbol to fetch data for
        
    Returns:
        int: Number of records inserted
    """
    cursor = conn.cursor()
    records_inserted = 0
    
    try:
        # Get financial ratios from FMP
        ratios_data = connect_to_fmp(ticker, endpoint="ratios")
        
        if ratios_data and isinstance(ratios_data, list):
            for period_data in ratios_data[:4]:  # Get last 4 periods
                try:
                    # Store fundamental data
                    cursor.execute('''
                    INSERT OR REPLACE INTO fundamental_data 
                    (ticker, period, period_end_date, pe_ratio, pb_ratio, dividend_yield, 
                     debt_to_equity, roa, roe, gross_margin, operating_margin, net_margin, data_source)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        ticker,
                        period_data.get('period', ''),
                        period_data.get('date', ''),
                        period_data.get('priceEarningsRatio', 0),
                        period_data.get('priceToBookRatio', 0),
                        period_data.get('dividendYield', 0),
                        period_data.get('debtToEquity', 0),
                        period_data.get('returnOnAssets', 0),
                        period_data.get('returnOnEquity', 0),
                        period_data.get('grossProfitMargin', 0),
                        period_data.get('operatingProfitMargin', 0),
                        period_data.get('netProfitMargin', 0),
                        'fmp'
                    ))
                    records_inserted += 1
                except Exception as e:
                    print(f"Error inserting fundamental data for {ticker}: {e}")
        
        # Get income statement data
        income_data = connect_to_fmp(ticker, endpoint="income-statement")
        
        if income_data and isinstance(income_data, list):
            for period_data in income_data[:4]:  # Get last 4 periods
                try:
                    # Update fundamental data with income statement info
                    cursor.execute('''
                    UPDATE fundamental_data 
                    SET revenue = ?, net_income = ?, eps = ?, free_cash_flow = ?
                    WHERE ticker = ? AND period_end_date = ?
                    ''', (
                        period_data.get('revenue', 0),
                        period_data.get('netIncome', 0),
                        period_data.get('eps', 0),
                        period_data.get('freeCashFlow', 0),
                        ticker,
                        period_data.get('date', '')
                    ))
                except Exception as e:
                    print(f"Error updating fundamental data for {ticker}: {e}")
    except Exception as e:
        print(f"Error fetching fundamental data for {ticker}: {e}")
    
    conn.commit()
    return records_inserted 