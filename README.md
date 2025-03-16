# Financial Data Collection and Analysis

Este proyecto recopila y almacena datos financieros de múltiples APIs para su análisis posterior. Está diseñado para ser modular y fácilmente extensible para añadir más fuentes de datos o funcionalidades.

## Demo

La aplicación está disponible en línea en: [https://github.com/KemVCLand/financial-data-explorer](https://github.com/KemVCLand/financial-data-explorer)

## Estructura del Proyecto

```
.
├── api/                    # Módulos para conectar con APIs
│   ├── __init__.py
│   ├── connectors.py       # Conectores para cada API
│   └── data_fetchers.py    # Funciones para obtener y procesar datos
├── config/                 # Configuración del proyecto
│   ├── __init__.py
│   └── settings.py         # Configuraciones y claves API
├── database/               # Gestión de base de datos
│   ├── __init__.py
│   ├── db_manager.py       # Funciones para gestionar la base de datos
│   └── schema.py           # Definiciones de esquemas de tablas
├── utils/                  # Utilidades
│   ├── __init__.py
│   ├── data_utils.py       # Funciones para procesar datos
│   └── indicators.py       # Cálculo de indicadores técnicos
├── web/                    # Frontend web
│   ├── static/             # Archivos estáticos
│   │   ├── css/            # Hojas de estilo
│   │   └── js/             # Scripts JavaScript
│   └── templates/          # Plantillas HTML
├── app.py                  # Punto de entrada principal para recolección de datos
├── web_app.py              # Aplicación web para visualizar datos
├── tickers.json            # Archivo JSON con los tickers a analizar
├── financial_data.db       # Base de datos SQLite
└── README.md               # Este archivo
```

## Funcionalidades

- Recopilación de datos de múltiples APIs financieras:
  - AlphaVantage (datos históricos diarios)
  - Finhub (cotizaciones en tiempo real)
  - Polygon (datos agregados)
  - Financial Modeling Prep (perfiles de empresas)
  - News API (noticias relacionadas)

- Base de datos optimizada con tablas para:
  - Datos históricos diarios
  - Cotizaciones en tiempo real
  - Perfiles de empresas
  - Noticias
  - Indicadores técnicos
  - Datos fundamentales
  - Carteras y listas de seguimiento

- Cálculo de indicadores técnicos:
  - Medias móviles (SMA, EMA)
  - MACD
  - RSI
  - Bandas de Bollinger
  - ATR

- Frontend web para visualización de datos:
  - Dashboard interactivo con gráficos
  - Explorador de base de datos
  - Visualización de perfiles de empresas
  - Visualización de noticias
  - Visualización de indicadores técnicos

## Requisitos

- Python 3.9+
- Bibliotecas requeridas:
  - requests
  - pandas
  - numpy
  - sqlite3
  - flask
  - plotly
  - dash
  - dash-bootstrap-components

## Instalación

1. Clona este repositorio:
   ```bash
   git clone https://github.com/KemVCLand/financial-data-explorer.git
   cd financial-data-explorer
   ```
2. Crea un entorno virtual: `python -m venv venv39`
3. Activa el entorno virtual:
   - Windows: `venv39\Scripts\activate`
   - macOS/Linux: `source venv39/bin/activate`
4. Instala las dependencias: `pip install -r requirements.txt`
5. (Opcional) Configura las variables de entorno para las claves API:
   ```
   export ALPHAVANTAGE_API_KEY="tu_clave_aqui"
   export FINANCIAL_DATA_SET_API_KEY="tu_clave_aqui"
   export FINHUB_API_KEY="tu_clave_aqui"
   export FMP_API_KEY="tu_clave_aqui"
   export NEWS_API_KEY="tu_clave_aqui"
   ```
   Si no se configuran, se usarán las claves por defecto incluidas en el código.

## Uso

Para ejecutar la aplicación de recolección de datos:

```bash
python app.py
```

Para calcular indicadores técnicos:

```bash
python -m utils.indicators
```

Para iniciar la aplicación web:

```bash
python web_app.py
```

Luego, abre tu navegador y ve a `http://localhost:8050` para acceder a la interfaz web.

## Añadir Nuevos Tickers

Para añadir nuevos tickers, simplemente edita el archivo `tickers.json` en la raíz del proyecto. El archivo tiene el siguiente formato:

```json
{
  "tickers": [
    "AMZN",
    "AAPL",
    "NVDA",
    "MSFT",
    "GOOGL"
  ]
}
```

Puedes añadir o eliminar tickers según tus necesidades. Los cambios se aplicarán automáticamente la próxima vez que ejecutes la aplicación.

## Extensión

Para añadir nuevas APIs:
1. Añade las claves API en `config/settings.py`
2. Crea funciones de conexión en `api/connectors.py`
3. Crea funciones de obtención de datos en `api/data_fetchers.py`
4. Añade esquemas de tablas en `database/schema.py`
5. Actualiza `app.py` para incluir las nuevas funciones

## Licencia

Este proyecto está licenciado bajo la Licencia MIT. 