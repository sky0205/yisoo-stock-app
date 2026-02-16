import streamlit as st
import yfinance as yf
import pandas as pd
import altair as alt
import time

# 1. 화면 스타일
st.set_page_config(page_title="이수 주식 v230", layout="wide")
st.markdown("<style>.stApp { background-color: #FFFFFF; } .traffic-light { padding: 40px; border-radius: 25px; text-align: center; font-size: 45px; font-weight: bold; border: 12px solid; margin-bottom: 25px; }</style>", unsafe_allow_html=True)

st.title("👨‍💻 이수할아버지의 마스터 분석기 v230")

# 2. 입력창
t_input = st.text_input("📊 종목코드 (예: 005930.KS, NVDA, IONQ)", value="005930.KS").strip().upper()

# 3. 데이터 엔진 (에러 수정 버전)
@st.cache_data(ttl=600)
def get_stock_data(t):
    try:
        time.sleep(1)
        df = yf.download(t, period="1y", interval="1d", auto_adjust=True)
        if df is None or df.empty: return None
        
        # [핵심 수정] 데이터 구조를 강제로 단순하게 만듭니다.
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df.columns = [str(c).lower().strip() for c in df.columns]
        return df
    except: return None

if t_input:
    df = get_stock_data(t_input)
    if df is not None and 'close' in df.columns:
        df = df.reset_index()
        # 지표 계산
        diff = df['close'].diff(); g = diff.where(diff > 0, 0).rolling(14).mean(); l = -diff.where(diff < 0, 0).rolling(14).mean().replace(0, 0.001)
        rsi = (100 - (100 / (1 + (g / l)))).iloc[-1]
        h14 = df['high'].rolling(14).max(); l14 = df['low'].rolling(14).min(); wr = ((h14 - df['close']) / (h14 - l14)).iloc[-1] * -100
        
        # 결과 출력
        st.write("---")
        if rsi < 35 or wr < -80:
            st.success(f"🔴 {t_input} : 적극 매수 구간 (RSI: {rsi:.1f})")
        elif rsi > 65 or wr > -20:
            st.warning(f"🟢 {t_input} : 매도 검토 구간 (RSI: {rsi:.1f})")
        else:
            st.info(f"🟡 {t_input} : 관망 및 대기 (RSI: {rsi:.1f})")

        # 차트
        chart = alt.Chart(df.tail(100)).mark_line().encode(x='Date:T', y=alt.Y('close:Q', scale=alt.Scale(zero=False)))
        st.altair_chart(chart, use_container_width=True)
    else:
        st.error("데이터를 불러오지 못했습니다. 종목코드를 확인해 주세요.")
