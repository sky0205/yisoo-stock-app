import streamlit as st
import FinanceDataReader as fdr
import pandas as pd

# 1. 고대비 및 대형 글자 스타일 설정
st.set_page_config(layout="centered")
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    .signal-box { padding: 35px; border-radius: 15px; text-align: center; font-size: 40px; font-weight: bold; color: black; border: 10px solid; margin-bottom: 25px; }
    .buy { background-color: #FFECEC; border-color: #E63946; color: #E63946 !important; }
    .wait { background-color: #FFFBEB; border-color: #F59E0B; color: #92400E !important; }
    .sell { background-color: #ECFDF5; border-color: #10B981; color: #065F46 !important; }
    h1, h2, h3, p, span { color: #1E3A8A !important; font-weight: bold; }
    .trend-card { font-size: 20px; line-height: 1.8; color: #1E293B !important; padding: 25px; background: #F1F5F9; border-left: 10px solid #1E3A8A; border-radius: 12px; }
    .history-item { padding: 10px; border-bottom: 1px solid #EEE; font-size: 18px; color: #475569; }
    </style>
    """, unsafe_allow_html=True)

# 2. 검색 기록 저장소 (기억 장치)
if 'history' not in st.session_state:
    st.session_state['history'] = []

st.title("👨‍💻 이수할아버지의 '완전체' 분석기 v1300")

# 3. 종목코드 입력
symbol = st.text_input("📊 종목코드 입력 (예: 005930, NVDA, IONQ)", "005930").strip().upper()

if symbol:
    try:
        df = fdr.DataReader(symbol)
        if df is not None and not df.empty:
            # 검색 기록 저장 (중복 제거)
            if symbol not in st.session_state['history']:
                st.session_state['history'].insert(0, symbol)
            
            # 종목명 찾기 로직
            stock_name = symbol
            try:
                krx = fdr.StockListing('KRX')
                name_row = krx[krx['Code'] == symbol]
                if not name_row.empty: stock_name = name_row.iloc[0]['Name']
            except: pass

            df = df.tail(100)
            df.columns = [str(c).lower() for c in df.columns]
            close = df['close']
            unit = "$" if not symbol.isdigit() else "원"
            
            # 지표 계산 (RSI, Williams %R, MACD)
            diff = close.diff(); g = diff.where(diff > 0, 0).rolling(14).mean(); l = -diff.where(diff < 0, 0).rolling(14).mean().replace(0, 0.001)
            rsi = (100 - (100 / (1 + (g/l)))).iloc[-1]
            h14 = df['high'].rolling(14).max(); l14 = df['low'].rolling(14).min(); wr = ((h14 - close) / (h14 - l14)).iloc[-1] * -100
            
            exp12 = close.ewm(span=12).mean(); exp26 = close.ewm(span=26).mean()
            macd = exp12 - exp26; signal = macd.ewm(span=9).mean()

            # 4. [상단 출력] 종목명과 현재가
            curr_p = close.iloc[-1]
            price_txt = f"{unit}{curr_p:,.2f}" if unit == "$" else f"{curr_p:,.0f}{unit}"
            st.subheader(f"🏢 {stock_name} ({symbol})")
            st.write(f"## 현재가: {price_txt}")

            # 5. [신호등]
            if rsi < 35 or wr < -80:
                st.markdown(f"<div
