import streamlit as st
import FinanceDataReader as fdr
import pandas as pd

# 1. 고대비 스타일 및 버튼 색상(흰 바탕/파랑) 설정
st.set_page_config(layout="centered")
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    /* 버튼 스타일: 흰 바탕에 파란 글씨/테두리 */
    div.stButton > button:first-child {
        background-color: white !important;
        color: #1E3A8A !important;
        border: 2px solid #1E3A8A !important;
        font-weight: bold !important;
        border-radius: 10px;
    }
    div.stButton > button:hover {
        background-color: #F1F5F9 !important;
        border: 2px solid #1E40AF !important;
    }
    .signal-box { padding: 35px; border-radius: 15px; text-align: center; font-size: 42px; font-weight: bold; color: black; border: 12px solid; margin-bottom: 25px; }
    .buy { background-color: #FFECEC; border-color: #E63946; color: #E63946 !important; }
    .wait { background-color: #FFFBEB; border-color: #F59E0B; color: #92400E !important; }
    .sell { background-color: #ECFDF5; border-color: #10B981; color: #065F46 !important; }
    h1, h2, h3, p, span { color: #1E3A8A !important; font-weight: bold; }
    .trend-card { font-size: 21px; line-height: 1.8; color: #1E293B !important; padding: 25px; background: #F8FAFC; border-left: 12px solid #1E3A8A; border-radius: 12px; }
    </style>
    """, unsafe_allow_html=True)

# 2. 기억 장치 설정
if 'history' not in st.session_state: st.session_state['history'] = []
if 'sel_sym' not in st.session_state: st.session_state['sel_sym'] = "005930"

st.title("👨‍💻 이수할아버지의 정밀 추세 분석기 v1800")

# 3. 종목 입력창
symbol = st.text_input("📊 종목코드 입력", value=st.session_state['sel_sym']).strip().upper()

# 4. 분석 엔진
if symbol:
    try:
        df = fdr.DataReader(symbol)
        if df is not None and not df.empty:
            if symbol not in st.session_state['history']:
                st.session_state['history'].insert(0, symbol)
            
            # 종목명 찾기
            stock_name = symbol
            try:
                krx = fdr.StockListing('KRX')
                stock_name = krx[krx['Code'] == symbol].iloc[0]['Name']
            except: pass

            df = df.tail(120)
            df.columns = [str(c).lower() for c in df.columns]
            close = df['close']
            unit = "$" if not symbol.isdigit() else "원"
            
            # 지표 계산: 볼린저 밴드
            ma20 = close.rolling(20).mean()
            std20 = close.rolling(20).std()
            upper_b = ma20 + (std20 * 2)
            lower_b = ma20 - (std20 * 2)
            
            # RSI 및 MACD
            diff = close.diff(); g = diff.where(diff > 0, 0).rolling(14).mean(); l = -diff.where(diff < 0, 0).rolling(14).mean().replace(0, 0.001)
            rsi = (100 - (100 / (1 + (g/l)))).iloc[-1]
            
            exp12 = close.ewm(span=12, adjust=False).mean(); exp26 = close.ewm(span=26, adjust=False).mean()
            macd = exp12 - exp26; signal = macd.ewm(span=9, adjust=False).mean()

            # 5. [출력] 종목명과 현재가
            curr_p = close.iloc[-1]
            price_txt = f"{unit}{curr_p:,.2f}" if unit == "$" else f"{curr_p:,.0f}{unit}"
            st.subheader(f"🏢 {stock_name} ({symbol})")
            st.write(f"## 현재가: {price_txt}")

            # 6. 신호등
            if rsi < 35 or curr_p <= lower_b.iloc[-1]:
                st.markdown(f"<div class='signal-box buy'>🔴 매수 사정권 진입</div>", unsafe_allow_html=True)
            elif rsi > 65 or curr_p >= upper_b.iloc[-1]:
                st.markdown(f"<div class='signal-box sell'>🟢 매도 검토 구간</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='signal-box wait'>🟡 관망 및 대기</div>", unsafe_allow_html=True)

            # 7. [지수 및 볼린저 수치 테이블]
            st.write("### 📋 핵심 기술 지표 및 볼린저 밴드 수치")
            st.table(pd.DataFrame({
                "지표 항목": ["볼린저 상단", "볼린저 중단(MA20)", "볼린저 하단", "RSI 강도", "MACD 추세"],
                "분석 수치": [
                    f"{upper_b.iloc[-1]:,.2f}{unit}", 
                    f"{ma20.iloc[-1]:,.2f}{unit}", 
                    f"{lower_b.iloc[-1]:,.2f}{unit}",
                    f"{rsi:.1f}", 
                    "상승" if macd.iloc[-1] > signal.iloc[-1] else "하락"
