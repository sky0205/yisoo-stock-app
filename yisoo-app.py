import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup

# --- [0] 기본 설정 및 스타일 ---
st.set_page_config(page_title="v36000 마스터", layout="wide")

# 종목 데이터베이스 (여기에 추가하면 자동으로 불러옵니다)
stock_db = {
    "005930": {"name": "삼성전자", "market": "국장 (KR)", "target": 210000.0},
    "000100": {"name": "유한양행", "market": "국장 (KR)", "target": 135000.0},
    "NVDA": {"name": "엔비디아", "market": "미장 (US)", "target": 195.00},
    "IONQ": {"name": "아이온큐", "market": "미장 (US)", "target": 39.23},
    "AAPL": {"name": "애플", "market": "미장 (US)", "target": 250.00},
    "000660": {"name": "SK하이닉스", "market": "국장 (KR)", "target": 250000.0}
}

if 'analyzed' not in st.session_state:
    st.session_state['analyzed'] = False

st.markdown("""
    <style>
    .big-price { font-size: 42px !important; font-weight: 800; color: #1E1E1E; margin-bottom: 5px; }
    .signal-box { padding: 30px; border-radius: 20px; text-align: center; color: white !important; line-height: 1.2; margin-bottom: 20px; }
    .signal-title { font-size: 26px; font-weight: 700; opacity: 0.9; color: white !important; }
    .signal-content { font-size: 45px; font-weight: 900; display: block; margin-top: 5px; color: white !important; }
    .target-box { background-color: #F0F9FF; border: 4px solid #007BFF; padding: 25px; border-radius: 20px; text-align: center; color: #0056b3; font-size: 30px; font-weight: 700; margin-bottom: 25px; }
    .summary-box { background-color: #FFFDE7; border-left: 10px solid #FBC02D; padding: 20px; font-size: 19px; line-height: 1.6; margin-bottom: 30px; border-radius: 0 15px 15px 0; color: #1E1E1E !important; }
    .stButton>button { width: 100%; height: 60px; font-size: 22px; font-weight: 700; background-color: #1E1E1E; color: white; border-radius: 12px; margin-top: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- [1] 데이터 엔진 ---
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

# --- [2] 메인 상단 입력창 (자동 연동 로직) ---
st.title("🏆 이수할아버지 v36000 마스터")

# 코드 입력창을 먼저 배치
t_input = st.text_input("🔢 종목 코드 또는 티커를 입력하세요", "005930", help="국장은 숫자 6자리, 미장은 영문 티커")

# 데이터베이스 확인 후 자동 값 설정
default_name = "삼성전자"
default_market = "국장 (KR)"
default_target = 210000.0

if t_input in stock_db:
    default_name = stock_db[t_input]["name"]
    default_market = stock_db[t_input]["market"]
    default_target = stock_db[t_input]["target"]

# 설정창 가로 배치
c1, c2, c3 = st.columns([2, 1.5, 2.5])
with c1: in_name = st.text_input("📍 종목명 (자동완성)", value=default_name)
with c2: in_market = st.selectbox("🌎 시장 선택", ["국장 (KR)", "미장 (US)"], index=0 if default_market=="국장 (KR)" else 1)
with c3: in_target = st.number_input("💎 나의 적정가 (자동매칭)", value=default_target, step=0.1)

if st.button("🚀 실시간 정밀 분석 시작"):
    st.session_state['analyzed'] = True
    st.session_state['n'], st.session_state['t'], st.session_state['m'], st.session_state['tg'] = in_name, t_input, in_market, in_target

# --- [3] 분석 결과 ---
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

        if tech['rsi'] > 70 or price > tech['up']:
            bg, status = "#28A745", "🟢 매도 검토 (과열)"
        elif price < tg * 0.95:
            bg, status = "#FF4B4B", "🔴 매수 사정권 (기회)"
        else:
            bg, status = "#FFC107; color: black !important;", "🟡 관망 대기 (중립)"
        
        st.markdown(f"<div class='signal-box' style='background-color: {bg};'><span class='signal-title'>🚦 신호등 상태</span><br><span class='signal-content'>{status}</span></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='target-box'>💎 적정주가 기준: {f_tg}</div>", unsafe_allow_html=True)

        # 요약 박스 (글자색 검정 고정)
        st.markdown("### 📝 추세 분석 요약")
        sum_msg = "상승세가 강해 밴드 상단을 넘보고 있습니다." if price > tech['up'] else "바닥을 확인하며 에너지를 모으는 중입니다."
        st.markdown(f"<div class='summary-box'><b>이수할아버지 의견:</b> 현재 {n}은(는) {sum_msg}<br>RSI {round(tech['rsi'],1)}는 {'과열 상태입니다. 익절을 고민하세요.' if tech['rsi']>70 else '바닥 구간입니다. 용기를 낼 때입니다.' if tech['rsi']<35 else '안정적인 흐름입니다.'}</div>", unsafe_allow_html=True)

        # 상세 진단표
        b_diag = "⚠️ 상단 돌파 (과열)" if price > tech['up'] else "✅ 하단 지입 (바닥)" if price < tech['dn'] else "밴드 내 안정적 주행"
        f_up = f"{tech['up']:,.2f}" if "US" in m else f"{round(tech['up'],0):,.0f}"
        f_dn = f"{tech['dn']:,.2f}" if "US" in m else f"{round(tech['dn'],0):,.0f}"

        st.table(pd.DataFrame({
            "핵심 지표": ["Bollinger Band", "RSI (심리)", "Williams %R", "MACD Osc"],
            "실시간 수치": [f"{f_up} / {f_dn}", f"{round(tech['rsi'],1)}", f"{round(tech['wr'],1)}", f"{round(tech['macd'],3)}"],
            "상세 진단 (현지수 비교)": [b_diag, "심리 과열" if tech['rsi']>70 else "심리 바닥" if tech['rsi']<30 else "보통", "단기천장" if tech['wr']>-20 else "단기바닥" if tech['wr']<-80 else "보통", "상승 가속" if tech['macd']>0 else "하락 압력"]
        }))
    else:
        st.error(f"❌ '{t}' 데이터를 찾을 수 없습니다. 코드를 다시 확인해 주세요!")
