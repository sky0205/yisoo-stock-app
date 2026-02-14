import streamlit as st
import FinanceDataReader as fdr
import yfinance as yf
import pandas as pd
import altair as alt

# 1. 화면 설정 (가장 보기 편한 큰 글씨와 깔끔한 배경)
st.set_page_config(page_title="이수 주식분석기 v162", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    .buy-box { padding: 30px; border-radius: 15px; text-align: center; font-size: 38px; font-weight: bold; border: 8px solid #FF4B4B; background-color: #FFF5F5; color: #FF4B4B; }
    .wait-box { padding: 30px; border-radius: 15px; text-align: center; font-size: 38px; font-weight: bold; border: 8px solid #6B7280; background-color: #F9FAFB; color: #6B7280; }
    .stButton>button { width: 100%; height: 60px; font-size: 20px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("📈 이수할아버지의 완벽 주식분석기")
st.write(f"### 🗓️ 오늘 날짜: {pd.Timestamp.now().strftime('%Y-%m-%d')}")

# 2. 선생님의 주요 종목 버튼 (누르면 바로 분석)
st.write("---")
st.write("#### 🚀 즐겨찾는 종목 바로 분석")
col1, col2, col3, col4 = st.columns(4)

# 보유 종목 위주로 버튼 구성
if col1.button("삼성전자"): st.session_state.ticker = "005930"
if col2.button("쿠팡 (CPNG)"): st.session_state.ticker = "CPNG"
if col3.button("아이온큐 (IONQ)"): st.session_state.ticker = "IONQ"
if col4.button("넷플릭스 (NFLX)"): st.session_state.ticker = "NFLX"

# 직접 입력창
ticker_input = st.text_input("🔍 직접 종목 번호 입력 (예: 005930)", value=st.session_state.get('ticker', '005930'))
ticker = ticker_input.strip()

# 3. 데이터 분석 엔진
@st.cache_data(ttl=60)
def get_stock_data(t):
    try:
        if t.isdigit(): # 국내주식
            df = fdr.DataReader(t, '2024')
        else: # 해외주식
            df = yf.download(t, period="1y", interval="1d", auto_adjust=True, multi_level_index=False)
        
        if df is not None and not df.empty:
            df = df.reset_index()
            df.columns = [str(c).lower().strip() for c in df.columns]
            return df
    except: return None
    return None

if ticker:
    df = get_stock_data(ticker)
    if isinstance(df, pd.DataFrame):
        close_price = df['close'].iloc[-1]
        
        # RSI 계산 (매수 신호 판단)
        # $$RSI = 100 - \frac{100}{1 + \frac{Average Gain}{Average Loss}}$$
        diff = df['close'].diff()
        gain = diff.where(diff > 0, 0).rolling(14).mean()
        loss = -diff.where(diff < 0, 0).rolling(14).mean().replace(0, 0.001)
        rsi = (100 - (100 / (1 + (gain / loss)))).iloc[-1]

        # 결과 표시
        st.write("---")
        if rsi <= 35:
            st.markdown(f"<div class='buy-box'>🚨 {ticker}: 지금은 매수 기회! 🚨</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='wait-box'>🟡 {ticker}: 조금 더 지켜보세요 🟡</div>", unsafe_allow_html=True)

        # 삼성전자의 경우 평균단가 비교 서비스
        if ticker == "005930":
            avg_cost = 58000 #
            profit_rate = ((close_price - avg_cost) / avg_cost) * 100
            st.info(f"💡 선생님의 삼성전자 평균단가(58,000원) 대비 수익률: **{profit_rate:.2f}%** 입니다.")

        # 차트
        st.write(f"#### 📊 {ticker} 최근 주가 흐름")
        chart = alt.Chart(df.tail(120)).mark_line(color='#1E40AF', strokeWidth=3).encode(
            x=alt.X(df.columns[0]+':T', title='날짜'),
            y=alt.Y('close:Q', scale=alt.Scale(zero=False), title='주가')
        ).properties(height=500)
        st.altair_chart(chart, use_container_width=True)
    else:
        st.error("⚠️ 데이터를 불러오지 못했습니다. 종목 번호를 확인해주세요.")
