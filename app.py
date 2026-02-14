import streamlit as st
import FinanceDataReader as fdr
import yfinance as yf
import pandas as pd
import altair as alt

# 1. 화면 설정 및 제목 (v152)
st.set_page_config(page_title="이수 주식앱 v152", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #F0F9FF; } 
    .buy-box { padding: 25px; border-radius: 12px; text-align: center; font-size: 35px; font-weight: bold; border: 6px solid #FF4B4B; background-color: #FFEEEE; color: #FF4B4B; }
    </style>
    """, unsafe_allow_html=True)

st.title("👨‍💻 이수할아버지의 주식분석기 v152")
st.success("🎉 드디어 'app.py' 연결에 성공하셨습니다! 이제 진짜 시작입니다.")

u_input = st.text_input("🔍 종목 번호 6자리 입력 (예: 005930)", value="005930")
ticker = u_input.strip()

@st.cache_data(ttl=60)
def fetch_v152(t):
    try:
        df = fdr.DataReader(t, '2024')
        if df is not None and not df.empty:
            df = df.reset_index()
            df.columns = [str(c).lower().strip() for c in df.columns]
            return df, "데이터 연결 성공"
    except: return None, "데이터를 불러오는 중입니다..."

if ticker:
    df, msg = fetch_v152(ticker)
    if isinstance(df, pd.DataFrame):
        close = df['close']
        st.markdown(f"<div class='buy-box'>📈 {ticker} 분석 차트</div>", unsafe_allow_html=True)
        # 차트 그리기
        chart = alt.Chart(df.tail(100)).mark_line(color='#1E40AF', strokeWidth=3).encode(
            x=alt.X(df.columns[0]+':T', title='날짜'),
            y=alt.Y('close:Q', scale=alt.Scale(zero=False), title='주가')
        )
        st.altair_chart(chart.properties(height=450), use_container_width=True)
