import streamlit as st
import FinanceDataReader as fdr
import yfinance as yf
import pandas as pd
import altair as alt

# 1. 화면 설정
st.set_page_config(page_title="이수 주식분석기", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    .buy-box { padding: 30px; border-radius: 15px; text-align: center; font-size: 35px; font-weight: bold; border: 8px solid #FF4B4B; background-color: #FFF5F5; color: #FF4B4B; }
    .wait-box { padding: 30px; border-radius: 15px; text-align: center; font-size: 35px; font-weight: bold; border: 8px solid #6B7280; background-color: #F9FAFB; color: #6B7280; }
    </style>
    """, unsafe_allow_html=True)

st.title("📈 이수할아버지의 주식분석기")
st.write("---")

# 2. 종목 입력 (기본값: 삼성전자)
ticker = st.text_input("🔍 분석할 종목 번호를 입력하세요 (예: 005930, IONQ)", value="005930").strip()

@st.cache_data(ttl=30)
def get_stock_data(t):
    try:
        if t.isdigit(): # 국내주식
            df = fdr.DataReader(t, '2024')
        else: # 해외주식
            df = yf.download(t, period="1y", interval="1d", auto_adjust=True)
        
        if df is not None and not df.empty:
            df = df.reset_index()
            df.columns = [str(c).lower().strip() for c in df.columns]
            return df
    except: return None
    return None

if ticker:
    df = get_stock_data(ticker)
    if isinstance(df, pd.DataFrame):
        # RSI 지표 계산
        # $$RSI = 100 - \frac{100}{1 + \frac{Average Gain}{Average Loss}}$$
        diff = df['close'].diff()
        gain = diff.where(diff > 0, 0).rolling(14).mean()
        loss = -diff.where(diff < 0, 0).rolling(14).mean().replace(0, 0.001)
        rsi = (100 - (100 / (1 + (gain / loss)))).iloc[-1]

        # 결과 출력
        if rsi <= 35:
            st.markdown(f"<div class='buy-box'>🚨 {ticker}: 지금 매수 검토 구간입니다 🚨</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='wait-box'>🟡 {ticker}: 조금 더 지켜볼 구간입니다 🟡</div>", unsafe_allow_html=True)

        # 차트
        st.write(f"#### 📊 {ticker} 최근 주가 흐름")
        chart = alt.Chart(df.tail(120)).mark_line(color='#1E40AF', strokeWidth=3).encode(
            x=alt.X(df.columns[0]+':T', title='날짜'),
            y=alt.Y('close:Q', scale=alt.Scale(zero=False), title='주가')
        ).properties(height=500)
        st.altair_chart(chart, use_container_width=True)
    else:
        st.error("⚠️ 데이터를 불러오지 못했습니다. 종목 번호를 확인해주세요.")
