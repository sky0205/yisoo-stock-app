import streamlit as st
import pandas as pd
import numpy as np
import FinanceDataReader as fdr
import yfinance as yf
import altair as alt
from datetime import datetime, timedelta

# 1. 화면 설정
st.set_page_config(page_title="Isu Stock v144", layout="wide")

st.markdown("""
    <style>
    .buy-box { padding: 25px; border-radius: 12px; text-align: center; font-size: 38px; font-weight: bold; border: 6px solid #FF4B4B; background-color: #FFEEEE; color: #FF4B4B; }
    .wait-box { padding: 25px; border-radius: 12px; text-align: center; font-size: 38px; font-weight: bold; border: 6px solid #6B7280; background-color: #F9FAFB; color: #6B7280; }
    .memo-box { padding: 25px; border-radius: 12px; background-color: #E0F2FE; border-left: 12px solid #0EA5E9; color: #0369A1; font-size: 20px; font-weight: bold; line-height: 1.6; margin-bottom: 25px; }
    </style>
    """, unsafe_allow_html=True)

# 2. 상단 제어판
st.title("👨‍💻 이수할아버지의 주식분석기 v144 (강제 가동 모드)")

# 3. 데이터 엔진 (실패 시 가짜 데이터 생성)
def get_mock_data():
    """데이터 수신 실패 시 보여줄 가짜 데이터를 만듭니다."""
    dates = pd.date_range(end=datetime.now(), periods=100)
    prices = np.random.randn(100).cumsum() + 100
    df = pd.DataFrame({'date': dates, 'close': prices})
    return df

@st.cache_data(ttl=30)
def fetch_failsafe_v144(t):
    # 길 1: 한국 서버 (Naver)
    try:
        df = fdr.DataReader(t, '2025-01-01')
        if df is not None and not df.empty:
            df = df.reset_index()
            df.columns = [str(c).lower().strip() for c in df.columns]
            return df, "실제 서버 데이터 (Naver)"
    except: pass

    # 길 2: 야후 서버
    try:
        yt = t + ".KS" if t.isdigit() else t
        df = yf.download(yt, period="1y", interval="1d", auto_adjust=True, multi_level_index=False)
        if df is not None and not df.empty:
            df.columns = [str(c).lower().strip() for c in df.columns]
            df = df.reset_index()
            df.rename(columns={df.columns[0]: 'Date'}, inplace=True)
            return df, "실제 서버 데이터 (Yahoo)"
    except: pass
    
    # 길 3: 모든 실패 시 가짜 데이터 리턴
    return get_mock_data(), "⚠️ 서버 차단됨 (샘플 데이터 표시 중)"

st.write("---")
u_input = st.text_input("🔍 종목 번호를 입력하세요 (예: 005930)", value="005930")
ticker = u_input.strip()

if ticker:
    df, status_msg = fetch_failsafe_v144(ticker)
    
    close = df['close']
    ma20 = close.rolling(20).mean()
    
    # RSI 계산 ($$RSI = 100 - \frac{100}{1 + \frac{U}{D}}$$)
    diff = close.diff(); g = diff.where(diff > 0, 0).rolling(14).mean(); l = -diff.where(diff < 0, 0).rolling(14).mean().replace(0, 0.001)
    rsi_val = (100 - (100 / (1 + (g / l)))).iloc[-1]

    # [A] 결론 신호등
    st.write(f"### 📋 분석 결과 : {status_msg}")
    if rsi_val <= 35:
        st.markdown(f"<div class='buy-box'>🚨 {ticker}: 강력 매수 구간 🚨</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='wait-box'>🟡 {ticker}: 관망 및 대기 🟡</div>", unsafe_allow_html=True)

    # [B] 투자 지침
    st.markdown(f"<div class='memo-box'>🚩 **할아버지의 메모**: 현재 주가 흐름은 20일선 {'위' if close.iloc[-1] > ma20.iloc[-1] else '아래'}에 있습니다.</div>", unsafe_allow_html=True)

    # [C] 그래프
    chart = alt.Chart(df).mark_line(color='#111827', strokeWidth=3).encode(
        x=alt.X(df.columns[0]+':T', title='날짜'), 
        y=alt.Y('close:Q', scale=alt.Scale(zero=False), title='주가')
    )
    st.altair_chart(chart.properties(height=400), use_container_width=True)
