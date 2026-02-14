import streamlit as st
import subprocess
import sys

# [긴급 수리] 필요한 부품(라이브러리) 자동 설치 기능
def ensure_packages():
    pkgs = ["yfinance", "finance-datareader", "pandas-ta"]
    for p in pkgs:
        try:
            __import__(p.replace("-", "_"))
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", p])

ensure_packages()
import yfinance as yf
import FinanceDataReader as fdr
import pandas as pd
import altair as alt

# 1. 화면 설정
st.set_page_config(page_title="Isu Stock v141", layout="wide")

st.markdown("""
    <style>
    .buy-box { padding: 25px; border-radius: 12px; text-align: center; font-size: 38px; font-weight: bold; border: 6px solid #FF4B4B; background-color: #FFEEEE; color: #FF4B4B; }
    .wait-box { padding: 25px; border-radius: 12px; text-align: center; font-size: 38px; font-weight: bold; border: 6px solid #6B7280; background-color: #F9FAFB; color: #6B7280; }
    .memo-box { padding: 25px; border-radius: 12px; background-color: #FFF9C4; border-left: 12px solid #FBC02D; color: #37474F; font-size: 20px; font-weight: bold; line-height: 1.6; margin-bottom: 25px; }
    </style>
    """, unsafe_allow_html=True)

# 2. 메인 화면
st.title("📊 주식 분석기 v141 (최종 돌파판)")

# 에러 기억을 싹 지우는 버튼
if st.button("🔄 [필살기] 데이터 통로 강제 청소"):
    st.cache_data.clear()
    st.rerun()

st.write("---")
u_input = st.text_input("🔍 종목 번호(6자리)나 티커 입력 후 엔터", value="005930")
ticker = u_input.strip()

# 3. 데이터 엔진 (네이버/야후 이중 우회)
@st.cache_data(ttl=60)
def fetch_robust_v141(t):
    # 길 1: 한국 서버 직통 (네이버/KRX)
    try:
        df = fdr.DataReader(t, '2024')
        if df is not None and not df.empty:
            df = df.reset_index()
            df.columns = [str(c).lower().strip() for c in df.columns]
            return df, "국내 서버(Naver) 성공"
    except: pass

    # 길 2: 야후 서버 우회
    try:
        yt = t + ".KS" if t.isdigit() else t
        df = yf.download(yt, period="1y", interval="1d", auto_adjust=True, multi_level_index=False)
        if df is not None and not df.empty:
            df.columns = [str(c).lower().strip() for c in df.columns]
            df = df.reset_index()
            df.rename(columns={df.columns[0]: 'Date'}, inplace=True)
            return df, "해외 서버(Yahoo) 성공"
    except: pass
    
    return None, "모든 통로가 차단되었습니다. 잠시 휴식이 필요합니다."

if ticker:
    df, msg = fetch_robust_v141(ticker)
    
    if isinstance(df, pd.DataFrame):
        close = df['close']
        
        # 지표 계산: RSI
        # $$RSI = 100 - \frac{100}{1 + \frac{U}{D}}$$
        diff = close.diff(); g = diff.where(diff > 0, 0).rolling(14).mean(); l = -diff.where(diff < 0, 0).rolling(14).mean().replace(0, 0.001)
        rsi = (100 - (100 / (1 + (g / l)))).iloc[-1]
        
        # MACD
        # $$MACD = EMA_{12} - EMA_{26}$$
        macd = close.ewm(span=12).mean() - close.ewm(span=26).mean()
        ma20 = close.rolling(20).mean()

        st.write("---")
        if rsi <= 35:
            st.markdown(f"<div class='buy-box'>🚨 {ticker}: 강력 매수 🚨</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='wait-box'>🟡 {ticker}: 관망 대기 🟡</div>", unsafe_allow_html=True)

        memo = f"🚩 **대응 전략** ({msg})<br>"
        if close.iloc[-1] > ma20.iloc[-1]: memo += "✅ **흐름**: 20일선 위에서 힘차게 달리는 중입니다."
        else: memo += "❌ **흐름**: 아직 20일선 아래입니다. 더 기다려보세요."
        st.markdown(f"<div class='memo-box'>{memo}</div>", unsafe_allow_html=True)

        chart = alt.Chart(df.tail(100)).mark_line(color='#111827', strokeWidth=3).encode(
            x=alt.X(df.columns[0]+':T', title='날짜'), 
            y=alt.Y('close:Q', scale=alt.Scale(zero=False), title='주가')
        )
        st.altair_chart(chart.properties(height=450), use_container_width=True)
    else:
        st.error(f"⚠️ {msg}")
