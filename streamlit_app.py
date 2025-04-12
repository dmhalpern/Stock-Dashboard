
import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime

st.set_page_config(page_title="📈 Stock & Option Dashboard", layout="wide")

# Load data safely
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("positions_cleaned.csv")
        # Filter out non-stock symbols (e.g., CASH, ACCOUNT TOTAL)
        df = df[df["Symbol"].str.match("^[A-Z]{1,5}$", na=False)]
        return df
    except FileNotFoundError:
        st.error("CSV file not found. Please upload 'positions_cleaned.csv' to the repo.")
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.stop()

st.title("📊 Daily Stock & Option Dashboard")
st.caption(f"Last refreshed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Fetch live prices
with st.spinner("Getting real-time prices..."):
    symbols = df["Symbol"].unique().tolist()
    live_prices = {}
    for sym in symbols:
        try:
            live_prices[sym] = yf.Ticker(sym).history(period="1d")["Close"].iloc[-1]
        except:
            live_prices[sym] = None

df["Current Price"] = df["Symbol"].map(live_prices)
df["Current Value"] = df["Quantity"] * df["Current Price"]
df["Gain/Loss"] = df["Current Value"] - df["Cost Basis"]
df["Gain %"] = (df["Gain/Loss"] / df["Cost Basis"]) * 100

# Summary table
st.subheader("📋 Portfolio Summary")
st.dataframe(df[[
    "Symbol", "Quantity", "Current Price", "Strike Price", "Strike Value", "Current Value",
    "Cost Basis", "Cost Value", "Liquidation Value", "Option Exercise Value",
    "Total % Gain @ Strike", "APR @ Strike"
]].sort_values("Total % Gain @ Strike", ascending=False).reset_index(drop=True), use_container_width=True)

# Charts
st.subheader("📈 Visual Analytics")

col1, col2 = st.columns(2)
with col1:
    st.markdown("### 🔹 Strike Value")
    st.bar_chart(df.set_index("Symbol")["Strike Value"].dropna())

    st.markdown("### 🔹 Option Exercise Value")
    st.bar_chart(df.set_index("Symbol")["Option Exercise Value"].dropna())

with col2:
    st.markdown("### 🔹 Total % Gain @ Strike")
    st.bar_chart(df.set_index("Symbol")["Total % Gain @ Strike"].dropna())

    st.markdown("### 🔹 APR @ Strike")
    st.bar_chart(df.set_index("Symbol")["APR @ Strike"].dropna())

st.success("All data and charts updated successfully.")
