
import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime

st.set_page_config(page_title="Daily Stock Dashboard", layout="wide")

# Load cleaned data (simulate upload for Streamlit Cloud)
@st.cache_data
def load_data():
    df = pd.read_csv("positions_cleaned.csv")  # Upload this CSV separately on Streamlit Cloud
    return df

positions_df = load_data()

# Title
st.title("📈 Daily Stock Dashboard")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Pull current prices using yfinance
symbols = positions_df["Symbol"].unique().tolist()

with st.spinner("Fetching current prices..."):
    current_prices = {}
    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            price = ticker.history(period="1d")["Close"].iloc[-1]
            current_prices[symbol] = price
        except:
            current_prices[symbol] = None

positions_df["Current Price"] = positions_df["Symbol"].map(current_prices)
positions_df["Current Value"] = positions_df["Quantity"] * positions_df["Current Price"]
positions_df["Cost Value"] = positions_df["Cost Basis"]
positions_df["Gain/Loss"] = positions_df["Current Value"] - positions_df["Cost Value"]
positions_df["Gain %"] = (positions_df["Gain/Loss"] / positions_df["Cost Value"]) * 100

# Display data
st.dataframe(
    positions_df[["Symbol", "Quantity", "Current Price", "Cost Basis", "Current Value", "Gain/Loss", "Gain %"]]
    .sort_values("Gain %", ascending=False)
    .reset_index(drop=True),
    use_container_width=True
)

# Charts
st.subheader("📊 Gain/Loss Overview")
chart_data = positions_df.dropna(subset=["Gain/Loss"])
st.bar_chart(chart_data.set_index("Symbol")["Gain/Loss"])

st.subheader("📈 Current Value by Symbol")
st.bar_chart(chart_data.set_index("Symbol")["Current Value"])

st.success("Dashboard loaded successfully. Schedule this app to run at 6:30 AM and 1:00 PM PT daily.")
