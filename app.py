import streamlit as st
import FinanceDataReader as fdr
import yfinance as yf
import pandas as pd
import altair as alt

# 1. 화면 설정 및 스타일 (신호등 색상 정의)
st.set_page_config(page_title="이수 주식분석기 v205", layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    .traffic-light { padding: 30px; border-radius: 20px; text-align: center; font-size: 45px; font-weight: bold; border: 10px solid; margin-bottom: 20px; }
    .buy { border-color: #EF4444; background-color: #FEF2F2; color: #EF4444; } /* 빨강: 매수 */
    .wait { border-color: #F59E0B; background-color: #FFFBEB; color: #F59E0B; } /* 노랑: 관망 */
    .sell { border-color: #10B981; background-color: #ECFDF5; color: #10B981; } /* 초록: 매도 */
    .history-btn { margin-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

st.title("👨‍💻 이수할아버지의 마스터 분석기 v205")

# 2. 검색 기록 저장 기능 (History)
if 'history' not in st.session_state: st.session_state.history = []

with st.sidebar:
    st.header("📜 최근 검색 종목")
    if st.button("🗑️ 기록 삭제"): st.session_state.history = []
    for h in reversed(st.session_state.history):
        if st.button(f"🔍 {h}", key=f"btn_{h}"): st.session_state.ticker_input = h

# 3. 입력창
t_input = st.text_input("📊 분석할 종목 번호를 입력하세요 (예: 005930, IONQ, NFLX)", 
                       value=st.session_state.get('ticker_input', '005930'))

# 4. 데이터 엔진 (국내/해외 통합)
@st.cache_data(ttl=60)
def get_total_data(t):
    try:
        if t.isdigit(): df = fdr.DataReader(t, '2024')
        else: df = yf.download(t, period="1y", interval="1d", auto_adjust=True)
        if df is not None and not df.empty:
            df = df.reset_index()
            df.columns = [str(c).lower().strip() for c in df.columns]
            return df
    except: return None

if t_input:
    ticker = t_input.strip().upper()
    df = get_total_data(ticker)
    
    if isinstance(df, pd.DataFrame):
        # 검색 기록 저장
        if ticker not in st.session_state.history:
            st.session_state.history.append(ticker)
            if len(st.session_state.history) > 10: st.session_state.history.pop(0)

        # 5. 지표 계산 (BB, RSI, Williams, MACD)
        # 볼린저 밴드
        df['ma20'] = df['close'].rolling(20).mean()
        df['std'] = df['close'].rolling(20).std()
        df['upper'] = df['ma20'] + (df['std'] * 2)
        df['lower'] = df['ma20'] - (df['std'] * 2)
        # RSI
        diff = df['close'].diff(); g = diff.where(diff > 0, 0).rolling(14).mean(); l = -diff.where(diff < 0, 0).rolling(14).mean().replace(0, 0.001)
        rsi = (100 - (100 / (1 + (g / l)))).iloc[-1]
        # Williams %R
        h14 = df['high'].rolling(14).max(); l14 = df['low'].rolling(14).min()
        w_r = ((h14 - df['close']) / (h14 - l14)).iloc[-1] * -100
        # MACD
        df['ema12'] = df['close'].ewm(span=
