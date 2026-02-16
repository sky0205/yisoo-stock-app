import streamlit as st
import FinanceDataReader as fdr
import pandas as pd

# 스타일 설정
st.set_page_config(layout="centered")
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    .signal-box { padding: 30px; border-radius: 15px; text-align: center; font-size: 38px; font-weight: bold; border: 10px solid; margin-bottom: 20px; }
    .buy { background-color: #FFECEC; border-color: #E63946; color: #E63946; }
    .wait { background-color: #FFFBEB; border-color: #F59E0B; color: #92400E; }
    .sell { background-color: #ECFDF5; border-color: #10B981; color: #065F46; }
    .trend-card { font-size: 20px; line-height: 1.8; color: #1E293B; padding: 20px; background: #F8FAFC; border-left: 10px solid #1E3A8A; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

if 'target' not in st.session_state: st.session_state['target'] = "257720"

st.title("👨‍💻 이수할아버지의 '글로벌' 분석기 v2500")

# 실시간 환율 가져오기 (원/달러)
try:
    usd_krw = fdr.DataReader('USD/KRW').iloc[-1]['close']
except:
    usd_krw = 1350.0  # 오류 시 기본값

symbol = st.text_input("📊 종목코드 입력 (예: 257720 또는 NVDA)", value=st.session_state['target']).strip().upper()

if symbol:
    try:
        df = fdr.DataReader(symbol).tail(120)
        if not df.empty:
            df.columns = [str(c).lower() for c in df.columns]
            curr_p = df['close'].iloc[-1]
            
            # 미국 주식 여부 판단
            is_us = not symbol.isdigit()
            
            # 제목 출력
            st.header(f"🏢 {symbol} 분석 결과")
            if is_us:
                st.subheader(f"현재가: ${curr_p:,.2f} (약 {curr_p * usd_krw:,.0f}원)")
                st.caption(f"기준 환율: 1달러당 {usd_krw:,.1f}원")
            else:
                st.subheader(f"현재가: {curr_p:,.0f}원")

            # 지표 계산 로직 (이전과 동일)
            ma20 = df['close'].rolling(20).mean(); std20 = df['close'].rolling(20).std()
            lo_b = ma20 - (std20 * 2); up_b = ma20 + (std20 * 2)
            exp12 = df['close'].ewm(span=12, adjust=False).mean(); exp26 = df['close'].ewm(span=26, adjust=False).mean()
            macd = exp12 - exp26; signal = macd.ewm(span=9, adjust=False).mean()
            h14 = df['high'].rolling(14).max(); l14 = df['low'].rolling(14).min(); wr = ((h14 - df['close']) / (h14 - l14)).iloc[-1] * -100
            
            # 신호등 및 추세 진단
            is_buy = curr_p <= lo_b.iloc[-1] or wr < -80
            if is_buy:
                st.markdown("<div class='signal-box buy'>🔴 매수 사정권 진입</div>", unsafe_allow_html=True)
                msg = "현재 바닥을 다지며 **조심스럽게 바닥 확인 중**입니다."
            else:
                st.markdown("<div class='signal-box wait'>🟡 관망 및 대기</div>", unsafe_allow_html=True)
                msg = "추세를 관망하며 숨을 고르는 중입니다."

            st.markdown(f"<div class='trend-card'><b>종합 의견:</b> {msg}</div>", unsafe_allow_html=True)
