import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# 1. 앱 설정
st.set_page_config(page_title="이수 할아버지의 투자 비책", layout="wide")

# [보강] 글씨 크기와 색상을 더 강조한 스타일
st.markdown("""
    <style>
    .big-font { font-size:32px !important; font-weight: bold; margin-bottom: 0px; }
    .index-font { font-size:28px !important; font-weight: bold; color: #007BFF; }
    .time-font { font-size:16px !important; color: #666666; }
    .buy-signal { font-size:55px !important; color: #FF4B4B; font-weight: bold; text-align: center; background-color: #FFEEEE; padding: 25px; border-radius: 15px; border: 3px solid #FF4B4B; }
    .sell-signal { font-size:55px !important; color: #2E7D32; font-weight: bold; text-align: center; background-color: #EEFFEE; padding: 25px; border-radius: 15px; border: 3px solid #2E7D32; }
    .wait-signal { font-size:55px !important; color: #FFA000; font-weight: bold; text-align: center; background-color: #FFF9EE; padding: 25px; border-radius: 15px; border: 3px solid #FFA000; }
    </style>
    """, unsafe_allow_html=True)

st.title("📈 이수 할아버지의 무적 분석기 (지표 강조형)")

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
stock_dict = {"삼성전자": "005930.KS", "유한양행": "000100.KS", "실리콘투": "247020.KQ", "삼성E&A": "028050.KS", "아이온큐": "IONQ", "엔비디아": "NVDA", "넷플릭스": "NFLX"}

user_input = st.text_input("종목 검색 (한글 이름이나 코드 6자리)", value="유한양행").strip()
ticker = stock_dict.get(user_input, user_input).upper()
if user_input.isdigit() and len(user_input) == 6: ticker = user_input + ".KS"

if ticker:
    df = get_safe_data(ticker)
    if df is not None and 'close' in df.columns:
        close = df['close']
        last_time = df.index[-1].strftime('%Y-%m-%d %H:%M')
        
        # 지표 계산
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rsi = 100 - (100 / (1 + (gain / loss)))
        
        high_14 = df['high'].rolling(14).max()
        low_14 = df['low'].rolling(14).min()
        willr = -100 * (high_14 - close) / (high_14 - low_14)
        
        sma20 = close.rolling(20).mean()
        std20 = close.rolling(20).std()
        upper_bb, lower_bb = sma20 + (std20 * 2), sma20 - (std20 * 2)

        # 현재가 및 시각 출력
        is_korea = ".KS" in ticker or ".KQ" in ticker
        unit, fmt = ("원", "{:,.0f}") if is_korea else ("달러($)", "{:,.2f}")
        curr_p = close.iloc[-1]
        
        st.write(f"### 🔍 {user_input} ({ticker})")
        st.markdown(f"<p class='big-font'>현재가: {fmt.format(curr_p)} {unit}</p>", unsafe_allow_html=True)
        st.markdown(f"<p class='time-font'>⏰ 기준 시각: {last_time} (지연 데이터)</p>", unsafe_allow_html=True)
        
        # --- [핵심 추가] RSI와 윌리엄 지수를 왕글씨로 표시 ---
        c_rsi, c_will = rsi.iloc[-1], willr.iloc[-1]
        
        st.write("---")
        col_idx1, col_idx2 = st.columns(2)
        with col_idx1:
            st.markdown(f"**RSI (강도)**")
            st.markdown(f"<p class='index-font'>{c_rsi:.1f}</p>", unsafe_allow_html=True)
        with col_idx2:
            st.markdown(f"**윌리엄 지수**")
            st.markdown(f"<p class='index-font'>{c_will:.1f}</p>", unsafe_allow_html=True)
        # ------------------------------------------------

        # 종합 판독 신호 (가장 크게!)
        st.write("---")
        c_up, c_low = upper_bb.iloc[-1], lower_bb.iloc[-1]
        if curr_p <= c_low and c_rsi <= 35 and c_will <= -80:
            st.markdown("<div class='buy-signal'>🚨 강력 매수 🚨</div>", unsafe_allow_html=True)
        elif curr_p >= c_up and c_rsi >= 65 and c_will >= -20:
            st.markdown("<div class='sell-signal'>💰 매도 권장 💰</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='wait-signal'>🟡 신호 대기 🟡</div>", unsafe_allow_html=True)

        st.write("---")
        st.subheader("📈 주가 및 볼린저 밴드")
        chart_data = pd.DataFrame({'현재가': close, '상단': upper_bb, '하단': lower_bb}).tail(100)
        st.line_chart(chart_data)
