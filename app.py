import streamlit as st
import FinanceDataReader as fdr
import yfinance as yf
import pandas as pd
import altair as alt

# 1. 화면 설정 (가장 큰 글씨)
st.set_page_config(page_title="이수 주식분석기", layout="wide")

st.title("👨‍💻 이수할아버지의 주식분석기 v164")
st.write("---")

# 2. 종목 입력 (기본값 삼성전자)
ticker = st.text_input("🔍 종목 번호나 이름을 입력하세요 (예: 005930, CPNG, IONQ)", value="005930").strip()

@st.cache_data(ttl=30)
def get_stock(t):
    try:
        if t.isdigit(): df = fdr.DataReader(t, '2024')
        else: df = yf.download(t, period="1y", interval="1d", auto_adjust=True)
        if df is not None and not df.empty:
            df = df.reset_index()
            df.columns = [str(c).lower().strip() for c in df.columns]
            return df
    except: return None
    return None

if ticker:
    df = get_stock(ticker)
    if isinstance(df, pd.DataFrame):
        # RSI 계산: $$RSI = 100 - \frac{100}{1 + \frac{\text{Average Gain}}{\text{Average Loss}}}$$
        diff = df['close'].diff()
        gain = diff.where(diff > 0, 0).rolling(14).mean()
        loss = -diff.where(diff < 0, 0).rolling(14).mean().replace(0, 0.001)
        rsi = (100 - (100 / (1 + (gain / loss)))).iloc[-1]

        # [결론 표시]
        if rsi <= 35: st.error(f"🚨 {ticker}: 현재 매수 검토 구간입니다 (RSI: {rsi:.1f})")
        else: st.info(f"🟡 {ticker}: 현재 관망 구간입니다 (RSI: {rsi:.1f})")

        # [차트 그리기]
        chart = alt.Chart(df.tail(100)).mark_line(color='#1E40AF', strokeWidth=3).encode(
            x=alt.X(df.columns[0]+':T', title='날짜'),
            y=alt.Y('close:Q', scale=alt.Scale(zero=False), title='주가')
        ).properties(height=500)
        st.altair_chart(chart, use_container_width=True)
    else:
        st.warning("⚠️ 데이터를 가져오지 못했습니다. 종목 번호를 다시 확인해 주세요.")
