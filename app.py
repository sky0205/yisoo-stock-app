import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup

# 1. 화면 설정
st.set_page_config(page_title="이수 투자비책 v5", layout="wide")

# 히스토리 초기화 (에러 방지용)
if 'history' not in st.session_state:
    st.session_state.history = ["삼성전자", "아이온큐", "엔비디아", "유한양행"]

# 2. 스타일 설정
st.markdown("""
    <style>
    .stButton > button { width: 100%; height: 50px; font-weight: bold; font-size: 20px !important; }
    .big-font { font-size:35px !important; font-weight: bold; color: #1E1E1E; }
    .status-box { padding: 20px; border-radius: 15px; text-align: center; font-size: 30px; font-weight: bold; margin: 10px 0; border: 3px solid; }
    </style>
    """, unsafe_allow_html=True)

# 데이터 가져오기 (가장 튼튼한 방식)
@st.cache_data(ttl=60)
def get_safe_data(ticker_symbol):
    try:
        data = yf.download(ticker_symbol, period="1y", interval="1d", multi_level_index=False)
        if data.empty: return None
        # 컬럼명을 모두 소문자로 통일 (에러 방지 핵심)
        data.columns = [c.lower() for c in data.columns]
        return data
    except:
        return None

# 종목 매핑
stock_dict = {
    "삼성전자": "005930.KS", "유한양행": "000100.KS", "에스피지": "058610.KQ",
    "아이온큐": "IONQ", "엔비디아": "NVDA", "넷플릭스": "NFLX", "삼성E&A": "028050.KS"
}

st.title("📈 이수 할아버지의 튼튼한 투자 분석기")

# 자동완성 검색창
selected_stock = st.selectbox(
    "종목을 선택하거나 직접 입력하세요",
    options=st.session_state.history,
    index=None,
    placeholder="예: 아이온큐, 삼성전자..."
)

# 분석 실행
if selected_stock:
    # 히스토리 업데이트
    if selected_stock not in st.session_state.history:
        st.session_state.history.insert(0, selected_stock)
    
    # 티커 변환
    ticker = stock_dict.get(selected_stock, selected_stock).upper()
    df = get_safe_data(ticker)
    
    if df is not None:
        # 데이터 추출 (최신 데이터가 가장 아래에 있음)
        close = df['close']
        
        # 1. 볼린저 밴드 (20일 기준)
        ma20 = close.rolling(20).mean()
        std20 = close.rolling(20).std()
        upper = ma20 + (std20 * 2)
        lower = ma20 - (std20 * 2)
        
        # 2. RSI (14일 기준)
        diff = close.diff()
        gain = diff.where(diff > 0, 0).rolling(14).mean()
        loss = -diff.where(diff < 0, 0).rolling(14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        # 3. MACD
        ema12 = close.ewm(span=12, adjust=False).mean()
        ema26 = close.ewm(span=26, adjust=False).mean()
        macd_line = ema12 - ema26
        signal_line = macd_line.ewm(span=9, adjust=False).mean()

        # 결과 표시
        curr_p = close.iloc[-1]
        st.markdown(f"<p class='big-font'>{selected_stock}: {curr_p:,.2f}</p>", unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("현재 RSI", f"{rsi.iloc[-1]:.1f}")
        c2.metric("밴드 하단", f"{lower.iloc[-1]:,.2f}")
        c3.metric("추세(MACD)", "상승" if macd_line.iloc[-1] > signal_line.iloc[-1] else "하락")

        # 종합 신호등
        st.write("---")
        last_rsi = rsi.iloc[-1]
        if last_rsi <= 35:
            st.markdown("<div style='background-color:#FFEEEE; color:#FF4B4B; border-color:#FF4B4B;' class='status-box'>🚨 강력 매수 (매우 저렴) 🚨</div>", unsafe_allow_html=True)
        elif last_rsi >= 70:
            st.markdown("<div style='background-color:#EEFFEE; color:#2E7D32; border-color:#2E7D32;' class='status-box'>💰 수익 실현 (과열 상태) 💰</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='background-color:#FFF9EE; color:#FFA000; border-color:#FFA000;' class='status-box'>🟡 관망 및 관찰 중 🟡</div>", unsafe_allow_html=True)

        # 차트
        st.write("### 📊 주가 흐름 및 볼린저 밴드")
        st.line_chart(pd.DataFrame({'주가': close, '상단': upper, '하단': lower}).tail(80))
        
        st.write("### 📉 MACD 추세 (위로 꺾여야 좋습니다)")
        st.line_chart(pd.DataFrame({'MACD': macd_line, '시그널': signal_line}).tail(80))
        
        # 사정권 강조
        if ticker == "IONQ" and curr_p <= 31:
            st.info(f"💡 아이온큐가 선생님의 사정권($30)에 진입했습니다!")
    else:
        st.error(f"'{selected_stock}' 데이터를 가져올 수 없습니다. 종목명이나 티커를 확인해 주세요.")

# 사이드바
if st.sidebar.button("검색 기록 초기화"):
    st.session_state.history = ["삼성전자", "아이온큐", "엔비디아"]
    st.rerun()
