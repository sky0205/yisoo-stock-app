import streamlit as st
import yfinance as yf
import pandas as pd
import altair as alt
import numpy as np

# 1. 화면 설정
st.set_page_config(page_title="이수 Stock Analyzer v129", layout="wide")

st.markdown("""
    <style>
    .buy-box { padding: 25px; border-radius: 12px; text-align: center; font-size: 38px; font-weight: bold; border: 6px solid #FF4B4B; background-color: #FFEEEE; color: #FF4B4B; }
    .wait-box { padding: 25px; border-radius: 12px; text-align: center; font-size: 38px; font-weight: bold; border: 6px solid #6B7280; background-color: #F9FAFB; color: #6B7280; }
    .memo-box { padding: 25px; border-radius: 12px; background-color: #FFF9C4; border-left: 12px solid #FBC02D; color: #37474F; font-size: 22px; font-weight: bold; line-height: 1.8; margin-bottom: 30px; }
    </style>
    """, unsafe_allow_html=True)

# 2. 메인 화면
st.title("👨‍💻 이수할아버지의 튼튼분석기 v129")

# [긴급] 데이터 기억 초기화 버튼
if st.button("🔄 [응급처치] 데이터 통로 새로고침"):
    st.cache_data.clear()
    st.rerun()

st.write("---")
u_input = st.text_input("🔍 종목 번호나 티커 입력 (예: 005930)", value="005930")
ticker = u_input.upper().strip()
if u_input.isdigit() and len(u_input) == 6:
    ticker += ".KS"

# 3. 데이터 엔진 (가장 원초적인 방식으로 변경)
@st.cache_data(ttl=60)
def fetch_failsafe(t):
    try:
        # 최근 야후 에러를 피하기 위한 최신 설정
        df = yf.download(t, period="1y", interval="1d", auto_adjust=True, multi_level_index=False)
        if df is not None and not df.empty:
            df.columns = [str(c).lower().strip() for c in df.columns]
            df = df.reset_index()
            df.rename(columns={df.columns[0]: 'Date'}, inplace=True)
            return df
    except:
        return None
    return None

df = fetch_failsafe(ticker)

if df is not None:
    # 데이터가 있을 때 (정상 작동)
    close = df['close']
    ma20 = close.rolling(20).mean()
    rsi = 50 # 단순화
    
    st.write("---")
    if close.iloc[-1] > ma20.iloc[-1]:
        st.markdown(f"<div class='buy-box'>🚨 {ticker}: 상승 추세 진입 🚨</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='wait-box'>🟡 {ticker}: 관망 및 대기 🟡</div>", unsafe_allow_html=True)

    st.markdown(f"<div class='memo-box'>🚩 **대응 지침**: 현재 주가가 20일선 위에 있는지 확인하세요. 이수와 함께 보는 차트가 곧 나타납니다.</div>", unsafe_allow_html=True)
    
    chart = alt.Chart(df.tail(100)).mark_line(color='#111827').encode(x='Date:T', y='close:Q')
    st.altair_chart(chart.properties(height=400), use_container_width=True)
else:
    # 데이터가 없을 때 (응급 화면)
    st.warning(f"⚠️ 현재 야후 서버가 '{ticker}' 데이터를 보내주지 않고 있습니다.")
    st.info("이럴 때는 잠시 기다리시거나, 다른 종목 번호를 입력해 보세요. 번역 기능은 이미 잘 끄셨으니 곧 해결될 것입니다.")
    
    # 가짜 그래프라도 보여드려 화면이 깨지지 않게 합니다.
    dummy_data = pd.DataFrame({'Date': pd.date_range(start='2024-01-01', periods=100), 'Value': np.random.randn(100).cumsum()})
    st.write("### 📉 (참고용 샘플 차트)")
    st.line_chart(dummy_data.set_index('Date'))
