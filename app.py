import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup
import altair as alt

# 1. 시스템 무결성 체크 (이게 영문으로 보여야 합니다)
st.set_page_config(page_title="Isu Grandpa Analyzer v49", layout="wide")

# 사이드바에 번역기 작동 여부 표시
st.sidebar.title("🛠️ System Check")
st.sidebar.info("If you see English below, it's SUCCESS:")
st.sidebar.success("STATUS: ENGLISH_MODE_OK")
st.sidebar.write("---")

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
    </style>
    """, unsafe_allow_html=True)

# 데이터 로딩 로직 (철저한 영문 고정)
@st.cache_data(ttl=60)
def get_clean_data_final(ticker):
    try:
        df = yf.download(ticker, period="1y", interval="1d", auto_adjust=True, multi_level_index=False)
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(-1)
        df.columns = [str(c).lower().strip() for c in df.columns]
        return df.ffill().bfill().dropna()
    except: return None

# UI 시작
st.title("👨‍💻 이수할아버지의 주식분석기")
st.write("---")

h_list = list(st.session_state.name_map.keys())
sel_name = st.selectbox("📋 분석할 종목 선택", options=h_list, index=0)
t_ticker = st.session_state.name_map[sel_name]

if t_ticker:
    with st.spinner('데이터를 불러오고 있습니다...'):
        df = get_clean_data_final(t_ticker)
        if (df is None or df.empty) and ".KS" in t_ticker:
            df = get_clean_data_final(t_ticker.replace(".KS", ".KQ"))

    if df is not None and not df.empty and 'close' in df.columns:
        close = df['close']
        
        # 지표 계산: RSI
        diff = close.diff()
        gain = diff.where(diff > 0, 0).rolling(14).mean()
        loss = -diff.where(diff < 0, 0).rolling(14).mean().replace(0, 0.001)
        rsi_val = 100 - (100 / (1 + (gain / loss)))
        
        # 볼린저 밴드
        ma20 = close.rolling(20).mean(); std20 = close.rolling(20).std()
        upper = ma20 + (std20 * 2); lower = ma20 - (std20 * 2)
        y_high = close.max(); curr_p = close.iloc[-1]

        st.markdown(f"<p class='big-font'>{sel_name} 분석 보고서</p>", unsafe_allow_html=True)
        
        m1, m2, m3 = st.columns(3)
        m1.metric("현재가", f"{curr_p:,.0f}" if ".K" in t_ticker else f"{curr_p:,.2f}")
        m2.metric("RSI (과열도)", f"{rsi_val.iloc[-1]:.1f}")
        m3.metric("1년 최고가", f"{y_high:,.0f}" if ".K" in t_ticker else f"{y_high:,.2f}")

        # 신호등
        st.write("---")
        if rsi_val.iloc[-1] <= 35:
            st.markdown("<div style='background-color:#FFEEEE; color:#FF4B4B; border-color:#FF4B4B;' class='status-box'>🚨 강력 매수 구간 🚨</div>", unsafe_allow_html=True)
        elif curr_p >= y_high * 0.97:
            st.markdown("<div style='background-color:#E8F5E9; color:#2E7D32; border-color:#2E7D32;' class='status-box'>📈 추세 상승 중 (보유) 📈</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='background-color:#F5F5F5; color:#616161; border-color:#9E9E9E;' class='status-box'>🟡 관망 및 대기 🟡</div>", unsafe_allow_html=True)

        # 차트 (볼린저 밴드)
        st.write("### 📊 주가 흐름 및 볼린저 밴드")
        c_df = pd.DataFrame({'Date': df.index, 'Close': close, 'Upper': upper, 'Lower': lower, 'MA20': ma20}).tail(100).reset_index()
        base = alt.Chart(c_df).encode(x=alt.X('Date:T', axis=alt.Axis(title=None)))
        area = base.mark_area(opacity=0.1, color='gray').encode(y='Lower:Q', y2='Upper:Q')
        line = base.mark_line(color='#1E1E1E', strokeWidth=2).encode(y=alt.Y('Close:Q', scale=alt.Scale(zero=False)))
        ma_line = base.mark_line(color='#EF5350', strokeWidth=2).encode(y='MA20:Q')
        st.altair_chart((area + line + ma_line).properties(height=400), use_container_width=True)
    else:
        st.error("데이터 로딩 실패. 화면 상단의 번역 아이콘이 '회색'인지 꼭 확인하고 새로고침하세요.")

if st.sidebar.button("🗑️ 리셋"):
    st.session_state.clear()
    st.rerun()
