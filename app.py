import streamlit as st
import yfinance as yf
import FinanceDataReader as fdr
import pandas as pd
import altair as alt
import requests

# 1. 화면 설정
st.set_page_config(page_title="Stock Analyzer v137", layout="wide")

st.markdown("""
    <style>
    .buy-box { padding: 25px; border-radius: 12px; text-align: center; font-size: 38px; font-weight: bold; border: 6px solid #FF4B4B; background-color: #FFEEEE; color: #FF4B4B; }
    .wait-box { padding: 25px; border-radius: 12px; text-align: center; font-size: 38px; font-weight: bold; border: 6px solid #6B7280; background-color: #F9FAFB; color: #6B7280; }
    .memo-box { padding: 25px; border-radius: 12px; background-color: #FFF9C4; border-left: 12px solid #FBC02D; color: #37474F; font-size: 22px; font-weight: bold; line-height: 1.8; margin-top: 20px; margin-bottom: 30px; }
    </style>
    """, unsafe_allow_html=True)

# 2. 메인 화면
st.title("👨‍💻 이수할아버지의 주식분석기 v137")

if st.button("🔄 [긴급] 데이터 기억 싹 지우고 다시 부르기"):
    st.cache_data.clear()
    st.rerun()

u_input = st.text_input("🔍 종목 번호 입력 후 엔터 (예: 005930)", value="005930")
ticker = u_input.strip()

# 3. 데이터 엔진 (사람인 척 위장하는 기능 추가)
@st.cache_data(ttl=60)
def fetch_stealth_v137(t):
    # 길 1: 한국 전용 서버 시도
    try:
        df = fdr.DataReader(t, '2024')
        if df is not None and not df.empty:
            df = df.reset_index()
            df.columns = [str(c).lower().strip() for c in df.columns]
            return df, "국내 서버 직통 성공"
    except: pass

    # 길 2: 야후 서버 (사람인 척 위장)
    try:
        yt = t + ".KS" if t.isdigit() else t
        # 서버를 속이는 가짜 신분증(User-Agent)
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        df = yf.download(yt, period="1y", interval="1d", auto_adjust=True, multi_level_index=False, proxy=None)
        if df is not None and not df.empty:
            df.columns = [str(c).lower().strip() for c in df.columns]
            df = df.reset_index()
            df.rename(columns={df.columns[0]: 'Date'}, inplace=True)
            return df, "해외 서버 위장 성공"
    except: pass
    
    return None, "모든 통로가 차단되었습니다. 핫스팟을 연결하거나 30분 뒤에 시도해 보세요."

if ticker:
    df, msg = fetch_stealth_v137(ticker)
    if isinstance(df, pd.DataFrame):
        close = df['close']
        # 지표 계산 ($RSI$, $MACD$)
        diff = close.diff(); gain = diff.where(diff > 0, 0).rolling(14).mean(); loss = -diff.where(diff < 0, 0).rolling(14).mean().replace(0, 0.001)
        rsi_val = (100 - (100 / (1 + (gain / loss)))).iloc[-1]
        
        # MACD: $MACD = EMA_{12} - EMA_{26}$
        macd = close.ewm(span=12, adjust=False).mean() - close.ewm(span=26, adjust=False).mean()
        sig = macd.ewm(span=9, adjust=False).mean()
        ma20 = close.rolling(20).mean(); std20 = close.rolling(20).std()
        up_b, lo_b = ma20 + (std20 * 2), ma20 - (std20 * 2)

        st.write("---")
        if rsi_val <= 35:
            st.markdown(f"<div class='buy-box'>🚨 {ticker}: 강력 매수 🚨</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='wait-box'>🟡 {ticker}: 관망 대기 🟡</div>", unsafe_allow_html=True)

        memo = f"🚩 **대응 지침** ({msg})<br>"
        if close.iloc[-1] > ma20.iloc[-1]: memo += "✅ **이평선**: 주가가 20일선 위에 있어 안전합니다."
        else: memo += "❌ **이평선**: 아직 20일선 아래입니다. 더 기다리세요."
        st.markdown(f"<div class='memo-box'>{memo}</div>", unsafe_allow_html=True)

        # 차트 출력
        chart = alt.Chart(df.tail(100)).mark_line(color='#111827', strokeWidth=3).encode(
            x=alt.X(df.columns[0]+':T', title='날짜'), 
            y=alt.Y('close:Q', scale=alt.Scale(zero=False), title='주가')
        )
        st.altair_chart(chart.properties(height=400), use_container_width=True)
    else:
        st.error(f"⚠️ {msg}")
