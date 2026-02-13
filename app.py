import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup

# 1. 화면 및 간판 고정
st.set_page_config(page_title="이수할아버지의 주식분석기", layout="wide")

# 미장 한글 사전
US_KR_MAP = {
    "AAPL": "애플", "TSLA": "테슬라", "NVDA": "엔비디아", "IONQ": "아이온큐",
    "NFLX": "넷플릭스", "MSFT": "마이크로소프트", "AMZN": "아마존"
}

if 'name_map' not in st.session_state:
    st.session_state.name_map = {
        "삼성전자": "005930.KS", "아이온큐": "IONQ", "엔비디아": "NVDA", 
        "유한양행": "000100.KS", "넷플릭스": "NFLX"
    }

# 종목명 가져오기
def fetch_stock_name(symbol):
    symbol = symbol.upper().strip()
    if symbol.isdigit() and len(symbol) == 6:
        try:
            url = f"https://finance.naver.com/item/main.naver?code={symbol}"
            res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(res.text, 'html.parser')
            return soup.select_one(".wrap_company h2 a").text, symbol + ".KS"
        except: return symbol, symbol + ".KS"
    else:
        if symbol in US_KR_MAP: return US_KR_MAP[symbol], symbol
        try:
            t = yf.Ticker(symbol); name = t.info.get('shortName', symbol).split(' ')[0]
            return name, symbol
        except: return symbol, symbol

@st.cache_data(ttl=60)
def get_analysis_data(ticker):
    try:
        data = yf.download(ticker, period="1y", interval="1d", multi_level_index=False)
        if data.empty: return None
        data.columns = [c.lower() for c in data.columns]
        return data
    except: return None

# 앱 시작
st.title("👨‍💻 이수할아버지의 주식분석기")
st.write("---")

# 검색 및 입력
history_list = list(st.session_state.name_map.keys())
selected_name = st.selectbox("📋 나의 종목 수첩", options=history_list, index=None, placeholder="종목 선택")
new_symbol = st.text_input("➕ 새 종목 추가", value="", placeholder="번호 또는 티커 입력")

target_name = ""; target_ticker = ""

if new_symbol:
    name, ticker = fetch_stock_name(new_symbol)
    if name not in st.session_state.name_map:
        st.session_state.name_map[name] = ticker
        st.rerun()
    target_name = name; target_ticker = ticker
elif selected_name:
    target_name = selected_name; target_ticker = st.session_state.name_map[selected_name]

if target_ticker:
    df = get_analysis_data(target_ticker)
    if df is None and ".KS" in target_ticker:
        target_ticker = target_ticker.replace(".KS", ".KQ")
        df = get_analysis_data(target_ticker)

    if df is not None:
        close = df['close']; high = df['high']; low = df['low']
        
        # 지표 계산
        ma20 = close.rolling(20).mean(); std20 = close.rolling(20).std()
        upper = ma20 + (std20 * 2); lower = ma20 - (std20 * 2)
        
        ema12 = close.ewm(span=12, adjust=False).mean()
        ema26 = close.ewm(span=26, adjust=False).mean()
        macd = ema12 - ema26
        sig = macd.ewm(span=9, adjust=False).mean()

        # 제목 및 현재가만 깔끔하게 표시 (박스 제거)
        st.markdown(f"### 📈 {target_name} ({target_ticker}) : {close.iloc[-1]:,.2f}")
        st.write("---")

        # 📊 볼린저 밴드 차트
        st.write("### 1. 볼린저 밴드 흐름")
        band_df = pd.DataFrame({
            '현재가': close, '상단선': upper, '중심선': ma20, '하단선': lower
        }).tail(100)
        # 선 굵기 및 색상 최적화
        st.line_chart(band_df, color=["#1f77b4", "#ff4b4b", "#999999", "#2e7d32"])
        
        # 📉 MACD 차트 (색상 교정: MACD 파랑, 시그널 주황)
        st.write("### 2. MACD 추세 (파란선이 주황선을 뚫고 올라와야 합니다)")
        macd_df = pd.DataFrame({
            'MACD선(파랑)': macd,
            '시그널선(주황)': sig
        }).tail(100)
        
        # 색상 지정: 파란색(#0000FF), 주황색(#FF8C00)
        st.line_chart(macd_df, color=["#0000FF", "#FF8C00"])
        
    else:
        st.error("데이터를 가져오는 중입니다. 잠시만 기다려주세요.")

if st.sidebar.button("🗑️ 수첩 초기화"):
    st.session_state.name_map = {"삼성전자": "005930.KS", "아이온큐": "IONQ", "엔비디아": "NVDA"}
    st.rerun()
