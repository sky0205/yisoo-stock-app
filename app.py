import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# 1. 화면 설정
st.set_page_config(page_title="이수 투자비책 v4", layout="wide")

# 검색 히스토리 메모리 설정
if 'history' not in st.session_state:
    st.session_state.history = ["삼성전자", "아이온큐", "엔비디아", "유한양행", "에스피지"]

st.markdown("""
    <style>
    .stButton > button { width: 100%; height: 55px; font-weight: bold; font-size: 22px !important; background-color: #2E7D32; color: white; border-radius: 12px; }
    .big-font { font-size:40px !important; font-weight: bold; color: #1E1E1E; }
    .buy-signal { font-size:45px !important; color: #FF4B4B; font-weight: bold; text-align: center; background-color: #FFEEEE; padding: 20px; border-radius: 15px; border: 4px solid #FF4B4B; }
    .sell-signal { font-size:45px !important; color: #2E7D32; font-weight: bold; text-align: center; background-color: #EEFFEE; padding: 20px; border-radius: 15px; border: 4px solid #2E7D32; }
    .wait-signal { font-size:45px !important; color: #FFA000; font-weight: bold; text-align: center; background-color: #FFF9EE; padding: 20px; border-radius: 15px; border: 4px solid #FFA000; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(ttl=30)
def get_analysis_data(ticker):
    try:
        df = yf.download(ticker, period="1y", interval="1d", multi_level_index=False)
        if df.empty: return None
        df.columns = [str(col).lower() for col in df.columns]
        return df
    except: return None

stock_dict = {
    "삼성전자": "005930.KS", "유한양행": "000100.KS", "에스피지": "058610.KQ",
    "아이온큐": "IONQ", "엔비디아": "NVDA", "넷플릭스": "NFLX", "삼성E&A": "028050.KS"
}

st.title("📈 이수 할아버지의 통합 투자 대시보드")

# 자동완성 검색창
st.subheader("🔍 종목을 선택하거나 입력하세요")
selected_stock = st.selectbox(
    "최근 본 종목 리스트:",
    options=st.session_state.history,
    index=None,
    placeholder="종목명을 입력하면 자동으로 기억합니다..."
)

if selected_stock:
    if selected_stock not in st.session_state.history:
        st.session_state.history.insert(0, selected_stock)
    
    ticker = stock_dict.get(selected_stock, selected_stock).upper()
    df = get_analysis_data(ticker)
    
    if df is not None:
        close = df['close']
        
        # 1. 볼린저 밴드 계산
        sma20 = close.rolling(20).mean()
        std20 = close.rolling(20).std()
        upper = sma20 + (std20 * 2)
        lower = sma20 - (std20 * 2)
        
        # 2. RSI 계산
        delta = close.diff()
        rsi = 100 - (100 / (1 + (delta.where(delta > 0, 0).rolling(14).mean() / -delta.where(delta < 0, 0).rolling(14).mean())))
        
        # 3. MACD 계산
        exp1 = close.ewm(span=12).mean()
        exp2 = close.ewm(span=26).mean()
        macd_line = exp1 - exp2
        signal_line = macd_line.ewm(span=9).mean()

        # 결과 출력
        curr_p = close.iloc[-1]
        st.markdown(f"<p class='big-font'>{selected_stock}: {curr_p:,.2f}</p>", unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("RSI (강도)", f"{rsi.iloc[-1]:.1f}")
        c2.metric("밴드 하단", f"{lower.iloc[-1]:,.2f}")
        c3.metric("MACD 상태", "상승세" if macd_line.iloc[-1] > signal_line.iloc[-1] else "하락세")

        # [신호등 다시 설치]
        st.write("---")
        c_rsi = rsi.iloc[-1]
        c_macd = macd_line.iloc[-1]
        c_sig = signal_line.iloc[-1]
        
        # 매수 신호: 가격이 밴드 하단 근처 + RSI 낮음 + MACD 골든크로스 혹은 상승세
        if curr_p <= lower.iloc[-1] * 1.02 and c_rsi <= 40:
            st.markdown("<div class='buy-signal'>🚨 강력 매수 구간 🚨</div>", unsafe_allow_html=True)
        elif c_rsi >= 70:
            st.markdown("<div class='sell-signal'>💰 익절 권장 구간 💰</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='wait-signal'>🟡 관망 및 대기 🟡</div>", unsafe_allow_html=True)

        # 차트 그리기
        st.write("### 📊 볼린저 밴드 및 주가 흐름")
        st.line_chart(pd.DataFrame({'현재가': close, '상단': upper, '하단': lower}).tail(80))
        
        st.write("### 📉 MACD 지표 (추세 확인)")
        st.line_chart(pd.DataFrame({'MACD': macd_line, '시그널': signal_line}).tail(8
