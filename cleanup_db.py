"""
Script para limpiar la base de datos y actualizar los datos.
"""
import sqlite3
from config.settings import DB_NAME, TICKERS
from database.db_manager import cleanup_database, get_connection
from api.data_fetchers import fetch_yfinance_data, fetch_finhub_data, fetch_fmp_data, fetch_news_data, fetch_fundamental_data

def remove_duplicate_data():
    """
    Elimina datos duplicados de las tablas principales.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Eliminar duplicados en stock_daily_data
    try:
        cursor.execute("""
        DELETE FROM stock_daily_data
        WHERE id NOT IN (
            SELECT MIN(id)
            FROM stock_daily_data
            GROUP BY ticker, date, source
        )
        """)
        print(f"Se eliminaron {cursor.rowcount} registros duplicados de stock_daily_data.")
    except Exception as e:
        print(f"Error al eliminar duplicados de stock_daily_data: {e}")
    
    # Eliminar duplicados en company_profiles
    try:
        cursor.execute("""
        DELETE FROM company_profiles
        WHERE id NOT IN (
            SELECT MIN(id)
            FROM company_profiles
            GROUP BY ticker, source
        )
        """)
        print(f"Se eliminaron {cursor.rowcount} registros duplicados de company_profiles.")
    except Exception as e:
        print(f"Error al eliminar duplicados de company_profiles: {e}")
    
    # Eliminar duplicados en market_quotes
    try:
        cursor.execute("""
        DELETE FROM market_quotes
        WHERE id NOT IN (
            SELECT MIN(id)
            FROM market_quotes
            GROUP BY ticker, timestamp, source
        )
        """)
        print(f"Se eliminaron {cursor.rowcount} registros duplicados de market_quotes.")
    except Exception as e:
        print(f"Error al eliminar duplicados de market_quotes: {e}")
    
    conn.commit()
    conn.close()

def update_all_data():
    """
    Actualiza todos los datos de las APIs.
    """
    conn = sqlite3.connect(DB_NAME)
    
    # Actualizar datos de Yahoo Finance
    print("\nActualizando datos de Yahoo Finance...")
    yf_records = fetch_yfinance_data(conn, TICKERS)
    print(f"Se insertaron {yf_records} registros de Yahoo Finance.")
    
    # Actualizar datos de Finhub
    print("\nActualizando datos de Finhub...")
    fh_records = fetch_finhub_data(conn, TICKERS)
    print(f"Se insertaron {fh_records} registros de Finhub.")
    
    # Actualizar datos de FMP
    print("\nActualizando datos de FMP...")
    fmp_records = fetch_fmp_data(conn, TICKERS)
    print(f"Se insertaron {fmp_records} registros de FMP.")
    
    # Actualizar noticias
    print("\nActualizando noticias...")
    news_records = fetch_news_data(conn, TICKERS)
    print(f"Se insertaron {news_records} noticias.")
    
    # Actualizar datos fundamentales
    print("\nActualizando datos fundamentales...")
    fund_records = 0
    for ticker in TICKERS:
        fund_records += fetch_fundamental_data(conn, ticker)
    print(f"Se insertaron {fund_records} registros de datos fundamentales.")
    
    conn.close()

def main():
    """
    Función principal para limpiar y actualizar la base de datos.
    """
    print("=== Limpieza y actualización de la base de datos ===")
    
    # Eliminar tablas antiguas
    print("\n1. Eliminando tablas antiguas...")
    deleted_tables = cleanup_database()
    print(f"Se eliminaron {len(deleted_tables)} tablas antiguas: {', '.join(deleted_tables)}")
    
    # Eliminar datos duplicados
    print("\n2. Eliminando datos duplicados...")
    remove_duplicate_data()
    
    # Actualizar datos
    print("\n3. Actualizando datos...")
    update_all_data()
    
    print("\n=== Proceso completado ===")

if __name__ == "__main__":
    main() 