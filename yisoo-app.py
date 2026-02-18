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
    .signal-box { padding: 35px; border-radius: 20px; text-align: center; color: white; line-height: 1.2; margin-bottom: 20px; }
    .signal-title { font-size: 28px; font-weight: 700; opacity: 0.9; }
    .signal-content { font-size: 52px; font-weight: 900; display: block; margin-top: 8px; }
    .target-box { background-color: #F0F9FF; border: 4px solid #007BFF; padding: 25px; border-radius: 20px; text-align: center; color: #0056b3; font-size: 32px; font-weight: 700; margin-bottom: 25px; }
    .summary-box { background-color: #f9f9f9; border-left: 10px solid #FFC107; padding: 20px; font-size: 20px; line-height: 1.6; margin-bottom: 30px; border-radius: 0 15px 15px 0; }
    </style>
    """, unsafe_allow_html=True)

# --- [1] 종목 DB ---
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
        # 미장은 소수점을 그대로 유지해서 반환
        return {"p": float(close.iloc[-1]), "up": float(ma20.iloc[-1]+std.iloc[-1]*2), "dn": float(ma20.iloc[-1]-std.iloc[-1]*2), "rsi": float(rsi.iloc[-1]), "wr": float(wr.iloc[-1]), "macd": float(macd.iloc[-1])}
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
    price = get_naver_price(info["ticker"]) if info["market"] == "KR" else (tech["p"] if tech else None)

    if price and tech:
        st.markdown("---")
        # [미장 소수점 두자리 핵심 로직]
        if info["market"] == "KR":
            fmt_p = f"{format(int(price), ',')} 원"
            fmt_t = f"{format(int(info['target']), ',')} 원"
        else:
            fmt_p = f"${price:,.2f}"  # 소수점 두자리 고정
            fmt_t = f"${info['target']:,.2f}"

        st.markdown(f"<p class='big-price'>🔍 {name} 현재가: {fmt_p}</p>", unsafe_allow_html=True)

        # 🚦 지능형 신호등 (과열 로직 포함)
        if price > tech['up'] or tech['rsi'] > 70: bg, status = "#28A745", "🟢 매도 검토 (과열)"
        elif price < info["target"] * 0.9: bg, status = "#FF4B4B", "🔴 매수 사정권"
        else: bg, status = "#FFC107; color: black;", "🟡 관망 대기"
        
        st.markdown(f"""<div class='signal-box' style='background-color: {bg};'>
            <span class='signal-title'>🚦 신호등 상태</span><br>
            <span class='signal-content'>{status}</span>
        </div>""", unsafe_allow_html=True)

        st.markdown(f"<div class='target-box'>💎 테이버 적정주가: {fmt_t}</div>", unsafe_allow_html=True)

        # 추세 요약
        st.markdown("### 📝 추세 분석 요약")
        trend_msg = "에너지가 위로 분출되는 중입니다." if tech['macd'] > 0 else "숨을 고르며 바닥을 확인 중입니다."
        st.markdown(f"""<div class='summary-box'>
            <b>이수할아버지 의견:</b> {name}은(는) 현재 {trend_msg}<br>
            RSI 지수가 {round(tech['rsi'],1)}로 {'과열' if tech['rsi']>70 else '침체' if tech['rsi']<35 else '안정'} 상태이니 무리한 추격보다는 계획대로 대응하세요.
        </div>""", unsafe_allow_html=True)

        # 지수 분석표 (미장 수치도 소수점 두자리 반영)
        st.markdown("### 📊 실시간 지표 상세 진단표")
        
        b_diag = "⚠️ 상단 돌파 (매도주의)" if price > tech['up'] else "✅ 하단 지지 (매수기회)" if price < tech['dn'] else "밴드 내 안정적 주행"
        r_diag = f"심리 과열({round(tech['rsi'],1)})" if tech['rsi'] > 70 else f"심리 바닥({round(tech['rsi'],1)})" if tech['rsi'] < 30 else "투자 심리 보통"

        # 수치 포맷팅 (미장/국장 구분)
        f_up = f"{tech['up']:,.2f}" if info["market"] == "US" else f"{round(tech['up'],0):,.0f}"
        f_dn = f"{tech['dn']:,.2f}" if info["market"] == "US" else f"{round(tech['dn'],0):,.0f}"

        idx_df = pd.DataFrame({
            "핵심 지표": ["Bollinger Band", "RSI (심리)", "Williams %R", "MACD Osc"],
            "실시간 수치": [f"{f_up} / {f_dn}", f"{round(tech['rsi'],1)}", f"{round(tech['wr'],1)}", f"{round(tech['macd'],3)}"],
            "현지수 대비 상세 진단": [b_diag, r_diag, "바닥권 반등임박" if tech['wr'] < -80 else "천장권 조정주의" if tech['wr'] > -20 else "보통", "전진 가속" if tech['macd'] > 0 else "하락 압력"]
        })
        st.table(idx_df)
