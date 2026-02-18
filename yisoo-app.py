import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup

# --- [0] 기본 설정 및 스타일 ---
st.set_page_config(page_title="v36000 글로벌 분석기", layout="wide")

# CSS를 사용하여 박스 크기와 폰트를 강제로 키웁니다 (선생님 요청 반영)
st.markdown("""
    <style>
    .big-font { font-size:30px !important; font-weight: bold; }
    .signal-box { padding: 30px; border-radius: 15px; text-align: center; color: white; font-size: 35px; font-weight: bold; margin-bottom: 20px; }
    .target-box { background-color: #E1F5FE; border: 3px solid #03A9F4; padding: 25px; border-radius: 15px; text-align: center; color: #01579B; font-size: 30px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

if 'history' not in st.session_state:
    st.session_state['history'] = []

# --- [1] 종목 데이터베이스 ---
stock_db = {
    "아이온큐 (IONQ)": {"ticker": "IONQ", "market": "US", "target": 39.23},
    "엔비디아 (NVDA)": {"ticker": "NVDA", "market": "US", "target": 170.00},
    "삼성전자": {"ticker": "005930", "market": "KR", "target": 68000},
    "유한양행": {"ticker": "000100", "market": "KR", "target": 162000},
    "대한항공": {"ticker": "003490", "market": "KR", "target": 28500},
    "실리콘투": {"ticker": "257720", "market": "KR", "target": 49450},
    "넷플릭스 (NFLX)": {"ticker": "NFLX", "market": "US", "target": 850.00},
}

# --- [2] 데이터 수집 및 지수 계산 함수 ---
def get_naver_price(code):
    try:
        url = f"https://finance.naver.com/item/main.naver?code={code}"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(res.text, 'html.parser')
        return int(soup.select_one(".no_today .blind").text.replace(",", ""))
    except: return None

@st.cache_data(ttl=60)
def get_analysis(ticker):
    try:
        df = yf.download(ticker, period="6mo", interval="1d", progress=False)
        if df.empty: return None
        close = df['Close']
        # 볼린저
        ma20 = close.rolling(20).mean(); std20 = close.rolling(20).std()
        # RSI
        delta = close.diff(); gain = delta.where(delta > 0, 0).rolling(14).mean(); loss = -delta.where(delta < 0, 0).rolling(14).mean()
        rsi = 100 - (100 / (1 + (gain / loss)))
        # Williams %R
        h14 = df['High'].rolling(14).max(); l14 = df['Low'].rolling(14).min()
        wr = (h14 - close) / (h14 - l14) * -100
        # MACD
        ema12 = close.ewm(span=12).mean(); ema26 = close.ewm(span=26).mean(); macd = ema12 - ema26; sig = macd.ewm(span=9).mean()
        
        return {
            "p": float(close.iloc[-1]), "up": float(ma20.iloc[-1] + std20.iloc[-1]*2), "dn": float(ma20.iloc[-1] - std20.iloc[-1]*2),
            "rsi": float(rsi.iloc[-1]), "wr": float(wr.iloc[-1]), "macd": float((macd-sig).iloc[-1])
        }
    except: return None

# --- [3] 메인 화면 ---
st.title("🏆 이수할아버지 v36000 마스터 분석기")

search_name = st.selectbox("분석 종목 선택", list(stock_db.keys()))
item = stock_db[search_name]

if st.button("🚀 실시간 정밀 분석 시작"):
    if search_name not in st.session_state['history']:
        st.session_state['history'].insert(0, search_name)

# 데이터 로드
y_ticker = item["ticker"] + (".KS" if item["market"] == "KR" and len(item["ticker"]) == 6 else ".KQ" if len(item["ticker"]) == 6 else "")
tech = get_analysis(y_ticker)
price = get_naver_price(item["ticker"]) if item["market"] == "KR" else (tech["p"] if tech else None)

if price and tech:
    st.markdown("---")
    unit = "원" if item["market"] == "KR" else "$"
    fmt_p = f"{format(int(price), ',')} {unit}" if item["market"] == "KR" else f"{unit}{price}"
    st.markdown(f"<p class='big-font'>🔍 종목명: {search_name} / 현재가: {fmt_p}</p>", unsafe_allow_html=True)

    # 🚦 [A] 초대형 신호등 박스
    if price < item["target"] * 0.9:
        st.markdown(f"<div class='signal-box' style='background-color: #FF4B4B;'>🚦 신호등: 🔴 매수 사정권 (적기)</div>", unsafe_allow_html=True)
    elif price > item["target"]:
        st.markdown(f"<div class='signal-box' style='background-color: #28A745;'>🚦 신호등: 🟢 매도 검토 (수익실현)</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='signal-box' style='background-color: #FFC107; color: black;'>🚦 신호등: 🟡 관망 (대기)</div>", unsafe_allow_html=True)

    # 💎 [B] 초대형 적정주가 박스
    fmt_t = f"{format(int(item['target']), ',')} {unit}" if item["market"] == "KR" else f"{unit}{item['target']}"
    st.markdown(f"<div class='target-box'>💎 테이버 적정주가: {fmt_t}</div>", unsafe_allow_html=True)

    # 📝 [C] 추세 분석 요약
    st.markdown("### 📝 추세 분석 요약")
    summary = "상승 에너지가 살아나고 있습니다." if tech['macd'] > 0 else "단기 조정 중이나 바닥을 다지는 구간입니다."
    st.info(f"**이수할아버지 진단:** {summary} 평단가 관리를 위해 분할로 접근하세요.")

    # 📊 [D] 4대 지수 정밀 분석표
    st.markdown("### 📊 4대 핵심 지표 정밀 분석표")
    idx_df = pd.DataFrame({
        "핵심 지표": ["Bollinger Band", "RSI (심리)", "Williams %R", "MACD Osc"],
        "실시간 수치": [f"{round(tech['up'],2)} / {round(tech['dn'],2)}", f"{round(tech['rsi'],2)}", f"{round(tech['wr'],2)}", f"{round(tech['macd'],4)}"],
        "이수할아버지의 상세 해석": [
            "하단선 지지 시 매수, 상단선 돌파 시 매도 시점" if price < tech['up'] else "상단 돌파 과열 상태",
            "30이하(침체-매수), 70이상(과열-매도)" if tech['rsi'] < 70 else "70이상 초과열 구간",
            "-80이하(바닥-반등임박), -20이상(고점-조심)" if tech['wr'] < -20 else "-20이상 단기 고점",
            "0보다 크면 상승세 가속, 0보다 작으면 하락세"
        ]
    })
    st.table(idx_df)

st.markdown("---")
st.subheader("🕒 오늘 검색한 종목")
st.write(", ".join(st.session_state['history']))
