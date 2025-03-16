import os
import sys
from config.settings import TICKERS, TICKER_DATA
from database.db_manager import create_database, insert_or_update_ticker_info
from api.data_fetchers import (
    fetch_yfinance_data,
    fetch_finhub_data,
    fetch_fmp_data,
    fetch_news_data
)

def main():
    """Main function to create and populate the database."""
    print("Iniciando la aplicación...")
    
    # Print tickers to verify filtering
    print(f"Tickers a procesar: {TICKERS}")
    print(f"Tipos de tickers: {[TICKER_DATA.get(ticker, {}).get('tipo', 'Desconocido') for ticker in TICKERS]}")
    
    # Create database and get connection
    conn = create_database()
    
    # Store ticker information
    print("Almacenando información de tickers...")
    records_inserted = insert_or_update_ticker_info(TICKER_DATA)
    print(f"Se han almacenado {records_inserted} registros de información de tickers.")
    
    # Fetch and store data from each API
    print("Obteniendo datos de Yahoo Finance...")
    fetch_yfinance_data(conn, TICKERS)
    
    print("Obteniendo datos de Finhub...")
    fetch_finhub_data(conn, TICKERS)
    
    print("Obteniendo datos de Financial Modeling Prep...")
    fetch_fmp_data(conn, TICKERS)
    
    print("Obteniendo noticias...")
    fetch_news_data(conn, TICKERS)
    
    # Close connection
    conn.close()
    print("Base de datos creada y poblada exitosamente!")

if __name__ == "__main__":
    main()