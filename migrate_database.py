"""
Script para migrar datos de las tablas antiguas a las nuevas tablas optimizadas.
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

def create_new_tables(conn):
    """
    Crea las nuevas tablas optimizadas.
    
    Args:
        conn (sqlite3.Connection): Conexión a la base de datos
    """
    cursor = conn.cursor()
    
    # Crear las nuevas tablas
    cursor.execute(STOCK_DAILY_SCHEMA)
    cursor.execute(FINHUB_QUOTES_SCHEMA)
    cursor.execute(COMPANY_PROFILES_SCHEMA)
    cursor.execute(NEWS_ARTICLES_SCHEMA)
    cursor.execute(TECHNICAL_INDICATORS_SCHEMA)
    cursor.execute(FUNDAMENTAL_DATA_SCHEMA)
    cursor.execute(PORTFOLIO_SCHEMA)
    cursor.execute(WATCHLIST_SCHEMA)
    
    conn.commit()
    print("Nuevas tablas creadas exitosamente.")

def migrate_data(conn):
    """
    Migra datos de las tablas antiguas a las nuevas.
    
    Args:
        conn (sqlite3.Connection): Conexión a la base de datos
        
    Returns:
        dict: Resultados de la migración
    """
    cursor = conn.cursor()
    results = {}
    
    # Migrar datos de alphavantage_daily a stock_daily_data
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='alphavantage_daily'")
        if cursor.fetchone():
            print("Migrando datos de alphavantage_daily a stock_daily_data...")
            cursor.execute("""
            INSERT OR IGNORE INTO stock_daily_data 
            (ticker, date, open, high, low, close, volume, source)
            SELECT ticker, date, open, high, low, close, volume, 'alphavantage'
            FROM alphavantage_daily
            """)
            results['alphavantage_daily'] = cursor.rowcount
            print(f"Se migraron {cursor.rowcount} registros de alphavantage_daily.")
    except Exception as e:
        print(f"Error migrando alphavantage_daily: {e}")
        results['alphavantage_daily'] = f"Error: {e}"
    
    # Migrar datos de polygon_data a stock_daily_data
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='polygon_data'")
        if cursor.fetchone():
            print("Migrando datos de polygon_data a stock_daily_data...")
            cursor.execute("""
            INSERT OR IGNORE INTO stock_daily_data 
            (ticker, date, open, high, low, close, volume, source)
            SELECT ticker, date, open, high, low, close, volume, 'polygon'
            FROM polygon_data
            """)
            results['polygon_data'] = cursor.rowcount
            print(f"Se migraron {cursor.rowcount} registros de polygon_data.")
    except Exception as e:
        print(f"Error migrando polygon_data: {e}")
        results['polygon_data'] = f"Error: {e}"
    
    # Migrar datos de finhub_quotes a market_quotes
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='finhub_quotes'")
        if cursor.fetchone():
            print("Migrando datos de finhub_quotes a market_quotes...")
            cursor.execute("""
            INSERT OR IGNORE INTO market_quotes 
            (ticker, current_price, change, percent_change, high, low, open, previous_close, source, timestamp)
            SELECT ticker, current_price, change, percent_change, high, low, open, previous_close, 'finhub', timestamp
            FROM finhub_quotes
            """)
            results['finhub_quotes'] = cursor.rowcount
            print(f"Se migraron {cursor.rowcount} registros de finhub_quotes.")
    except Exception as e:
        print(f"Error migrando finhub_quotes: {e}")
        results['finhub_quotes'] = f"Error: {e}"
    
    # Migrar datos de fmp_profiles a company_profiles
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='fmp_profiles'")
        if cursor.fetchone():
            print("Migrando datos de fmp_profiles a company_profiles...")
            cursor.execute("""
            INSERT OR IGNORE INTO company_profiles 
            (ticker, company_name, industry, sector, market_cap, employees, description, ceo, website, exchange, ipo_date, source)
            SELECT ticker, company_name, industry, sector, market_cap, employees, description, ceo, website, exchange, ipo_date, 'fmp'
            FROM fmp_profiles
            """)
            results['fmp_profiles'] = cursor.rowcount
            print(f"Se migraron {cursor.rowcount} registros de fmp_profiles.")
    except Exception as e:
        print(f"Error migrando fmp_profiles: {e}")
        results['fmp_profiles'] = f"Error: {e}"
    
    # Migrar datos de ticker_info a company_profiles
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ticker_info'")
        if cursor.fetchone():
            print("Migrando datos de ticker_info a company_profiles...")
            cursor.execute("""
            INSERT OR IGNORE INTO company_profiles 
            (ticker, sector, subsector, country, founded, years_public, type, description, source)
            SELECT symbol, sector, subsector, pais, fundacion, anos_en_bolsa, tipo, resena, 'manual'
            FROM ticker_info
            """)
            results['ticker_info'] = cursor.rowcount
            print(f"Se migraron {cursor.rowcount} registros de ticker_info.")
    except Exception as e:
        print(f"Error migrando ticker_info: {e}")
        results['ticker_info'] = f"Error: {e}"
    
    conn.commit()
    return results

def main():
    """
    Función principal para migrar la base de datos.
    """
    print(f"Conectando a la base de datos {DB_NAME}...")
    conn = sqlite3.connect(DB_NAME)
    
    # Crear nuevas tablas
    create_new_tables(conn)
    
    # Migrar datos
    results = migrate_data(conn)
    
    # Mostrar resumen
    print("\nResumen de la migración:")
    for table, result in results.items():
        print(f"  {table}: {result}")
    
    # Cerrar conexión
    conn.close()
    print("\nMigración completada.")

if __name__ == "__main__":
    main() 