import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pandas as pd
import requests
import os
import sys

# Add path for local backend modules
backend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'backend')
sys.path.append(backend_path)
from data_pipeline.export_utils import export_to_csv, export_to_excel

# Link to local API
API_URL = "http://127.0.0.1:8000"
API_HEADERS = {"X-API-KEY": os.getenv("API_KEY", "pricing-secret-key-2026")}

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX])

app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col(html.H1("Market-Aware Pricing Intelligence", className="text-center text-primary my-4"), width=12)
    ]),
    
    # Overview Cards
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H5("Active Products", className="card-title"),
                html.H2(id="total-products", className="text-info")
            ])
        ], color="dark", inverse=True), width=4),
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H5("Market Price Gap", className="card-title"),
                html.H2(id="avg-market-gap", className="text-warning")
            ])
        ], color="dark", inverse=True), width=4),
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H5("Profit Opportunity", className="card-title"),
                html.H2(id="profit-opportunity", className="text-success")
            ])
        ], color="dark", inverse=True), width=4),
    ], className="mb-4"),

    # Main Dashboard
    dbc.Row([
        # Sidebar/Controls
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Controls"),
                dbc.CardBody([
                    html.Label("Select Product:"),
                    dcc.Dropdown(id='product-dropdown', placeholder="Choose a product..."),
                    html.Br(),
                    html.Br(),
                    dbc.Button("Refresh Data", id="refresh-btn", color="primary", className="w-100 mb-2"),
                    html.Hr(),
                    html.P("Export Reports:", className="small text-muted"),
                    dbc.ButtonGroup([
                        dbc.Button("CSV", id="export-csv-btn", color="secondary", outline=True, size="sm"),
                        dbc.Button("Excel", id="export-excel-btn", color="secondary", outline=True, size="sm"),
                    ], className="w-100"),
                    html.Div(id="export-status", className="small mt-2 text-success")
                ])
            ])
        ], width=3),
        
        # Insights
        dbc.Col([
            dbc.Tabs([
                dbc.Tab(label="Market Performance", children=[
                    dbc.Row([
                        dbc.Col(dcc.Graph(id='price-history-chart'), width=12)
                    ]),
                    dbc.Row([
                        dbc.Col(dcc.Graph(id='competitor-comp-chart'), width=6),
                        dbc.Col(dbc.Card([
                            dbc.CardHeader("AI Recommendation"),
                            dbc.CardBody(id='recommendation-box')
                        ], className="mt-4"), width=6)
                    ])
                ]),
                dbc.Tab(label="Demand Analytics", children=[
                    dbc.Row([
                        dbc.Col(dcc.Graph(id='volume-elasticity-chart'), width=12)
                    ]),
                    dbc.Row([
                        dbc.Col(dcc.Graph(id='quarterly-performance-chart'), width=12)
                    ])
                ])
            ])
        ], width=9)
    ])
], fluid=True, style={"backgroundColor": "#f8f9fa", "minHeight": "100vh"})

# Callbacks
@app.callback(
    [Output('product-dropdown', 'options'),
     Output('total-products', 'children'),
     Output('avg-market-gap', 'children'),
     Output('profit-opportunity', 'children')],
    [Input('refresh-btn', 'n_clicks')]
)
def update_metadata(n):
    try:
        resp = requests.get(f"{API_URL}/products", headers=API_HEADERS).json()
        options = [{'label': p['name'], 'value': p['id']} for p in resp]
        
        trend_resp = requests.get(f"{API_URL}/market-trend", headers=API_HEADERS).json()
        avg_gap = sum(t['gap'] for t in trend_resp) / len(trend_resp) if trend_resp else 0

        # Price Advantage: how much cheaper we are vs market average (flip sign of gap)
        # gap = (our_price - market_avg) / market_avg * 100
        # If gap is negative, we are cheaper — advantage is positive
        price_advantage = -avg_gap
        advantage_str = f"{price_advantage:+.1f}%"
        
        return options, len(resp), f"{avg_gap:+.1f}%", advantage_str
    except Exception:
        return [], "0", "0.0%", "N/A"

