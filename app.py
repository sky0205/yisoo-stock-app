import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup
import altair as alt

# 1. Page Setting (이 부분은 번역되면 안 됩니다)
st.set_page_config(page_title="이수할아버지의 주식분석기", layout="wide")

# Stock Name Map
if 'name_map' not in st.session_state:
    st.session_state.name_map = {
        "삼성전자": "005930.KS", "아이온큐": "IONQ", "엔비디아": "NVDA", 
        "유한양행": "000100.KS", "넷플릭스": "NFLX"
    }

st.markdown("""
    <style>
    .stMetric { background-color: #F8F9FA; padding: 15px; border-radius: 10px; border: 1px solid #DEE2E6; }
    .big-font { font-size:45px !important; font-weight: bold; color: #1E1E1E; }
    .status-box { padding: 25px; border-radius: 15px; text-align: center; font-size: 35px; font-weight: bold; margin: 15px 0; border: 5px solid; }
    .info-box { background-color: #E3F2FD; padding: 20px; border-radius: 10px; border-left: 10px solid #2196F3; margin-bottom: 25px; }
    </style>
    """, unsafe_allow_html=True)

# Function to get name
def fetch_stock_name(symbol):
    symbol = symbol.upper().strip()
    if symbol.isdigit() and len(symbol) == 6:
        try:
            url = f"https://finance.naver.com/item/main.naver?code={symbol}"
            res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=5)
            soup = BeautifulSoup(res.text, 'html.parser')
            return soup.select_one(".wrap_company h2 a").text, symbol + ".KS"
        except: return symbol, symbol + ".KS"
    return symbol, symbol

# Safe Data Fetch
@st.cache_data(ttl=60)
def get_clean_data(ticker):
    try:
        df = yf.download(ticker, period="1y", interval="1d", auto_adjust=True, multi_level_index=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        df.columns = [str(c).lower() for c in df.columns]
        return df.dropna()
    except: return None

# UI Start
st.title("👨‍💻 이수할아버지의 주식분석기")
st.write("---")

col1, _ = st.columns([4, 1])
with col1:
    history_list = list(st.session_state.name_map.keys())
    selected_name = st.selectbox("📋 나의 종목 수첩", options=history_list, index=None)
    new_symbol = st.text_input("➕ 새 종목 추가", placeholder="예: 000660")

target_name = ""; target_ticker = ""
if new_symbol:
    name, ticker = fetch_stock_name(new_symbol)
    if name not in st.session_state.name_map:
        st.session_state.name_map[name] = ticker
        st.rerun()
    target_name, target_ticker = name, ticker
elif selected_name:
    target_name = selected_name
    target_ticker = st.session_state.name_map[selected_name]

if target_ticker:
    df = get_clean_data(target_ticker)
    if (df is None or df.empty) and ".KS" in target_ticker:
        df = get_clean_data(target_ticker.replace(".KS", ".KQ"))

    if df is not None and 'close' in df.columns:
        close = df['close']; high = df['high']; low = df['low']
        
        # Indicators
        diff = close.diff()
        gain = diff.where(diff > 0, 0).rolling(14).mean()
        loss = -diff.where(diff < 0, 0).rolling(14).mean().replace(0, 0.001)
        rsi_val = 100 - (100 / (1 + (gain / loss)))
        w_r = (high.rolling(14).max() - close) / (high.rolling(14).max() - low.rolling(14).min()).replace(0, 0.001) * -100
        macd = close.ewm(span=12, adjust=False).mean() - close.ewm(span=26, adjust=False).mean()
        sig = macd.ewm(span=9, adjust=False).mean()
        ma20 = close.rolling(20).mean()

        # New High Analysis
        year_high = close.iloc[:-1].max(); curr_p = close.iloc[-1]
        is_high = curr_p >= (year_high * 0.97)

        st.markdown(f"<p class='big-font'>{target_name} 분석 결과</p>", unsafe_allow_html=True)
        if is_high: st.markdown("<div class='info-box'>🚀 <strong>신고가 영역!</strong> 기세가 아주 강합니다.</div>", unsafe_allow_html=True)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("현재가", f"{curr_p:,.0f}" if ".KS" in target_ticker else f"{curr_p:,.2f}")
        m2.metric("RSI", f"{rsi_val.iloc[-1]:.1f}")
        m3.metric("윌리엄 %R", f"{w_r.iloc[-1]:.1f}")
        m4.metric("전고점", f"{year_high:,.0f}" if ".KS" in target_ticker else f"{year_high:,.2f}")

        # Signal Light
        st.write("---")
        if is_high and macd.iloc[-1] > macd.iloc[-2]: st.markdown("<div style='background-color:#E8F5E9; color:#2E7D32; border-color:#2E7D32;' class='status-box'>📈 추세 상승 구간 📈</div>", unsafe_allow_html=True)
        elif rsi_val.iloc[-1] <= 35: st.markdown("<div style='background-color:#FFEEEE; color:#FF4B4B; border-color:#FF4B4B;' class='status-box'>🚨 강력 매수 구간 🚨</div>", unsafe_allow_html=True)
        else: st.markdown("<div style='background-color:#F5F5F5; color:#616161; border-color:#9E9E9E;' class='status-box'>🟡 관망 구간 🟡</div>", unsafe_allow_html=True)

        # Charts
        c_df = pd.DataFrame({'Date': df.index, 'Price': close, 'MA20': ma20}).tail(80).reset_index()
        base = alt.Chart(c_df).encode(x=alt.X('Date:T', axis=alt.Axis(title=None)))
        st.altair_chart(alt.layer(base.mark_line(color='#1E1E1E').encode(y=alt.Y('Price:Q', scale=alt.Scale(zero=False))), base.mark_line(color='#EF5350').encode(y='MA20:Q')).properties(height=300), use_container_width=True)

        m_df = pd.DataFrame({'Date': df.index, 'MACD': macd, 'Signal': sig}).tail(80).reset_index()
        m_base = alt.Chart(m_df).encode(x=alt.X('Date:T', axis=alt.Axis(title=None)))
        st.altair_chart(alt.layer(m_base.mark_line(color='#0059FF').encode(y='MACD:Q'), m_base.mark_line(color='#FF8000').encode(y='Signal:Q')).properties(height=200), use_container_width=True)
    else: st.error("Data loading failed.")

if st.sidebar.button("🗑️ 수첩 초기화"):
    st.session_state.name_map = {"삼성전자": "005930.KS", "아이온큐": "IONQ", "엔비디아": "NVDA"}
    st.rerun()
