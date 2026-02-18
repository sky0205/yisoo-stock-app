import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup

# --- [0] 기본 설정 및 스타일 (글자색 진하게 보정) ---
st.set_page_config(page_title="v36000 마스터", layout="wide")

if 'analyzed' not in st.session_state:
    st.session_state['analyzed'] = False

st.markdown("""
    <style>
    .big-price { font-size: 42px !important; font-weight: 800; color: #1E1E1E; margin-bottom: 5px; }
    .signal-box { padding: 30px; border-radius: 20px; text-align: center; color: white !important; line-height: 1.2; margin-bottom: 20px; }
    .signal-title { font-size: 26px; font-weight: 700; opacity: 0.9; color: white !important; }
    .signal-content { font-size: 45px; font-weight: 900; display: block; margin-top: 5px; color: white !important; }
    .target-box { background-color: #F0F9FF; border: 4px solid #007BFF; padding: 25px; border-radius: 20px; text-align: center; color: #0056b3; font-size: 30px; font-weight: 700; margin-bottom: 25px; }
    /* 요약 박스 글자색을 검정색(#1E1E1E)으로 강제 고정 */
    .summary-box { background-color: #FFFDE7; border-left: 10px solid #FBC02D; padding: 20px; font-size: 19px; line-height: 1.6; margin-bottom: 30px; border-radius: 0 15px 15px 0; color: #1E1E1E !important; }
    .summary-box b { color: #000000 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- [1] 데이터 엔진 ---
def get_naver_price(code):
    try:
        url = f"https://finance.naver.com/item/main.naver?code={code}"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(res.text, 'html.parser')
        price_text = soup.select_one(".no_today .blind").text.replace(",", "")
        return int(price_text)
    except: return None

@st.cache_data(ttl=60)
def get_tech_analysis(ticker):
    try:
        df = yf.download(ticker, period="6mo", interval="1d", progress=False)
        if df.empty: return None
        close = df['Close']
        ma20 = close.rolling(20).mean(); std = close.rolling(20).std()
        delta = close.diff(); g = delta.where(delta > 0, 0).rolling(14).mean(); l = -delta.where(delta < 0, 0).rolling(14).mean()
        rsi = 100 - (100 / (1 + (g/l)))
        h14, l14 = df['High'].rolling(14).max(), df['Low'].rolling(14).min()
        wr = (h14 - close) / (h14 - l14) * -100
        e12 = close.ewm(span=12).mean(); e26 = close.ewm(span=26).mean(); macd = (e12 - e26) - (e12 - e26).ewm(span=9).mean()
        return {"p": float(close.iloc[-1]), "up": float(ma20.iloc[-1]+std.iloc[-1]*2), "dn": float(ma20.iloc[-1]-std.iloc[-1]*2), 
                "rsi": float(rsi.iloc[-1]), "wr": float(wr.iloc[-1]), "macd": float(macd.iloc[-1])}
    except: return None

# --- [2] 사이드바 입력창 ---
with st.sidebar:
    st.header("🔍 종목 분석 설정")
    in_name = st.text_input("1. 종목명 입력", "삼성전자")
    in_ticker = st.text_input("2. 코드(숫자) / 티커(영문)", "005930")
    in_market = st.radio("3. 시장 선택", ["국장 (KR)", "미장 (US)"])
    in_target = st.number_input("4. 나의 적정주가 (S-RIM)", value=210000.0, step=0.1)
    
    if st.button("🚀 실시간 분석 시작"):
        st.session_state['analyzed'] = True
        st.session_state['n'], st.session_state['t'], st.session_state['m'], st.session_state['tg'] = in_name, in_ticker, in_market, in_target

# --- [3] 결과 출력부 ---
if st.session_state.get('analyzed'):
    n, t, m, tg = st.session_state['n'], st.session_state['t'], st.session_state['m'], st.session_state['tg']
    
    if "KR" in m:
        tech = get_tech_analysis(t + ".KS")
        if not tech: tech = get_tech_analysis(t + ".KQ")
        price = get_naver_price(t)
    else:
        tech = get_tech_analysis(t)
        price = tech["p"] if tech else None

    if price and tech:
        st.markdown("---")
        cur = "원" if "KR" in m else "$"
        f_p = f"{format(int(price), ',')} {cur}" if "KR" in m else f"{cur}{price:,.2f}"
        f_tg = f"{format(int(tg), ',')} {cur}" if "KR" in m else f"{cur}{tg:,.2f}"
        
        st.markdown(f"<p class='big-price'>🔍 {n} ({t}) 현재가: {f_p}</p>", unsafe_allow_html=True)

        # 🚦 2단 지능형 신호등
        if tech['rsi'] > 70 or price > tech['up']:
            bg, status = "#28A745", "🟢 매도 검토 (과열 구간)"
        elif price < tg * 0.95:
            bg, status = "#FF4B4B", "🔴 매수 사정권 (기회 구간)"
        else:
            bg, status = "#FFC107; color: black !important;", "🟡 관망 대기 (중립 구간)"
        
        st.markdown(f"""<div class='signal-box' style='background-color: {bg};'>
            <span class='signal-title'>🚦 신호등 상태</span><br>
            <span class='signal-content'>{status}</span>
        </div>""", unsafe_allow_html=True)

        st.markdown(f"<div class='target-box'>💎 내가 설정한 적정주가: {f_tg}</div>", unsafe_allow_html=True)

        # 📝 추세 분석 요약 (시인성 보정 완료)
        st.markdown("### 📝 추세 분석 요약")
        sum_msg = "에너지가 위로 분출되어 밴드 상단을 넘보고 있습니다." if price > tech['up'] else "바닥을 확인하며 지지력을 테스트 중입니다."
        st.markdown(f"""<div class='summary-box'>
            <b>이수할아버지 의견:
