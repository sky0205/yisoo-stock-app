import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="이수 투자비책 v6", layout="wide")

if 'history' not in st.session_state:
    st.session_state.history = ["삼성전자", "아이온큐", "엔비디아"]

# 데이터 분석 함수 (안정화)
@st.cache_data(ttl=60)
def get_refined_data(ticker):
    try:
        data = yf.download(ticker, period="1y", interval="1d", multi_level_index=False)
        if data.empty: return None
        data.columns = [c.lower() for c in data.columns]
        return data
    except: return None

st.title("📈 이수 할아버지의 '칼날 방지' 분석기")

selected_stock = st.selectbox("종목 선택", options=st.session_state.history)

if selected_stock:
    ticker = selected_stock.upper() if selected_stock != "삼성전자" else "005930.KS"
    df = get_refined_data(ticker)
    
    if df is not None:
        close = df['close']
        
        # 1. 볼린저 밴드
        ma20 = close.rolling(20).mean(); std20 = close.rolling(20).std()
        upper = ma20 + (std20 * 2); lower = ma20 - (std20 * 2)
        
        # 2. RSI
        diff = close.diff(); gain = diff.where(diff > 0, 0).rolling(14).mean(); loss = -diff.where(diff < 0, 0).rolling(14).mean()
        rsi = 100 - (100 / (1 + (gain / loss)))
        
        # 3. MACD
        ema12 = close.ewm(span=12, adjust=False).mean(); ema26 = close.ewm(span=26, adjust=False).mean()
        macd = ema12 - ema26; sig = macd.ewm(span=9, adjust=False).mean()

        # [핵심 로직 수정]
        curr_rsi = rsi.iloc[-1]
        macd_up = macd.iloc[-1] > macd.iloc[-2] # MACD가 고개를 들었는가?
        is_golden = macd.iloc[-1] > sig.iloc[-1] # 골든크로스인가?

        st.markdown(f"### {selected_stock}: {close.iloc[-1]:,.2f}")
        
        # 신호등 로직
        st.write("---")
        if curr_rsi <= 35:
            if macd_up: # 싸고 + 고개도 들었다
                st.markdown("<div style='background-color:#FFEEEE; color:#FF4B4B; padding:20px; border-radius:15px; text-align:center; font-size:40px; font-weight:bold; border:5px solid #FF4B4B;'>🚨 지금입니다! 매수 신호 🚨</div>", unsafe_allow_html=True)
            else: # 싸지만 + 계속 떨어지는 중이다
                st.markdown("<div style='background-color:#FFF4E5; color:#FFA000; padding:20px; border-radius:15px; text-align:center; font-size:40px; font-weight:bold; border:5px solid #FFA000;'>✋ 싸지만 기다리세요 (하락 중) </div>", unsafe_allow_html=True)
        elif curr_rsi >= 70:
            st.markdown("<div style='background-color:#EEFFEE; color:#2E7D32; padding:20px; border-radius:15px; text-align:center; font-size:40px; font-weight:bold; border:5px solid #2E7D32;'>💰 과열입니다! 일부 매도 💰</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='background-color:#F0F2F6; color:#31333F; padding:20px; border-radius:15px; text-align:center; font-size:40px; font-weight:bold; border:5px solid #D1D5DB;'>🟡 관망 (박스권 흐름) 🟡</div>", unsafe_allow_html=True)

        st.line_chart(pd.DataFrame({'주가': close, '하단': lower}).tail(60))
        st.line_chart(pd.DataFrame({'MACD': macd, '시그널': sig}).tail(60))
