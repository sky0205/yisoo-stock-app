import streamlit as st
import subprocess
import sys
import time

# [응급 구조 1단계] 필요한 부품이 없으면 강제로 설치합니다.
def repair_engine():
    packages = ["finance-datareader", "yfinance", "pandas-ta"]
    for p in packages:
        try:
            __import__(p.replace("-", "_"))
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", p])

repair_engine()
import FinanceDataReader as fdr
import yfinance as yf
import pandas as pd
import altair as alt

# 1. 화면 설정
st.set_page_config(page_title="Stock Analyzer v133", layout="wide")

st.markdown("""
    <style>
    .buy-box { padding: 25px; border-radius: 12px; text-align: center; font-size: 38px; font-weight: bold; border: 6px solid #FF4B4B; background-color: #FFEEEE; color: #FF4B4B; }
    .wait-box { padding: 25px; border-radius: 12px; text-align: center; font-size: 38px; font-weight: bold; border: 6px solid #6B7280; background-color: #F9FAFB; color: #6B7280; }
    .memo-box { padding: 25px; border-radius: 12px; background-color: #FFF9C4; border-left: 12px solid #FBC02D; color: #37474F; font-size: 22px; font-weight: bold; line-height: 1.8; margin-bottom: 30px; }
    </style>
    """, unsafe_allow_html=True)

# 2. 메인 화면 상단
st.title("👨‍💻 이수할아버지의 주식분석기 v133")

# [필살기] 에러 기억을 싹 지우는 버튼
if st.button("🔄 [필살기] 데이터 기억 싹 지우고 다시 부르기"):
    st.cache_data.clear()
    st.rerun()

st.write("---")
u_input = st.text_input("🔍 종목 번호(6자리)나 티커 입력 후 엔터", value="005930")
ticker = u_input.strip()

# 3. 데이터 엔진 (우회로 3개 확보)
@st.cache_data(ttl=30)
def rescue_fetch(t):
    # 길 1: 한국 서버(네이버/KRX) 직통
    try:
        df = fdr.DataReader(t, '2024')
        if df is not None and not df.empty:
            df = df.reset_index()
            df.columns = [str(c).lower().strip() for c in df.columns]
            return df, "한국 서버 성공"
    except: pass

    # 길 2: 야후 서버 우회 (MultiIndex 방어)
    try:
        yt = t + ".KS" if t.isdigit() else t
        df = yf.download(yt, period="1y", interval="1d", auto_adjust=True, multi_level_index=False, threads=False)
        if df is not None and not df.empty:
            df.columns = [str(c).lower().strip() for c in df.columns]
            df = df.reset_index()
            df.rename(columns={df.columns[0]: 'Date'}, inplace=True)
            return df, "야후 서버 성공"
    except: pass
    
    return None, "모든 통로가 막혔습니다"

if ticker:
    with st.spinner('서버에서 데이터를 끈질기게 찾는 중...'):
        df, msg = rescue_fetch(ticker)
        
    if isinstance(df, pd.DataFrame):
        # 성공 시 로직
        close = df['close']
        ma20 = close.rolling(20).mean()
        curr_p = close.iloc[-1]
        
        # 지표 계산: $RSI = 100 - \frac{100}{1+RS}$
        diff = close.diff(); gain = diff.where(diff > 0, 0).rolling(14).mean(); loss = -diff.where(diff < 0, 0).rolling(14).mean().replace(0, 0.001)
        rsi = (100 - (100 / (1 + (gain / loss)))).iloc[-1]

        st.write("---")
        if rsi <= 35:
            st.markdown(f"<div class='buy-box'>🚨 {ticker}: 강력 매수 구간 🚨</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='wait-box'>🟡 {ticker}: 관망 및 대기 🟡</div>", unsafe_allow_html=True)

        memo = f"🚩 **{ticker} 대응 지침** ({msg})<br>"
        if curr_p > ma20.iloc[-1]: memo += "✅ **이평선**: 주가가 빨간 20일선 위에 있어 안전합니다.<br>"
        else: memo += "❌ **이평선**: 아직 20일선 아래에 있습니다. 반등을 더 기다리세요."
        st.markdown(f"<div class='memo-box'>{memo}</div>", unsafe_allow_html=True)

        chart = alt.Chart(df.tail(100)).mark_line(color='#111827', strokeWidth=3).encode(x=alt.X(df.columns[0]+':T', title='날짜'), y=alt.Y('close:Q', scale=alt.Scale(zero=False)))
        st.altair_chart(chart.properties(height=400), use_container_width=True)
    else:
        st.error(f"⚠️ {msg}")
        st.info("해결책: 1. 인터넷 연결 확인 2. 상단 '필살기' 버튼 클릭 3. 5분 뒤 다시 시도")

with st.sidebar:
    if st.button("🗑️ 모든 기록 리셋"):
        st.session_state.clear()
        st.rerun()
