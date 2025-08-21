import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
from data_handler import DataHandler
from charts import ChartBuilder
from config import TICKER_MAP
import numpy as np


class Dashboard:
    def __init__(self):
        self.app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
        self.data_handler = DataHandler()
        self.chart_builder = ChartBuilder()
        self._set_layout()
        self._register_callbacks()

    def _set_layout(self):
        companies = self.data_handler.get_companies()

        self.app.layout = dbc.Container([
            html.H1("📊 Tech Giants Stock & Revenue Dashboard", className="text-center my-4"),

            dcc.Tabs(id="tabs", value="company", children=[
                dcc.Tab(label="📈 Company View", value="company"),
                dcc.Tab(label="🏆 Compare Companies", value="compare"),
            ]),

            html.Div(id="company-content"),   # Always present
            html.Div(id="compare-content")    # Always present
        ], fluid=True)

        # Store company list for later
        self.companies = companies

    def _register_callbacks(self):
        # --- Tab switching logic ---
        @self.app.callback(
            [Output("company-content", "style"),
             Output("compare-content", "style")],
            Input("tabs", "value")
        )
        def toggle_tabs(tab):
            if tab == "company":
                return {"display": "block"}, {"display": "none"}
            else:
                return {"display": "none"}, {"display": "block"}

        # --- Company content ---
        self.app.layout.children[2].children = dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.Label("Select Company:"),
                    dcc.Dropdown(
                        id="company-dropdown",
                        options=[{"label": c, "value": c} for c in self.companies],
                        value=self.companies[0],
                        clearable=False
                    )
                ], width=4),
            ]),

            html.Hr(),

            # KPI cards row
            dbc.Row([
                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H6("Revenue Growth", className="card-title"),
                    html.H3(id="kpi-revenue-growth", className="text-success")
                ])), md=3),

                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H6("R&D Efficiency", className="card-title"),
                    html.H3(id="kpi-rd-efficiency", className="text-info")
                ])), md=3),

                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H6("Net Income Margin", className="card-title"),
                    html.H3(id="kpi-net-margin", className="text-warning")
                ])), md=3),

                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H6("Stock % Change", className="card-title"),
                    html.H3(id="kpi-stock-change", className="text-primary")
                ])), md=3),
            ], className="mb-4"),

            # Charts
            dbc.Row([
                dbc.Col(dcc.Graph(id="revenue-chart"), md=6),
                dbc.Col(dcc.Graph(id="rd-chart"), md=6),
            ]),

            dbc.Row([
                dbc.Col(dcc.Graph(id="netincome-chart"), md=6),
                dbc.Col(dcc.Graph(id="stock-chart"), md=6),
            ])
        ])

        # --- Compare content ---
        self.app.layout.children[3].children = dbc.Container([
            dbc.Row([
                dbc.Col(dcc.Graph(id="leaderboard-chart"), md=6),
                dbc.Col(dcc.Graph(id="scatter-chart"), md=6),
            ])
        ])

        # --- Company callbacks ---
        @self.app.callback(
            [Output("revenue-chart", "figure"),
             Output("rd-chart", "figure"),
             Output("netincome-chart", "figure"),
             Output("stock-chart", "figure"),
             Output("kpi-revenue-growth", "children"),
             Output("kpi-rd-efficiency", "children"),
             Output("kpi-net-margin", "children"),
             Output("kpi-stock-change", "children")],
            [Input("company-dropdown", "value")]
        )
        def update_charts(company):
            try:
                df_revenue = self.data_handler.get_revenue_data(company)
                ticker = TICKER_MAP[company]
                df_stock = self.data_handler.get_stock_data(ticker)

                rev_growth = rd_efficiency = net_margin = stock_change = np.nan

                if not df_revenue.empty:
                    if len(df_revenue) >= 2:
                        rev_growth = (df_revenue["Revenue"].iloc[-1] - df_revenue["Revenue"].iloc[-2]) / df_revenue["Revenue"].iloc[-2] * 100
                    if df_revenue["RD_Spending"].iloc[-1] != 0:
                        rd_efficiency = df_revenue["Revenue"].iloc[-1] / df_revenue["RD_Spending"].iloc[-1]
                    if df_revenue["Revenue"].iloc[-1] != 0:
                        net_margin = df_revenue["Net_Income"].iloc[-1] / df_revenue["Revenue"].iloc[-1] * 100

                if not df_stock.empty and len(df_stock) >= 2:
                    stock_change = (df_stock["Close"].iloc[-1] - df_stock["Close"].iloc[0]) / df_stock["Close"].iloc[0] * 100

                return (
                    self.chart_builder.revenue_chart(df_revenue, company),
                    self.chart_builder.rd_chart(df_revenue, company),
                    self.chart_builder.net_income_chart(df_revenue, company),
                    self.chart_builder.stock_chart(df_stock, company, ticker),
                    f"{rev_growth:.2f}%" if not np.isnan(rev_growth) else "N/A",
                    f"{rd_efficiency:.2f}" if not np.isnan(rd_efficiency) else "N/A",
                    f"{net_margin:.2f}%" if not np.isnan(net_margin) else "N/A",
                    f"{stock_change:.2f}%" if not np.isnan(stock_change) else "N/A"
                )
            except Exception as e:
                print(f"❌ Callback error: {e}")
                return dash.no_update

        # --- Compare callbacks ---
        @self.app.callback(
            [Output("leaderboard-chart", "figure"),
             Output("scatter-chart", "figure")],
            Input("tabs", "value")
        )
        def update_compare(tab):
            if tab == "compare":
                df_all = self.data_handler.get_all_revenue_data()
                return (
                    self.chart_builder.leaderboard_chart(df_all),
                    self.chart_builder.scatter_efficiency_chart(df_all)
                )
            return dash.no_update, dash.no_update

    def run(self):
        self.app.run(debug=True)
