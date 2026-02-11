import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# 1. 앱 설정
st.set_page_config(page_title="이수 할아버지의 투자 비책", layout="wide")

st.markdown("""
    <style>
    .big-font { font-size:30px !important; font-weight: bold; }
    .time-font { font-size:18px !important; color: #666666; }
    .buy-signal { font-size:50px !important; color: #FF4B4B; font-weight: bold; text-align: center; background-color: #FFEEEE; padding: 20px; border-radius: 10px; }
    .sell-signal { font-size:50px !important; color: #2E7D32; font-weight: bold; text-align: center; background-color: #EEFFEE; padding: 20px; border-radius: 10px; }
    .wait-signal { font-size:50px !important; color: #FFA000; font-weight: bold; text-align: center; background-color: #FFF9EE; padding: 20px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("📈 이수 할아버지의 투자 비책 (시각 표시형)")

@st.cache_data(ttl=600)
def get_safe_data(ticker):
    try:
        df = yf.download(ticker, period="1y", multi_level_index=False)
        if df is None or df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        df.columns = [str(col).lower() for col in df.columns]
        return df
    except: return None

# 똑똑한 사전
stock_dict = {"삼성전자": "005930.KS", "유한양행": "000100.KS", "실리콘투": "247020.KQ", "삼성E&A": "028050.KS", "아이온큐": "IONQ"}

user_input = st.text_input("종목 검색", value="유한양행").strip()
ticker = stock_dict.get(user_input, user_input).upper()

if ticker:
    df = get_safe_data(ticker)
    if df is not None and 'close' in df.columns:
        close = df['close']
        
        # [핵심] 마지막 데이터 시각 가져오기
        last_time = df.index[-1].strftime('%Y-%m-%d %H:%M')
        
        # 지표 계산
        rsi = 100 - (100 / (1 + (close.diff().where(close.diff() > 0, 0).rolling(14).mean() / -close.diff().where(close.diff() < 0, 0).rolling(14).mean())))
        willr = -100 * (df['high'].rolling(14).max() - close) / (df['high'].rolling(14).max() - df['low'].rolling(14).min())
        sma20 = close.rolling(20).mean()
        std20 = close.rolling(20).std()
        upper_bb, lower_bb = sma20 + (std20 * 2), sma20 - (std20 * 2)

        # 출력
        is_korea = ".KS" in ticker or ".KQ" in ticker
        unit, fmt = ("원", "{:,.0f}") if is_korea else ("달러($)", "{:,.2f}")
        curr_p = close.iloc[-1]
        
        st.write(f"### 🔍 {user_input} ({ticker})")
        st.markdown(f"<p class='big-font'>현재가: {fmt.format(curr_p)} {unit}</p>", unsafe_allow_html=True)
        # 시각 표시 추가
        st.markdown(f"<p class='time-font'>⏰ 데이터 기준 시각: {last_time} (약 15~20분 지연)</p>", unsafe_allow_html=True)
        
        c_rsi, c_will = rsi.iloc[-1], willr.iloc[-1]
        c_up, c_low = upper_bb.iloc[-1], lower_bb.iloc[-1]
        
        st.write("---")
        if curr_p <= c_low and c_rsi <= 35 and c_will <= -80:
            st.markdown("<div class='buy-signal'>🚨 강력 매수 🚨</div>", unsafe_allow_html=True)
        elif curr_p >= c_up and c_rsi >= 65 and c_will >= -20:
            st.markdown("<div class='sell-signal'>💰 매도 권장 💰</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='wait-signal'>🟡 신호 대기 🟡</div>", unsafe_allow_html=True)

        st.write("---")
        st.subheader("📈 최근 주가 흐름")
        chart_data = pd.DataFrame({'현재가': close, '상단': upper_bb, '하단': lower_bb}).tail(100)
        st.line_chart(chart_data)
      
