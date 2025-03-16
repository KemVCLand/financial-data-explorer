// Main JavaScript for Financial Data Explorer

document.addEventListener('DOMContentLoaded', function() {
    // Database Explorer Modal
    const databaseExplorerLink = document.getElementById('database-explorer-link');
    const databaseExplorerModal = new bootstrap.Modal(document.getElementById('databaseExplorerModal'));
    
    if (databaseExplorerLink) {
        databaseExplorerLink.addEventListener('click', function(e) {
            e.preventDefault();
            loadTables();
            databaseExplorerModal.show();
        });
    }
    
    // Ticker Info Modal
    const tickerInfoButtons = document.querySelectorAll('.ticker-info');
    const tickerInfoModal = new bootstrap.Modal(document.getElementById('tickerInfoModal'));
    
    tickerInfoButtons.forEach(button => {
        button.addEventListener('click', function() {
            const ticker = this.getAttribute('data-ticker');
            loadTickerInfo(ticker);
            document.getElementById('ticker-modal-title').innerHTML = `<i class="fas fa-info-circle me-2"></i>${ticker} Information`;
            tickerInfoModal.show();
        });
    });

    // Inicializar gráficos de previsualización para cada ticker
    initTickerPreviews();
});

// Inicializar gráficos de previsualización para cada ticker
function initTickerPreviews() {
    const tickerCards = document.querySelectorAll('.ticker-item');
    
    tickerCards.forEach(card => {
        const ticker = card.getAttribute('data-ticker');
        const previewContainer = card.querySelector('.ticker-preview');
        
        if (previewContainer) {
            // Mostrar un estado de carga mientras se obtienen los datos
            previewContainer.innerHTML = `
                <div class="text-center py-2">
                    <div class="spinner-border spinner-border-sm text-accent" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <p class="small mb-0 mt-1">Cargando datos...</p>
                </div>
            `;
            
            // Obtener datos del ticker y calcular retornos
            Promise.all([
                fetch(`/api/ticker/${ticker}`).then(response => response.json()),
                fetch(`/api/returns/${ticker}`).then(response => response.json())
            ])
            .then(([data, returns]) => {
                console.log(`Returns data for ${ticker}:`, returns);
                
                // Find the returns grid container
                const returnsGrid = previewContainer.querySelector('.returns-grid');
                
                if (!returnsGrid) {
                    console.error('Returns grid not found in the DOM');
                    return;
                }
                
                // Clear existing content
                returnsGrid.innerHTML = '';
                
                // Function to create a return element
                function createReturnElement(label, value) {
                    console.log(`Creating return element for ${label} with value:`, value);
                    
                    const returnEl = document.createElement('div');
                    returnEl.className = 'text-center mx-1';
                    
                    const labelEl = document.createElement('div');
                    labelEl.className = 'small text-muted fw-bold';
                    labelEl.textContent = label;
                    
                    const valueEl = document.createElement('div');
                    if (value !== null && value !== undefined) {
                        const returnValue = parseFloat(value);
                        console.log(`Parsed return value for ${label}:`, returnValue);
                        const isPositive = returnValue >= 0;
                        valueEl.className = `fw-bold ${isPositive ? 'text-success' : 'text-danger'}`;
                        
                        // Add arrow icon based on positive or negative
                        const icon = isPositive ? '▲' : '▼';
                        valueEl.innerHTML = `${icon} ${isPositive ? '+' : ''}${returnValue.toFixed(2)}%`;
                    } else {
                        console.log(`No value for ${label}, showing N/A`);
                        valueEl.className = 'text-muted';
                        valueEl.textContent = 'N/A';
                    }
                    
                    returnEl.appendChild(labelEl);
                    returnEl.appendChild(valueEl);
                    return returnEl;
                }
                
                // Add return elements with real API data
                if (returns && typeof returns === 'object') {
                    console.log('Returns object is valid:', returns);
                    // Convert decimal returns to percentages (multiply by 100)
                    const ytdReturn = returns.ytd !== null ? returns.ytd * 100 : null;
                    const quarterReturn = returns.quarter !== null ? returns.quarter * 100 : null;
                    const yearReturn = returns.year !== null ? returns.year * 100 : null;
                    
                    console.log('Converted returns:', {
                        ytd: ytdReturn,
                        quarter: quarterReturn,
                        year: yearReturn
                    });
                    
                    returnsGrid.appendChild(createReturnElement('YTD', ytdReturn));
                    returnsGrid.appendChild(createReturnElement('Quarter', quarterReturn));
                    returnsGrid.appendChild(createReturnElement('Year', yearReturn));
                } else {
                    console.log('Returns object is invalid:', returns);
                    returnsGrid.appendChild(createReturnElement('YTD', null));
                    returnsGrid.appendChild(createReturnElement('Quarter', null));
                    returnsGrid.appendChild(createReturnElement('Year', null));
                }
                
                // Add current price and change if available
                if (data.quotes && data.quotes.current_price) {
                    const changeClass = data.quotes.change >= 0 ? 'text-success' : 'text-danger';
                    const changeIcon = data.quotes.change >= 0 ? '▲' : '▼';
                    const priceInfo = document.createElement('div');
                    priceInfo.className = 'd-flex justify-content-between align-items-center mt-2';
                    priceInfo.innerHTML = `
                        <span class="fw-bold">$${data.quotes.current_price.toFixed(2)}</span>
                        <span class="${changeClass}">
                            ${changeIcon} ${data.quotes.percent_change?.toFixed(2) || '0.00'}%
                        </span>
                    `;
                    previewContainer.appendChild(priceInfo);
                }
            })
            .catch(error => {
                console.error(`Error loading data for ${ticker}:`, error);
                console.error('Error details:', error.message, error.stack);
                
                // Find the returns grid container
                const returnsGrid = previewContainer.querySelector('.returns-grid');
                
                if (returnsGrid) {
                    // Clear existing content
                    returnsGrid.innerHTML = '';
                    
                    // Add placeholder elements
                    const ytdEl = document.createElement('div');
                    ytdEl.className = 'text-center mx-1';
                    ytdEl.innerHTML = `
                        <div class="small text-muted fw-bold">YTD</div>
                        <div class="fw-bold text-muted">N/A</div>
                    `;
                    
                    const quarterEl = document.createElement('div');
                    quarterEl.className = 'text-center mx-1';
                    quarterEl.innerHTML = `
                        <div class="small text-muted fw-bold">Quarter</div>
                        <div class="fw-bold text-muted">N/A</div>
                    `;
                    
                    const yearEl = document.createElement('div');
                    yearEl.className = 'text-center mx-1';
                    yearEl.innerHTML = `
                        <div class="small text-muted fw-bold">Year</div>
                        <div class="fw-bold text-muted">N/A</div>
                    `;
                    
                    returnsGrid.appendChild(ytdEl);
                    returnsGrid.appendChild(quarterEl);
                    returnsGrid.appendChild(yearEl);
                } else {
                    console.error('Returns grid not found in the DOM for error handling');
                }
            });
        }
    });
}

