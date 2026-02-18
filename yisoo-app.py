import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup

# --- [0] 기본 설정 및 스타일 ---
st.set_page_config(page_title="v36000 마스터", layout="wide")

if 'analyzed' not in st.session_state:
    st.session_state['analyzed'] = False
    st.session_state['last_stock'] = ""

st.markdown("""
    <style>
    .big-price { font-size: 45px !important; font-weight: 800; color: #1E1E1E; margin-bottom: 10px; }
    .signal-box { padding: 35px; border-radius: 20px; text-align: center; color: white; line-height: 1.4; margin-bottom: 20px; }
    .signal-title { font-size: 30px; font-weight: 700; opacity: 0.9; }
    .signal-content { font-size: 50px; font-weight: 900; display: block; margin-top: 10px; }
    .target-box { background-color: #F0F9FF; border: 4px solid #007BFF; padding: 25px; border-radius: 20px; text-align: center; color: #0056b3; font-size: 32px; font-weight: 700; margin-bottom: 25px; }
    .summary-box { background-color: #f9f9f9; border-left: 10px solid #FFC107; padding: 20px; font-size: 20px; line-height: 1.6; margin-bottom: 30px; }
    </style>
    """, unsafe_allow_html=True)

# --- [1] 종목 DB (2026년 실시간 상황 반영) ---
stock_db = {
    "삼성전자": {"ticker": "005930", "market": "KR", "target": 210000}, # 18만 전자 시대 반영
    "유한양행": {"ticker": "000100", "market": "KR", "target": 135000}, # 10만 원대 안착 반영
    "아이온큐 (IONQ)": {"ticker": "IONQ", "market": "US", "target": 39.23},
    "엔비디아 (NVDA)": {"ticker": "NVDA", "market": "US", "target": 170.00},
}

# --- [2] 데이터 엔진 ---
def get_naver_price(code):
    try:
        url = f"https://finance.naver.com/item/main.naver?code={code}"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(res.text, 'html.parser')
        return int(soup.select_one(".no_today .blind").text.replace(",", ""))
    except: return None

@st.cache_data(ttl=60)
def get_tech_analysis(ticker):
    try:
        df = yf.download(ticker, period="6mo", interval="1d", progress=False)
        close = df['Close']
        ma20 = close.rolling(20).mean(); std = close.rolling(20).std()
        delta = close.diff(); g = delta.where(delta > 0, 0).rolling(14).mean(); l = -delta.where(delta < 0, 0).rolling(14).mean()
        rsi = 100 - (100 / (1 + (g/l)))
        h14, l14 = df['High'].rolling(14).max(), df['Low'].rolling(14).min()
        wr = (h14 - close) / (h14 - l14) * -100
        e12 = close.ewm(span=12).mean(); e26 = close.ewm(span=26).mean(); macd = (e12 - e26) - (e12 - e26).ewm(span=9).mean()
        return {"p": float(close.iloc[-1]), "up": float(ma20.iloc[-1]+std.iloc[-1]*2), "dn": float(ma20.iloc[-1]-std.iloc[-1]*2), "rsi": float(rsi.iloc[-1]), "wr": float(wr.iloc[-1]), "macd": float(macd.iloc[-1])}
    except: return None

# --- [3] 메인 화면 ---
st.title("🏆 이수할아버지 v36000 마스터")
choice = st.selectbox("어떤 종목을 분석할까요?", list(stock_db.keys()))

if st.button("🚀 실시간 분석 시작"):
    st.session_state['analyzed'] = True
    st.session_state['last_stock'] = choice

if st.session_state['analyzed']:
    name = st.session_state['last_stock']
    info = stock_db[name]
    y_ticker = info["ticker"] + (".KS" if info["market"] == "KR" else "")
    tech = get_tech_analysis(y_ticker)
    price = get_naver_price(info["ticker"]) if info["market"] == "KR" else tech["p"]

    if price and tech:
        st.markdown("---")
        unit = "원" if info["market"] == "KR" else "$"
        fmt_p = f"{format(int(price), ',')} {unit}" if info["market"] == "KR" else f"{unit}{price}"
        
        # 1. 현주가
        st.markdown(f"<p class='big-price'>🔍 {name} 현재가: {fmt_p}</p>", unsafe
