import os
import pandas as pd
from alpha_vantage.timeseries import TimeSeries


class DataHandler:
    def __init__(self):
        # Read API key from environment variable
        self.api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
        if not self.api_key:
            raise ValueError("Alpha Vantage API key not found. Please set ALPHA_VANTAGE_API_KEY.")

        # Initialize Alpha Vantage TimeSeries client
        self.ts = TimeSeries(key=self.api_key, output_format="pandas")

    def get_stock_data(self, ticker: str):
        """
        Fetch daily stock data for a given ticker from Alpha Vantage.
        Returns a DataFrame with columns: Date, Open, High, Low, Close, Volume
        """
        try:
            df, meta = self.ts.get_daily(symbol=ticker, outputsize="compact")
            # Rename columns to simpler names
            df = df.rename(columns={
                "1. open": "Open",
                "2. high": "High",
                "3. low": "Low",
                "4. close": "Close",
                "5. volume": "Volume"
            })
            # Reset index so 'Date' is a column
            df.index.name = "Date"
            df.reset_index(inplace=True)
            return df
        except Exception as e:
            print(f"Error fetching stock data for {ticker}: {e}")
            # Return empty DataFrame with correct columns to avoid Plotly errors
            return pd.DataFrame(columns=["Date", "Open", "High", "Low", "Close", "Volume"])

    def get_revenue_data(self, company: str):
        """
        Load revenue/financial data from local CSV.
        """
        try:
            df = pd.read_csv("data/financials.csv")  # Updated to match your CSV file
            return df[df["Company"] == company]
        except Exception as e:
            print(f"Error loading revenue data: {e}")
            return pd.DataFrame(columns=["Company", "Ticker", "Quarter", "Revenue", "RD_Spending", "Net_Income"])

    def get_companies(self):
        """
        Get a list of unique companies from the financials CSV.
        """
        try:
            df = pd.read_csv("data/financials.csv")  # Updated to match your CSV file
            return df["Company"].unique().tolist()
        except Exception as e:
            print(f"Error loading companies: {e}")
            return []

    def get_all_revenue_data(self):
        """
        Load financial data for all companies from the CSV and return as a single DataFrame.
        """
        try:
            df = pd.read_csv("data/financials.csv")
            return df
        except Exception as e:
            print(f"Error loading all revenue data: {e}")
            return pd.DataFrame(columns=["Company", "Ticker", "Quarter", "Revenue", "RD_Spending", "Net_Income"])