// Calcular retornos para un ticker
function calculateReturns(ticker) {
    return fetch(`/api/returns/${ticker}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        });
}

// Load tables for database explorer
function loadTables() {
    fetch('/api/tables')
        .then(response => response.json())
        .then(tables => {
            const tableList = document.getElementById('table-list');
            if (!tableList) return;
            
            tableList.innerHTML = '';
            
            tables.forEach(table => {
                const option = document.createElement('option');
                option.value = table;
                option.textContent = table;
                tableList.appendChild(option);
            });
            
            // Load first table by default
            if (tables.length > 0) {
                loadTableData(tables[0]);
            }
        })
        .catch(error => console.error('Error loading tables:', error));
}

function loadTableData(tableName) {
    const tableContainer = document.getElementById('table-data-container');
    if (!tableContainer) return;
    
    tableContainer.innerHTML = '<div class="text-center my-5"><div class="spinner-border text-primary" role="status"></div><p class="mt-2">Loading data...</p></div>';
    
    fetch(`/api/table/${tableName}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                tableContainer.innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
                return;
            }
            
            if (data.length === 0) {
                tableContainer.innerHTML = '<div class="alert alert-info">No data available for this table.</div>';
                return;
            }
            
            // Create table
            const table = document.createElement('table');
            table.className = 'table table-striped table-hover';
            
            // Create header
            const thead = document.createElement('thead');
            const headerRow = document.createElement('tr');
            
            Object.keys(data[0]).forEach(key => {
                const th = document.createElement('th');
                th.textContent = key;
                headerRow.appendChild(th);
            });
            
            thead.appendChild(headerRow);
            table.appendChild(thead);
            
            // Create body
            const tbody = document.createElement('tbody');
            
            data.forEach(row => {
                const tr = document.createElement('tr');
                
                Object.values(row).forEach(value => {
                    const td = document.createElement('td');
                    
                    // Format value based on type
                    if (value === null) {
                        td.textContent = 'NULL';
                        td.className = 'text-muted';
                    } else if (typeof value === 'object') {
                        td.textContent = JSON.stringify(value);
                    } else {
                        td.textContent = value;
                    }
                    
                    tr.appendChild(td);
                });
                
                tbody.appendChild(tr);
            });
            
            table.appendChild(tbody);
            
            // Add table to container
            tableContainer.innerHTML = '';
            tableContainer.appendChild(table);
            
            // Update table name
            const tableNameElement = document.getElementById('current-table-name');
            if (tableNameElement) {
                tableNameElement.textContent = tableName;
            }
        })
        .catch(error => {
            console.error('Error loading table data:', error);
            tableContainer.innerHTML = '<div class="alert alert-danger">Error loading table data. Please try again.</div>';
        });
}

