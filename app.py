import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import yfinance as yf
from streamlit_option_menu import option_menu

st.set_page_config(page_title="OrderBlock Cyborg", layout="wide")

st.title("🚀 OrderBlock Cyborg - Supply/Demand Fast")
st.markdown("**LuxAlgo SMC + Your 5M Rules | Real-time Forex | Top 0.01%**")

# Sidebar
with st.sidebar:
    symbol = st.selectbox("Forex Pair", ["EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X"])
    tf = st.selectbox("Timeframe", ["5m", "15m", "1H"])
    
    selected = option_menu(
        menu_title="Dashboard",
        options=["📈 Live Chart", "🚨 Signals", "📊 Backtest", "⚖️ Kelly", "🧠 Tilt"],
        icons=["activity", "bell", "graph-up", "bar-chart", "brain"],
        menu_icon="cast",
        default_index=0,
    )

@st.cache_data(ttl=120)
def get_data(symbol, tf):
    data = yf.download(symbol, period="5d", interval=tf)
    return data.dropna()

data = get_data(symbol, tf)

# === ORDER BLOCK DETECTION (Your Deepest Candle) ===
def order_blocks(df):
    df = df.copy()
    df['wick'] = df['High'] - df['Low']
    df['is_ob'] = df['wick'].rolling(20).apply(lambda x: x == x.max(), raw=False)
    return df['is_ob']

# === FVG + BOS ===
def fvg_bos(df):
    fvg_bull = df['Low'] > df['High'].shift(2)
    fvg_bear = df['High'] < df['Low'].shift(2)
    bos_bull = df['Close'] > df['High'].shift(1)
    bos_bear = df['Close'] < df['Low'].shift(1)
    return fvg_bull, fvg_bear, bos_bull, bos_bear

ob = order_blocks(data)
fvg_bull, fvg_bear, bos_bull, bos_bear = fvg_bos(data)

# Pages
if selected == "📈 Live Chart":
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=data.index, open=data.Open, high=data.High, low=data.Low, close=data.Close
    ))
    
    # Order Blocks
    ob_times = data[ob].index[-10:]
    for t in ob_times:
        row = data.loc[t]
        fig.add_hrect(y0=row.Low, y1=row.High, fillcolor="blue", opacity=0.2)
    
    # EMAs
    ema21 = data.Close.ewm(span=21).mean()
    ema50 = data.Close.ewm(span=50).mean()
    fig.add_trace(go.Scatter(x=data.index, y=ema21, name="EMA21", line=dict(color="lime")))
    fig.add_trace(go.Scatter(x=data.index, y=ema50, name="EMA50
