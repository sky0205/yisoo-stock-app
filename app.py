import streamlit as st
import yfinance as yf
import pandas as pd

# 1. 앱 설정
st.set_page_config(page_title="이수 할아버지의 투자 비책", layout="wide")

# [보강] 글씨 크기를 키우는 특별 마술 (CSS 스타일)
st.markdown("""
    <style>
    .big-font { font-size:30px !important; font-weight: bold; }
    .buy-signal { font-size:50px !important; color: #FF4B4B; font-weight: bold; text-align: center; background-color: #FFEEEE; padding: 20px; border-radius: 10px; }
    .sell-signal { font-size:50px !important; color: #2E7D32; font-weight: bold; text-align: center; background-color: #EEFFEE; padding: 20px; border-radius: 10px; }
    .wait-signal { font-size:50px !important; color: #FFA000; font-weight: bold; text-align: center; background-color: #FFF9EE; padding: 20px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("📈 나만의 투자 비책 (왕글씨 버전)")

@st.cache_data(ttl=600)
def get_safe_data(ticker):
    try:
        df = yf.download(ticker, period="1y", multi_level_index=False)
        if df is None or df.empty: return None
        if isinstance(df.columns, pd.MultiIndex): df.columns = df.columns.get_level_values(0)
        df.columns = [str(col).lower() for col in df.columns]
        return df
    except: return None

if 'history' not in st.session_state: st.session_state['history'] = []
stock_dict = {"삼성전자": "005930.KS", "유한양행": "000100.KS", "실리콘투": "247020.KQ", "아이온큐": "IONQ"}

user_input = st.text_input("종목 검색 (이름을 입력하세요)", value="유한양행").strip()
ticker = stock_dict.get(user_input, user_input).upper()

if ticker:
    df = get_safe_data(ticker)
    if df is not None and 'close' in df.columns:
        if user_input not in st.session_state['history']: st.session_state['history'].insert(0, user_input)
        
        close = df['close']
        # 지표 계산 (RSI, 윌리엄, 볼린저)
        rsi = 100 - (100 / (1 + (close.diff().where(close.diff() > 0, 0).rolling(14).mean() / -close.diff().where(close.diff() < 0, 0).rolling(14).mean())))
        willr = -100 * (df['high'].rolling(14).max() - close) / (df['high'].rolling(14).max() - df['low'].rolling(14).min())
        sma20 = close.rolling(20).mean()
        std20 = close.rolling(20).std()
        upper_bb, lower_bb = sma20 + (std20 * 2), sma20 - (std20 * 2)

        is_korea = ticker.endswith(".KS") or ticker.endswith(".KQ")
        unit, fmt = ("원", "{:,.0f}") if is_korea else ("달러($)", "{:,.2f}")
        curr_p = close.iloc[-1]
        
        st.write(f"### 🔍 {user_input} ({ticker})")
        st.markdown(f"<p class='big-font'>현재가: {fmt.format(curr_p)} {unit}</p>", unsafe_allow_html=True)
        
        c_rsi, c_will = rsi.iloc[-1], willr.iloc[-1]
        c_up, c_low = upper_bb.iloc[-1], lower_bb.iloc[-1]
        
        # --- [왕글씨 결과창] ---
        st.write("---")
        if curr_p <= c_low and c_rsi <= 35 and c_will <= -80:
            st.markdown("<div class='buy-signal'>🚨 강력 매수 🚨</div>", unsafe_allow_html=True)
            st.write("모든 지표가 바닥입니다! 지금이 기회입니다.")
        elif curr_p >= c_up and c_rsi >= 65 and c_will >= -20:
            st.markdown("<div class='sell-signal'>💰 매도 권장 💰</div>", unsafe_allow_html=True)
            st.write("주가가 천장에 닿았습니다. 수익 실현을 고려하세요.")
        else:
            st.markdown("<div class='wait-signal'>🟡 신호 대기 🟡</div>", unsafe_allow_html=True)
            st.write("현재는 안정권입니다. 느긋하게 지켜보세요.")

        # 그래프 및 상세 수치
        st.write("---")
        st.subheader("📈 주가 및 볼린저 밴드")
        chart_data = pd.DataFrame({'현재가': close, '상단': upper_bb, '하단': lower_bb}).tail(100)
        st.line_chart(chart_data)
        
        col1, col2, col3 = st.columns(3)
        col1.metric("RSI 강도", f"{c_rsi:.1f}")
        col2.metric("윌리엄 지수", f"{c_will:.1f}")
        col3.metric("밴드 하단", f"{fmt.format(c_low)}")