// Load ticker information
function loadTickerInfo(ticker) {
    fetch(`/api/ticker/${ticker}`)
        .then(response => response.json())
        .then(data => {
            const modalBody = document.getElementById('ticker-modal-body');
            
            // Crear gráfico de precios
            let priceChartHtml = '';
            if (data.daily_data && data.daily_data.length > 0) {
                priceChartHtml = `
                    <div class="col-md-12 mb-4">
                        <div class="card">
                            <div class="card-header d-flex justify-content-between align-items-center">
                                <h5 class="mb-0"><i class="fas fa-chart-line me-2"></i>Price History</h5>
                                <div class="btn-group btn-group-sm" role="group" id="timeframe-selector">
                                    <button type="button" class="btn btn-secondary active" data-days="7">1W</button>
                                    <button type="button" class="btn btn-secondary" data-days="30">1M</button>
                                    <button type="button" class="btn btn-secondary" data-days="90">3M</button>
                                    <button type="button" class="btn btn-secondary" data-days="180">6M</button>
                                    <button type="button" class="btn btn-secondary" data-days="365">1Y</button>
                                </div>
                            </div>
                            <div class="card-body">
                                <canvas id="price-chart" height="250"></canvas>
                            </div>
                        </div>
                    </div>
                `;
            }
            
            let html = '<div class="row">';
            
            // Ticker information
            html += `
                <div class="col-md-12 mb-4">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0"><i class="fas fa-info-circle me-2"></i>Ticker Information</h5>
                        </div>
                        <div class="card-body">
            `;
            
            if (Object.keys(data.ticker_info).length > 0) {
                html += `
                    <div class="row">
                        <div class="col-md-4">
                            <div class="mb-3">
                                <label class="text-muted small">Fundación</label>
                                <p class="mb-0 fs-5">${data.ticker_info.fundacion || 'N/A'}</p>
                            </div>
                            <div class="mb-3">
                                <label class="text-muted small">País</label>
                                <p class="mb-0 fs-5">${data.ticker_info.pais || 'N/A'}</p>
                            </div>
                            <div class="mb-3">
                                <label class="text-muted small">Años en bolsa</label>
                                <p class="mb-0 fs-5">${data.ticker_info.anos_en_bolsa || 'N/A'}</p>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="mb-3">
                                <label class="text-muted small">Sector</label>
                                <p class="mb-0 fs-5">${data.ticker_info.sector || 'N/A'}</p>
                            </div>
                            <div class="mb-3">
                                <label class="text-muted small">Subsector</label>
                                <p class="mb-0 fs-5">${data.ticker_info.subsector || 'N/A'}</p>
                            </div>
                            <div class="mb-3">
                                <label class="text-muted small">Tipo</label>
                                <p class="mb-0 fs-5"><span class="badge bg-accent">${data.ticker_info.tipo || 'N/A'}</span></p>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="mb-3">
                                <label class="text-muted small">Reseña</label>
                                <p class="mb-0">${data.ticker_info.resena || 'No hay reseña disponible.'}</p>
                            </div>
                        </div>
                    </div>
                `;
            } else {
                html += '<p>No ticker information available.</p>';
            }
            
            html += `
                        </div>
                    </div>
                </div>
            `;
            
            // Añadir gráfico de precios
            html += priceChartHtml;
            
            // Latest quote
            html += `
                <div class="col-md-6 mb-4">
                    <div class="card h-100">
                        <div class="card-header">
                            <h5 class="mb-0"><i class="fas fa-dollar-sign me-2"></i>Latest Quote</h5>
                        </div>
                        <div class="card-body">
            `;
            
            if (Object.keys(data.quotes).length > 0) {
                const changeClass = data.quotes.change >= 0 ? 'text-success' : 'text-danger';
                const changeIcon = data.quotes.change >= 0 ? '<i class="fas fa-caret-up me-1"></i>' : '<i class="fas fa-caret-down me-1"></i>';
                
                html += `
                    <div class="text-center mb-4">
                        <h2 class="display-4 mb-0">$${data.quotes.current_price?.toFixed(2) || 'N/A'}</h2>
                        <p class="${changeClass} fs-4">
                            ${changeIcon} ${data.quotes.change?.toFixed(2) || '0.00'} (${data.quotes.percent_change?.toFixed(2) || '0.00'}%)
                        </p>
                    </div>
                    <div class="row">
                        <div class="col-6 mb-3">
                            <label class="text-muted small">Open</label>
                            <p class="mb-0 fs-5">$${data.quotes.open?.toFixed(2) || 'N/A'}</p>
                        </div>
                        <div class="col-6 mb-3">
                            <label class="text-muted small">Previous Close</label>
                            <p class="mb-0 fs-5">$${data.quotes.previous_close?.toFixed(2) || 'N/A'}</p>
                        </div>
                        <div class="col-6 mb-3">
                            <label class="text-muted small">High</label>
                            <p class="mb-0 fs-5">$${data.quotes.high?.toFixed(2) || 'N/A'}</p>
                        </div>
                        <div class="col-6 mb-3">
                            <label class="text-muted small">Low</label>
                            <p class="mb-0 fs-5">$${data.quotes.low?.toFixed(2) || 'N/A'}</p>
                        </div>
                    </div>
                `;
            } else {
                html += '<div class="text-center py-4"><p>No quote data available.</p></div>';
            }
            
            html += `
                        </div>
                    </div>
                </div>
            `;
            
            // Company profile
            html += `
                <div class="col-md-6 mb-4">
                    <div class="card h-100">
                        <div class="card-header">
                            <h5 class="mb-0"><i class="fas fa-building me-2"></i>Company Profile</h5>
                        </div>
                        <div class="card-body">
            `;
            
            if (Object.keys(data.profile).length > 0) {
                html += `
                    <h4 class="mb-3">${data.profile.company_name || ticker}</h4>
                    <div class="row mb-3">
                        <div class="col-md-6">
                            <div class="mb-2">
                                <label class="text-muted small">Industry</label>
                                <p class="mb-0">${data.profile.industry || 'N/A'}</p>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="mb-2">
                                <label class="text-muted small">Sector</label>
                                <p class="mb-0">${data.profile.sector || 'N/A'}</p>
                            </div>
                        </div>
                    </div>
                    <div class="row mb-3">
                        <div class="col-md-6">
                            <div class="mb-2">
                                <label class="text-muted small">Market Cap</label>
                                <p class="mb-0">${data.profile.market_cap ? '$' + data.profile.market_cap.toLocaleString() : 'N/A'}</p>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="mb-2">
                                <label class="text-muted small">Employees</label>
                                <p class="mb-0">${data.profile.employees ? data.profile.employees.toLocaleString() : 'N/A'}</p>
                            </div>
                        </div>
                    </div>
                    <div>
                        <label class="text-muted small">Description</label>
                        <p class="mb-0 small">${data.profile.description || 'No description available.'}</p>
                    </div>
                `;
            } else {
                html += '<div class="text-center py-4"><p>No profile data available.</p></div>';
            }
            
            html += `
                        </div>
                    </div>
                </div>
            `;
            
            // Latest news
            html += `
                <div class="col-md-12 mb-4">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0"><i class="fas fa-newspaper me-2"></i>Latest News</h5>
                        </div>
                        <div class="card-body">
            `;
            
            if (data.news && data.news.length > 0) {
                html += '<div class="row">';
                
                data.news.forEach(article => {
                    const date = new Date(article.published_at);
                    const formattedDate = date.toLocaleDateString('es-ES', { 
                        year: 'numeric', 
                        month: 'short', 
                        day: 'numeric' 
                    });
                    
                    html += `
                        <div class="col-md-6 mb-3">
                            <div class="card h-100">
                                <div class="card-body">
                                    <h6 class="card-title">${article.title}</h6>
                                    <p class="card-text small mb-2">${article.content?.substring(0, 100)}...</p>
                                    <div class="d-flex justify-content-between align-items-center mt-3">
                                        <small class="text-muted">${article.source} · ${formattedDate}</small>
                                        <a href="${article.url}" target="_blank" class="btn btn-sm btn-primary">
                                            <i class="fas fa-external-link-alt me-1"></i>Read
                                        </a>
                                    </div>
                                </div>
                            </div>
                        </div>
                    `;
                });
                
                html += '</div>';
            } else {
                html += '<p>No news available for this ticker.</p>';
            }
            
            html += `
                        </div>
                    </div>
                </div>
            `;
            
            html += '</div>';
            
            modalBody.innerHTML = html;
            
            // Inicializar el gráfico de precios si hay datos
            if (data.daily_data && data.daily_data.length > 0) {
                initPriceChart(data.daily_data, 7); // Por defecto mostrar 7 días
                
                // Manejar cambios en el timeframe
                document.querySelectorAll('#timeframe-selector button').forEach(button => {
                    button.addEventListener('click', function() {
                        // Quitar clase activa de todos los botones
                        document.querySelectorAll('#timeframe-selector button').forEach(btn => {
                            btn.classList.remove('active');
                        });
                        
                        // Añadir clase activa al botón clickeado
                        this.classList.add('active');
                        
                        // Actualizar gráfico con el nuevo timeframe
                        const days = parseInt(this.getAttribute('data-days'));
                        initPriceChart(data.daily_data, days);
                    });
                });
            }
            
            // Aplicar estilos a los badges
            document.querySelectorAll('.bg-accent').forEach(el => {
                el.style.backgroundColor = 'var(--accent-color)';
            });
        })
        .catch(error => {
            console.error(`Error loading ticker info for ${ticker}:`, error);
            document.getElementById('ticker-modal-body').innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-circle me-2"></i>
                    Error loading data for ${ticker}. Please try again later.
                </div>
            `;
        });
}

// Inicializar gráfico de precios
function initPriceChart(data, days) {
    // Filtrar datos según el timeframe seleccionado
    const filteredData = data.slice(0, days).reverse();
    
    // Preparar datos para el gráfico
    const dates = filteredData.map(d => d.date);
    const prices = filteredData.map(d => d.close);
    
    // Determinar color basado en tendencia
    const startPrice = prices[0];
    const endPrice = prices[prices.length - 1];
    const trendColor = endPrice >= startPrice ? 'rgba(0, 184, 148, 1)' : 'rgba(255, 118, 117, 1)';
    const trendBg = endPrice >= startPrice ? 'rgba(0, 184, 148, 0.1)' : 'rgba(255, 118, 117, 0.1)';
    
    // Crear o actualizar gráfico
    const ctx = document.getElementById('price-chart').getContext('2d');
    
    // Destruir gráfico existente si hay uno
    if (window.priceChart) {
        window.priceChart.destroy();
    }
    
    // Crear nuevo gráfico
    window.priceChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [{
                label: 'Price',
                data: prices,
                borderColor: trendColor,
                backgroundColor: trendBg,
                borderWidth: 2,
                pointRadius: 3,
                pointHoverRadius: 6,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        label: function(context) {
                            return `$${context.raw.toFixed(2)}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false,
                        drawBorder: false
                    },
                    ticks: {
                        maxRotation: 0,
                        maxTicksLimit: 5
                    }
                },
                y: {
                    grid: {
                        drawBorder: false
                    },
                    ticks: {
                        callback: function(value) {
                            return '$' + value.toFixed(2);
                        }
                    }
                }
            },
            interaction: {
                mode: 'index',
                intersect: false
            }
        }
    });
}

// Initialize database explorer if on admin page
document.addEventListener('DOMContentLoaded', function() {
    const databaseExplorerModal = document.getElementById('databaseExplorerModal');
    if (databaseExplorerModal) {
        const tableList = document.getElementById('table-list');
        if (tableList) {
            tableList.addEventListener('change', function() {
                loadTableData(this.value);
            });
            
            // Load tables when modal is shown
            const modal = new bootstrap.Modal(databaseExplorerModal);
            databaseExplorerModal.addEventListener('shown.bs.modal', function() {
                loadTables();
            });
            
            // Database explorer button
            const databaseExplorerBtn = document.getElementById('database-explorer-btn');
            if (databaseExplorerBtn) {
                databaseExplorerBtn.addEventListener('click', function() {
                    modal.show();
                });
            }
        }
    }
}); 