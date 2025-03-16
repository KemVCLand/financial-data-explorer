"""
Database schema definitions for the financial data application.
"""

# AlphaVantage daily data schema (renombrada a stock_daily_data para ser más genérica)
STOCK_DAILY_SCHEMA = '''
CREATE TABLE IF NOT EXISTS stock_daily_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT NOT NULL,
    date TEXT NOT NULL,
    open REAL,
    high REAL,
    low REAL,
    close REAL,
    volume INTEGER,
    source TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(ticker, date, source)
)
'''

# Finhub quotes schema (para datos en tiempo real)
FINHUB_QUOTES_SCHEMA = '''
CREATE TABLE IF NOT EXISTS market_quotes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT NOT NULL,
    current_price REAL,
    change REAL,
    percent_change REAL,
    high REAL,
    low REAL,
    open REAL,
    previous_close REAL,
    source TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(ticker, timestamp, source)
)
'''

# Company profiles schema (unificando FMP y otros perfiles)
COMPANY_PROFILES_SCHEMA = '''
CREATE TABLE IF NOT EXISTS company_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT NOT NULL,
    company_name TEXT,
    industry TEXT,
    sector TEXT,
    subsector TEXT,
    market_cap REAL,
    employees INTEGER,
    description TEXT,
    ceo TEXT,
    website TEXT,
    exchange TEXT,
    ipo_date TEXT,
    country TEXT,
    founded TEXT,
    years_public TEXT,
    type TEXT,
    source TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(ticker, source)
)
'''

# News articles schema
NEWS_ARTICLES_SCHEMA = '''
CREATE TABLE IF NOT EXISTS news_articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT NOT NULL,
    title TEXT,
    source TEXT,
    url TEXT UNIQUE,
    published_at TEXT,
    content TEXT,
    sentiment REAL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
'''

# Technical indicators schema
TECHNICAL_INDICATORS_SCHEMA = '''
CREATE TABLE IF NOT EXISTS technical_indicators (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT NOT NULL,
    date TEXT NOT NULL,
    sma_20 REAL,
    sma_50 REAL,
    sma_200 REAL,
    ema_12 REAL,
    ema_26 REAL,
    macd REAL,
    macd_signal REAL,
    macd_histogram REAL,
    rsi_14 REAL,
    bollinger_upper REAL,
    bollinger_middle REAL,
    bollinger_lower REAL,
    atr_14 REAL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(ticker, date)
)
'''

# Fundamental data schema (para datos financieros)
FUNDAMENTAL_DATA_SCHEMA = '''
CREATE TABLE IF NOT EXISTS fundamental_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT NOT NULL,
    period TEXT NOT NULL,
    period_end_date TEXT NOT NULL,
    revenue REAL,
    net_income REAL,
    eps REAL,
    pe_ratio REAL,
    pb_ratio REAL,
    dividend_yield REAL,
    debt_to_equity REAL,
    roa REAL,
    roe REAL,
    gross_margin REAL,
    operating_margin REAL,
    net_margin REAL,
    free_cash_flow REAL,
    data_source TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(ticker, period, period_end_date)
)
'''

# Portfolio schema (para seguimiento de carteras)
PORTFOLIO_SCHEMA = '''
CREATE TABLE IF NOT EXISTS portfolio (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    portfolio_name TEXT NOT NULL,
    ticker TEXT NOT NULL,
    shares REAL NOT NULL,
    purchase_price REAL NOT NULL,
    purchase_date TEXT NOT NULL,
    notes TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(portfolio_name, ticker, purchase_date)
)
'''

# Watchlist schema (para listas de seguimiento)
WATCHLIST_SCHEMA = '''
CREATE TABLE IF NOT EXISTS watchlist (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    watchlist_name TEXT NOT NULL,
    ticker TEXT NOT NULL,
    added_date TEXT NOT NULL,
    notes TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(watchlist_name, ticker)
)
''' 