# charts.py
# Responsible only for building styled plotly charts

import plotly.express as px
import pandas as pd


class ChartBuilder:
    @staticmethod
    def revenue_chart(df: pd.DataFrame, company: str):
        fig = px.bar(
            df, x="Quarter", y="Revenue",
            title=f"{company} Revenue per Quarter",
            text="Revenue",
            color_discrete_sequence=["#1f77b4"]  # Blue
        )
        fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(size=14, family="Arial", color="#333"),
            title=dict(x=0.5),
            yaxis=dict(showgrid=True, gridcolor="lightgrey")
        )
        return fig

    @staticmethod
    def rd_chart(df: pd.DataFrame, company: str):
        fig = px.line(
            df, x="Quarter", y="RD_Spending", markers=True,
            title=f"{company} R&D Spending per Quarter",
            color_discrete_sequence=["#ff7f0e"]  # Orange
        )
        fig.update_traces(line=dict(width=3))
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(size=14, family="Arial", color="#333"),
            title=dict(x=0.5),
            yaxis=dict(showgrid=True, gridcolor="lightgrey")
        )
        return fig

    @staticmethod
    def net_income_chart(df: pd.DataFrame, company: str):
        fig = px.bar(
            df, x="Quarter", y="Net_Income",
            title=f"{company} Net Income per Quarter",
            text="Net_Income",
            color_discrete_sequence=["#2ca02c"]  # Green
        )
        fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(size=14, family="Arial", color="#333"),
            title=dict(x=0.5),
            yaxis=dict(showgrid=True, gridcolor="lightgrey")
        )
        return fig

    @staticmethod
    def stock_chart(df: pd.DataFrame, company: str, ticker: str):
        fig = px.line(
            df, x="Date", y="Close",
            title=f"{company} ({ticker}) Stock Price Trend",
            color_discrete_sequence=["#9467bd"]  # Purple
        )
        fig.update_traces(line=dict(width=2))
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(size=14, family="Arial", color="#333"),
            title=dict(x=0.5),
            xaxis=dict(showgrid=True, gridcolor="lightgrey"),
            yaxis=dict(showgrid=True, gridcolor="lightgrey")
        )
        return fig

    # --- New Comparison Charts ---
    @staticmethod
    def leaderboard_chart(df: pd.DataFrame):
        """Leaderboard ranking companies by Net Income Margin"""
        if df.empty:
            return px.bar(title="No data available")

        df["NetMargin"] = df["Net_Income"] / df["Revenue"] * 100
        latest = df.sort_values("Quarter").groupby("Company").last().reset_index()

        fig = px.bar(
            latest, x="Company", y="NetMargin",
            title="🏆 Leaderboard: Net Income Margin (Latest Quarter)",
            color="Company",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            title=dict(x=0.5)
        )
        return fig

    @staticmethod
    def scatter_efficiency_chart(df: pd.DataFrame):
        """Scatter plot comparing Revenue Growth vs R&D Spending"""
        if df.empty or df["Company"].nunique() < 2:
            return px.scatter(title="Not enough data for comparison")

        df_sorted = df.sort_values("Quarter")

        # Ensure each company has at least 2 quarters
        valid_companies = df_sorted.groupby("Company").filter(lambda x: len(x) >= 2)
        if valid_companies.empty:
            return px.scatter(title="Not enough history for comparison")

        latest = valid_companies.groupby("Company").last().reset_index()
        prev = valid_companies.groupby("Company").nth(-2).reset_index()

        merged = latest.merge(prev, on="Company", suffixes=("_latest", "_prev"))
        merged["RevenueGrowth"] = (merged["Revenue_latest"] - merged["Revenue_prev"]) / merged["Revenue_prev"] * 100
        merged["RDEfficiency"] = merged["Revenue_latest"] / merged["RD_Spending_latest"]

        fig = px.scatter(
            merged, x="RDEfficiency", y="RevenueGrowth", text="Company",
            size="Net_Income_latest", color="Company",
            title="⚖️ R&D Efficiency vs Revenue Growth",
            hover_data=["Revenue_latest", "RD_Spending_latest", "Net_Income_latest"],
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig.update_traces(textposition="top center")
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            title=dict(x=0.5)
        )
        return fig