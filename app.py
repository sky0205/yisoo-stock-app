import streamlit as st
import FinanceDataReader as fdr
import pandas as pd

# 1. 고대비 테마 및 대형 텍스트 스타일 설정
st.set_page_config(layout="centered") # 화면 중앙 집중
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    .signal-box { padding: 40px; border-radius: 20px; text-align: center; font-size: 45px; font-weight: bold; color: black; border: 12px solid; margin-bottom: 30px; }
    .buy { background-color: #FFECEC; border-color: #E63946; color: #E63946 !important; }
    .wait { background-color: #FFFBEB; border-color: #F59E0B; color: #92400E !important; }
    .sell { background-color: #ECFDF5; border-color: #10B981; color: #065F46 !important; }
    h1, h2, h3, p, span { color: #1E3A8A !important; font-weight: bold; }
    .trend-card { font-size: 22px; line-height: 1.8; color: #1E293B !important; padding: 25px; background: #F1F5F9; border-left: 10px solid #1E3A8A; border-radius: 12px; }
    .stTable { font-size: 20px !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("👨‍💻 이수할아버지의 텍스트 중심 매매 분석기")

# 2. 종목코드 입력
symbol = st.text_input("📊 종목코드 입력 (예: 005930, NVDA, IONQ)", "005930").strip().upper()

if symbol:
    try:
        # 최근 데이터 가져오기
        df = fdr.DataReader(symbol).tail(30)
        if not df.empty:
            df.columns = [str(c).lower() for c in df.columns]
            close = df['close']
            unit = "$" if not symbol.isdigit() else "원"
            
            # 3. 기술적 지표 계산 (RSI, Williams %R, MACD, Bollinger)
            # RSI
            diff = close.diff(); g = diff.where(diff > 0, 0).rolling(14).mean(); l = -diff.where(diff < 0, 0).rolling(14).mean().replace(0, 0.001)
            rsi = (100 - (100 / (1 + (g/l)))).iloc[-1]
            # Williams %R
            h14 = df['high'].rolling(14).max(); l14 = df['low'].rolling(14).min(); wr = ((h14 - close) / (h14 - l14)).iloc[-1] * -100
            # Bollinger Bands (밴드 위치 파악용)
            ma20 = close.rolling(20).mean(); std20 = close.rolling(20).std()
            upper = ma20 + (std20 * 2); lower = ma20 - (std20 * 2)

            # 4. [신호등 출력] 최상단 배치
            curr_p = close.iloc[-1]
            price_txt = f"{unit}{curr_p:,.2f}" if unit == "$" else f"{curr_p:,.0f}{unit}"
            st.subheader(f"📢 {symbol} 실시간 상태 (현재가: {price_txt})")
            
            if rsi < 35 or wr < -80 or curr_p <= lower.iloc[-1]:
                st.markdown(f"<div class='signal-box buy'>🔴 매수 사정권 (저점)</div>", unsafe_allow_html=True)
            elif rsi > 65 or wr > -20 or curr_p >= upper.iloc[-1]:
                st.markdown(f"<div class='signal-box sell'>🟢 매도 검토 (고점)</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='signal-box wait'>🟡 관망 및 대기 (중립)</div>", unsafe_allow_html=True)

            # 5. [지수 분석 테이블]
            st.write("### 📋 4대 전문 지표 정밀 진단")
            summary = pd.DataFrame({
                "지표 항목": ["현재가", "RSI (매수강도)", "Williams %R", "볼린저 위치"],
                "분석 수치": [price_txt, f"{rsi:.1f}", f"{wr:.1f}", "하단 근접" if curr_p < ma20.iloc[-1] else "상단 근
