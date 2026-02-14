import streamlit as st
import FinanceDataReader as fdr
import yfinance as yf
import pandas as pd
import altair as alt

# 1. 화면 설정 및 제목 (v153)
st.set_page_config(page_title="이수 주식앱 v153", layout="wide")

st.markdown("""
    <style>
    /* 성공 시 배경이 연한 주황색으로 바뀝니다 */
    .stApp { background-color: #FFF7ED; } 
    .buy-box { padding: 25px; border-radius: 12px; text-align: center; font-size: 35px; font-weight: bold; border: 6px solid #F97316; background-color: #FFEDD5; color: #EA580C; }
    </style>
    """, unsafe_allow_html=True)

st.title("👨‍💻 이수할아버지의 주식분석기 v153")
st.success("🎉 드디어 'app.py' 파일 연결에 성공하셨습니다! v106은 이제 안녕입니다.")

u_input = st.text_input("🔍 종목 번호 6자리 입력 (예: 005930)", value="005930")
ticker = u_input.strip()

@st.cache_data(ttl=60)
def fetch_v153(t):
    try:
        # 국내 서버 시도
        df = fdr.DataReader(t, '2024')
        if df is not None and not df.empty:
            df = df.reset_index()
            df.columns = [str(c).lower().strip() for c in df.columns]
            return df, "실시간 데이터 연결 성공"
    except: return None, "데이터를 불러오는 중입니다..."

if ticker:
    df, msg = fetch_v153(ticker)
    if isinstance(df, pd.DataFrame):
        close = df['close']
        st.markdown(f"<div class='buy-box'>📈 {ticker} 분석 차트 가동 중</div>", unsafe_allow_html=True)
        # 차트 그리기
        chart = alt.Chart(df.tail(100)).mark_line(color='#EA580C', strokeWidth=3).encode(
            x=alt.X(df.columns[0]+':T', title='날짜'),
            y=alt.Y('close:Q', scale=alt.Scale(zero=False), title='주가')
        )
        st.altair_chart(chart.properties(height=450), use_container_width=True)
