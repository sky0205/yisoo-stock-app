import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# 1. 화면 설정 및 스타일
st.set_page_config(page_title="이수 투자비책 v3", layout="wide")

# 검색 히스토리 메모리 설정
if 'history' not in st.session_state:
    st.session_state.history = ["삼성전자", "아이온큐", "엔비디아", "유한양행"]

st.markdown("""
    <style>
    .stButton > button { width: 100%; height: 55px; font-weight: bold; font-size: 22px !important; background-color: #2E7D32; color: white; border-radius: 12px; }
    .big-font { font-size:40px !important; font-weight: bold; color: #1E1E1E; }
    .status-box { padding: 20px; border-radius: 15px; text-align: center; font-size: 30px; font-weight: bold; margin: 10px 0; }
    </style>
    """, unsafe_allow_html=True)

# 한국 주식 실시간 가격 함수
def get_naver_price(code):
    try:
        url = f"https://finance.naver.com/item/main.naver?code={code}"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(res.text, 'html.parser')
        price = soup.select_one(".today .no_today .blind").text
        return float(price.replace(',', ''))
    except: return None

# 데이터 다운로드 함수
@st.cache_data(ttl=30)
def get_analysis_data(ticker):
    try:
        df = yf.download(ticker, period="1y", interval="1d", multi_level_index=False)
        if df.empty: return None
        df.columns = [str(col).lower() for col in df.columns]
        return df
    except: return None

# 종목 매핑 사전
stock_dict = {
    "삼성전자": "005930.KS", "유한양행": "000100.KS", "에스피지": "058610.KQ",
    "아이온큐": "IONQ", "엔비디아": "NVDA", "넷플릭스": "NFLX"
}

st.title("📈 이수 할아버지의 스마트 투자 비책")

# 자동완성 검색창
st.subheader("🔍 종목을 선택하거나 입력하세요")
selected_stock = st.selectbox(
    "최근 본 종목 리스트:",
    options=st.session_state.history,
    index=None,
    placeholder="종목명을 입력하면 자동으로 기억합니다..."
)

# 분석 버튼
if st.button("🚀 분석 시작") or selected_stock:
    target = selected_stock if selected_stock else "삼성전자"
    
    # 히스토리에 추가
    if target not in st.session_state.history:
        st.session_state.history.insert(0, target)
    
    ticker = stock_dict.get(target, target).upper()
    df = get_analysis_data(ticker)
    
    if df is not None:
        close = df['close']
        
        # MACD 계산
        exp1 = close.ewm(span=12).mean()
        exp2 = close.ewm(span=26).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9).mean()
        
        # RSI 계산
        delta = close.diff()
        rsi = 100 - (100 / (1 + (delta.where(delta > 0, 0).rolling(14).mean() / -delta.where(delta < 0, 0).rolling(14).mean())))

        # 결과 출력
        curr_p = close.iloc[-1]
        st.markdown(f"<p class='big-font'>{target}: {curr_p:,.2f}</p>", unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("RSI (강도)", f"{rsi.iloc[-1]:.1f}")
        c2.metric("MACD 점수", f"{macd.iloc[-1]:.2f}")
        c3.metric("추세", "상승 중" if macd.iloc[-1] > signal.iloc[-1] else "하락 중")

        # 사정권 긴급 체크
        if ticker == "IONQ" and curr_p <= 31:
            st.markdown("<div style='background-color:#FFF4E5; border:2px solid #FFA000;' class='status-box'>🚨 아이온큐 사정권 진입 ($30 대기!)</div>", unsafe_allow_html=True)
        elif ticker == "NVDA" and curr_p <= 175:
            st.markdown("<div style='background-color:#FFF4E5; border:2px solid #FFA000;' class='status-box'>🚨 엔비디아 사정권 진입 ($170 대기!)</div>", unsafe_allow_html=True)

        st.write("### 📊 최근 60일 주가 흐름")
        st.line_chart(close.tail(60))
    else:
        st.error("종목명을 다시 확인해주세요. (예: 삼성전자, IONQ)")

# 사이드바 관리
if st.sidebar.button("검색 기록 지우기"):
    st.session_state.history = ["삼성전자", "아이온큐", "엔비디아"]
    st.rerun()
