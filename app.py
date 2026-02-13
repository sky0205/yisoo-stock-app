import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup
import altair as alt

# 1. 화면 설정 및 번역 방지 체크
st.set_page_config(page_title="이수할아버지 주식분석기 v41", layout="wide")
st.sidebar.write("Checking System... OK") # 번역기가 작동하면 이 글자가 한글로 변합니다.

if 'name_map' not in st.session_state:
    st.session_state.name_map = {
        "삼성전자": "005930.KS", "현대차": "005380.KS", "엔비디아": "NVDA", 
        "아이온큐": "IONQ", "유한양행": "000100.KS"
    }

st.markdown("""
    <style>
    .stMetric { background-color: #F8F9FA; padding: 15px; border-radius: 10px; border: 1px solid #DEE2E6; }
    .big-font { font-size:40px !important; font-weight: bold; color: #1E1E1E; }
    .status-box { padding: 25px; border-radius: 15px; text-align: center; font-size: 32px; font-weight: bold; margin: 15px 0; border: 5px solid; }
    .info-box { background-color: #E3F2FD; padding: 20px; border-radius: 10px; border-left: 10px solid #2196F3; margin-bottom: 25px; }
    </style>
    """, unsafe_allow_html=True)

# 데이터 로직 (번역 내성 강화)
@st.cache_data(ttl=60)
def get_safe_data_v41(ticker):
    try:
        df = yf.download(ticker, period="1y", interval="1d", auto_adjust=True, multi_level_index=False)
        if df.empty: return None
        df.columns = [str(c).lower().strip() for c in df.columns]
        if 'close' not in df.columns:
            df['close'] = df.iloc[:, 0]
        return df.dropna()
    except: return None

st.title("👨‍💻 이수할아버지의 주식분석기")
st.write("---")

# 종목 선택 창
h_list = list(st.session_state.name_map.keys())
sel_name = st.selectbox("📋 종목 선택", options=h_list, index=0)
t_ticker = st.session_state.name_map[sel_name]

if t_ticker:
    df = get_safe_data_v41(t_ticker)
    if (df is None or df.empty) and ".KS" in t_ticker:
        df = get_safe_data_v41(t_ticker.replace(".KS", ".KQ"))

    if df is not None and not df.empty:
        # 주요 데이터 설정
        close = df['close']; high = df.get('high', close); low = df.get('low', close)
        
        # 지표 계산: RSI, MACD
        # $RSI = 100 - \frac{100}{1 + RS}$
        diff = close.diff()
        gain = diff.where(diff > 0, 0).rolling(14).mean()
        loss = -diff.where(diff < 0, 0).rolling(14).mean().replace(0, 0.001)
        rsi_val = 100 - (100 / (1 + (gain / loss)))
        
        # $MACD = EMA_{12} - EMA_{26}$
        macd = close.ewm(span=12).mean() - close.ewm(span=26).mean()
        sig = macd.ewm(span=9).mean()
        
        y_high = close.max(); curr_p = close.iloc[-1]

        # 1. 지표 상단 바
        st.markdown(f"<p class='big-font'>{sel_name} 분석 보고서</p>", unsafe_allow_html=True)
        
        if curr_p >= y_high * 0.97:
            st.markdown(f"<div class='info-box'>🚀 <strong>신고가 근처:</strong> 현재 돌파 기세가 아주 강합니다!</div>", unsafe_allow_html=True)

        m1, m2, m3 = st.columns(3)
        m1.metric("현재가", f"{curr_p:,.0f}" if ".K" in t_ticker else f"{curr_p:,.2f}")
        m2.metric("RSI (과열도)", f"{rsi_val.iloc[-1]:.1f}")
        m3.metric("1년 최고가", f"{y_high:,.0f}" if ".K" in t_ticker else f"{y_high:,.2f}")

        # 2. 신호등 섹션
        st.write("---")
        last_rsi = rsi_val.iloc[-1]
        if last_rsi <= 35:
            st.markdown("<div style='background-color:#FFEEEE; color:#FF4B4B; border-color:#FF4B4B;' class='status-box'>🚨 강력 매수 (바닥 탈출) 🚨</div>", unsafe_allow_html=True)
        elif curr_p >= y_high * 0.97 and macd.iloc[-1] > macd.iloc[-2]:
            st.markdown("<div style='background-color:#E8F5E9; color:#2E7D32; border-color:#2E7D32;' class='status-box'>📈 추세 상승 (수익 극대화) 📈</div>", unsafe_allow_html=True)
        elif last_rsi >= 75:
            st.markdown("<div style='background-color:#E1F5FE; color:#0288D1; border-color:#0288D1;' class='status-box'>💰 과열 주의 (익절 고려) 💰</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='background-color:#F5F5F5; color:#616161; border-color:#9E9E9E;' class='status-box'>🟡 관망 및 대기 🟡</div>", unsafe_allow_html=True)

        # 3. 차트 섹션
        st.write("### 📊 최근 주가 흐름")
        st.line_chart(close.tail(100))
        
        st.write("### 📉 MACD 추세 (파란선이 주황선 위에 있어야 함)")
        m_df = pd.DataFrame({'MACD': macd, 'Signal': sig}).tail(100).reset_index()
        st.line_chart(m_df.set_index('Date'))
        
    else:
        st.error("데이터를 가져오는 데 실패했습니다. 종목을 다시 선택하거나 새로고침해 보세요.")
