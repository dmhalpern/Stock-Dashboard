
import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime

st.set_page_config(page_title="📈 Advanced Stock Dashboard", layout="wide")

# Load cleaned data
@st.cache_data
def load_data():
    return pd.read_csv("positions_cleaned.csv")

df = load_data()

st.title("📊 Daily Stock and Option Dashboard")
st.caption(f"Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Fetch current prices
with st.spinner("Getting live prices..."):
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

# Display main metrics table
st.subheader("📋 Summary Table")
st.dataframe(df[[
    "Symbol", "Quantity", "Current Price", "Strike Price", "Strike Value", "Current Value",
    "Cost Basis", "Cost Value", "Liquidation Value", "Option Exercise Value",
    "Total % Gain @ Strike", "APR @ Strike"
]].sort_values("Total % Gain @ Strike", ascending=False).reset_index(drop=True), use_container_width=True)

# Chart layout
st.subheader("📈 Option Strategy Visualizations")

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

st.success("Dashboard fully updated with options and strike-level metrics.")
