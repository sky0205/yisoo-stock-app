import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup

# --- [0] 기본 설정 ---
st.set_page_config(page_title="v36000 마스터 분석기", layout="wide")

# --- [1] 종목 DB (2026년 타겟가 업데이트) ---
stock_db = {
    "삼성전자": {"ticker": "005930", "market": "KR", "target": 210000},
    "유한양행": {"ticker": "000100", "market": "KR", "target": 135000},
    "아이온큐 (IONQ)": {"ticker": "IONQ", "market": "US", "target": 39.23},
    "엔비디아 (NVDA)": {"ticker": "NVDA", "market": "US", "target": 170.00},
}

# --- [2] 엔진 (네이버/야후) ---
def get_naver_price(code):
    try:
        url = f"https://finance.naver.com/item/main.naver?code={code}"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(res.text, 'html.parser')
        return int(soup.select_one(".no_today .blind").text.replace(",", ""))
    except: return None

@st.cache_data(ttl=60)
def get_tech(ticker):
    try:
        df = yf.download(ticker, period="6mo", interval="1d", progress=False)
        close = df['Close']
        ma20 = close.rolling(20).mean(); std = close.rolling(20).std()
        delta = close.diff(); g = delta.where(delta > 0, 0).rolling(14).mean(); l = -delta.where(delta < 0, 0).rolling(14).mean()
        rsi = 100 - (100 / (1 + (g/l)))
        h14, l14 = df['High'].rolling(14).max(), df['Low'].rolling(14).min()
        wr = (h14 - close) / (h14 - l14) * -100
        e12 = close.ewm(span=12).mean(); e26 = close.ewm(span=26).mean(); macd = e12 - e26; sig = macd.ewm(span=9).mean()
        return {"p": float(close.iloc[-1]), "up": float(ma20.iloc[-1]+std.iloc[-1]*2), "dn": float(ma20.iloc[-1]-std.iloc[-1]*2), "rsi": float(rsi.iloc[-1]), "wr": float(wr.iloc[-1]), "macd": float((macd-sig).iloc[-1])}
    except: return None

# --- [3] 화면 ---
st.title("🏆 이수할아버지 v36000 마스터")
name = st.selectbox("종목 선택", list(stock_db.keys()))
info = stock_db[name]

if st.button("🚀 분석 시작"):
    y_ticker = info["ticker"] + (".KS" if info["market"] == "KR" else "")
    tech = get_tech(y_ticker)
    price = get_naver_price(info["ticker"]) if info["market"] == "KR" else tech["p"]

    if price and tech:
        st.header(f"🔍 {name} / 현재가: {format(int(price), ',') if info['market']=='KR' else price}")
        
        # 신호등 & 적정주가 (대형 박스)
        if price < info["target"] * 0.9: st.error(f"# 🚦 신호등: 🔴 매수 사정권")
        elif price > info["target"]: st.success(f"# 🚦 신호등: 🟢 매도 검토")
        else: st.warning(f"# 🚦 신호등: 🟡 관망")
        st.info(f"## 💎 적정주가: {format(int(info['target']), ',') if info['market']=='KR' else info['target']}")

        # 4대 지수 표
        st.table(pd.DataFrame({"지표": ["볼린저(상/하)", "RSI", "Williams %R", "MACD"], "수치": [f"{tech['up']} / {tech['dn']}", tech['rsi'], tech['wr'], tech['macd']]}))
