"""
Web application for visualizing financial data.
"""
import os
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from flask import Flask, render_template, request, jsonify, redirect, url_for
from dash import Dash, html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
from config.settings import DB_NAME, TICKERS
from api.data_fetchers import (
    fetch_yfinance_data,
    fetch_finhub_data,
    fetch_fmp_data,
    fetch_news_data,
    fetch_fundamental_data
)
from database.db_manager import create_database, insert_or_update_company_profile, cleanup_database
from utils.data_utils import (
    get_company_profile, 
    get_market_quotes, 
    get_stock_data, 
    get_latest_news,
    update_technical_indicators_for_all_stocks
)
from cleanup_db import remove_duplicate_data
from datetime import datetime, timedelta

# Initialize Flask app
server = Flask(__name__, 
               template_folder='web/templates',
               static_folder='web/static')

# Initialize Dash app
app = Dash(__name__, 
           server=server, 
           routes_pathname_prefix='/dash/',
           external_stylesheets=[dbc.themes.BOOTSTRAP])

# Remove the default Dash index page
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>Financial Data Explorer - Dashboard</title>
        {%favicon%}
        {%css%}
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <link rel="stylesheet" href="/static/css/style.css">
    </head>
    <body class="dark-theme">
        {%app_entry%}
        <footer class="text-center py-4 mt-5">
            <div class="container">
                <div class="row">
                    <div class="col-md-12">
                        <p class="mb-0">
                            <i class="fas fa-chart-line me-2"></i>Financial Data Explorer &copy; 2025
                        </p>
                    </div>
                </div>
            </div>
        </footer>
        {%config%}
        {%scripts%}
        {%renderer%}
    </body>
