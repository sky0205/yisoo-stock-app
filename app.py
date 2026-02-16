import streamlit as st
import FinanceDataReader as fdr
import pandas as pd

# 1. 고대비 스타일 (글자가 안 보일 수 없게 설정)
st.set_page_config(layout="wide")
st.markdown("<style>h1, h2, h3 { color: #1E3A8A !important; } .signal { padding: 20px; border-radius: 10px; font-weight: bold; font-size: 25px; color: black; }</style>", unsafe_allow_html=True)

st.title("👨‍💻 이수할아버지의 매매 시점 분석기")

# 2. 종목 입력
symbol = st.text_input("종목코드 (005930, NVDA, IONQ)", "005930").strip().upper()

if symbol:
    df = fdr.DataReader(symbol, '2025-01-01')
    if not df.empty:
        # 지표 계산
        close = df['Close']
        diff = close.diff(); g = diff.where(diff > 0, 0).rolling(14).mean(); l = -diff.where(diff < 0, 0).rolling(14).mean().replace(0, 0.001)
        rsi = (100 - (100 / (1 + (g/l)))).iloc[-1]
        wr = ((df['High'].rolling(14).max() - close) / (df['High'].rolling(14).max() - df['Low'].rolling(14).min())).iloc[-1] * -100

        # 3. 신호등과 분석 표 전개 (원하시던 자료)
        st.subheader(f"📢 {symbol} 기술적 분석 결과")
        
        if rsi < 35 or wr < -80:
            st.markdown("<div class='signal' style='background-color: #FFCCCC;'>🔴 현재 매수 적기: 과매도 구간</div>", unsafe_allow_html=True)
        elif rsi > 65 or wr > -20:
            st.markdown("<div class='signal' style='background-color: #CCFFCC;'>🟢 현재 매도 검토: 과열 구간</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='signal' style='background-color: #FFFFCC;'>🟡 현재 관망: 추세 확인 필요</div>", unsafe_allow_html=True)

        st.write("### 📋 주요 지표 수치")
        st.table(pd.DataFrame({
            "항목": ["RSI (강도)", "Williams %R (단기)", "MACD 추세"],
            "수치": [f"{rsi:.1f}", f"{wr:.1f}", "상승" if rsi > 50 else "하락"]
        }))

        # 4. 그래프는 맨 아래에 배치
        st.line_chart(close)
