"""
Database manager module for creating and managing the SQLite database.
"""
import sqlite3
from config.settings import DB_NAME
from database.schema import (
    STOCK_DAILY_SCHEMA,
    FINHUB_QUOTES_SCHEMA,
    COMPANY_PROFILES_SCHEMA,
    NEWS_ARTICLES_SCHEMA,
    TECHNICAL_INDICATORS_SCHEMA,
    FUNDAMENTAL_DATA_SCHEMA,
    PORTFOLIO_SCHEMA,
    WATCHLIST_SCHEMA
)

def create_database():
    """
    Create the SQLite database and all required tables.
    
    Returns:
        sqlite3.Connection: Database connection object
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Create tables for each data type
    cursor.execute(STOCK_DAILY_SCHEMA)
    cursor.execute(FINHUB_QUOTES_SCHEMA)
    cursor.execute(COMPANY_PROFILES_SCHEMA)
    cursor.execute(NEWS_ARTICLES_SCHEMA)
    cursor.execute(TECHNICAL_INDICATORS_SCHEMA)
    
    # Create additional tables for extended functionality
    cursor.execute(FUNDAMENTAL_DATA_SCHEMA)
    cursor.execute(PORTFOLIO_SCHEMA)
    cursor.execute(WATCHLIST_SCHEMA)
    
    # Migrar datos de tablas antiguas si existen
    migrate_data(conn)
    
    conn.commit()
    return conn

def migrate_data(conn):
    """
    Migra datos de las tablas antiguas a las nuevas si existen.
    
    Args:
        conn (sqlite3.Connection): Conexión a la base de datos
    """
    cursor = conn.cursor()
    
    # Verificar si existen tablas antiguas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='alphavantage_daily'")
    if cursor.fetchone():
        print("Migrando datos de alphavantage_daily a stock_daily_data...")
        cursor.execute("""
        INSERT OR IGNORE INTO stock_daily_data 
        (ticker, date, open, high, low, close, volume, source)
        SELECT ticker, date, open, high, low, close, volume, 'alphavantage'
        FROM alphavantage_daily
        """)
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='polygon_data'")
    if cursor.fetchone():
        print("Migrando datos de polygon_data a stock_daily_data...")
        cursor.execute("""
        INSERT OR IGNORE INTO stock_daily_data 
        (ticker, date, open, high, low, close, volume, source)
        SELECT ticker, date, open, high, low, close, volume, 'polygon'
        FROM polygon_data
        """)
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='finhub_quotes'")
    if cursor.fetchone():
        print("Migrando datos de finhub_quotes a market_quotes...")
        cursor.execute("""
        INSERT OR IGNORE INTO market_quotes 
        (ticker, current_price, change, percent_change, high, low, open, previous_close, source, timestamp)
        SELECT ticker, current_price, change, percent_change, high, low, open, previous_close, 'finhub', timestamp
        FROM finhub_quotes
        """)
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='fmp_profiles'")
    if cursor.fetchone():
        print("Migrando datos de fmp_profiles a company_profiles...")
        cursor.execute("""
        INSERT OR IGNORE INTO company_profiles 
        (ticker, company_name, industry, sector, market_cap, employees, description, ceo, website, exchange, ipo_date, source)
        SELECT ticker, company_name, industry, sector, market_cap, employees, description, ceo, website, exchange, ipo_date, 'fmp'
        FROM fmp_profiles
        """)
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ticker_info'")
    if cursor.fetchone():
        print("Migrando datos de ticker_info a company_profiles...")
        cursor.execute("""
        INSERT OR IGNORE INTO company_profiles 
        (ticker, sector, subsector, country, founded, years_public, type, source)
        SELECT symbol, sector, subsector, pais, fundacion, anos_en_bolsa, tipo, 'manual'
        FROM ticker_info
        """)
    
    conn.commit()

def get_connection():
    """
    Get a connection to the database.
    
    Returns:
        sqlite3.Connection: Database connection object
    """
    return sqlite3.connect(DB_NAME)

def execute_query(query, params=None):
    """
    Execute a SQL query and return the results.
    
    Args:
        query (str): SQL query to execute
        params (tuple, optional): Parameters for the query
        
    Returns:
        list: Query results
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    if params:
        cursor.execute(query, params)
    else:
        cursor.execute(query)
        
    results = cursor.fetchall()
    conn.commit()
    conn.close()
    
    return results

def insert_many(table, columns, values):
    """
    Insert multiple rows into a table.
    
    Args:
        table (str): Table name
        columns (list): Column names
        values (list): List of value tuples to insert
        
    Returns:
        int: Number of rows inserted
    """
    if not values:
        return 0
        
    conn = get_connection()
    cursor = conn.cursor()
    
    placeholders = ', '.join(['?' for _ in range(len(columns))])
    column_str = ', '.join(columns)
    
    query = f"INSERT OR REPLACE INTO {table} ({column_str}) VALUES ({placeholders})"
    
    cursor.executemany(query, values)
    rows_inserted = cursor.rowcount
    
    conn.commit()
    conn.close()
    
    return rows_inserted

def insert_or_update_company_profile(ticker_data):
    """
    Insert or update company profile information in the database.
    
    Args:
        ticker_data (dict): Dictionary mapping ticker symbols to their metadata
        
    Returns:
        int: Number of records inserted or updated
    """
    if not ticker_data:
        return 0
    
    conn = get_connection()
    cursor = conn.cursor()
    
    records_inserted = 0
    
    for ticker, info in ticker_data.items():
        try:
            cursor.execute('''
            INSERT OR REPLACE INTO company_profiles 
            (ticker, sector, subsector, country, founded, years_public, type, description, source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                ticker,
                info.get('sector', ''),
                info.get('subsector', ''),
                info.get('pais', ''),
                info.get('fundacion', ''),
                info.get('anos_en_bolsa', ''),
                info.get('tipo', ''),
                info.get('resena', ''),
                'manual'
            ))
            records_inserted += 1
        except Exception as e:
            print(f"Error inserting company profile for {ticker}: {e}")
    
    conn.commit()
    conn.close()
    
    return records_inserted

def cleanup_database():
    """
    Elimina tablas antiguas y redundantes después de la migración.
    
    Returns:
        list: Lista de tablas eliminadas
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Tablas antiguas que deben ser eliminadas
    old_tables = [
        'alphavantage_daily',
        'finhub_quotes',
        'fmp_profiles',
        'ticker_info',
        'polygon_data'
    ]
    
    deleted_tables = []
    
    for table in old_tables:
        try:
            cursor.execute(f"DROP TABLE IF EXISTS {table}")
            deleted_tables.append(table)
            print(f"Tabla {table} eliminada correctamente.")
        except Exception as e:
            print(f"Error al eliminar la tabla {table}: {e}")
    
    conn.commit()
    conn.close()
    
    return deleted_tables 