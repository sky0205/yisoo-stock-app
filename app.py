import streamlit as st
import FinanceDataReader as fdr
import pandas as pd
import altair as alt

# 1. 고대비 & 대형 글자 스타일
st.set_page_config(layout="wide")
st.markdown("""
    <style>
    .stApp { background-color: #FFFFFF; }
    .signal-box { padding: 30px; border-radius: 15px; text-align: center; font-size: 40px; font-weight: bold; color: black; border: 12px solid; margin-bottom: 20px; }
    .buy { background-color: #FFCCCC; border-color: #FF0000; }
    .wait { background-color: #FFFFCC; border-color: #FFCC00; }
    .sell { background-color: #CCFFCC; border-color: #00FF00; }
    h1, h2, h3, p { color: #1E3A8A !important; font-weight: bold !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("👨‍💻 이수할아버지의 볼린저 매매 분석기")

# 2. 종목코드 입력 (이름 대신 코드로만 작동)
symbol = st.text_input("📊 종목코드 6자리 또는 티커 입력 (예: 005930, NVDA, IONQ)", "005930").strip().upper()

if symbol:
    # 최신 데이터를 위해 시작 날짜를 자동으로 계산
    df = fdr.DataReader(symbol)
    
    if not df.empty:
        df = df.tail(120) # 최근 120일치만 보기 좋게 추출
        close = df['Close']
        
        # 3. 볼린저 밴드 계산 ($MA_{20} \pm 2\sigma$)
        ma20 = close.rolling(20).mean()
        std20 = close.rolling(20).std()
        df['Upper'] = ma20 + (std20 * 2)
        df['Lower'] = ma20 - (std20 * 2)
        df['MA20'] = ma20

        # 4. 보조지표 (RSI, Williams %R)
        diff = close.diff(); g = diff.where(diff > 0, 0).rolling(14).mean(); l = -diff.where(diff < 0, 0).rolling(14).mean().replace(0, 0.001)
        rsi = (100 - (100 / (1 + (g/l)))).iloc[-1]
        h14 = df['High'].rolling(14).max(); l14 = df['Low'].rolling(14).min(); wr = ((h14 - close) / (h14 - l14)).iloc[-1] * -100

        # 5. [신호등 출력]
        st.write("---")
        curr_p = close.iloc[-1]
        st.subheader(f"📢 {symbol} 실시간 분석 (현재가: {curr_p:,.0f}원)")
        
        if rsi < 35 or curr_p <= df['Lower'].iloc[-1]:
            st.markdown(f"<div class='signal-box buy'>🔴 매수 사정권 (밴드 하단)</div>", unsafe_allow_html=True)
        elif rsi > 65 or curr_p >= df['Upper'].iloc[-1]:
            st.markdown(f"<div class='signal-box sell'>🟢 매도 검토 (밴드 상단)</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='signal-box wait'>🟡 관망 유지 (밴드 내부)</div>", unsafe_allow_html=True)

        # 6. [볼린저 밴드 그래프] - 주가 그래프 대신 출력
        df_plot = df.reset_index()
        base = alt.Chart(df_plot).encode(x='Date:T')
        
        # 밴드 영역 (상단~하단 사이 채우기)
        band = base.mark_area(opacity=0.2, color='gray').encode(y='Lower:Q', y2='Upper:Q')
        # 주가 선
        line = base.mark_line(color='#1E40AF', size=3).encode(y=alt.Y('Close:Q', scale=alt.Scale(zero=False)))
        # 상/하단 선
        upper_l = base.mark_line(color='red', strokeDash=[5,5]).encode(y='Upper:Q')
        lower_l = base.mark_line(color='green', strokeDash=[5,5]).encode(y='Lower:Q')

        st.altair_chart(band + line + upper_l + lower_l, use_container_width=True)

        # 7. [상세 분석표]
        st.write("### 📋 분석 요약 보고서")
        summary = pd.DataFrame({
            "지표": ["현재가", "RSI 강도", "볼린저 위치", "Williams %R"],
            "수치": [f"{curr_p:,.0f}", f"{rsi:.1f}", "상단 근접" if curr_p > ma20.iloc[-1] else "하단 근접", f"{wr:.1f}"],
            "판단": ["-", "저점" if rsi < 30 else "고점" if rsi > 70 else "중립", "과열" if curr_p >= df['Upper'].iloc[-1] else "저평가", "매수권" if wr < -80 else "보통"]
        })
        st.table(summary)