@app.callback(
    [Output('price-history-chart', 'figure'),
     Output('competitor-comp-chart', 'figure'),
     Output('recommendation-box', 'children'),
     Output('volume-elasticity-chart', 'figure'),
     Output('quarterly-performance-chart', 'figure')],
    [Input('product-dropdown', 'value')]
)
def update_product_charts(product_id):
    if not product_id:
        return go.Figure(), go.Figure(), "Select a product to see insights.", go.Figure(), go.Figure()
    
    data = requests.get(f"{API_URL}/analytics/{product_id}", headers=API_HEADERS).json()
    
    # 1. Price/Sales History
    sales_df = pd.DataFrame(data['sales_history'])
    sales_df['date'] = pd.to_datetime(sales_df['date'])
    sales_df = sales_df.sort_values('date')
    
    fig_hist = make_subplots(specs=[[{"secondary_y": True}]])
    fig_hist.add_trace(go.Scatter(x=sales_df['date'], y=sales_df['selling_price'], name="Selling Price"), secondary_y=False)
    fig_hist.add_trace(go.Bar(x=sales_df['date'], y=sales_df['quantity'], name="Volume Sold", opacity=0.3), secondary_y=True)
    fig_hist.update_layout(title="Price vs Sales Volume Over Time", 
                            yaxis_title="Price (₹)",
                            yaxis2_title="Units Sold",
                            template="plotly_white")
    
    # 2. Competitor Comparison
    comp_df = pd.DataFrame(data['competitor_prices'])
    # Add our current price
    our_price = data['product']['current_price']
    comp_comp = pd.concat([comp_df, pd.DataFrame([{'competitor_name': 'Our Store', 'price': our_price}])])
    
    fig_comp = px.bar(comp_comp, x='competitor_name', y='price', 
                      title="Market Positioning", 
                      color='competitor_name',
                      labels={"price": "Price (₹)", "competitor_name": "Competitor"},
                      template="plotly_white")
    
    # 3. Recommendation Box
    rec = data['latest_recommendation']
    if rec:
        diff = rec['recommended_price'] - our_price
        color = "success" if diff > 0 else "danger"
        rec_html = html.Div([
            html.H3(f"₹{rec['recommended_price']}", className=f"text-{color}"),
            html.P(f"Confidence: {rec['confidence_score']*100:.1f}%"),
            html.Small(f"Logic: {rec['logic_type']}"),
            html.Hr(),
            html.P("Recommended action based on market trends and elasticity index.")
        ])
    else:
        rec_html = "No recommendation generated yet."

    # 4. Elasticity Chart (Scatter)
    fig_elas = px.scatter(sales_df, x='selling_price', y='quantity', trendline="ols",
                          title="Price Sensitivity (Demand Curve)",
                          labels={"selling_price": "Price (₹)", "quantity": "Units Sold"},
                          template="plotly_white")

    # 5. Quarterly Performance
    sales_df['quarter'] = sales_df['date'].dt.to_period('Q').astype(str)
    q_df = sales_df.groupby('quarter').agg({'quantity': 'sum', 'selling_price': 'mean'}).reset_index()
    
    fig_q = px.bar(q_df, x='quarter', y='quantity', 
                   title="Quarterly Sales Volume (Last 6 Months)",
                   labels={"quarter": "Quarter", "quantity": "Total Units Sold"},
                   template="plotly_white",
                   color_discrete_sequence=['#2C3E50'])

    return fig_hist, fig_comp, rec_html, fig_elas, fig_q

# Export Callbacks
@app.callback(
    Output('export-status', 'children'),
    [Input('export-csv-btn', 'n_clicks'),
     Input('export-excel-btn', 'n_clicks')],
    [dash.State('product-dropdown', 'value')]
)
def handle_export(csv_n, excel_n, product_id):
    ctx = dash.callback_context
    if not ctx.triggered or not product_id:
        return ""
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    try:
        if button_id == 'export-csv-btn':
            path = export_to_csv(product_id)
            return f"CSV Saved: {os.path.basename(path)}"
        elif button_id == 'export-excel-btn':
            path = export_to_excel(product_id)
            return f"Excel Saved: {os.path.basename(path)}"
    except Exception as e:
        return f"Export Error: {str(e)}"
    
    return ""

if __name__ == "__main__":
    app.run(debug=True, port=8050)