</html>
'''

# Database connection
def get_db_connection():
    """Get a connection to the SQLite database."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

# Routes
@server.route('/')
def index():
    """Render the home page."""
    return render_template('index.html', tickers=TICKERS)

@server.route('/admin')
def admin():
    """Render the admin page for database management."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row['name'] for row in cursor.fetchall()]
    
    # Define now as a function that can be called from the template
    def now():
        return datetime.now()
    
    conn.close()
    return render_template('admin.html', tables=tables, now=now)

@server.route('/update_data', methods=['POST'])
def update_data():
    """Update data for selected tables."""
    tables = request.form.getlist('tables')
    
    if not tables:
        return redirect(url_for('admin', message='No tables selected'))
    
    conn = create_database()
    
    for table in tables:
        print(f"Updating {table}...")
        
        if table == 'company_profiles':
            fetch_fmp_data(conn, TICKERS)
        elif table == 'stock_daily_data':
            fetch_yfinance_data(conn, TICKERS)
        elif table == 'market_quotes':
            fetch_finhub_data(conn, TICKERS)
        elif table == 'news_articles':
            fetch_news_data(conn, TICKERS)
        elif table == 'fundamental_data':
            for ticker in TICKERS:
                fetch_fundamental_data(conn, ticker)
        elif table == 'technical_indicators':
            update_technical_indicators_for_all_stocks()
    
    conn.close()
    
    return redirect(url_for('admin', message=f'Updated {len(tables)} tables successfully'))

@server.route('/api/ticker/<ticker>')
def get_ticker_data(ticker):
    """API endpoint to get data for a specific ticker."""
    conn = get_db_connection()
    
    # Get daily price data
    daily_data = pd.read_sql_query("""
    SELECT date, open, high, low, close, volume
    FROM stock_daily_data
    WHERE ticker = ?
    ORDER BY date DESC
    LIMIT 30;
    """, conn, params=(ticker,))
    
    # Get company profile
    profile = get_company_profile(ticker)
    
    # Get market quotes
    quotes = get_market_quotes(ticker)
    
    # Get news
    news = get_latest_news(ticker, limit=5)
    
    conn.close()
    
    result = {
        'daily_data': daily_data.to_dict('records') if not daily_data.empty else [],
        'profile': profile,
        'quotes': quotes,
        'news': news.to_dict('records') if not news.empty else []
    }
    
    return jsonify(result)

@server.route('/api/tables')
def get_tables():
    """Get all tables in the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row['name'] for row in cursor.fetchall()]
    conn.close()
    return jsonify(tables)

@server.route('/api/table/<table_name>')
def get_table_data(table_name):
    """Get data from a specific table."""
    conn = get_db_connection()
    try:
        df = pd.read_sql_query(f"SELECT * FROM {table_name} LIMIT 100", conn)
        return jsonify(df.to_dict('records'))
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@server.route('/cleanup_database', methods=['POST'])
def cleanup_db_route():
    """Limpiar la base de datos y actualizar los datos."""
    # Eliminar tablas antiguas
    deleted_tables = cleanup_database()
    
    # Eliminar datos duplicados
    remove_duplicate_data()
    
    return redirect(url_for('admin', message=f'Base de datos limpiada. Se eliminaron {len(deleted_tables)} tablas antiguas.'))

@server.route('/api/returns/<ticker>')
def get_ticker_returns(ticker):
    """API endpoint to get returns for a specific ticker."""
    # Try alphavantage first, then yfinance, then polygon
    returns = calculate_returns(ticker, 'alphavantage')
    
    # If any of the returns are None, try with yfinance
    if returns['ytd'] is None or returns['quarter'] is None or returns['year'] is None:
        yf_returns = calculate_returns(ticker, 'yfinance')
        
        # Fill in any missing returns
        if returns['ytd'] is None:
            returns['ytd'] = yf_returns['ytd']
        if returns['quarter'] is None:
            returns['quarter'] = yf_returns['quarter']
        if returns['year'] is None:
            returns['year'] = yf_returns['year']
    
    return jsonify(returns)

def calculate_returns(ticker, source='alphavantage'):
    """
    Calculate returns for different time periods.
    
    Args:
        ticker (str): Stock ticker symbol
        source (str): Data source
        
    Returns:
        dict: Returns for different time periods
    """
    conn = sqlite3.connect(DB_NAME)
    
    # Get current date
    current_date = datetime.now()
    
    # Calculate start dates for different periods
    ytd_start = datetime(current_date.year, 1, 1).strftime('%Y-%m-%d')
    quarter_start = (current_date - timedelta(days=90)).strftime('%Y-%m-%d')
    year_start = (current_date - timedelta(days=365)).strftime('%Y-%m-%d')
    
    # Query for YTD return
    ytd_query = f"""
    SELECT 
        CASE 
            WHEN (SELECT COUNT(*) FROM stock_daily_data 
                 WHERE ticker = '{ticker}' AND source = '{source}' 
                 AND date >= '{ytd_start}') > 0
            THEN
                (SELECT close FROM stock_daily_data 
                 WHERE ticker = '{ticker}' AND source = '{source}' 
                 ORDER BY date DESC LIMIT 1) /
                (SELECT close FROM stock_daily_data 
                 WHERE ticker = '{ticker}' AND source = '{source}' 
                 AND date >= '{ytd_start}' 
                 ORDER BY date ASC LIMIT 1) - 1
            ELSE NULL
        END AS ytd_return
    """
    
    # Query for quarterly return
    quarter_query = f"""
    SELECT 
        CASE 
            WHEN (SELECT COUNT(*) FROM stock_daily_data 
                 WHERE ticker = '{ticker}' AND source = '{source}' 
                 AND date >= '{quarter_start}') > 0
            THEN
                (SELECT close FROM stock_daily_data 
                 WHERE ticker = '{ticker}' AND source = '{source}' 
                 ORDER BY date DESC LIMIT 1) /
                (SELECT close FROM stock_daily_data 
                 WHERE ticker = '{ticker}' AND source = '{source}' 
                 AND date >= '{quarter_start}' 
                 ORDER BY date ASC LIMIT 1) - 1
            ELSE NULL
        END AS quarter_return
    """
    
    # Query for yearly return
    year_query = f"""
    SELECT 
        CASE 
            WHEN (SELECT COUNT(*) FROM stock_daily_data 
                 WHERE ticker = '{ticker}' AND source = '{source}' 
                 AND date >= '{year_start}') > 0
            THEN
                (SELECT close FROM stock_daily_data 
                 WHERE ticker = '{ticker}' AND source = '{source}' 
                 ORDER BY date DESC LIMIT 1) /
                (SELECT close FROM stock_daily_data 
                 WHERE ticker = '{ticker}' AND source = '{source}' 
                 AND date >= '{year_start}' 
                 ORDER BY date ASC LIMIT 1) - 1
            ELSE NULL
        END AS year_return
    """
    
    # Execute queries
    try:
        ytd_return = pd.read_sql_query(ytd_query, conn).iloc[0, 0]
        ytd_return = float(ytd_return) if ytd_return is not None else None
    except:
        ytd_return = None
        
    try:
        quarter_return = pd.read_sql_query(quarter_query, conn).iloc[0, 0]
        quarter_return = float(quarter_return) if quarter_return is not None else None
    except:
        quarter_return = None
        
    try:
        year_return = pd.read_sql_query(year_query, conn).iloc[0, 0]
        year_return = float(year_return) if year_return is not None else None
    except:
        year_return = None
    
    conn.close()
    
    return {
        'ytd': ytd_return,
        'quarter': quarter_return,
        'year': year_return
    }

# Dash layout
app.layout = html.Div([
    dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H1([
                    html.I(className="fas fa-chart-line me-2"),
                    "Financial Data Dashboard"
                ], className="my-4 text-center")
            ], width=12)
        ]),
        
        dbc.Row([
            dbc.Col([
                html.Label("Select Ticker:"),
                dcc.Dropdown(
                    id='ticker-dropdown',
                    options=[{'label': ticker, 'value': ticker} for ticker in TICKERS],
                    value=TICKERS[0] if TICKERS else None,
                    className="mb-3"
                )
            ], width=4)
        ]),
        
        dbc.Row([
            dbc.Col([
                html.H3("Ticker Information"),
                html.Div(id='ticker-info')
            ], width=12, className="mb-4")
        ]),
        
        dbc.Row([
            dbc.Col([
                html.H3("Price Chart"),
                dcc.Graph(id='price-chart')
            ], width=12, className="mt-4 mb-4")
        ]),
        
        dbc.Row([
            dbc.Col([
                html.H3("Technical Indicators"),
                dcc.Graph(id='technical-chart')
            ], width=12, className="mt-4 mb-4")
        ]),
        
        dbc.Row([
            dbc.Col([
                html.H3("Company Profile"),
                html.Div(id='company-profile')
            ], width=6),
            
            dbc.Col([
                html.H3("Latest News"),
                html.Div(id='news-container')
            ], width=6)
        ])
    ])
])

@app.callback(
    [Output('ticker-info', 'children'),
     Output('company-profile', 'children'),
     Output('news-container', 'children'),
     Output('price-chart', 'figure'),
     Output('technical-chart', 'figure')],
    [Input('ticker-dropdown', 'value')]
)
def update_ticker_info(ticker):
    """Update ticker information based on selected ticker."""
    if not ticker:
        return html.Div("No ticker selected"), html.Div(), html.Div(), {}, {}
    
    # Get ticker data
    conn = get_db_connection()
    
    # Get market quotes
    quotes = get_market_quotes(ticker)
    
    # Get company profile
    profile = get_company_profile(ticker)
    
    # Get daily price data
    daily_data = get_stock_data(ticker, days=90, source='yfinance')
    
    # Calculate returns
    returns = calculate_returns(ticker)
    
    # Get technical indicators
    cursor = conn.cursor()
    cursor.execute("""
    SELECT date, sma_20, sma_50, sma_200, rsi_14, bollinger_upper, bollinger_middle, bollinger_lower
    FROM technical_indicators
    WHERE ticker = ?
    ORDER BY date
    """, (ticker,))
    
    tech_data = pd.DataFrame(cursor.fetchall(), columns=['date', 'sma_20', 'sma_50', 'sma_200', 'rsi_14', 
                                                        'bollinger_upper', 'bollinger_middle', 'bollinger_lower'])
    
    if not tech_data.empty:
        tech_data['date'] = pd.to_datetime(tech_data['date'])
        tech_data.set_index('date', inplace=True)
    
    # Get news
    news = get_latest_news(ticker, limit=3)
    
    conn.close()
    
    # Create ticker info card
    ticker_info_card = dbc.Card([
        dbc.CardHeader(f"{ticker} - {profile.get('sector', 'N/A')}"),
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.H4(f"${quotes.get('current_price', 'N/A')}", className="card-title"),
                    html.P([
                        html.Span(
                            f"{quotes.get('change', 0):.2f} ({quotes.get('percent_change', 0):.2f}%)",
                            className="text-success" if quotes.get('change', 0) >= 0 else "text-danger"
                        )
                    ]),
                    html.Div([
                        html.P(f"Open: ${quotes.get('open', 'N/A')}"),
                        html.P(f"High: ${quotes.get('high', 'N/A')}"),
                        html.P(f"Low: ${quotes.get('low', 'N/A')}"),
                        html.P(f"Previous Close: ${quotes.get('previous_close', 'N/A')}")
                    ])
                ], width=6),
                dbc.Col([
                    html.Div([
                        html.H5("Retornos", className="mb-3 text-center"),
                        html.Div([
                            dbc.Row([
                                dbc.Col([
                                    html.Div([
                                        html.H6("YTD", className="text-center mb-2"),
                                        html.P(
                                            f"{returns['ytd']*100:.2f}%" if returns['ytd'] is not None else "N/A",
                                            className=f"text-{'success' if returns.get('ytd', 0) >= 0 else 'danger'} text-center fs-4 fw-bold mb-0"
                                        )
                                    ], className="p-2 rounded", style={"background": "rgba(255,255,255,0.05)"})
                                ], width=4),
                                dbc.Col([
                                    html.Div([
                                        html.H6("Last Quarter", className="text-center mb-2"),
                                        html.P(
                                            f"{returns['quarter']*100:.2f}%" if returns['quarter'] is not None else "N/A",
                                            className=f"text-{'success' if returns.get('quarter', 0) >= 0 else 'danger'} text-center fs-4 fw-bold mb-0"
                                        )
                                    ], className="p-2 rounded", style={"background": "rgba(255,255,255,0.05)"})
                                ], width=4),
                                dbc.Col([
                                    html.Div([
                                        html.H6("Last Year", className="text-center mb-2"),
                                        html.P(
                                            f"{returns['year']*100:.2f}%" if returns['year'] is not None else "N/A",
                                            className=f"text-{'success' if returns.get('year', 0) >= 0 else 'danger'} text-center fs-4 fw-bold mb-0"
                                        )
                                    ], className="p-2 rounded", style={"background": "rgba(255,255,255,0.05)"})
                                ], width=4)
                            ])
                        ], className="p-3 rounded", style={"background": "rgba(108, 92, 231, 0.1)", "border": "1px solid rgba(108, 92, 231, 0.2)"})
                    ])
                ], width=6)
            ])
        ])
    ])
    
    # Create company profile card
    company_profile_card = dbc.Card([
        dbc.CardHeader(f"{profile.get('company_name', ticker)}"),
        dbc.CardBody([
            html.P(profile.get('description', 'No description available')),
            html.Div([
                html.P(f"Industry: {profile.get('industry', 'N/A')}"),
                html.P(f"Sector: {profile.get('sector', 'N/A')}"),
                html.P(f"Employees: {profile.get('employees', 'N/A')}"),
                html.P(f"CEO: {profile.get('ceo', 'N/A')}"),
                html.P(f"Exchange: {profile.get('exchange', 'N/A')}"),
                html.P(f"IPO Date: {profile.get('ipo_date', 'N/A')}"),
                html.A("Website", href=profile.get('website', '#'), target="_blank"),
            ])
        ])
    ])
    
    # Create news cards
    news_cards = []
    for _, row in news.iterrows():
        news_cards.append(
            dbc.Card([
                dbc.CardHeader(row['title']),
                dbc.CardBody([
                    html.P(f"Source: {row['source']}"),
                    html.P(f"Published: {row['published_at']}"),
                    html.P(row['content'][:200] + "..." if len(row['content']) > 200 else row['content']),
                    html.A("Read more", href=row['url'], target="_blank"),
                ])
            ], className="mb-3")
        )
    
    # Create price chart
    if not daily_data.empty:
        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=daily_data.index,
            open=daily_data['open'],
            high=daily_data['high'],
            low=daily_data['low'],
            close=daily_data['close'],
            name='Price'
        ))
        
        fig.update_layout(
            title=f"{ticker} Price Chart",
            xaxis_title="Date",
            yaxis_title="Price ($)",
            template="plotly_dark",
            xaxis_rangeslider_visible=False,
            height=500
        )
    else:
        fig = px.line(title=f"No data available for {ticker}")
    
    # Create technical indicators chart
    if not tech_data.empty and not daily_data.empty:
        # Merge price data with technical indicators
        merged_data = pd.merge(daily_data['close'], tech_data, left_index=True, right_index=True, how='left')
        
        tech_fig = go.Figure()
        
        # Add price line
        tech_fig.add_trace(go.Scatter(
            x=merged_data.index,
            y=merged_data['close'],
            mode='lines',
            name='Close Price',
            line=dict(color='white', width=2)
        ))
        
        # Add SMA lines
        tech_fig.add_trace(go.Scatter(
            x=merged_data.index,
            y=merged_data['sma_20'],
            mode='lines',
            name='SMA 20',
            line=dict(color='blue', width=1.5)
        ))
        
        tech_fig.add_trace(go.Scatter(
            x=merged_data.index,
            y=merged_data['sma_50'],
            mode='lines',
            name='SMA 50',
            line=dict(color='orange', width=1.5)
        ))
        
        tech_fig.add_trace(go.Scatter(
            x=merged_data.index,
            y=merged_data['sma_200'],
            mode='lines',
            name='SMA 200',
            line=dict(color='red', width=1.5)
        ))
        
        # Add Bollinger Bands
        tech_fig.add_trace(go.Scatter(
            x=merged_data.index,
            y=merged_data['bollinger_upper'],
            mode='lines',
            name='Bollinger Upper',
            line=dict(color='rgba(0,255,0,0.5)', width=1),
            showlegend=True
        ))
        
        tech_fig.add_trace(go.Scatter(
            x=merged_data.index,
            y=merged_data['bollinger_lower'],
            mode='lines',
            name='Bollinger Lower',
            line=dict(color='rgba(0,255,0,0.5)', width=1),
            fill='tonexty',
            fillcolor='rgba(0,255,0,0.1)',
            showlegend=True
        ))
        
        tech_fig.update_layout(
            title=f"{ticker} Technical Indicators",
            xaxis_title="Date",
            yaxis_title="Price ($)",
            template="plotly_dark",
            height=500,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
    else:
        tech_fig = px.line(title=f"No technical data available for {ticker}")
    
    return ticker_info_card, company_profile_card, news_cards, fig, tech_fig

if __name__ == "__main__":
    server.run(debug=True, host='127.0.0.1', port=8050) 