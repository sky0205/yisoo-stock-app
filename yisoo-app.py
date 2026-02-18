import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup

# --- [0] 기본 설정 ---
st.set_page_config(page_title="v36000 글로벌 실시간 분석기", layout="wide")
if 'history' not in st.session_state:
    st.session_state['history'] = []

# --- [1] 종목 데이터베이스 ---
stock_info = {
    "아이온큐 (IONQ)": {"ticker": "IONQ", "market": "US", "target": 39.23},
    "엔비디아 (NVDA)": {"ticker": "NVDA", "market": "US", "target": 170.00},
    "삼성전자": {"ticker": "005930", "market": "KR", "target": 68000},
    "유한양행": {"ticker": "000100", "market": "KR", "target": 162000},
    "대한항공": {"ticker": "003490", "market": "KR", "target": 28500},
    "실리콘투": {"ticker": "257720", "market": "KR", "target": 49450},
}

# --- [2] 데이터 수집 및 지수 계산 엔진 ---
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
        df = yf.download(ticker, period="3mo", interval="1d", progress=False)
        if df.empty: return None
        close = df['Close']
        ma20 = close.rolling(window=20).mean()
        std20 = close.rolling(window=20).std()
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rsi = 100 - (100 / (1 + (gain / loss)))
        h14, l14 = df['High'].rolling(window=14).max(), df['Low'].rolling(window=14).min()
        wr = (h14 - close) / (h14 - l14) * -100
        exp1, exp2 = close.ewm(span=12).mean(), close.ewm(span=26).mean()
        macd = exp1 - exp2
        sig = macd.ewm(span=9).mean()
        return {
            "price": round(float(close.iloc[-1]), 2), "up": round(float((ma20+std20*2).iloc[-1]), 2), "dn": round(float((ma20-std20*2).iloc[-1]), 2),
            "rsi": round(float(rsi.iloc[-1]), 2), "wr": round(float(wr.iloc[-1]), 2), "macd": round(float((macd-sig).iloc[-1]), 4)
        }
    except: return None

# --- [3] 화면 구성 ---
st.title("🏆 이수할아버지 v36000 글로벌 실시간 분석기")
search_stock = st.selectbox("어떤 종목을 분석할까요?", list(stock_info.keys()))
info = stock_info[search_stock]

if st.button("🚀 실시간 정밀 분석 시작"):
    if search_stock not in st.session_state['history']: st.session_state['history'].insert(0, search_stock)

# 데이터 호출
y_ticker = info["ticker"] + (".KS" if info["market"] == "KR" and "257720" not in info["ticker"] else ".KQ" if "257720" in info["ticker"] else "")
tech = get_tech_analysis(y_ticker)
price = get_naver_price(info["ticker"]) if info["market"] == "KR" else (tech["price"] if tech else None)

if price and tech:
    st.markdown("---")
    fmt_p = f"{format(int(price), ',')} 원" if info["market"] == "KR" else f"${price}"
    st.header(f"🔍 {search_stock} ({info['ticker']})")
    st.markdown(f"<h1 style='text-align: left; color: #1E1E1E;'>현재가: {fmt_p}</h1>", unsafe_allow_html=True)

    # [A] 초대형 신호등 박스
    if price < info["target"] * 0.9:
        sig_html = f"<div style='background-color: #FF4B4B; padding: 30px; border-radius: 15px;'><h1 style='color: white; text-align: center; margin: 0;'>🚦 신호등: 🔴 매수 사정권 (적기)</h1></div>"
    elif price > info["target"]:
        sig_html = f"<div style='background-color: #28A745; padding: 30px; border-radius: 15px;'><h1 style='color: white; text-align: center; margin: 0;'>🚦 신호등: 🟢 매도 검토 (수익실현)</h1></div>"
    else:
        sig_html = f"<div style='background-color: #FFC107; padding: 30px; border-radius: 15px;'><h1 style='color: black; text-align: center; margin: 0;'>🚦 신호등: 🟡 관망 (대기)</h1></div>"
    st.markdown(sig_html, unsafe_allow_html=True)

    # [B] 초대형 적정주가 박스
    fmt_t = f"{format(int(info['target']), ',')} 원" if info["market"] == "KR" else f"${info['target']}"
    st.markdown(f"<div style='background-color: #E1F5FE; border: 2px solid #03A9F4; padding: 25px; border-radius: 15px; margin-top: 20px;'><h2 style='color: #01579B; text-align: center; margin: 0;'>💎 테이버 적정주가: {fmt_t}</h2></div>", unsafe_allow_html=True)

    # [C] 추세 분석 요약
    st.markdown("### 📝 이수할아버지의 추세 진단")
    st.info(f"현재 **{search_stock}**은(는) {'상승 에너지가 페달을 밟기 시작한' if tech['macd'] > 0 else '숨을 고르며 내리막길을 지나고 있는'} 구간입니다. 고환율 시대에는 방어 운전이 최고입니다.")

    # [D] 상세 지수 분석표 (4대 지수 정밀 분석)
    st.markdown("### 📊 4대 핵심 지표 정밀 분석표")
    index_analysis = pd.DataFrame({
        "핵심 지표": ["Bollinger Band", "RSI (심리)", "Williams %R", "MACD Osc"],
        "실시간 수치": [f"{tech['upper']} / {tech['lower']}", f"{tech['rsi']}", f"{tech['wr']}", f"{tech['macd']}"],
        "이수할아버지의 상세 해석": [
            f"{'밴드 하단 이탈, 적극 매수 검토' if price < tech['lower'] else '밴드 중앙 주행 중' if price < tech['upper'] else '밴드 상단 돌파, 과열 주의'}",
            f"{'침체기(30이하). 용기 낼 시간' if tech['rsi'] < 30 else '안정권(30~70). 추세 확인' if tech['rsi'] < 70 else '과열권(70이상). 욕심 버릴 시간'}",
            f"{'바닥권(-80이하). 반등 가능성 높음' if tech['wr'] < -80 else '천장권(-20이상). 단기 조정 대비' if tech['wr'] > -20 else '중간 지점. 에너지 응축 중'}",
            f"{'상승 추세(0이상). 페달 밟는 중' if tech['macd'] > 0 else '하락 추세(0이하). 브레이크 조절'}"
        ]
    })
    st.table(index_analysis)

st.markdown("---")
st.subheader("🕒 오늘 검색한 종목 히스토리")
st.write(", ".join(st.session_state['history']))
