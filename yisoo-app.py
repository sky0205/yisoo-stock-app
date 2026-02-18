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
        unit = "원" if info["market"] == "KR" else "$"
        fmt_p = f"{format(int(price), ',')} {unit}" if info["market"] == "KR" else f"{unit}{price}"
        
        st.markdown(f"<p class='big-price'>🔍 {name} 현재가: {fmt_p}</p>", unsafe_allow_html=True)

        # 🚦 [보강된 지능형 신호등 논리]
        # 가격이 타겟보다 낮더라도 과열지표(RSI 70이상 또는 볼린저 상단돌파)가 뜨면 '매도' 혹은 '관망'
        if price > tech['up'] or tech['rsi'] > 70:
            bg, status = "#28A745", "🟢 매도 검토 (과열)"
        elif price < info["target"] * 0.9 and tech['rsi'] < 40:
            bg, status = "#FF4B4B", "🔴 매수 사정권 (바닥)"
        else:
            bg, status = "#FFC107; color: black;", "🟡 관망 대기"
        
        st.markdown(f"""<div class='signal-box' style='background-color: {bg};'>
            <span class='signal-title'>🚦 신호등 상태</span><br>
            <span class='signal-content'>{status}</span>
        </div>""", unsafe_allow_html=True)

        # 적정주가 표시
        fmt_t = f"{format(int(info['target']), ',')} {unit}" if info["market"] == "KR" else f"{unit}{info['target']}"
        st.markdown(f"<div class='target-box'>💎 테이버 적정주가: {fmt_t}</div>", unsafe_allow_html=True)

        # 추세 요약 (실시간 비교 진단 포함)
        st.markdown("### 📝 추세 분석 요약")
        sum_msg = "상단선을 뚫고 신고가를 달리는 중입니다. 브레이크가 필요합니다." if price > tech['up'] else "바닥에서 에너지를 응축하고 있습니다."
        st.markdown(f"""<div class='summary-box'>
            <b>이수할아버지 의견:</b> 현재 {name}은(는) {sum_msg}<br>
            RSI {round(tech['rsi'],1)}는 강력한 과열 신호입니다. 적정주가까지 공간이 남았어도 지표가 꺾일 때를 조심하세요.
        </div>""", unsafe_allow_html=True)

        # 지수 분석표 (실시간 비교)
        st.markdown("### 📊 실시간 지수 비교 분석")
        idx_df = pd.DataFrame({
            "핵심 지표": ["Bollinger Band", "RSI (심리)", "Williams %R", "MACD Osc"],
            "실시간 수치": [f"{round(tech['up'],0)} / {round(tech['dn'],0)}", f"{round(tech['rsi'],1)}", f"{round(tech['wr'],1)}", f"{round(tech['macd'],3)}"],
            "현지수 대비 상세 진단": [
                "⚠️ 상단선 돌파 (단기 고점)" if price > tech['up'] else "✅ 하단선 지지 (안전 주행)",
                "🚨 심리 과열 (70 돌파)" if tech['rsi'] > 70 else "💎 심리 바닥 (30 하회)" if tech['rsi'] < 30 else "안정적 구간",
                "🔥 천장 (조정 대비)" if tech['wr'] > -20 else "❄️ 바닥 (반등 임박)" if tech['wr'] < -80 else "보통",
                "▲ 전진 동력 우세" if tech['macd'] > 0 else "▼ 하락 압력 우세"
            ]
        })
        st.table(idx_df)
