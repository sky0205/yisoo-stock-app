import streamlit as st
import FinanceDataReader as fdr
import yfinance as yf
import pandas as pd
import altair as alt

# 1. 화면 설정 - 성공 시 배경이 연한 하늘색으로 바뀝니다
st.set_page_config(page_title="이수 주식앱 v157", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #F0F9FF; } 
    .buy-box { padding: 25px; border-radius: 12px; text-align: center; font-size: 35px; font-weight: bold; border: 6px solid #1E40AF; background-color: #DBEAFE; color: #1E3A8A; }
    </style>
    """, unsafe_allow_html=True)

# 2. 메인 화면
st.title("👨‍💻 이수할아버지의 주식분석기 v157")
st.success("🎉 드디어 v106 유령을 물리치고 최신 앱이 가동되었습니다!")

u_input = st.text_input("🔍 분석할 종목 번호를 입력하세요 (예: 005930)", value="005930")
ticker = u_input.strip()

@st.cache_data(ttl=60)
def fetch_v157(t):
    try:
        # 국내 서버 직통
        df = fdr.DataReader(t, '2024')
        if df is not None and not df.empty:
            df = df.reset_index()
            df.columns = [str(c).lower().strip() for c in df.columns]
            return df, "실시간 데이터 연결 성공"
    except: return None, "데이터를 불러오는 중입니다..."

if ticker:
    df, msg = fetch_v157(ticker)
    if isinstance(df, pd.DataFrame):
        close = df['close']
        # RSI 지표 계산: $$RSI = 100 - \frac{100}{1 + \frac{U}{D}}$$
        diff = close.diff(); g = diff.where(diff > 0, 0).rolling(14).mean(); l = -diff.where(diff < 0, 0).rolling(14).mean().replace(0, 0.001)
        rsi = (100 - (100 / (1 + (g / l)))).iloc[-1]

        st.write("---")
        st.markdown(f"<div class='buy-box'>📈 {ticker} 주가 분석 결과</div>", unsafe_allow_html=True)
        
        # 차트 그리기
        chart = alt.Chart(df.tail(100)).mark_line(color='#1E40AF', strokeWidth=3).encode(
            x=alt.X(df.columns[0]+':T', title='날짜'),
            y=alt.Y('close:Q', scale=alt.Scale(zero=False), title='주가')
        )
        st.altair_chart(chart.properties(height=450), use_container_width=True)
    else: st.info(msg)
