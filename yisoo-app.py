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
    .signal-box { padding: 35px; border-radius: 20px; text-align: center; color: white; line-height: 1.4; }
    .signal-title { font-size: 35px; font-weight: 700; opacity: 0.9; }
    .signal-content { font-size: 55px; font-weight: 900; display: block; margin-top: 10px; }
    .target-box { background-color: #F0F9FF; border: 4px solid #007BFF; padding: 25px; border-radius: 20px; text-align: center; color: #0056b3; font-size: 35px; font-weight: 700; margin-top: 15px; }
    </style>
    """, unsafe_allow_html=True)

# --- [1] 종목 DB (2026-02-18 실시간 반영) ---
stock_db = {
    "삼성전자": {"ticker": "005930", "market": "KR", "target": 210000},
    "유한양행": {"ticker": "000100", "market": "KR", "target": 135000},
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
        return {"up": float(ma20.iloc[-1]+std.iloc[-1]*2), "dn": float(ma20.iloc[-1]-std.iloc[-1]*2), "rsi": float(rsi.iloc[-1]), "wr": float(wr.iloc[-1]), "macd": float(macd.iloc[-1])}
    except: return None

# --- [3] 메인 화면 ---
st.title("🏆 이수할아버지 v36000 마스터")
choice = st.selectbox("종목 선택", list(stock_db.keys()))

if st.button("🚀 분석 시작"):
    st.session_state['analyzed'] = True
    st.session_state['last_stock'] = choice

if st.session_state['analyzed']:
    name = st.session_state['last_stock']
    info = stock_db[name]
    y_ticker = info["ticker"] + (".KS" if info["market"] == "KR" else "")
    tech = get_tech_analysis(y_ticker)
    price = get_naver_price(info["ticker"]) if info["market"] == "KR" else (tech["p"] if "p" in tech else None)

    if price and tech:
        st.markdown("---")
        unit = "원" if info["market"] == "KR" else "$"
        fmt_p = f"{format(int(price), ',')} {unit}" if info["market"] == "KR" else f"{unit}{price}"
        st.markdown(f"<p class='big-price'>🔍 {name} / 현재가: {fmt_p}</p>", unsafe_allow_html=True)

        # 🚦 2단 신호등 박스 (요청 반영)
        if price < info["target"] * 0.9:
            bg, status = "#FF4B4B", "🔴 매수 사정권"
        elif price > info["target"]:
            bg, status = "#28A745", "🟢 매도 검토"
        else:
            bg, status = "#FFC107; color: black;", "🟡 관망 대기"
        
        st.markdown(f"""<div class='signal-box' style='background-color: {bg};'>
            <span class='signal-title'>🚦 신호등</span><br>
            <span class='signal-content'>{status}</span>
        </div>""", unsafe_allow_html=True)

        # 💎 적정주가
        fmt_t = f"{format(int(info['target']), ',')} {unit}" if info["market"] == "KR" else f"{unit}{info['target']}"
        st.markdown(f"<div class='target-box'>💎 적정주가: {fmt_t}</div>", unsafe_allow_html=True)

        # 📈 1. 추세 분석표
        st.markdown("### 📈 1. 추세 분석표")
        st.table(pd.DataFrame({
            "항목": ["가격 위치", "추세 동력", "투자 심리"],
            "상태": [
                "밴드 하단선 지지 시도" if price < tech['dn'] * 1.05 else "상단 저항선 근접",
                "상승 에너지 강화" if tech['macd'] > 0 else "단기 조정 에너지 우세",
                "침체(저점 매수 유효)" if tech['rsi'] < 40 else "보통"
            ]
        }))

        # 📊 2. 지수 분석표 (4대 지수 상세 분석)
        st.markdown("### 📊 2. 지수 분석표 (Index Detail)")
        idx_df = pd.DataFrame({
            "핵심 지표": ["볼린저(상/하)", "RSI (심리)", "Williams %R", "MACD 오실레이터"],
            "실시간 수치": [f"{round(tech['up'],1)} / {round(tech['dn'],1)}", f"{round(tech['rsi'],1)}", f"{round(tech['wr'],1)}", f"{round(tech['macd'],3)}"],
            "상세 진단": [
                "도로의 폭을 확인하여 이격도를 봅니다.",
                "30이하(과매수 바닥) / 70이상(과열)",
                "-80이하(용수철 바닥) / -20이상(천장)",
                "0보다 크면 페달 밟는 힘(상승) 우세"
            ]
        })
        st.table(idx_df)
