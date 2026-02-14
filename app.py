import streamlit as st
import FinanceDataReader as fdr
import yfinance as yf
import pandas as pd
import altair as alt

# 1. 화면 설정 (가장 깨끗한 스타일)
st.set_page_config(page_title="이수 주식분석기 v161", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; } 
    .buy-box { padding: 30px; border-radius: 15px; text-align: center; font-size: 38px; font-weight: bold; border: 8px solid #FF4B4B; background-color: #FFF5F5; color: #FF4B4B; margin-bottom: 20px; }
    .wait-box { padding: 30px; border-radius: 15px; text-align: center; font-size: 38px; font-weight: bold; border: 8px solid #6B7280; background-color: #F9FAFB; color: #6B7280; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# 2. 메인 타이틀
st.title("📈 이수할아버지의 주식분석기 v161")
st.write("---")

# 3. 입력창 및 분석 엔진
u_input = st.text_input("🔍 분석할 종목 번호를 입력하세요 (예: 005930, 066570)", value="005930")
ticker = u_input.strip()

@st.cache_data(ttl=60)
def fetch_perfect_v161(t):
    try:
        df = fdr.DataReader(t, '2024')
        if df is not None and not df.empty:
            df = df.reset_index()
            df.columns = [str(c).lower().strip() for c in df.columns]
            return df
    except: return None

if ticker:
    df = fetch_perfect_v161(ticker)
    if isinstance(df, pd.DataFrame):
        close = df['close']
        # RSI 지표 계산 (매수 신호 판단용)
        diff = close.diff(); g = diff.where(diff > 0, 0).rolling(14).mean(); l = -diff.where(diff < 0, 0).rolling(14).mean().replace(0, 0.001)
        rsi = (100 - (100 / (1 + (g / l)))).iloc[-1]

        # [최종 결론 표시]
        if rsi <= 35:
            st.markdown(f"<div class='buy-box'>🚨 {ticker}: 강력 매수 구간 🚨</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='wait-box'>🟡 {ticker}: 관망 대기 구간 🟡</div>", unsafe_allow_html=True)

        # [차트 그리기]
        chart = alt.Chart(df.tail(120)).mark_line(color='#1E40AF', strokeWidth=3).encode(
            x=alt.X(df.columns[0]+':T', title='날짜'),
            y=alt.Y('close:Q', scale=alt.Scale(zero=False), title='주가 (원)')
        ).properties(height=500)
        st.altair_chart(chart, use_container_width=True)
    else:
        st.error("⚠️ 데이터를 불러올 수 없습니다. 종목 번호를 확인해 주세요.")
